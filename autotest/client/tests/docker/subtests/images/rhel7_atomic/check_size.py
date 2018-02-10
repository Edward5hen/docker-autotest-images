r"""
Summary
---------
Check container image's size

Operational Detail
----------------------
Check container image's size is between 0.9-1.1 x normal_size

Prerequisites
---------------
"""
import os

from autotest.client import utils
from rhel7_atomic import rhel7_atomic_base

NORMAL_SIZE = 78


class check_size(rhel7_atomic_base):

    def initialize(self):
        super(check_size, self).initialize()

        self.load_image()

    def check_size(self):
        """
        This method is to check image's size.
        The correct size must be between 90%-110% of 1.4GB.
        """
        can_pass = 0
        min_size = 0.9 * NORMAL_SIZE
        max_size = 1.1 * NORMAL_SIZE
        cmd = (
            'sudo docker images --format={{{{.Repository}}}}:{{{{.Tag}}}}'
            'hope-not-exist{{{{.Size}}}} '
            '| grep {}'.format(self.sub_stuff['img_name'])
            )
        rst = utils.run(cmd).stdout.split('hope-not-exist')[-1]
        actual_size = float(rst[:-3])
        self.loginfo('Image size is %s' % actual_size)
        self.loginfo('Need to be greater than 0.9*{}, lower than 1.1*{}'.format(NORMAL_SIZE, NORMAL_SIZE))
        if min_size < actual_size < max_size:
            can_pass = 1
        self.failif_ne(can_pass, 1, "Size is not Correct")

    def postprocess(self):
        super(check_size, self).postprocess()

        self.check_size()

    def cleanup(self):
        pass

