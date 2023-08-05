version_info = (0, 3, 0)
version = '.'.join(str(n) for n in version_info[:3])
release = version + ''.join(str(n) for n in version_info[3:])

from flask import Flask
import os, sys
import filer
import constants as con

app = Flask(__name__)
# needed to make state saving work
app.secret_key = "not_so_secret_lololol"

# global application controls
app._shutdown = False
app._sched = None

from datetime import datetime
app.config['datetime_launch'] = datetime.now()

import signal
def sigint_handler(signal, frame):
    app.logger.warn("Received signal: " + str(signal))
    app._shutdown = True
    aps.shutdown(app._sched)
    app.logger.warn("Shutting down.")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)


def config_paths():
    '''Based on assigned settings, compute log, state, and job paths'''

    if not app.config.get(con.SPEEDRACK_DIR, None):
        warning_msg = """!!!!!\n"NOTE: using temp directory, please set SPEEDRACK_DIR in settings\n!!!!!\n"""
        sys.stdout.write(warning_msg)

        import tempfile
        default_temp_dir = tempfile.gettempdir()
        speedrack_instance_name = app.config.get(con.APP_NAME, "speedrack")
        default_speedrack_dir = os.path.join(default_temp_dir, speedrack_instance_name)
        app.config[con.SPEEDRACK_DIR] = default_speedrack_dir

    def set_default_path(config_key, key_path):
        if not app.config.get(config_key) and app.config.get(con.SPEEDRACK_DIR):
            key_dir = os.path.join(app.config.get(con.SPEEDRACK_DIR), key_path)
            app.config[config_key] = key_dir
            print "setting {0} to {1}".format(config_key, key_dir)

    set_default_path(con.LOG_DIR, "logs")
    set_default_path(con.JOB_ROOT_DIR, "jobs")
    set_default_path(con.JOB_STATE, "speedrack.state")


def start_logger():

    app.debug_log_format = """%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s"""

    if not app.debug and app.config.get(con.LOG_DIR, None):

        # setup local log dir
        if not os.path.exists(app.config[con.LOG_DIR]):
            os.makedirs(app.config[con.LOG_DIR])

        import logging
        from logging.handlers import RotatingFileHandler
        app.logger.setLevel(logging.DEBUG)

        speedrack_log_file = os.path.join(app.config[con.LOG_DIR], "speedrack.log")
        handler = RotatingFileHandler(speedrack_log_file,
                                      maxBytes=app.config[con.LOG_MAX_SIZE],
                                      backupCount=app.config[con.LOG_COUNT])
        handler.setLevel(logging.INFO)
        lines = {
            'first': " ".join(['%(asctime)-15s',
                               '%(levelname)-8s',
                               '%(pathname)s:%(lineno)d']),
            'second': "  %(message)s",
        }
        formatter = logging.Formatter("%(first)s\n%(second)s" % lines)
        handler.setFormatter(formatter)

        app.logger.addHandler(handler)

    else:
        sys.stdout.write("NO LOG. Either in debug mode or {0} not configured.\n".format(con.LOG_DIR))


def launch_services():
    '''after settings have been loaded, start processes.'''

    # debug toolbar
    if app.config[con.FLASK_DEBUG_TOOLBAR]:
        app.debug = True
        app.config[con.SECRET_KEY] = app.secret_key # looks in config rather than in global
        app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
        from flask.ext.debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app) # returns the toolbar; we don't need it

    config_paths()
    start_logger()
    filer.assert_no_tilde(app.config[con.JOB_ROOT_DIR])
    if not os.path.exists(app.config[con.JOB_ROOT_DIR]):
        os.makedirs(app.config[con.JOB_ROOT_DIR])
    start_scheduler()

def _set_settings_file(settings_file):
    """updates config with settings"""
    from werkzeug.utils import ImportStringError    
    try:
        app.config.from_pyfile(settings_file)
    except ImportStringError:
        sys.stderr.write("Received an ImportStringError, please review your python settings file\n%s\n" % settings_file)
        sys.exit(1)

def set_default_settings_file(settings_file):
    _set_settings_file(settings_file)

set_user_settings_file = set_default_settings_file

def set_task_file(task_file):
    """overrides demo task file"""
    app.config[con.CONFIG_YAML] = task_file

import speedrack.context_processors
import speedrack.filters
import speedrack.views

from speedrack import models
from speedrack import timing
from speedrack import aps

def start_scheduler():
    app._sched = aps.init(app.config.get(con.CONFIG_YAML, None),
                          app.config.get(con.JOB_STATE, None))
    app.logger.info("Speedrack started in '%s' environment." % ("test"))
