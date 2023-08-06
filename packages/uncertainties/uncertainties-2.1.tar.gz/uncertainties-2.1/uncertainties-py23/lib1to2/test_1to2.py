#!/usr/bin/env python

'''
Unit tests for the uncertainties.lib1to2 code update package.

Meant to be run through nosetests.

(c) 2013 by Eric O. LEBIGOT (EOL).
'''

# Code inspired by:
#
# - lib2to3.tests.test_fixers.py

import sys

# !! Would it be possible to use an import hook so as to stop the
# import if the Python version is not high enough, instead of having
# like here a whole indented block?

if sys.version_info < (2, 7):
    # This package uses lib2to3, which requires Python 2.6+.

    # !!  Nosetests also fails (it looks like it tries to run tests
    # via lib2to3/tests/test_refactor.py):
    
    pass

else:
    import re
    import os
    import lib2to3.tests.support as support

    # The lib1to2.fixes package given to lib2to3 is the *local* package
    # (not to any other installed module) (this is done through the
    # __import__() used via support.get_refactorer()):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

    def check_refactor(refactorer, source, expected):
        """
        Raises an AssertionError if the given
        lib2to3.refactor.RefactoringTool does not refactor 'source' into
        'expected'.

        source, expected -- strings (typically with Python code).
        """

        new = unicode(
            refactorer.refactor_string(support.reformat(source), '<string>'))

        assert support.reformat(expected) == new, (
            "Refactoring failed: '{}' => '{}' instead of '{}'".format(
            source, new.strip(), expected))

    def check_all(fixer, tests):
        '''
        Takes a fixer name (module from fixes) and a mapping that maps
        code using the obsolete syntax into updated code, and checks
        whether the code is correctly updated.
        '''    

        refactorer = support.get_refactorer(
            fixer_pkg='lib1to2', fixers=[fixer])

        for (input_str, out_str) in tests.items():
            check_refactor(refactorer, input_str, out_str)

    def test_fix_std_dev():
        'Tests the transformation of std_dev() into std_dev.'


        tests = {
            'x.std_dev()': 'x.std_dev',
            'y.std_dev();  unc.std_dev(z)': 'y.std_dev;  unc.std_dev(z)',
            'uncertainties.std_dev(x)': 'uncertainties.std_dev(x)',
            'std_dev(x)': 'std_dev(x)',

            """
            long_name.std_dev(
            # No argument!
            )""":

            """
            long_name.std_dev"""
        }

        check_all('std_dev', tests)

    def test_ufloat():
        '''
        Test of the transformation of ufloat(tuple,...) and
        ufloat(string,...) into ufloat(nominal_value, std_dev, tag=...).
        '''

        tests = {
            # Tuples:
            'ufloat((3, 0.14))': 'ufloat(3, 0.14)',
            'ufloat((3, 0.14), "pi")': 'ufloat(3, 0.14, "pi")',
            "ufloat((3, 0.14), 'pi')": "ufloat(3, 0.14, 'pi')",
            "x = ufloat((3, 0.14), tag='pi')": "x = ufloat(3, 0.14, tag='pi')",

            # Simple expressions that can be transformed:
            'ufloat((n, s), tag="var")': 'ufloat(n, s, tag="var")',

            # Simple expressions that cannot be transformed automatically:
            'ufloat(str_repr, tag="var")': 'ufloat(str_repr, tag="var")',
            'ufloat(*tuple_repr, tag="var")': 'ufloat(*tuple_repr, tag="var")',
            'ufloat(*t[0, 0])': 'ufloat(*t[0, 0])',        

            # Strings:
            'ufloat("-1.23(3.4)")': 'ufloat_fromstr("-1.23(3.4)")',
            "ufloat('-1.23(3.4)')": "ufloat_fromstr('-1.23(3.4)')",
            'ufloat("-1.23(3.4)", "var")':
            'ufloat_fromstr("-1.23(3.4)", "var")',
            'ufloat("-1.23(3.4)", tag="var")':
                'ufloat_fromstr("-1.23(3.4)", tag="var")'

        }

        # Automatic addition of a dotted access:
        tests.update(dict(
            # !! Dictionary comprehension usable with Python 2.7+
            (re.sub('ufloat', 'unc.ufloat', orig),
             re.sub('ufloat', 'unc.ufloat', new))
            for (orig, new) in tests.iteritems()))

        # Test for space consistency:
        tests[' t  =  u.ufloat("3")'] = ' t  =  u.ufloat_fromstr("3")'

        # Exponentiation test:
        tests.update(dict(
            # !! Dictionary comprehension usable with Python 2.7+
            (orig+'**2', new+'**2')
            for (orig, new) in tests.iteritems()))

        # Exponent test:
        tests['2**ufloat("3")'] = '2**ufloat_fromstr("3")'

        # Opposite test:
        tests['-ufloat("3")'] = '-ufloat_fromstr("3")'

        check_all('ufloat', tests)
