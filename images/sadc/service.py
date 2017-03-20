r"""
Summary
---------

Test SPC rhel7/sadc according to redhat customer portal

Operational Detail
----------------------
Steps:
#. Run command docker exec sadc-docker /usr/lib64/sa/sa1 1 1 on host
#. Check file /var/log/sa/sa"$date" is generated

Prerequisites
---------------

*   sadc container is installed and started
"""

from autotest.client import utils
from dockertest.subtest import SubSubtest
import time
import datetime


class service(SubSubtest):

    def initialize(self):
        super(service, self).initialize()
        self.sub_stuff['check_file_rst'] = None

    def run_once(self):
        super(service, self).run_once()
        sa_cmd = 'sudo docker exec sadc-docker /usr/lib64/sa/sa1 1 1'
        utils.run(sa_cmd)
        time.sleep(3)

        today = datetime.datetime.today().day
        check_file_cmd = "sudo ls /var/log/sa/sa%s" % today
        self.sub_stuff['check_file_rst'] = utils.run(
                check_file_cmd).exit_status

    def postprocess(self):
        self.failif_ne(self.sub_stuff['check_file_rst'], 0,
                       '/var/log/sa/sa$date file is not generated!')
