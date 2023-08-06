#! /usr/bin/env python
"""
The "water_tank" class defines a model of a cylindrical water
tank that is open at the top (so rainfall can get in), with a
small, circular outlet.

The syntax to create an instance of the model is:
    >>> tank_model = WaterTank()

Once instantiated, we can call any of its methods or
"member functions", most of which are BMI functions. e.g.
    >>> tank_model.initialize(),
    >>> tank_model.update()
"""

#
# Copyright (c) 2009-2013, Scott D. Peckham
#
# Started from "model_tests.py" on 3/14/13 to create
# a BMI-compliant version for a hands-on example.
#
# Show how to inherit BMI functions from BMI_base.py.

# Previous version info.
# July 5-7, 2008
# Modified: July 23, 2008  (v = sqrt(2 * g * d))
# S. Peckham

# test_tank_model()
#
# class water_tank()
#
#     get_attribute()
#     get_input_var_names()
#     get_output_var_names()
#     ------------------------
#     get_var_name()
#     get_var_units()
#     get_var_type()
#     get_var_rank()            # (CHECK)
#     -------------------
#     get_start_time()
#     get_end_time()
#     get_current_time()
#     get_time_step()
#     get_time_units()         # (can also use get_attribute() now)
#     -------------------
#     initialize()
#     update()
#     finalize()
#     run_model()    # (not BMI)
#     -------------
#     get_value()
#     set_value()
#
#     -------------------
#     Non-BMI functions
#     -------------------
#     read_cfg_file()
#     update_rain()
#     print_tank_data()
#
#----------------------------------------------------------------

# import BMI_base

from __future__ import print_function

import sys

import numpy  # (for: float64, int16, pi, sqrt, zeros)
import time

import cmt.bmi.examples.water_tank.rainfall as rainfall
from cmt.bmi import BmiBase, BmiNoGrid
from cmt.bmi import (BadVarNameError, MissingModelAttributeError,
                     FatalError)


class Error(Exception):
    """Base class for exceptions for this module"""
    pass


class BadConfigFileError(FatalError, Error):
    """
    Raise this error if there is a problem with a configuration file
    """
    def __init__(self, filename):
        super(BadConfigFileError, self).__init__()
        self._filename = filename

    def __str__(self):
        return self._filename


def test_tank_model():
    """
    Create an instance of the water tank model
    and then call its "run_model()" method.
    """
    tank_model = WaterTank()
    tank_model.run_model()


# class water_tank(BMI_base.BMI_component):   # (option to inherit)
class WaterTank(object):
    """Define the water_tank class."""

    __implements__ = (BmiBase, BmiNoGrid, )

    #-------------------------------------------
    # Required, static attributes of the model
    #-------------------------------------------
    model_name = 'Water_Tank_Model'
    version = 1.0
    author_name = 'Scott D. Peckham'
    grid_type = 'none'
    time_step_type = 'fixed'
    step_method = 'explicit'
    time_units = 'seconds'

    #----------------------------------------------
    # Input variable names (CSDMS Standard Names)
    #----------------------------------------------
    _input_var_names = [
        'atmosphere_water__liquid_equivalent_precipitation_rate',
        'atmosphere_water__precipitation_duration',
    ]

    #-----------------------------------------------
    # Output variable names (CSDMS Standard Names)
    #-----------------------------------------------
    _output_var_names = [
        'model__time_step',
        'tank_cross_section__area',
        'tank_cross_section__radius',
        'tank_outlet__area',
        'tank__outlet__radius',
        'tank_outlet_water__flow_speed',
        'tank_water__depth',
        'tank_water__initial_depth',
        'tank_water__volume',
    ]

    #------------------------------------------------------
    # Create a Python dictionary that maps CSDMS Standard
    # Names to the model's internal variable names.
    #------------------------------------------------------
    _var_name_map = {
        'atmosphere_water__liquid_equivalent_precipitation_rate': 'rain_rate',
        'atmosphere_water__precipitation_duration': 'rain_duration',
        #----------------------------------------------------------------------
        'model__time_step':              'time_step',
        'tank_cross_section__area':      'top_area',
        'tank_cross_section__radius':    'radius',
        'tank_outlet__area':             'out_area',
        'tank_outlet__radius':           'out_radius',
        'tank_outlet_water__flow_speed': 'out_speed',
        'tank_water__depth':             'depth',
        'tank_water__initial_depth':     'init_depth',
        'tank_water__volume':            'volume'}

    #------------------------------------------------------
    # Create a Python dictionary that maps CSDMS Standard
    # Names to the units of each model variable.
    #------------------------------------------------------
    _var_units_map = {
        'atmosphere_water__liquid_equivalent_precipitation_rate': 'm s-1',
        'atmosphere_water__precipitation_duration': 's',
        #--------------------------------------------------------------------
        'model__time_step':              's',
        'tank_cross_section__area':      'm2',
        'tank_cross_section__radius':    'm',
        'tank_outlet__area':             'm2',
        'tank_outlet__radius':           'm',
        'tank_outlet_water__flow_speed': 'm s-1',
        'tank_water__depth':             'm',
        'tank_water__initial_depth':     'm',
        'tank_water__volume':            'm3'}

    def __init__(self):
        """
        Initialize class attributes.
        """
        self.depth = numpy.float64(0)
        self.out_speed = 0.
        self.volume = 0.
        self.out_area = 0.

        self.gravity = 9.81

        # This group of variables are read from the input file.
        self.time_step = 0.
        self.n_steps = 0
        self.init_depth = numpy.float64(0)
        self.top_area = 0.
        self.out_radius = 0.
        self.rain_data_filename = ''

        # This group of variables are read from the rain data file
        self.rain_rate = 0.
        self.rain_duration = 1.

        self.cfg_file = None
        self.rain_file = None

        self.time = numpy.float64(0)
        self.time_index = 0
        self.water_discharge_out = 0.
        self.timer_start = time.time()

        self._verbose = False

    #------------------------------------------------
    # Return NumPy string arrays vs. Python lists ?
    #------------------------------------------------
    ## _input_var_names  = numpy.array(_input_var_names)
    ## _output_var_names = numpy.array(_output_var_names)

    #-------------------------------------------------------------------
    # BMI: Model Information Functions
    #-------------------------------------------------------------------
    def get_attribute(self, att_name):
        """
        Get a static attribute of the model

        :att_name: Name of the attribute as a string

        :returns: The model's attribute (always as a string?)
        """

        try:
            return getattr(self, att_name.lower())
        except AttributeError:
            raise MissingModelAttributeError(att_name)

    #   get_attribute()
    #-------------------------------------------------------------------
    def get_input_var_names(self):
        """
        List of model's input items as standard name strings

        Note: These are currently variables needed from other
              components vs. those read from files or GUI.

        :returns: List of standard name strings
        """
        return self._input_var_names

    #   get_input_var_names()
    #-------------------------------------------------------------------
    def get_output_var_names(self):
        """
        List of model's output items as standard name strings

        :returns: List of standard name strings
        """
        return self._output_var_names

    #   get_output_var_names()
    #-------------------------------------------------------------------
    # BMI: Variable Information Functions
    #-------------------------------------------------------------------
    def get_var_name(self, long_var_name):
        """
        Local variable name from a standard name.

        :long_var_name: Standard name as a string

        :returns: Name of local variable as a string
        """
        return self._var_name_map[long_var_name]

    #   get_var_name()
    #-------------------------------------------------------------------
    def get_var_units(self, long_var_name):
        """
        Variable units from a standard name.

        :long_var_name: Standard name as a string

        :returns: Units as a udunits string
        """
        return self._var_units_map[long_var_name]

    #   get_var_units()
    #-------------------------------------------------------------------
    def get_var_type(self, long_var_name):
        """
        Variable type as a numpy units string.

        :long_var_name: Standard name as a string

        :returns: Units as a numpy.dtype string
        """
        #---------------------------------------
        # So far, all vars have type "double".
        #---------------------------------------
        if long_var_name in self._input_var_names + self._output_var_names:
            return 'float64'
        else:
            raise BadVarNameError(long_var_name)

    def get_var_rank(self, long_var_name):
        """
        Rank of an exchange item.

        :long_var_name: Standard name as a string

        :returns: Rank of the variable
        """
        if long_var_name in self._input_var_names + self._output_var_names:
            return numpy.int16(0)
        else:
            raise BadVarNameError(long_var_name)

    #   get_var_rank()
    #------------------------------------------------------------
    def get_start_time(self):
        """
        Start time of the model.

        :returns: Start time (with units provided by get_time_units method)
        """
        return 0.0

    #   get_start_time()
    #------------------------------------------------------------
    def get_end_time(self):
        """
        End time of the model

        :returns: End time (with units provided by get_time_units method)
        """
        return self.get_start_time() + self.n_steps * self.time_step

    #   get_end_time()
    #------------------------------------------------------------
    def get_current_time(self):
        """
        Current time of the model

        :returns: Current time (with units provided by get_time_units method)
        """
        return self.time

    #   get_current_time()
    #------------------------------------------------------------
    def get_time_step(self):
        """
        Model time step. This is the time that this class' update method
        runs the model for.

        :returns: Time step (with units provided by get_time_units method)
        """
        return self.time_step

    #   get_time_step()
    #------------------------------------------------------------
    def get_time_units(self):
        """
        Unit of all time variables of this model.

        :returns: Units as udunits string
        """
        return 'seconds'

        #--------------
        # Another way
        #--------------
        # units = self.get_attribute('time_units')
        # return units

    #   get_time_units()
    #------------------------------------------------------------
    # BMI: Model Control Functions
    #------------------------------------------------------------
    def initialize(self, cfg_file):
        """
        Initialize model from a configuration file.

        :cfg_file: Name of configuration file
        """
        self.timer_start = time.time()

        #-------------------------------------------
        # Used in read_cfg_file(), so needed here.
        #-------------------------------------------
        self.gravity = 9.81    # [m/s^2]

        #--------------------------------------
        # Read tank settings from "tank_file"
        #--------------------------------------
        self.cfg_file = cfg_file
        try:
            self.read_cfg_file()
        except IOError:
            raise BadConfigFileError(cfg_file)

        #-----------------------
        # Initialize variables
        #-----------------------
        self.depth = self.init_depth.copy()
        self.out_speed = numpy.sqrt(2 * self.gravity * self.depth)
        self.volume = self.depth * self.top_area  # [m^3]
        self.out_area = numpy.pi * self.out_radius ** 2.0
        if (self._verbose):
            self.print_tank_data()

        #----------------------------
        # Initialize time variables
        #----------------------------
        self.time = numpy.float64(0)
        self.time_index = 0

        #-------------------------------------------------
        # Use "input_file" class to create rain_file
        # object, then open "rain_file" to read data.
        # This will be used by the update_rain() method.
        #-------------------------------------------------
        try:
            self.rain_file = rainfall.InputFile(self.rain_data_filename)
            self.rain_file.open()
        except IOError:
            self.rain_file = None

    #   initialize()
    #------------------------------------------------------------
    def update(self, time_step=-1, report=True):
        """
        Update model for one time step.

        NOTE: The time_step keyword is ignored in calculations.

        :keyword time_step: Update duration
        :keyword report: If True, print a report to stdout
        """
        if (time_step == -1):
            time_step = self.time_step

        #------------------------------------------------
        # Read the next rainfall file data entry.
        # "rain_duration" is read, but ignored for now.
        #------------------------------------------------
        self.update_rain()
        rain_rate_mps = self.rain_rate / (3600.0 * 1000.0)

        #--------------------------------------------------
        # Compute volume inflow rate from rain, Q_in
        # and volume outflow rate, Q_out, in [m^3 / sec].
        #--------------------------------------------------
        water_discharge_in = rain_rate_mps * self.top_area
        if (self.depth > 0):
            water_discharge_out = self.out_speed * self.out_area
        else:
            water_discharge_out = 0.0
        d_vol = (water_discharge_in - water_discharge_out) * self.time_step

        #----------------------------
        # Store the state variables
        #----------------------------
        self.water_discharge_out = water_discharge_out
        self.volume = max(self.volume + d_vol, 0.0)
        self.depth = (self.volume / self.top_area)
        self.out_speed = numpy.sqrt(2.0 * self.gravity * self.depth)

        #-------------------------
        # Optional status report
        #-------------------------
        if (report and self._verbose):
            print('--------------------------------------')
            print('rain_rate = %f [mmph]' % self.rain_rate)
            print('depth     = %f [meters]' % self.depth)

        #--------------------------------------
        # Write new depth to an output file ?
        #--------------------------------------

        #------------------------
        # Update the model time
        #------------------------
        self.time += time_step
        self.time_index += 1

    #   update()
    #------------------------------------------------------------
##    def update_until(self, time):
##
##        #----------------------------------------------------
##        # Call update() method as many times as necessary
##        # in order to get to the requested time.  Note that
##        # we do not override the value of n_steps from
##        # the tank model's cfg_file.
##        #----------------------------------------------------
##        n_steps = numpy.int16(time / self.time_step)
##        for k in xrange(1,n_steps+1):
##            self.update()
##
##    #   update_until()
    #------------------------------------------------------------
    def finalize(self):
        """
        Clean up the model, and free resources.
        """

        timer_stop = time.time()
        run_time = (timer_stop - self.timer_start)

        if (self._verbose):
            print(' ')
            print('Finished with water tank simulation.')
            print('Model run time = %f [secs]' % run_time)
            print('Simulated time = %f [secs]' % self.time)
            print('Final depth    = %f [m]' % self.depth)
            print(' ')

        #-------------------
        # Close input file
        #-------------------
        try:
            self.rain_file.close()
        except AttributeError:
            pass

        #-----------------------
        # Close output files ?
        #-----------------------

    #   finalize()
    #------------------------------------------------------------
    def run_model(self, **kwds):
        """
        Run the model for it's entire duration.

        Note: This is not a required BMI function, but gives
              an easy way to run the stand-alone model.
        """
        self.initialize(**kwds)
        for _ in xrange(1, self.n_steps + 1):
            self.update()
        self.finalize()

    #   run_model()
    #------------------------------------------------------------
    # BMI: Variable Getters and Setters
    #------------------------------------------------------------
    def get_value(self, long_var_name):
        """
        Get the value of a variable from its standard name.

        :long_var_name: Standard name as a string

        :returns: Value as a numpy.float64
        """
        var_name = self.get_var_name(long_var_name)

        try:
            return getattr(self, var_name)
        except AttributeError:
            raise BadVarNameError(long_var_name)

    #   get_value()
    #-------------------------------------------------------------------
    def set_value(self, long_var_name, value):
        """
        Set the value of model's variable.

        Notes: The "long_var_name" string cannot contain a ".". (5/17/12)

        (2/7/13) We are now using 0D numpy arrays as a way to
        produce "mutable scalars" that allow a component with a
        reference to the scalar to see changes to its value.
        But we can't apply numpy.float64() to the value as we did
        before or it destroys the reference.
        See BMI_base.initialize_scalar() for more information.

        :long_var_name: Standard name as a string
        :value: New value as a numpy.float64
        """
        var_name = self.get_var_name(long_var_name)
        setattr(self, var_name, value)

    #   set_value()
    #------------------------------------------------------------
    # Non-BMI functions that are only used internally.
    #------------------------------------------------------------
    def read_cfg_file(self, cfg_file=None):
        """
        Read a values into the class from a configuration file. If cfg_file
        keyword is not provided or is None, use the class' cfg_file attribute.

        :keyword cfg_file: Name of the configuration file, or None
        """

        #-----------------------------------
        # What if cfg_file doesn't exist ?
        #-----------------------------------
        if (cfg_file == None):
            cfg_file = self.cfg_file

        tank_file = rainfall.InputFile(cfg_file)
        tank_file.open()

        #------------------------------------------------
        # Read values from cfg_file and store in "self"
        #------------------------------------------------
        self.time_step = tank_file.read_value()
        self.n_steps = tank_file.read_value(dtype='integer')
        self.init_depth = tank_file.read_value()
        self.top_area = tank_file.read_value()
        self.out_radius = tank_file.read_value()
        self.rain_data_filename = tank_file.read_value(dtype='string')
        tank_file.close()

    #   read_cfg_file
    #------------------------------------------------------------
    def update_rain(self):
        """
        Update the current rain conditions.
        """
        if self.rain_file is None:
            return

        if (self.time_index < self.rain_file.n_lines):
            record = self.rain_file.read_record()
            self.rain_rate = record[0]
            self.rain_duration = record[1]
        else:
            self.rain_rate = 0.0
            self.rain_duration = 1.0

    #   update_rain()
    #------------------------------------------------------------
    def print_tank_data(self):
        """
        Print a summary of the current model state to stdout.
        """

        print('   dt         = %f' % self.time_step)
        print('   n_steps    = %d' % self.n_steps)
        print('   init_depth = %f' % self.init_depth)
        print('   top_area   = %f' % self.top_area)
        print('   out_radius = %f' % self.out_radius)
        print('   out_speed  = %f' % self.out_speed)
        print('   depth      = %f' % self.depth)
        print('   volume     = %f' % self.volume)
        print('   out_area   = %f' % self.out_area)
        print('   rain_file  = %f' % self.rain_data_filename)
        print(' ')

    #   print_tank_data()
    #------------------------------------------------------------


def main():
    """
    Run the water tank model.
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file', default='tank_info.cfg',
                        help='Water tank info file.')
    args = parser.parse_args()

    start_time = time.time()

    model = WaterTank()
    try:
        model.initialize(cfg_file=args.file)
    except Error as error:
        print('%s: Unable to initialize' % error)
        sys.exit(1)

    while 1:
        if model.get_current_time() <= model.get_end_time():
            model.update(report=False)
            water_depth = model.get_value('tank_water__depth')
            print('%f, %f' % (model.get_current_time(), water_depth))
        else:
            break

    print(' ', file=sys.stderr)
    print('Finished with water tank simulation.', file=sys.stderr)
    print('Wall time      = %f [secs]' % (time.time() - start_time),
          file=sys.stderr)
    print('Simulated time = %f [secs]' % model.get_current_time(),
          file=sys.stderr)
    print('Final depth    = %f [meters]' %
          model.get_value('tank_water__depth'), file=sys.stderr)
    print(' ', file=sys.stderr)

    model.finalize()


if __name__ == '__main__':
    main()
