# Speedrack configuration file

DEBUG = False

FLASK_DEBUG_TOOLBAR = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

CONFIG_YAML = "config/test.yaml"

# Overloaded in testing to remind of where you are
APP_NAME="speedrack"

# Number of executions to display 
EXECUTION_DISPLAY = 20

#
# task execution
#

# If the file is this size or less, just show the whole thing
FSIZE_MAX     = 10000 # bytes
# If the file is too big to show, show this much
FSIZE_SUMMARY = 5000  # bytes

#
# Global error defaults
#

# Nonzero status code is failure
FAIL_BY_RETCODE = True
# Generating stderr is failure
FAIL_BY_STDERR = True

# This is the default for all tasks. False indicates to retain results from all executions.
MAX_RUNS = False

#
# state and file settings
#

# Default is system temp
#SPEEDRACK_DIR = None

# Individual storage overrides
#JOB_ROOT_DIR = "./jobs"
#JOB_STATE = "./sprack.shelve"
#LOG_DIR = "./logs"

# log
LOG_MAX_SIZE = 1024 * 1024 * 5
LOG_COUNT = 5

#
# notification settings
#

# Global switch, overrides other email settings
EMAIL_DISABLED = False
#EMAIL_SMTP = "smtp.yourdomain.org"
#EMAIL_FROM_ADDRESS = "sample@yourdomain.org"
# if set, all emails are sent to this address, ignoring settings on
# individual tasks
#EMAIL_TO_GLOBAL = "you@yourdomain.org"
