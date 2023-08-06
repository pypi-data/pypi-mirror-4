#!/usr/bin/env python
"""
Run the BMI checker plugin for pylint.
"""
import sys

from pylint.lint import Run


def main():
    """
    Run pylint on some code with the cmt.bmi.checker plugin loaded.
    """
    args = ['--load-plugins=cmt.bmi.checker',
            '--disable=all',
            '--enable=bmi,E0222,W0221',
           ] + sys.argv[1:] 
    Run(args)

if __name__ == '__main__':
    main()
