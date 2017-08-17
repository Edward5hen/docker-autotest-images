r"""
Summary
---------

Test SPC rhel7/rhel-tools according to redhat customer portal

Operational Detail
----------------------
#. Load image rhel-tools
#. Run image rhel-tools

Prerequisites
---------------

*   Clean host without rhel-tools container ever installed
"""
import re

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from autotest.client.shared import error


class rhel_tools(SubSubtestCaller):

    config_section = 'images/rhel_tools'


class rhel_tools_base(SubSubtest):

    def initialize(self):
        super(rhel_tools_base, self).initialize()
        self.sub_stuff['img_name'] = None
        self.regx = '[0-9]{1,3}'

    def load_image(self, location):
        if not self.check_loaded():
            cmd = 'cat %s | sudo docker load' % location
            utils.run(cmd, timeout=300, ignore_status=True)
            self.check_loaded()
        else:
            self.loginfo('image does not need to load')

    def check_loaded(self):
        images = DockerImages(self)
        cmd = 'sudo docker inspect %s | grep -i "\\"release\\":" | head -1'
        for image_name in images.list_imgs_full_name():
            if 'rhel-tools' in image_name:
                release_line = utils.run(cmd % image_name, timeout=30)
                rst = re.search(self.regx, release_line.stdout)
                if rst is not None:
                    if str(self.config['rls_ver']) == rst.group():
                        self.sub_stuff['img_name'] = image_name
                        return True
                else:
                    raise ValueError('No digital release info found!')
        return False

    def format_output(self, output):
        """
        Output of a linux command often includes tabs and spaces,
        this method tries to convert output to python lists
        """
        converted = []
        tmp = []
        for eachLine in output.split('\n'):
            tmp = re.split('\s\s+|\t+', eachLine)
            # Sometimes returned list need to change to set
            tmp = tuple(tmp)
            converted.append(tmp)
        return converted


class run_img(rhel_tools_base):

    def initialize(self):
        super(run_img, self).initialize()
        self.sub_stuff['img_name'] = None
        self.sub_stuff['run_rst'] = None
        self.load_image(self.config['img_stored_location'])

    def check_size(self):
        """
        This method is to check image's size.
        The correct size must be between 90%-110% of 1.4GB.
        """
        can_pass = 0
        min_size = 0.9 * 1.4
        max_size = 1.1 * 1.4
        cmd = "sudo docker images --format={{.Repository}}:{{.Tag}}\
hope-not-exist{{.Size}} | grep %s" % self.sub_stuff['img_name']
        rst = utils.run(cmd).stdout.split('hope-not-exist')[-1]
        actual_size = float(rst[:-3])
        self.loginfo('Image size is %s' % actual_size)
        if min_size < actual_size < max_size:
            can_pass = 1
        self.failif_ne(can_pass, 1, "Size is not Correct")

    def run_once(self):
        super(run_img, self).run_once()
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        try:
            utils.run(run_cmd, timeout=30)
        except error.CmdError, exc:
            err = exc.result_obj.stdout
            self.sub_stuff['run_rst'] = err

    def postprocess(self):
        super(run_img, self).postprocess()
        self.failif(
            not self.sub_stuff['run_rst'].strip().endswith('#'),
            "Container is not automatically attched!")
        self.check_size()
