from nose.tools import *

from speedrack import notification

class TestEmail(object):

    # Not testing the entire structure of email because the underlying
    # libraries should get it right. Just making sure that we haven't
    # screwed something up fundamentally.
    def test_create_email(self):

        task_name    = "tasker"
        task_status  = "huge success"
        from_address = "wham@example.com"
        to_addresses = ["bam@example.com"]
        task_link    = "http://beepbeepimajeep.com"
        message      = "You are the best!"

        email_str = notification.create_mail(
            task_name=task_name,
            task_status=task_status,
            to_addresses=to_addresses,
            task_link=task_link,
            message=message,
            from_address=from_address
        )

        assert_in(task_name, email_str)
        assert_in(task_status, email_str)
        assert_in(task_link, email_str)
        assert_in(message, email_str)
