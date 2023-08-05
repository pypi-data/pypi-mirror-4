from speedrack import app
from speedrack import filer
from speedrack import notification
from speedrack import status
import constants as con
import constants.task_params as task_params

from datetime import datetime
from decorators import memoize

from operator import attrgetter
import os
try:
    import simplejson as json
except ImportError:
    import json
import subprocess
import traceback
import yaml

# This file makes heavy use of memoize. Maybe a little too much. But task
# state is stored in files on disk rather than something clever, so I wanted
# to minimize disk access.

class TaskList():
    ''' A list of all currently scheduled Tasks. Currently polled from the
    scheduler and the unscheduled tasks existing on disk. '''
    
    def __init__(self,
                 job_root_dir = None,
                 sched = None):
        self.sched = sched
        self.tasks = None
        if not job_root_dir:
            self.job_root_dir = app.config.get(con.JOB_ROOT_DIR, None)
        else:
            self.job_root_dir = job_root_dir

    def _tasks_from_sched(self):
        tasks = {}
        if not self.sched:
            return tasks
        jobs = self.sched.get_jobs()
        for job in jobs:
            # little hairy -- this is where we set attach our
            # execution logic to our task structure
            params = job.args[0]
            task = Task(params[task_params.NAME],
                        max_keep = params.get(task_params.MAX_KEEP, None),
                        description = params.get(task_params.DESCRIPTION, None))

            task.conf_error = is_conf_error(params)
            task.running = job.instances != 0
            task.active = True
            task.next_run_time = job.next_run_time
            task.num_active_runs = job.runs

            tasks[task.name] = task
        return tasks

    def _tasks_from_disk(self):
        directories = os.listdir(self.job_root_dir)
        tasks = {}
        for directory in directories:
            task = Task(name=directory)
            task.running = False
            task.active = False
            task.description = "TODO: store description?"
            task.next_run_time = None
            task.num_active_runs = None
            tasks[task.name] = task
        return tasks

    def get(self, hide_inactive=False):
        """ creates a snapshot into the running system and past
        executions"""

        if self.tasks:
            return self.tasks

        if hide_inactive:
            self.tasks = self._tasks_from_sched().values()
        else:
            # Start with inactive tasks. Update (and overwrite) those
            # tasks with tasks generated from the active scheduler.
            tasks = self._tasks_from_disk()
            active_tasks = self._tasks_from_sched()
            tasks.update(active_tasks)
            self.tasks = tasks.values()
        self.tasks.sort(key=attrgetter(task_params.NAME))
        return self.tasks

    def find_task(self, name):
        tasks = self.get()
        for task in tasks:
            if task.name == name:
                return task


def is_conf_error(params):
    command         = params.get(task_params.COMMAND, None)
    name            = params.get(task_params.NAME, None)
    parsed_cron     = params.get(task_params.PARSED_CRON, None)
    parsed_interval = params.get(task_params.PARSED_INTERVAL, None)

    if (not name or
        not command or
        parsed_cron is False or
        (parsed_cron is None and parsed_interval is None) or
        (parsed_cron and parsed_interval)):

        return True

    return False


# if spam, just answer with success/fail
# returns string with message if notification
# is needed, otherwise False
def needs_notification(execution, prev_exec = None, spam = None):

    if (not execution.success()
        and (spam or not prev_exec or prev_exec.success())):
        return "failed"

    if (execution.success()
        and (spam or (prev_exec and not prev_exec.success()))):
        return "success"

    return False


# The parent concept of executing job (in scheduler) and pointer
# to past executions of that job
class Task():
    def __init__(self, name,
                 max_keep = None,
                 description = None,
                 count = None,
                 fail_by_stderr = None,
                 fail_by_retcode = None,
                 job_root_dir = None):

        if not job_root_dir:
            self.job_root_dir = app.config.get(con.JOB_ROOT_DIR, None)
        else:
            self.job_root_dir = job_root_dir

        self.count = count
        self.name = name
        self.max_keep = max_keep
        self.description = description
        self.fail_by_stderr = fail_by_stderr
        self.fail_by_retcode = fail_by_retcode

        self.conf_error = None
        self.running = False
        self.active = False

        self.next_run_time = None
        self.num_runs = None

    #@memoize
    def get_status(self):
        if not self.active:
            return status.INACTIVE
        if self.running:
            return status.RUNNING
        if self.conf_error:
            return status.CONF_ERROR
        last_execution = self.get_last_execution()
        if not last_execution:
            return status.NEVER_RUN
        else:
            return last_execution.get_status()

    @memoize
    def get_task_path(self):
        return self.name.lower()

    @memoize
    def get_job_path(self):
        job_dir = os.path.join(self.job_root_dir,
                               self.get_task_path())
        if not os.path.isdir(job_dir):
            app.logger.warn("%s: couldn't find task path : %s" % (self.name, job_dir))
            return None
        return job_dir

    def count_executions(self):
        return len(self._get_execution_dirs())

    def has_executions(self):
        return self.count_executions() > 0

    def _get_execution_dirs(self):
        '''
        List of all execution directories, absolute paths.
        This list is sorted in reverse chronological order.
        '''
        job_path = self.get_job_path()
        if job_path is None:
            return []

        dirs = os.listdir(job_path)
        dirs.sort()
        dirs.reverse()

        dirs = [os.path.join(job_path, x) for x in dirs]
        dirs = [x for x in dirs if os.path.isdir(x)]

        return dirs

    def get_executions(self, count = None):
        '''
        Get list of {count} most recent executions; or all if
        {count} > number of executions.
        '''
        if not count:
            count = self.count
        dirs = self._get_execution_dirs()
        results = []
        if len(dirs) > count:
            results = [Execution(x) for x in dirs[:count]]
        else:
            results = [Execution(x) for x in dirs]
        return results

    @memoize
    def success_rate(self, count = None):
        if not count:
            count = self.count
        results = self.get_executions(count)
        if not results:
            return None
        successes = [x for x in results if x.success()]
        return float(len(successes) / float(len(results)))

    def find_execution(self, timestamp):
        '''Get execution for given timestamp; None if given cannot be found'''
        dirs = self._get_execution_dirs()
        for x in dirs:
            if os.path.split(x)[-1] == timestamp:
                return Execution(x)
        return None

    def find_previous_execution(self, timestamp):
        '''Get previous execution to the given timestamp; None if
        given cannot be found or previous timestamp not available'''
        dirs = self._get_execution_dirs()
        this_index = -1
        for i, x in enumerate(dirs):
            if os.path.split(x)[-1] == timestamp:
                this_index = i
                break
        if this_index in (-1, len(dirs)-1):
            return None
        previous_timestamp = dirs[i+1]
        return Execution(previous_timestamp)

    def get_last_execution(self):
        '''Returns None if no executions found.'''
        results = self.get_executions(1)
        if not results or len(results) == 0:
            return None
        return results[0]

    # APScheduler is a task scheduler, so we have to hack in the immediate-execution
    # aspect. Immediate execution is handled here by using a scheduled execution
    # with a time of "now".
    # For intervals, this means descheduling the interval runner, executing now, then
    # then rescheduling the interval runner.
    # For cron tasks, this means running now and crossing our fingers.
    def run_now(self):
        pass

    def __str__(self):
        return "{name}:{status}:{path}:{executions}".format(
            name = self.name,
            status = self.get_status(),
            path = self.get_task_path(),
            executions = self.get_executions())


class Executor():
    ''' Callable with a memory. '''
    def __init__(self, name, command, max_keep = None,
                 job_root_dir = None):
        self.command = command
        self.config = None
        self.description = None
        self.email_recipients = None
        self.max_keep = max_keep
        self.name = name
        self.parsed_cron = None
        self.parsed_interval = None
        self.spam = None
        self.fail_by_stderr = None
        self.fail_by_retcode = None

        if not job_root_dir:
            self.job_root_dir = app.config.get(con.JOB_ROOT_DIR, None)
        else:
            self.job_root_dir = job_root_dir

    @memoize
    def get_op_params(self):
        return {
            task_params.NAME            : self.name,
            task_params.COMMAND         : self.command,
            task_params.PARSED_CRON     : self.parsed_cron,
            task_params.PARSED_INTERVAL : self.parsed_interval,
            task_params.SPAM            : self.spam,
            task_params.MAX_KEEP        : self.max_keep,
            task_params.FAIL_BY_STDERR  : self.fail_by_stderr,
            task_params.FAIL_BY_RETCODE : self.fail_by_retcode,
        }
        
    def get_conf_error(self):
        return is_conf_error(self.get_op_params())

    def get_task_path_name(self):
        return self.name.lower()

    def get_task_path(self):
        return os.path.join(self.job_root_dir,
                            self.get_task_path_name())

    def allocate_results(self):
        now = datetime.now()
        time_format = '%Y-%m-%d_%H:%M:%S'
        timestamp = now.strftime(time_format)
        this_run = os.path.join(self.get_task_path(), timestamp)
        if os.path.isdir(this_run):
            app.logger.info("Found task run target for %s" % this_run)
        else:
            app.logger.info("Creating path: %s" % this_run)
            os.makedirs(this_run)
        return this_run

    def needs_notification(self, execution):
        _task = Task(execution.name, job_root_dir = execution.task_root)
        prev_exec = _task.find_previous_execution(execution.timestamp)
        return needs_notification(execution, prev_exec, self.spam)

    def run(self):
        '''execute task, ping notifiers, clean up old tasks'''
        # allocate results in advance of running task in case it takes
        # a while -- timestamps would be unintuitive

        if self.get_conf_error():
            app.logger.error("%s: Configuration error and still asked to launch." % self.command)
            return

        results_dir = self.allocate_results()
        execution = Execution(results_dir)

        # set as running; run; set as not running
        try:
            execution.write_op_params(json.dumps(self.get_op_params(), sort_keys=True, indent=2))
            execution.start_running()
            with open(execution.std_out, "w") as fout, \
                open(execution.std_err, "w") as ferr:
                status_code = subprocess.call(self.command, stdout=fout, stderr=ferr, shell=True)
            execution.write_status_code(status_code)
        except Exception as inst:
            msg = "Exception running %s:\n%s\n%s" % (str(self.name), inst, traceback.format_exc())
            execution.write_op_error(msg)
            # task failure isn't our failure, but note it anyway
            app.logger.info("Exception executing %s:\n%s\n%s" % (str(self.name), inst, traceback.format_exc()))
        finally:
            execution.end_running()

        # email 'if needed'
        # TODO: this -> somewhere else?
        if not app.config.get(con.EMAIL_DISABLED, None):
            app.logger.debug("{0} testing for signal (run)".format(self.name))
            response = self.needs_notification(execution)
            app.logger.debug("{0} test response: {1}".format(self.name, response))
            if response is not False:
                app.logger.debug("{0} sending email".format(self.name))
                self.send_email(execution, response)

        # cleanup old runs if needed
        # TODO: this -> somewhere else?
        if self.max_keep:
            try:
                app.logger.info("Attempting to delete superfluous execution history for: " + self.name)
                app.logger.info("Checking: " + self.get_task_path())
                filer.clear_old_dirs(self.get_task_path(), self.max_keep)
            except Exception as inst:
                msg = "Exception cleaning old dirs %s:\n%s\n%s" % (str(self.name), inst, traceback.format_exc())
                app.logger.error(msg)
                execution.write_op_error(msg)

    def send_email(self, execution, flag):

        to_addresses = []
        global_addresses = app.config.get(con.EMAIL_TO_GLOBAL, [])
        to_addresses.extend(global_addresses)
        if self.email_recipients:
            to_addresses.extend(self.email_recipients)

        app.logger.debug("Attempting to send email to: {0}".format(str(to_addresses)))

        from_address = app.config.get(con.EMAIL_FROM_ADDRESS)
        smtp_server = app.config.get(con.EMAIL_SMTP)

        if not from_address:
            app.logger.warn("No sender available for this failing task: {0}".format(execution.name))
            return

        if not to_addresses:
            app.logger.warn("No recipients targeted for this failing task: {0}".format(execution.name))
            return

        if not smtp_server:
            app.logger.warn("No smtp server specified for this failing task: {0}".format(execution.name))
            return

        app.logger.info("Attempting to send failure notification for failing task {0}".format(execution.name))

        summary = ""
        if filer.is_file(execution.std_err) and filer.get_size(execution.std_err) > 0:
            summary = "stderr:\n" + filer.get_file_summary(execution.std_err, 2000, True)
        elif filer.is_file(execution.std_out) and filer.get_size(execution.std_out) > 0:
            summary = "stdout:\n" + filer.get_file_summary(execution.std_out, 2000, True)

        task_link = None
        if app.config.get(con.URL_ROOT, None):
            # not my favorite flaskism
            with app.test_request_context():
                from flask import url_for
                task_link_args = {
                    'server': app.config.get(con.URL_ROOT, None),
                    'port': app.config.get(con.PORT, None),
                    'route': url_for('show_tasks',
                                     task_name = execution.name,
                                     timestamp = execution.timestamp),
                }
                task_link = "http://{server}:{port}/{route}".format(**task_link_args)

        message = notification.create_mail(
            app_name = app.config.get(con.APP_NAME, "Speedrack"),
            task_name = execution.name,
            task_status = flag,
            task_link = task_link,
            to_addresses = to_addresses,
            message = summary,
            from_address = from_address)
        notification.send_mail(message, from_address, to_addresses, smtp_server)

    def __call__(self):
        self.run()


def is_execution_success(execution,
                         default_fail_by_stderr,
                         default_fail_by_retcode):
    # failing by retcode means either not finding a retcode OR finding
    # a retcode other than 0
    fail_by_stderr = default_fail_by_stderr
    fail_by_retcode = default_fail_by_retcode

    app.logger.debug("{0} {1}: fail_by_stderr {2}".format(execution.name, execution.timestamp, fail_by_stderr))
    app.logger.debug("{0} {1}: fail_by_retcode {2}".format(execution.name, execution.timestamp, fail_by_retcode))
    if execution.has_status_code():
        app.logger.debug("{0} {1}: status code: {2}".format(execution.name, execution.timestamp, execution.get_status_code()))

    # a task's individual settings override application settings
    if execution.has_params():
        params_read = execution.get_op_params()
        if params_read:
            if (task_params.FAIL_BY_STDERR in params_read
                and params_read[task_params.FAIL_BY_STDERR] != None):
                fail_by_stderr = params_read.get(task_params.FAIL_BY_STDERR, fail_by_stderr)
            if (task_params.FAIL_BY_RETCODE in params_read
                and params_read[task_params.FAIL_BY_RETCODE] != None):
                fail_by_retcode = params_read.get(task_params.FAIL_BY_RETCODE, fail_by_retcode)

    if fail_by_stderr and execution.has_std_err():
        app.logger.debug("%s %s: std_err found" % (execution.name, execution.timestamp))
        return False

    if fail_by_retcode and not execution.has_status_code():
        app.logger.debug("%s %s: no status code" % (execution.name, execution.timestamp))
        return False

    if fail_by_retcode and execution.get_status_code() != 0:
        app.logger.debug("%s %s: status code: %d" % (execution.name, execution.timestamp, execution.get_status_code()))
        return False

    return True


class Execution():
    ''' The working directory and results of one task. '''
    
    def __init__(self, job_dir):
        self.job_dir = job_dir
        self.op_error       = os.path.join(self.job_dir, "op_error.txt")
        self.running_status = os.path.join(self.job_dir, ".is_running")
        self.status_code    = os.path.join(self.job_dir, "status_code.txt")
        self.std_err        = os.path.join(self.job_dir, "std_err.txt")
        self.std_out        = os.path.join(self.job_dir, "std_out.txt")
        self.op_params      = os.path.join(self.job_dir, "op_params.txt")

        # TODO: yuck
        self.task_dir, self.timestamp = os.path.split(self.job_dir)
        self.task_root, self.name = os.path.split(self.task_dir)

        self._success = None
        self._status = None

    @memoize
    def get_status(self):
        if self._status:
            return self._status
        
        if self.execution_error():
            self._status = status.EXEC_ERROR
        elif self.is_running():
            self._status = status.RUNNING
        elif self.success():
            self._status = status.SUCCESS
        else:
            self._status = status.FAILURE

        return self._status

    def _write_to_file(self, file, content):
        try:
            with open(file, "w") as fout:
                fout.write(content)
                fout.flush()
        except EnvironmentError:
            app.logger.error("Could not write file: {0}".format(file))

    def start_running(self):
        self._write_to_file(self.running_status, str(True))

    def end_running(self):
        if os.path.isfile(self.running_status):
            os.unlink(self.running_status)

    def is_running(self):
        return os.path.isfile(self.running_status)

    def write_std_out(self, output):
        self._write_to_file(self.std_out, output)

    def write_std_err(self, error):
        self._write_to_file(self.std_err, error)

    def write_status_code(self, code):
        self._write_to_file(self.status_code, str(code))

    def write_op_error(self, op_error):
        self._write_to_file(self.op_error, op_error)

    def write_op_params(self, op_params):
        self._write_to_file(self.op_params, op_params)

    def get_status_code(self):
        """ Returns -999 if no status code found. """
        with open(self.status_code) as fin:
            lines = fin.readlines()
        if len(lines) == 0:
            return -999
        status = int(lines[0])
        return status

    @memoize
    def execution_error(self):
        return os.path.isfile(self.op_error)

    @memoize
    def has_std_out(self):
        return os.path.isfile(self.std_out) and os.path.getsize(self.std_out) > 0

    @memoize
    def has_std_err(self):
        return os.path.isfile(self.std_err) and os.path.getsize(self.std_err) > 0

    @memoize
    def has_status_code(self):
        return os.path.isfile(self.status_code) and os.path.getsize(self.status_code) > 0

    @memoize
    def has_params(self):
        return os.path.isfile(self.op_params)

    @memoize
    def get_default_label(self):
        if self.execution_error():
            return "operror"
        if self.has_std_err():
            return "stderr"
        return "stdout"

    @memoize
    def get_default_file(self):
        if self.execution_error():
            return self.op_error
        if self.has_std_err():
            return self.std_err
        return self.std_out

    @memoize
    def get_op_params(self):
        if not self.has_params():
            app.logger.info("{0} {1}: no parameters found".format(str(self.name), self.timestamp))
            return None

        with open(self.op_params) as fin:
            params_read = fin.read()

        if not params_read:
            app.logger.info("{0} {1}: parameters empty".format(str(self.name), self.timestamp))
            return None
        try:
            params = json.loads(params_read)
        except Exception as inst:
            msg = "Exception parsing {0} {1} params from json:\n{2}\n{3}".format(
                str(self.name), self.timestamp, inst, traceback.format_exc())
            app.logger.warn(msg)
            return None
        return params

    @memoize
    def success(self):
        return is_execution_success(self,
            default_fail_by_stderr = app.config.get(con.FAIL_BY_STDERR),
            default_fail_by_retcode = app.config.get(con.FAIL_BY_RETCODE))

    def __str__(self):
        msg = "Execution:%s" % (self.job_dir)
        if self.is_running():
            msg += ":running"
        elif self.success():
            msg += ":success"
        return msg


def load_config(file_name):
    with open(file_name) as fin:
        config = yaml.load(fin)
    return config


class Config():
    def __init__(self, file_name):
        self.parsed = load_config(file_name)

    def __str__(self):
        # we use json as a pretty printer because python's
        # pretty printer ain't pretty
        return str(json.dumps(self.parsed['tasks'], sort_keys=True, indent=2))
