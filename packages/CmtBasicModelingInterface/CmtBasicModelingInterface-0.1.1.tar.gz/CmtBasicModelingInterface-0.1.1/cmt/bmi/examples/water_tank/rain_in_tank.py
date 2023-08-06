"""
Example of coupling two BMI components.
"""

from __future__ import print_function


def main():
    """
    Run the water tank model coupled with the rainfall model.
    """
    import sys
    import time
    import argparse

    from cmt.bmi.examples.water_tank import (Rainfall, WaterTank,
                                             RainfallError, WaterTankError)

    parser = argparse.ArgumentParser()
    parser.add_argument('tank_file', help='Water tank info file.')
    parser.add_argument('rain_file', help='Rainfall data file.')
    args = parser.parse_args()

    start_time = time.time()

    rain = Rainfall()
    tank = WaterTank()

    try:
        tank.initialize(args.tank_file)
    except WaterTankError as error:
        print('%s: Unable to initialize tank' % error)
        sys.exit(1)

    try:
        rain.initialize(args.rain_file)
    except RainfallError as error:
        print('%s: Unable to initialize rainfall' % error)
        sys.exit(1)

    while 1:
        if tank.get_current_time() <= tank.get_end_time():
            rain.update()
            precip = rain.get_value(
                'atmosphere_water__liquid_equivalent_precipitation_rate')
            tank.set_value(
                'atmosphere_water__liquid_equivalent_precipitation_rate',
                precip)

            tank.update(report=False)
            water_depth = tank.get_value('tank_water__depth')
            print('%f, %f' % (tank.get_current_time(), water_depth))
        else:
            break

    print(' ', file=sys.stderr)
    print('Finished with water tank simulation.', file=sys.stderr)
    print('Wall time      = %f [secs]' % (time.time() - start_time),
          file=sys.stderr)
    print('Simulated time = %f [secs]' % tank.get_current_time(),
          file=sys.stderr)
    print('Final depth    = %f [meters]' % tank.get_value('tank_water__depth'),
          file=sys.stderr)
    print(' ', file=sys.stderr)

    tank.finalize()


if __name__ == '__main__':
    main()
