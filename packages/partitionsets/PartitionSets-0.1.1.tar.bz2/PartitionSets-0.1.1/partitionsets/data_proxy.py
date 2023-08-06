#!/usr/bin/env python
""" Keep the data files in reach for the helper scripts,
regardless of user install location for scripts and package.

"""

import os, json

ABS_PATH_DATA = os.path.join(os.path.dirname(__file__), 'data')

def bell_number_data():
    """ Bell or exponential numbers: ways of placing n labeled balls
    into n indistinguishable boxes. at http://oeis.org/A000110  """
    with open(os.path.join(ABS_PATH_DATA, 'OEIS_A000110.json')) as f_d:
        data = json.load(f_d)
        bells = tuple(data['/OESIS/A0001101'])
        # f_d.close()
        return bells
