# how to pollute the jinja namespace conveniently

from speedrack import app
from speedrack import status

from datetime import datetime

import filer

@app.context_processor
def inject_filer():
    return { "filer": filer }

@app.context_processor
def inject_launch():
    # set in __init__, lame
    return dict(datetime_launch=app.config['datetime_launch'])

@app.context_processor
def inject_now():
    return dict(get_datetime_now=datetime.now)

@app.context_processor
def inject_status():
    return {
        "get_all_status": status.get_all_status,
        "get_status_description": status.get_description,
        "get_status_severity": status.get_severity,
    }
