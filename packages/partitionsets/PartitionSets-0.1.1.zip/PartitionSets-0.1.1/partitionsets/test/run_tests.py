#! /usr/bin/env python
""" This is the main test runner.
It discovers the tests available and runs them.  """

if __name__ == '__main__':
  import nose2
  nose2.discover()
