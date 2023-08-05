from speedrack import app
from speedrack import models
from speedrack import aps

from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

HIDE_INACTIVE_TASKS = "hide_inactive"

@app.route("/tasks/")
@app.route("/")
@app.route("/tasks/<task_name>")
@app.route("/tasks/<task_name>/<timestamp>")
def show_tasks(task_name = None, timestamp = None):

    hide_inactive = g.hide_inactive

    task_list = models.TaskList(sched = app._sched)
    tasks = task_list.get(hide_inactive)
    display_task = None
    display_execution = None
    display_label = None
    display_file = None
    just_launched = False

    if 'just_launched' in request.args:
        just_launched = True

    if task_name:
        task_name = task_name.lower()
        display_task = task_list.find_task(task_name)
        if timestamp:
            display_execution = display_task.find_execution(timestamp)
        else:
            display_execution = display_task.get_last_execution()


        # if we have a specific request, honor that; otherwise deduce
        # the best
        if ('operror' in request.args
            or 'opparams' in request.args
            or 'stderr' in request.args
            or 'stdout' in request.args):
            if 'operror' in request.args:
                display_label = 'operror'
                display_file = display_execution.op_error
            elif 'opparams' in request.args:
                display_label = 'opparams'
                display_file = display_execution.op_params
            elif 'stderr' in request.args:
                display_label = 'stderr'
                display_file = display_execution.std_err
            elif 'stdout' in request.args:
                display_label = 'stdout'
                display_file = display_execution.std_out
        else:
            if display_execution:
                display_label = display_execution.get_default_label()
                display_file = display_execution.get_default_file()

    return render_template("tasks.html.jinja",
                           task_list = tasks,
                           display_task = display_task,
                           display_execution = display_execution,
                           display_label = display_label,
                           display_file = display_file,
                           just_launched = just_launched,
        )

@app.route("/tasks/<task_name>/<timestamp>/<display_label>")
def show_task_file(task_name = None, timestamp = None, display_label = None):
    if task_name is None:
        flash("How did you get here with no task? It's a mystery.", "error")
        return redirect(url_for('show_tasks'))
    if timestamp is None:
        flash("How did you get here with no timestamp? It's a mystery.", "error")
        return redirect(url_for('show_tasks', task_name=task_name))
    if display_label is None:
        flash("How did you get here with no file? It's a mystery.", "error")
        return redirect(url_for('show_tasks', task_name=task_name))

    task_list = models.TaskList(sched = app._sched)
    task_name = task_name.lower()
    display_task = task_list.find_task(task_name)
    display_execution = display_task.find_execution(timestamp)

    display_file = None
    if 'stderr' == display_label:
        display_file = display_execution.std_err
    elif 'stdout' == display_label:
        display_file = display_execution.std_out
    elif 'params' == display_label:
        display_file = display_execution.op_params

    return render_template("file.html.jinja",
                           task_name = task_name,
                           timestamp = timestamp,
                           display_label = display_label,
                           file_name = display_file)

@app.route("/tasks/<task_name>/execute")
def run_task(task_name = None):
    if task_name is None:
        flash("How did we end up here? It's a mystery.", "warning")
        return redirect(url_for('show_tasks'))

    task_name = task_name.lower()
    success = aps.run_task(app._sched, task_name)
    if not success:
        flash("Couldn't find your job. How did we get here?", "error")
        return redirect(url_for('show_tasks'))

    flash("Submitted [%s] for immediate execution." % task_name, "info")
    return redirect(url_for('show_tasks', task_name = task_name, just_launched = True))

@app.route("/config/reload")
def reload_config():
    app._shutdown = True
    app._sched = aps.update(app._sched,
                            app.config.get('CONFIG_YAML', None),
                            app.config.get('JOB_STATE', None))
    app._shutdown = False
    _flash_msg = "Reloaded config file: {conf}".format(conf=app.config.get('CONFIG_YAML', None))
    flash(_flash_msg, "success")
    return redirect(url_for('show_debug'))

@app.route("/config/clear")
def clear_config():
    aps.clear(app._sched,
              app.config.get('JOB_STATE', None))
    flash("Scheduler cleared of running tasks; consider reloading config now.")
    return redirect(url_for('show_debug'))

@app.route("/debug")
def show_debug():
    yaml_config = models.Config(app.config['CONFIG_YAML'])
    display_data = 'scheduled'
    if ('scheduled' in request.args
        or 'settings' in request.args
        or 'raw' in request.args
        or 'parsed' in request.args):

        if 'scheduled' in request.args:
            display_data = 'scheduled'
        elif 'settings' in request.args:
            display_data = 'settings'
        elif 'raw' in request.args:
            display_data = 'raw'
        elif 'parsed' in request.args:
            display_data = 'parsed'

    jobs = app._sched.get_jobs()
    return render_template("debug.html.jinja",
                           jobs=jobs,
                           yaml_config=yaml_config,
                           display_data=display_data)

@app.route("/help")
def show_help():
    return render_template("help.html.jinja")

@app.route("/holding")
def show_holding():
    return render_template("holding.html.jinja")

@app.before_request
def before_request():
    if HIDE_INACTIVE_TASKS in session and session[HIDE_INACTIVE_TASKS]:
        g.hide_inactive = True
    else:
        g.hide_inactive = False

    if app._shutdown:
        flash("System is shutting down or restarting, stop clicking buttons.", "warning")
        redirect(url_for('show_holding'))
        g.shutdown = True
    else:
        g.shutdown = False

@app.route("/toggle_inactive")
def toggle_inactive_tasks():
    if HIDE_INACTIVE_TASKS not in session or not session[HIDE_INACTIVE_TASKS]:
        session[HIDE_INACTIVE_TASKS] = True
    else:
        session[HIDE_INACTIVE_TASKS] = False
    return redirect(url_for('show_tasks'))
