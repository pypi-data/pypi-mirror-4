import logging
import os

from nose.plugins import Plugin

from base import Knows


def parse_test_name(test_name):
    begin = test_name.index('<') + 1
    end = test_name.index('>')
    inside_brackets = test_name[begin:end]
    test_module_and_class, test_method = inside_brackets.split(' ', 1)
    if test_method.startswith('testMethod='):
        test_method = test_method[len('testMethod='):]
    test_module, test_class = test_module_and_class.rsplit('.', 1)
    return test_module + ':' + test_class + '.' + test_method


class KnowsNosePlugin(Plugin):
    name = 'knows'

    def __init__(self, *args, **kwargs):
        self.output = True
        self.enableOpt = 'with-knows'
        self.logger = logging.getLogger('nose.plugins.knows')

    def options(self, parser, env=os.environ):
        parser.add_option(
            '--knows-file',
            type='string',
            dest='knows_file',
            default='.knows',
            help='Output file for knows plugin.',
        )
        parser.add_option(
            '--knows-out',
            action='store_true',
            dest='knows_out',
            help='Whether to output the mapping of files to unit tests.',
        )
        parser.add_option(
            '--knows-dir',
            type='string',
            dest='knows_dir',
            default='',
            help='Include only this given directory. This should be your '
                 'project directory name, and does not need to be an absolute '
                 'path.',

        )
        parser.add_option(
            '--knows-exclude',
            type='string',
            action='append',
            dest='knows_exclude',
            help='Exclude files having this string (can use multiple times).',
        )
        super(KnowsNosePlugin, self).options(parser, env=env)

    def configure(self, options, config):
        self.enabled = getattr(options, self.enableOpt)
        if self.enabled:
            self.knows = Knows(
                knows_filename=options.knows_file,
                output=options.knows_out,
                knows_directory=options.knows_dir,
                exclude=options.knows_exclude,
            )
            input_files = config.testNames
            if not options.knows_out:
                if input_files:
                    config.testNames = self.knows.get_tests_to_run(
                        input_files,
                    )

        super(KnowsNosePlugin, self).configure(options, config)

    def begin(self):
        self.knows.begin()

    def startTest(self, test):
        self.knows.start_test(parse_test_name(repr(test)))

    def stopTest(self, test):
        self.knows.stop_test(parse_test_name(repr(test)))

    def finalize(self, result):
        self.knows.finalize()
