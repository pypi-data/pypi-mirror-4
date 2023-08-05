from email.mime.text import MIMEText
import email.utils
import smtplib

from speedrack import app

content_with_link = \
"""
task: {task_name}
execution: {task_link}

{message}
"""
content_no_link = \
"""
task: {task_name}

{message}
"""

def create_mail(task_name, task_status,
                from_address, to_addresses,
                app_name="", task_link="", message=""):
    """Returns a string suitable for handing to sendmail"""

    if task_link:
        content = content_with_link.format(task_name=task_name,
                                           task_link=task_link,
                                           message=message)
    else:
        content = content_no_link.format(task_name=task_name,
                                         message=message)
    
    subject_template = "[{app_name}] {name} {status}"
    subject = subject_template.format(app_name=app_name,
                                      name=task_name,
                                      status=task_status)

    mime = MIMEText(content)
    mime['Subject']  = subject
    mime['From']     = email.utils.formataddr((app_name, from_address))
    mime['Reply-to'] = email.utils.formataddr((None, from_address)) # needed by some sendmail configurations
    mime['To']       = ",".join([email.utils.formataddr((None, x)) for x in to_addresses])

    return mime.as_string()

def send_mail(outbound_message, from_address, to_addresses, smtp_server):
    """Uses app/config settings to sendmail"""

    to_addresses = [email.utils.formataddr((None, x)) for x in to_addresses]

    app.logger.debug("opening connection to {0}".format(smtp_server))

    smtp = None
    if not app.config.get("EMAIL_DEBUG"):
        smtp = smtplib.SMTP(smtp_server)
    try:
        app.logger.debug("from: {0}\nto: {1}\nmessage: {2}".format(from_address, to_addresses, outbound_message))
        failed = False
        if not app.config.get("EMAIL_DEBUG"):
            failed = smtp.sendmail(from_address, to_addresses, outbound_message)
    except Exception, e:
        failed = "Exception: {0}\n---".format(str(e))
    finally:
        if not app.config.get("EMAIL_DEBUG"):
            smtp.close()
        if failed:
            app.logger.error("undelivered(?) message:\n---\n{0}---\n{1}\n---\n".format(failed, outbound_message))
        else:
            app.logger.debug("notification sent successfully")
