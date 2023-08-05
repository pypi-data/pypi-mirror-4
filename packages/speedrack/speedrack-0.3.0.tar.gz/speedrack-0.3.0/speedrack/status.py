
SUCCESS    = "success"
FAILURE    = "failure"
NEVER_RUN  = "never run"
EXEC_ERROR = "execution error"
CONF_ERROR = "conf error"
RUNNING    = "running"
INACTIVE   = "inactive"

_all_status = [SUCCESS, FAILURE, NEVER_RUN, EXEC_ERROR, CONF_ERROR, RUNNING, INACTIVE]

# text descriptions
_description = {
    SUCCESS    : "task completed successfully",
    FAILURE    : "task failed according to defined criteria (e.g. a default task generating stderr)",
    NEVER_RUN  : "task is scheduled but has not yet been executed",
    EXEC_ERROR : "speedrack failed to execute this task &mdash; not a task failure",
    CONF_ERROR : "task is not configured correctly; cannot execute",
    RUNNING    : "task was running within the last second",
    INACTIVE   : "results have been found in job directory, but task is not scheduled for execution",
}

# state -> severity
# this maps task states to bootstrap alert levels. a little hacky.
_severity = {
    SUCCESS    : "success",
    FAILURE    : "important",
    NEVER_RUN  : "default", # super-hacky, currently grey
    CONF_ERROR : "warning",
    EXEC_ERROR : "warning",
    RUNNING    : "info",
    INACTIVE   : "inverse",
}

def get_all_status():
    return _all_status

def get_description(status):
    return _description[status]

def get_severity(status):
    return _severity[status]
