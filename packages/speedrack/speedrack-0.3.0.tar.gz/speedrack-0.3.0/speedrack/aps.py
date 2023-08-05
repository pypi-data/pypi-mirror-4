# Application interface to APScheduler
from datetime import datetime, date, timedelta
import os
import re

from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.shelve_store import ShelveJobStore
from apscheduler.triggers.interval import IntervalTrigger

import apscheduler.scheduler

from flask import flash

from speedrack import app
from speedrack import models
from speedrack import timing
from speedrack.constants import task_params

# The handle of 'default' is necessary, or a default RAMStore is created
# which is pretty confusing
_FHANDLE = 'file'

# connect apscheduler's logger to application's
apscheduler.scheduler.logger = app.logger
logger = app.logger # expose without referring to app

def init(yaml_file, job_state_file = None):
    """Set up apscheduler, recover existing file store if there is one,
    otherwise kick off a new one with existing config settings"""

    sched = new_scheduler()
    if job_state_file:
        recover(sched, job_state_file)

    recovered_job_count = len(sched.get_jobs())
    if recovered_job_count == 0:
        logger.info("Recovered NO jobs from store, creating new job store and seeding with config-generated params.")
        sched = update(sched, yaml_file, job_state_file)
    else:
        logger.info("Recovered %d jobs from store." % recovered_job_count)

    if not sched.running:
        sched.start()

    return sched

def recover(sched, job_state_file):
    """Recovers existing persistent job store."""
    logger.debug("jobs before shelve recovery: %d" % len(sched.get_jobs()))
    logger.debug("jobs: " + str(sched.get_jobs()))
    job_store = ShelveJobStore(job_state_file)
    sched.add_jobstore(job_store, _FHANDLE)
    logger.debug("jobs after shelve recovery: %d" % len(sched.get_jobs()))
    logger.debug("jobs: " + str(sched.get_jobs()))

def new_scheduler():
    # each task needs to explicitly set itself as stateful
    apsched_config = { "coalesce": True }
    logger.debug("creating new scheduler")
    sched = Scheduler(apsched_config)
    return sched

def update(sched, yaml_file, job_state_file):
    """Clears existing persistent job store, replaces with new one
    created from current config file contents."""

    # the file-based scheduler store needs to be removed completely
    # to update any of its shelved settings:
    # http://readthedocs.org/docs/apscheduler/en/latest/index.html#job-persistency

    logger.info("Update requested, waiting on running jobs.")
    shutdown(sched)
    clear(sched, job_state_file)

    # Also, a given scheduler cannot be restarted once it's shut down.
    # So in essence, we're gracefully stopping the scheduler and
    # replacing it with a new one.
    sched = new_scheduler()

    yaml_config = models.Config(yaml_file)
    load_tasks(sched, yaml_config)
    sched.add_jobstore(ShelveJobStore(job_state_file), _FHANDLE)
    sched.start()
    return sched

def clear(sched, job_state_file):
    '''detaching from existing jobstore isn't sufficient. must
    clear and rebuild'''

    # Above is not literally true. It would be possible to walk each
    # task and diff it agains the reloaded one.

    logger.info("Clear requested, removing filestore.")
    try:
        sched.remove_jobstore(_FHANDLE)
    except KeyError:
        logger.debug("No existing jobstore, skipping.")

    # this is a filthy hack but I can't find why I get .db on
    # OSX and not on CentOS linux
    if os.path.isfile(job_state_file):
        os.unlink(job_state_file)
    elif os.path.isfile(job_state_file + ".db"):
        os.unlink(job_state_file + ".db")

def run_task(sched, task_name):
    '''Executes a given task immediately. In APScheduler, this is
    handled by adding a task in the very-near (1s) future. An
    interval-driven task has its interval reset with this execution. A
    cron-driven task does not. Returns True if successful.'''

    jobs = sched.get_jobs()

    target_job = None
    params = None
    for job in jobs:
        params = job.args[0]
        if params[task_params.NAME] == task_name:
            target_job = job
            break

    if not target_job:
        logger.error("Couldn't find task [%s] in scheduler!" % task_name)
        return False

    if models.is_conf_error(params):
        logger.error("Can't execute task [%s] with configuration error" % task_name)
        return False

    # 1) adding 1s is such a hack, but if you add "now", then by the
    # time
    # 2) this explicitly is not set to use the filestore, but the
    # ramstore. this is not scheduled or repeating, and doubling up
    # the func/params seems to cause the function to always enter as
    # "repeating"
    sched.add_date_job(executor_func,
                       datetime.now() + timedelta(seconds=1),
                       args=[params])

    return True


def executor_func(params):
    '''Unpack parameters, construct Executor object, run function.'''

    # required
    name             = params[task_params.NAME]
    command          = params[task_params.COMMAND]
    config           = params[task_params.CONFIG]
    parsed_interval  = params[task_params.PARSED_INTERVAL]
    parsed_cron      = params[task_params.PARSED_CRON]

    # optional
    email_recipients = params.get(task_params.EMAIL_RECIPIENTS, [])
    spam             = params.get(task_params.SPAM, None)
    description      = params.get(task_params.DESCRIPTION, None)
    max_keep         = params.get(task_params.MAX_KEEP, None)
    fail_by_stderr   = params.get(task_params.FAIL_BY_STDERR, None)
    fail_by_retcode  = params.get(task_params.FAIL_BY_RETCODE, None)

    ex = models.Executor(name, command)
    ex.config = config
    if description:
        ex.description = description
    if max_keep:
        ex.max_keep = int(max_keep)
    if spam:
        ex.spam = spam
    ex.fail_by_stderr = fail_by_stderr
    ex.fail_by_retcode = fail_by_retcode
    ex.parsed_interval = parsed_interval
    ex.parsed_cron = parsed_cron
    ex.email_recipients = email_recipients
    ex.run()


def new_params(config_block):
    '''
    Converts a configuration block into parameters suitable
    for establishing a task.

    {
      'name': this name,
      'description': description,
      'max_keep': None,
    }
    '''

    logger.debug("new params requested: %s" % str(config_block))

    name = config_block.get(task_params.NAME, None)
    name = understate(name)
    description = config_block.get(task_params.DESCRIPTION, None)
    max_keep = config_block.get(task_params.MAX_KEEP, None)
    command = config_block.get(task_params.COMMAND, None)

    fail_by_retcode = config_block.get(task_params.FAIL_BY_RETCODE, None)
    fail_by_stderr = config_block.get(task_params.FAIL_BY_STDERR, None)

    email_recipients = config_block.get(task_params.TASK_EMAIL, None)
    if email_recipients:
        email_recipients = email_recipients.split(",")
    else:
        email_recipients = []

    spam = config_block.get(task_params.SPAM, None)

    unparsed_interval = config_block.get(task_params.TASK_INTERVAL, None)
    parsed_interval = timing.parse_interval(unparsed_interval)

    unparsed_cron = config_block.get(task_params.TASK_CRON, None)
    parsed_cron = timing.parse_cron(unparsed_cron)

    params = {
        task_params.NAME: name,
        task_params.DESCRIPTION: description,
        task_params.MAX_KEEP: max_keep,
        task_params.COMMAND: command,
        task_params.EMAIL_RECIPIENTS: email_recipients,
        task_params.PARSED_CRON: parsed_cron,
        task_params.PARSED_INTERVAL: parsed_interval,
        task_params.FAIL_BY_STDERR: fail_by_stderr,
        task_params.FAIL_BY_RETCODE: fail_by_retcode,
        task_params.CONFIG: config_block,
        task_params.SPAM: spam,
    }

    # In erroneous configurations, we add a dummy job with an
    # unrunnable* time so that we can display the errored
    # configuration to the user
    if models.is_conf_error(params):
        logger.warn("task %s has error:" % name)
        logger.warn(params)

    return params


def schedule_params(sched, params):
    '''Adds executor function to scheduler based on its members'''
    if models.is_conf_error(params):
        # using add_date_job as purgatory
        much_later = date.fromordinal(date.max.toordinal())
        sched.add_date_job(executor_func, much_later, args=[params], jobstore=_FHANDLE)
    elif params.get("parsed_interval", None):
        sched.add_interval_job(executor_func, args=[params], jobstore=_FHANDLE, coalesce=True, **params[task_params.PARSED_INTERVAL])
    elif params.get("parsed_cron", None):
        sched.add_cron_job(executor_func, args=[params], jobstore=_FHANDLE, **params[task_params.PARSED_CRON])
    else:
        raise Exception, "Shouldn't ever be here."


def load_tasks(sched, config):
    """Given a list of tasks, update the scheduler."""

    logger.debug("NUM TASKS: %d" % len(sched.get_jobs()))

    if config.parsed is None or len(config.parsed['tasks']) == 0:
        flash("Couldn't find any tasks in yaml.", "error")
        return

    for config_block in config.parsed['tasks']:
        params = new_params(config_block)
        schedule_params(sched, params)

def shutdown(sched):
    """Gracefully shutdown APScheduler."""
    logger.warn("Shutdown request received. Shutting down scheduler.")
    sched.shutdown()
    logger.warn("APScheduler shut down successfully.")


_disallowed_characters = r""" !@#$%^&\*(){}[]|'\""""
_disallowed_escaped = r"""[ !@#$%^&\*\(\){}\[\]\|'\"]+"""
def understate(name):
    ''' underscorify the given names '''
    name = name.lower()
    name = name.strip(_disallowed_characters)
    name = re.sub(_disallowed_escaped, r"_", name)
    return name
