from speedrack import app
from speedrack import status

@app.template_filter()
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)

@app.template_filter()
def status_severity(s):
    return status.get_severity(s)

@app.template_filter()
def leading(lobjs, count):
    return lobjs[0:count]
