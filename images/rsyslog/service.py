r"""
Summary
---------

Test SPC rhel7/rsyslog according to redhat customer portal

Operational Detail
----------------------
Steps:
#. Run command logger $msg on host
#. Check $msg is added /var/log/messages

Expectations:
#. Command is successfully run
#. $msg is added sucessfully

Prerequisites
---------------

*   rsyslog container is installed and started
"""

from autotest.client import utils
from rsyslog import rsyslog_base
import time


class service(rsyslog_base):

    def initialize(self):
        super(service, self).initialize()
        # Make sure images is loaded, installed and run
        self.load_image(self.config['img_stored_location'])
        self.get_run()

        self.sub_stuff['msg'] = 'Test that rsyslog is doing great'
        self.sub_stuff['last_line'] = ''

    def run_once(self):
        super(service, self).run_once()
        logger_cmd = "logger '%s'" % self.sub_stuff['msg']
        utils.run(logger_cmd)
        time.sleep(3)

        tail_cmd = "tail -n 1 /var/log/messages"
        self.sub_stuff['last_line'] = utils.run(tail_cmd).stdout

    def postprocess(self):
        self.loginfo(self.sub_stuff['last_line'])
        self.failif(self.sub_stuff['msg'] not in self.sub_stuff['last_line'],
                    'rsyslog service does not work!')
