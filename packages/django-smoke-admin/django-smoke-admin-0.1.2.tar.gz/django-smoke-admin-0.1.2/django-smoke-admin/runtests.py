#!/usr/bin/env python
import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'test_app.test_settings')

from optparse import OptionParser
from django_nose.runner import NoseTestSuiteRunner


def runtests(*test_args, **kwargs):

    if not test_args:
        test_args = ['tests']
    test_args.append('--with-spec')
    test_args.append('--spec-color')
    kwargs.setdefault('interactive', False)
    test_runner = NoseTestSuiteRunner(**kwargs)

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)


if __name__ == '__main__':
    runtests()