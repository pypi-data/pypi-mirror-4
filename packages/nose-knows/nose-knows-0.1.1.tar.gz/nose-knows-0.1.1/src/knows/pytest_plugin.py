from base import Knows


_EMPTY = object()
_knows = _EMPTY
_tests_to_run = []


def _init_knows(*args, **kwargs):
    global _knows
    if _knows is _EMPTY:
        _knows = Knows(*args, **kwargs)


def pytest_addoption(parser):
    group = parser.getgroup('knows', 'Knows Unit Test Mapping')
    group.addoption(
        '--with-knows',
        action='store_true',
        dest='knows_enabled',
        default=False,
        help='Enable knows plugin.',
    )
    group.addoption(
        '--knows-file',
        type='string',
        dest='knows_file',
        default='.knows',
        help='Output file for knows plugin.',
    )
    group.addoption(
        '--knows-out',
        action='store_true',
        dest='knows_out',
        default=False,
        help='Whether to output the mapping of files to unit tests.',
    )
    group.addoption(
        '--knows-dir',
        type='string',
        dest='knows_dir',
        default='',
        help='Include only this given directory. This should be your '
             'project directory name, and does not need to be an absolute '
             'path.',
    )
    group.addoption(
        '--knows-exclude',
        type='string',
        action='append',
        dest='knows_exclude',
        help='Exclude files having this string (can use multiple times).',
    )


def pytest_cmdline_preparse(config, args):
    if '--with-knows' in args:
        for x in list(args):
            if not x.startswith('--'):
                _tests_to_run.append(x)
                args.remove(x)


def parse_test_name(item):
    item_cls = str(item.cls)
    begin = item_cls.index("'") + 1
    end = item_cls.index("'", begin)
    test_module_and_class = item_cls[begin:end]
    test_module, test_class = test_module_and_class.rsplit('.', 1)
    return test_module + ':' + test_class + '.' + item.name


def pytest_configure(config):
    options = config.option
    if options.knows_enabled:
        _init_knows(
            knows_filename=options.knows_file,
            output=options.knows_out,
            knows_directory=options.knows_dir,
            exclude=options.knows_exclude,
        )
        config.pluginmanager.register(_knows)
        if not options.knows_out:
            input_files = config.args
            global _tests_to_run
            _tests_to_run = set(_knows.get_tests_to_run(_tests_to_run))

def pytest_sessionstart(session):
    if _knows is not _EMPTY:
        _knows.begin()


def pytest_runtest_protocol(item):
    if _knows is not _EMPTY:
        test_name = parse_test_name(item)
        if not _knows.output:
            if test_name not in _tests_to_run:
                return True

        _knows.start_test(parse_test_name(item))


def pytest_sessionfinish(session):
    if _knows is not _EMPTY:
        _knows.finalize()
