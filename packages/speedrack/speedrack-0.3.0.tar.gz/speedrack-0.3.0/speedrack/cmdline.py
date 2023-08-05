#!env python

import sys, os
sys.path.insert(0, os.path.join(sys.path.pop(0), ".."))

from speedrack import version

import argparse

with_gevent = False
try:
    from gevent.wsgi import WSGIServer
    with_gevent = True
except ImportError:
    sys.stdout.write("Couldn't find gevent, using dev server.\n")

def _get_default_config():
    SPEEDRACK_ROOT = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(SPEEDRACK_ROOT, "config")

def _get_default_settings():
    return os.path.join(_get_default_config(), "default.py")

def _get_default_yaml():
    return os.path.join(_get_default_config(), "test.yaml")


def init(target_path=None):
    """
    write fresh control files (speedrack_settings.py and speedrack_tasks.yml)
    """

    STOCK_SETTINGS = _get_default_settings()
    STOCK_YAML = _get_default_yaml()

    DEFAULT_SETTINGS = "speedrack_settings.py"
    DEFAULT_TASKS = "speedrack_tasks.yaml"

    import shutil
    if not target_path:
        target_path = os.getcwd()
    if not os.path.isdir(target_path):
        sys.stderr.write("Couldn't find target path: %s\n" % target_path)
        sys.exit(1)
    sys.stdout.write("Creating {settings} and {tasks}\n".format(settings=DEFAULT_SETTINGS, tasks=DEFAULT_TASKS))
    shutil.copy(STOCK_SETTINGS, os.path.join(target_path, DEFAULT_SETTINGS))
    shutil.copy(STOCK_YAML, os.path.join(target_path, DEFAULT_TASKS))
    sys.stdout.write("Speedrack configuration files created.\n")

def run(debug=False, port=8118, settings_file="", yaml_file=""):
    """
    launch the speedrack application

    :param port: (default 8118)
    :param settings_file: absolute path to settings.py controlling application behavior
    :param yaml_file: absolute path to task definitions
    """

    # Begin configuring speedrack application
    import speedrack
    import speedrack.filer
    from werkzeug.utils import ImportStringError

    speedrack.filer.assert_no_tilde(settings_file)
    speedrack.filer.assert_no_tilde(yaml_file)

    speedrack.set_default_settings_file(_get_default_settings())
    if settings_file:
        pyfile = os.path.join(os.getcwd(), settings_file)
        if not os.path.isfile(pyfile):
            sys.stderr.write("Couldn't find settings_file: %s\n" % pyfile)
            sys.exit(1)
        sys.stdout.write("Loading application settings: %s\n" % pyfile)
        speedrack.set_user_settings_file(pyfile)
    else:
        sys.stdout.write("Running in demo setting mode\n")

    if debug:
        speedrack.app.config.update({'DEBUG': True})

    speedrack.app.config.update({'PORT': port})

    if yaml_file:
        task_file = os.path.join(os.getcwd(), yaml_file)
        if not os.path.isfile(task_file):
            sys.stderr.write("Couldn't find yaml_file: %s\n" % task_file)
            sys.exit(1)
        sys.stdout.write("Initializing with task settings: %s\n" % task_file)
        speedrack.set_task_file(task_file)
    else:
        sys.stdout.write("Running with demo task set\n")
        speedrack.set_task_file(_get_default_yaml())

    # starts logger, scheduler
    speedrack.launch_services()

    msg = """Launching speedrack:
port: %d
settings: %s
yaml: %s""" % (port, str(settings_file), str(yaml_file))

    speedrack.app.logger.info(msg)
    if not with_gevent or debug:
        speedrack.app.logger.info("Speedrack serving via flask-dev server.")
        speedrack.app.run(host="0.0.0.0", debug=debug, port=port)
    else:
        speedrack.app.logger.info("Speedrack serving via gevent.")
        http_server = WSGIServer(('', port), speedrack.app)
        http_server.serve_forever()
    speedrack.app.logger.warn("STARTED")


def main():

    # create the top-level parser
    parser = argparse.ArgumentParser(version=version)

    subparsers = parser.add_subparsers(help='commands')

    init_parser = subparsers.add_parser('init', help='write fresh control files (speedrack_settings.py and speedrack_tasks.yml)')
    init_parser.set_defaults(func=init)

    run_parser = subparsers.add_parser('run', help='launch the speedrack application')
    run_parser.add_argument('--port', '-p',
                            type=int, default=8118, action='store',
                            help='new directory to create')
    run_parser.add_argument('--settings_file', '--settings', '-s',
                            default=None, action='store',
                            help='absolute path to settings.py controlling application behavior')
    run_parser.add_argument('--yaml_file', '--yaml', '-y',
                            default=False, action='store',
                            help='set permissions to prevent writing to the directory')
    run_parser.add_argument('--debug',
                            default=False, action='store_true',
                            help='spam a lot of debug messages')
    run_parser.set_defaults(func=run)

    args = parser.parse_args()

    # wow, now I understand why there are so many argument-parsing replacements

    # omg !@#$%^& argparse
    command = args.func
    arguments = vars(args)
    del arguments['func']
    command(**arguments)

if __name__ == '__main__':
    main()
