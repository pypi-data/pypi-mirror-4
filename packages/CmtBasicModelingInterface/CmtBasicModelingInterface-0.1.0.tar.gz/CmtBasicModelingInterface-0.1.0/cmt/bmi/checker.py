"""
A checker plugin for pylint that looks for BMI compliance.
"""
import logilab
from logilab import astng

from logilab.common.ureports import Table, Section
from logilab.common.ureports import List as ReportList
from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker, table_lines_from_stats

METHOD_RETURN_TYPES = {
    'initialize': ('None', ),
    'update': ('None', ),
    'update_until': ('None', ),
    'finalize': ('None', ),
    'get_input_var_names': ('list:str', 'tuple:str', ),
    'get_output_var_names': ('list:str', 'tuple:str', ),
    'get_component_name': ('str', ),
    'get_time_step': ('float', ),
    'get_start_time': ('float', ),
    'get_current_time': ('float', ),
    'get_end_time': ('float', ),
    'get_grid_shape': ('list:float', 'tuple:int', ),
    'get_grid_spacing': ('list:float', 'tuple:float', ),
    'get_grid_origin': ('list:float', 'tuple:float', ),
    'set_value': ('None', ),
    'set_value_at_indices': ('None', ),
    'get_var_rank': ('int', ),
    'get_var_units': ('str', ),
    'get_var_type': ('str', ),
    'get_grid_type': ('cmt.bmi.interfaces.BmiGridType', ),
}


def split_type_string(type_str):
    """
    Split a type string into it's parent and child components. If there
    is not child type, return an empty string for the child type.

    :type_str: A type string

    :returns: A tuple of parent and child types
    """
    try:
        (parent, child) = type_str.split(':', 1)
    except ValueError:
        (parent, child) = (type_str, '')

    return (parent, child)


def split_type_strings(type_strs):
    """
    Split a series of type strings into their parent/child components.

    :type_strs: Iterable of type strings

    :returns: A tuple of lists of parent and child types
    """
    parents = []
    children = []
    for type_str in type_strs:
        (parent, child) = split_type_string(type_str)
        parents.append(parent)
        if child:
            children.append(child)

    return (parents, children)


def node_matches_type(node, expected_types):
    """
    Check if a node (and perhaps it's children) match a given type string.

    :node: A astng node
    :expected_type: List of expected types

    :returns: True if the node's type matches
    """
    node_type = str(node.pytype())

    if node_type == 'YES':
        return True

    if node_type.startswith('__builtin__.'):
        node_type = node_type[len('__builtin__.'):]

    parent_types, child_types = split_type_strings(expected_types)

    if node_type in parent_types:
        matches = True

        if len(child_types) > 0:
            try:
                for item in node.itered():
                    if not node_matches_type(item, child_types):
                        matches = False
                        break
            except (AttributeError, TypeError):
                raise TypeError('Node is not iterable')
    else:
        matches = False

    return matches


def camel_case_to_words(name):
    """
    Convert a CamelCase word to separate words as a title.

    >>> camel_case_to_words(CamelCase)
    Camel Case

    :name: Camelcase string

    :returns: The converted string
    """
    import re
    str_1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', str_1).title()


def report_bmi(sect, stats, old_stats):
    """
    make a layout with some BMI stats.
    """
    lines = ['', 'now', 'previous', 'difference']
    lines += table_lines_from_stats(stats, old_stats,
                                    ('total_bmi_classes',
                                     'input_item_count',
                                     'output_item_count',
                                    ))
    sect.append(Table(children=lines, cols=4, rheaders=1, cheaders=1))

    grid_sect = Section('Implemented Grid Types')
    lines = []
    for name in stats['grid_type']:
        lines.append(name)
    grid_sect.append(ReportList(children=lines))
    sect.append(grid_sect)

    input_sect = Section('Input Exchange Items')
    lines = []
    for name in stats['input_item_names']:
        lines.append(name)
    input_sect.append(ReportList(children=lines))
    sect.append(input_sect)

    output_sect = Section('Output Exchange Items')
    lines = []
    for name in stats['output_item_names']:
        lines.append(name)
    output_sect.append(ReportList(children=lines))
    sect.append(output_sect)


class BmiChecker(BaseChecker):
    """
    Check a BMI implementation.
    """
    __implements__ = IASTNGChecker

    name = 'bmi_check'
    msgs = {
        'W9999': (
            'Class implements BmiBase but defines no input vars',
            'bmi-no-input-vars',
            'A BMI class should provides lists of input items'
        ),
        'W9998': (
            'Class implements BmiBase but defines no output vars',
            'bmi-no-output-vars',
            'A BMI class should provides lists of output items'
        ),
        'W9997': (
            'Exchange item is not a valid standard name',
            'bmi-bad-standard-name',
            'Input and output names must be valid CSDMS standard name'
        ),
        'W9996': (
            'Exchange items should be a list/tuple',
            'bmi-bad-exchange-items-type',
            'Input and output names must be lists of CSDMS standard names'
        ),
        'W9995': (
            'Method does not return expected type',
            'bmi-bad-return-type',
            'BMI method return value is not that expected by the BMI'
        ),
        'W9994': (
            'BMI implementation does not have a valid grid type',
            'bmi-bad-type',
            'BMI implementation should implement a BMI grid type interface'
        ),
    }
    options = ()
    # reports
    reports = (('RP9999', 'Basic Modeling Interface Summary', report_bmi), )

    priority = -1

    _in_class = False

    def __init__(self, linter=None):
        BaseChecker.__init__(self, linter)
        self.stats = None

    def open(self):
        """init statistics"""
        self.stats = self.linter.add_stats(total_bmi_classes=0,
                                           input_item_count=0,
                                           output_item_count=0,
                                           grid_type=set(),
                                           input_item_names=set(),
                                           output_item_names=set())

    def visit_class(self, node):
        """Visit a Class that implements a BMI, checking exchange items."""
        if _is_bmi(node):
            self.stats['total_bmi_classes'] += 1
            self._in_class = True

            self._check_grid_type(node)
            self._check_has_exchange_items(node, 'input')
            self._check_has_exchange_items(node, 'output')

    def leave_class(self, node):
        """Leave a Class node."""
        if self._in_class:
            assert(_is_bmi(node))
            self._in_class = False

    def visit_assign(self, node):
        """Check exchange item assignment."""
        if self._in_class:
            self._check_exchange_items(node)

    def visit_function(self, node):
        """
        Check if function return type matches what's expected

        :node: A Class node
        """
        if self._in_class:
            if node.name in METHOD_RETURN_TYPES:
                results = node.infer_call_result(None)
                for result in results:
                    if (not node_matches_type(result,
                                              METHOD_RETURN_TYPES[node.name])):
                        print result.pytype()
                        self.add_message('W9995', node=node)

    def _check_exchange_items(self, node):
        """
        Check for a valid exchange item assignment.

        :node: An Assign node
        """
        try:
            target_name = node.targets[0].name
        except AttributeError:
            return

        if target_name == 'input_vars':
            intent = 'input'
            stat_count = 'input_item_count'
        elif target_name == 'output_vars':
            intent = 'output'
            stat_count = 'output_item_count'
        else:
            return

        if (isinstance(node.value, astng.List) or
            isinstance(node.value, astng.Tuple)):

            name_iterable = node.value.itered()
            for name_const in name_iterable:
                if '__' in name_const.value:
                    self.stats[intent + '_item_names'].add(name_const.value)
                else:
                    self.add_message('W9997', node=name_const)
            self.stats[stat_count] += len(name_iterable)
        else:
            self.add_message('W9996', node=node.value)

    def _check_has_exchange_items(self, node, intent):
        """Check if class defines input or output exchange items"""
        assert(intent in ['input', 'output'])

        try:
            _ = node.local_attr(intent + '_vars')
        except logilab.astng.exceptions.NotFoundError:
            if intent == 'input':
                self.add_message('W9999', node=node)
            else:
                self.add_message('W9998', node=node)

    def _check_grid_type(self, node):
        """Check the BMI grid type"""
        grid_interfaces = set(['BmiUniformRectilinear', 'BmiRectilinear',
                               'BmiStructured', 'BmiUnstructured'])
        found_types = set([iface.name for iface in node.interfaces()])
        grid_types = found_types & grid_interfaces

        if len(grid_types) == 0:
            self.add_message('W9994', node=node)
        else:
            names = [camel_case_to_words(grid_type[3:])
                     for grid_type in grid_types]
            self.stats['grid_type'] |= set(names)


def _is_bmi(node):
    """Check if a class implements a BMI"""
    #return 'BmiBase' in node.interfaces()
    for iface in node.interfaces():
        if iface.name in ['BmiBase']:
            return True
    return False


def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(BmiChecker(linter))
