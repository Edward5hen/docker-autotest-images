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
import time
import datetime

from autotest.client import utils
from sadc import sadc_base


class service(sadc_base):

    def initialize(self):
        super(service, self).initialize()
        self.sub_stuff['check_file_rst'] = None

        # Make sure images is loaded, installed and run
        self.load_image()
        self.get_run()

    def run_once(self):
        super(service, self).run_once()
        sa_cmd = 'sudo docker exec sadc /usr/lib64/sa/sa1 1 1'
        utils.run(sa_cmd)
        self.loginfo('Run command %s' % sa_cmd)
        time.sleep(3)

        today = datetime.datetime.today().day
        check_file_cmd = "sudo ls /var/log/sa/sa%s" % today
        self.sub_stuff['check_file_rst'] = utils.run(
            check_file_cmd).exit_status

    def postprocess(self):
        self.failif_ne(self.sub_stuff['check_file_rst'], 0,
                       '/var/log/sa/sa$date file is not generated!')
        self.loginfo('/var/log/sa/sa$date is successfully generated')
