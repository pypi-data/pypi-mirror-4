"""
Example utility class to read data from a text file.
"""
#
# Copyright (c) 2009-2013, Scott D. Peckham
#
# Moved here from model_tests.py on 3/14/13.

#--------------------------------------------------------
# class input_file
#
#    __init__()
#    open()
#    check_format()
#    count_lines()
#    read_record()
#    read_value()
#    read_all()
#    close()
#
#--------------------------------------------------------
from __future__ import print_function

import sys
import numpy

from cmt.bmi import BmiBase, BmiNoGrid
from cmt.bmi import (BadVarNameError, TimeBoundsError,
                     MissingModelAttributeError, FatalError)


class Error(Exception):
    """
    Base class for exceptions for this module
    """
    pass


class InputFile(object):
    """
    Example utility class to read data from a text file.
    """
    def __init__(self, filename='data.txt'):

        self.filename = filename
        self.n_lines = 0
        self.n_vals = 0
        self.format = 'unknown'
        self.file = None
        self.data = numpy.zeros(0, dtype='d')

        self.count_lines()   # (set self.n_lines)

        #------------------------------------------------
        # Check format of input data to set self.format
        # to 'numeric', 'key_value' or 'words'.
        #------------------------------------------------
        self.check_format()  # (set self.format string)

    def open(self):
        """
        Open a data file for reading.
        """
        try:
            data_file = open(self.filename, 'r')
        except IOError:
            raise
        self.file = data_file   # save the file object as an attribute

    def check_format(self):
        """
        Guess at the format of the file. The result is stored internally
        within the class's format member. The format will be one of the
        following strings:
            - 'numeric': Lines contain numbers
            - 'key_value': Lines contain key=value pairs
            - 'unknown': An unknown format
        """

        self.open()

        record = self.read_record(data_format='words')
        n_words = len(record)

        #--------------------------------------
        # Is first value a number or keyword ?
        #--------------------------------------
        try:
            _ = numpy.float64(record[0])
            data_format = 'numeric'
        except ValueError:
            data_format = 'unknown'
            if (n_words > 1):
                if (record[1] == "="):
                    data_format = 'key_value'

        self.format = data_format
        #print '   data format =', data_format
        #print ' '
        self.close()

    def count_lines(self):
        """
        Count the data lines and values of the file. Ignore blank lines. The
        result is stored internally within the class memberss n_lines and
        n_vals.
        """

        self.open()
        ## print 'Counting lines in file...'

        n_lines = 0
        n_vals = 0
        for line in self.file:
            #-------------------------------------
            # Note: len(line) == 1 for null lines
            #-------------------------------------
            if (len(line.strip()) > 0):
                n_lines = (n_lines + 1)
                words = line.split()
                n_words = len(words)
                n_vals = max(n_vals, n_words)
        self.n_lines = n_lines
        self.n_vals = n_vals

        #--------------------------------------
        # Initialize an array for reading data
        #--------------------------------------
        self.data = numpy.zeros([n_lines, n_vals], dtype='d')
        self.data = self.data - 9999.0
        self.close()

    def read_record(self, data_format='not_set', dtype='double'):
        """
        Read a record from a line of a data file. The format of the returned
        depends on the value of the data_format keyword.

        Valid choices for data_format are:
            - 'numeric': Convert each word in the line to a numpy type and
                         return as a list of numbers.
            - 'key_value': Scan the line as a key/value assignment and return
                           as a tuple.
            - 'words': Split the line by whitespace and return the resulting
                       list of words.

        :keyword data_format: The format of the data
        :keyword dtype: Data type as a numpy type

        :returns: The data from the scanned line
        """

        # Should this be named "next_record" ?
        if (data_format == 'not_set'):
            data_format = self.format

        line = self.file.readline()
        while (len(line.strip()) == 0):
            line = self.file.readline()
        words = line.split()

        if (data_format == 'numeric'):
            return [numpy.float64(word) for word in words]
        if (data_format == 'key_value'):
            key = words[0]
            value = words[2]
            if (dtype == 'double'):
                value = numpy.float64(value)
            if (dtype == 'integer'):
                value = numpy.int16(value)
            return [key, value]
        if (data_format == 'words'):
            return words

    def scan_record(self, line, data_format='not_set', dtype='double'):
        """
        Scan a record from a string. The format of the returned depends on the
        value of the data_format keyword.

        Valid choices for data_format are:
            - 'numeric': Convert each word in the line to a numpy type and
                         return as a list of numbers.
            - 'key_value': Scan the line as a key/value assignment and return
                           as a tuple.
            - 'words': Split the line by whitespace and return the resulting
                       list of words.

        :keyword data_format: The format of the data
        :keyword dtype: Data type as a numpy type

        :returns: The data from the scanned line
        """
        assert(data_format in ['not_set', 'numeric', 'key_value', 'words'])

        if (data_format == 'not_set'):
            data_format = self.format

        if (data_format == 'numeric'):
            return [numpy.float64(word) for word in line.split()]
        elif (data_format == 'key_value'):
            (key, value) = line.split('=')
            if (dtype == 'double'):
                value = numpy.float64(value)
            if (dtype == 'integer'):
                value = numpy.int16(value)
            return (key, value)
        else:
            return line.split()

    def read_value(self, dtype='double'):
        """
        Read a value from a data file.

        :keyword dtype: The type of the value as a numpy type.

        :returns: The scanned value
        """

        # Should this be named "next_value" ?
        record = self.read_record(dtype=dtype)
        if (self.format == 'numeric'):
            return record[0]
        if (self.format == 'key_value'):
            return record[1]

    def read_all(self):
        """
        Read all the lines of an input file. The numeric data is placed in the
        class's data member as a numpy array.

        :warning: Currently assumes all values are doubles, but read_record()
                  and read_value() do not.
        """

        if (self.n_lines == 0):
            self.count_lines()

        self.open()
        for (row, line) in enumerate(self.file):
            record = self.scan_record(line)
            if self.format == 'numeric':
                for col in range(0, len(record)):
                    self.data[row, col] = numpy.float64(record[col])
            elif self.format == 'key_value':
                self.data[row, 0] = numpy.float64(record[1])
        self.close()

    def close(self):
        """
        Close the data file.
        """
        try:
            self.file.close()
        except AttributeError:
            pass


class Rainfall(InputFile):
    """
    Wrap an InputFile as a BMI component
    """

    __implements__ = (BmiBase, BmiNoGrid, )

    model_name = 'Input_File_Reader'
    version = 0.1
    author_name = 'Scott D. Peckham'
    grid_type = 'none'
    time_step_type = 'variable'
    step_method = 'explicit'
    time_units = 'seconds'

    _input_var_names = [
    ]

    _output_var_names = [
        'atmosphere_water__liquid_equivalent_precipitation_rate',
        'atmosphere_water__precipitation_duration',
    ]

    _var_units = {
        'atmosphere_water__liquid_equivalent_precipitation_rate': 'm s-1',
        'atmosphere_water__precipitation_duration': 's',
    }

    _var_type = {
        'atmosphere_water__liquid_equivalent_precipitation_rate': 'float64',
        'atmosphere_water__precipitation_duration': 'float64',
    }

    _var_rank = {
        'atmosphere_water__liquid_equivalent_precipitation_rate': 0,
        'atmosphere_water__precipitation_duration': 0,
    }

    def __init__(self):
        self._time_index = 0
        self._time = 0.
        self._start_time = 0.
        self._end_time = 0.

    def get_attribute(self, attrib_name):
        """
        Get a static attribute of the model

        :att_name: Name of the attribute as a string

        :returns: The model's attribute (always as a string?)
        """
        try:
            return getattr(self, attrib_name.lower())
        except AttributeError:
            raise MissingModelAttributeError(attrib_name)

    def get_input_var_names(self):
        """
        List of model's input items as standard name strings

        :returns: List of standard name strings
        """
        return self._input_var_names

    def get_output_var_names(self):
        """
        List of model's output items as standard name strings

        :returns: List of standard name strings
        """
        return self._output_var_names

    def get_var_units(self, long_var_name):
        """
        Variable units from a standard name.

        :long_var_name: Standard name as a string

        :returns: Units as a udunits string
        """
        try:
            return self._var_units[long_var_name]
        except KeyError:
            raise BadVarNameError(long_var_name)

    def get_var_type(self, long_var_name):
        """
        Variable type as a numpy units string.

        :long_var_name: Standard name as a string

        :returns: Units as a numpy.dtype string
        """
        try:
            return self._var_type[long_var_name]
        except KeyError:
            raise BadVarNameError(long_var_name)

    def get_var_rank(self, long_var_name):
        """
        Rank of an exchange item.

        :long_var_name: Standard name as a string

        :returns: Rank of the variable
        """
        try:
            return self._var_rank[long_var_name]
        except KeyError:
            raise BadVarNameError(long_var_name)

    def get_start_time(self):
        """
        Start time of the model.

        :returns: Start time (with units provided by get_time_units method)
        """
        return self._start_time

    def get_end_time(self):
        """
        End time of the model

        :returns: End time (with units provided by get_time_units method)
        """
        return self._end_time

    def get_current_time(self):
        """
        Current time of the model

        :returns: Current time (with units provided by get_time_units method)
        """
        return self._time

    def get_time_step(self):
        """
        Model time step. This is the time that this class' update method
        runs the model for.

        :returns: Time step (with units provided by get_time_units method)
        """
        return self.data[self._time_index, 1]

    def get_time_units(self):
        """
        Unit of all time variables of this model.

        :returns: Units as udunits string
        """
        return 'seconds'

    def initialize(self, filename):
        """
        Initialize model with a rain data file

        :cfg_file: Name of data file
        """
        try:
            super(Rainfall, self).__init__(filename=filename)
        except IOError:
            raise FatalError('Unable to initialize')
        super(Rainfall, self).read_all()

        self._start_time = 0.
        self._time = self._start_time
        self._end_time = self.data[:, 1].sum() + self._start_time
        self._time_index = 0

    def update(self):
        """
        Update model for one time step.
        """
        if (self.get_current_time() + self.get_time_step()
                >= self.get_end_time()):
            raise TimeBoundsError()
        else:
            self._time += self.data[self._time_index, 1]
            self._time_index += 1

    def finalize(self):
        """
        Clean up the model, and free resources.
        """
        pass

    def get_value(self, long_var_name):
        """
        Get the value of a variable from its standard name.

        :long_var_name: Standard name as a string

        :returns: Value as a numpy.float64
        """
        if (long_var_name ==
                'atmosphere_water__liquid_equivalent_precipitation_rate'):
            return self.data[self._time_index][0]
        elif long_var_name == 'atmosphere_water__precipitation_duration':
            return self.data[self._time_index][1]
        else:
            raise BadVarNameError(long_var_name)

    def set_value(self, long_var_name, value):
        """
        Set the value of model's variable.

        :warning: This model does not use variables from another component so
        this function will always raise a NotImplementedError if called.

        :long_var_name: Standard name as a string
        :value: New value as a numpy.float64
        """
        raise NotImplementedError('set_value')


def main():
    """
    Run the rainfall file reader.
    """
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('file', default='tank_info.cfg',
                        help='Water tank info file.')
    args = parser.parse_args()

    start_time = time.time()

    model = Rainfall()
    try:
        model.initialize(args.file)
    except Error as error:
        print('%s: Unable to initialize' % error)
        sys.exit(1)

    while 1:
        try:
            precipitation_rate = model.get_value(
                'atmosphere_water__liquid_equivalent_precipitation_rate')
            print('%f, %f' % (model.get_current_time(), precipitation_rate))
            model.update()
        except TimeBoundsError:
            break

    print(' ', file=sys.stderr)
    print('Finished with rainfall simulation.', file=sys.stderr)
    print('Wall time      = %f [secs]' % (time.time() - start_time),
          file=sys.stderr)
    print('Simulated time = %f [secs]' % model.get_current_time(),
          file=sys.stderr)
    print('Final depth    = %f [meters]' % model.get_value(
        'atmosphere_water__liquid_equivalent_precipitation_rate'),
        file=sys.stderr)
    print(' ', file=sys.stderr)

    model.finalize()


if __name__ == '__main__':
    main()
