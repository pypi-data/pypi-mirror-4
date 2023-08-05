=========
SPEEDRACK
=========

Speedrack is a single-node cron system with an attractive web interface, job-tracking and configurable notification via email. It's not the task runner you need, but it might be the one you deserve.

It is intended to drive regular executions of low-resource shell scripts, routing output to defined locations. The web front end makes it easy to see a high-level overview. It's convenient and easy.

Quick Installation and Local Demonstration
------------------------------------------

Easiest way to get a feel for it is to just install and play with it.

1. Start with python 2.6+: http://www.python.org/download
2. (bonus: Use virtualenv_ (intermediate, recommended))
3. Install pip: ``easy_install pip``
4. Install speedrack: ``pip install speedrack``
5. Start speedrack: ``speedrack run``
6. Done! Check it out: ``http://localhost:8118``

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

Speedrack comes with a demo mode, so look at your sample tasks churn. Results for these tasks are being pooled in your system temp directory.

For more information, please visit `speedrack's documentation`_.

For a picture, please visit `speedrack's introduction post`_.

.. _speedrack's documentation: http://speedrack.readthedocs.org/
.. _speedrack's introduction post: http://spaceponies.com/speedrack-initial-release.html

