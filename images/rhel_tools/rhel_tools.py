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

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from autotest.client.shared import error


class rhel_tools(SubSubtestCaller):

    config_section = 'images/rhel_tools'


class load(SubSubtest):

    def initialize(self):
        super(load, self).initialize()
        self.sub_stuff['load_result'] = None

    def load_image(self, location):
        cmd = 'cat %s | sudo docker load' % location
        cmd_result = utils.run(cmd, timeout=300, ignore_status=True)
        return cmd_result

    def run_once(self):
        img_stored_location = self.config['img_stored_location']
        cmd_result = self.load_image(img_stored_location)
        self.sub_stuff['load_result'] = cmd_result

    def postprocess(self):
        self.failif_ne(self.sub_stuff['load_result'].exit_status, 0,
                       'Fail to load image!')


class run_img(SubSubtest):

    def initialize(self):
        super(run_img, self).initialize()
        self.sub_stuff['img_name'] = None
        self.sub_stuff['run_rst'] = None

    def run_once(self):
        super(run_img, self).run_once()
        imgs = DockerImages(self)
        for img_name in imgs.list_imgs_full_name():
            if 'rhel-tools' in img_name:
                self.sub_stuff['img_name'] = img_name
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        try:
            utils.run(run_cmd, timeout=5)
        except error.CmdError, exc:
            err = exc.result_obj.stdout
            self.sub_stuff['run_rst'] = err

    def postprocess(self):
        super(run_img, self).postprocess()
        self.failif(
            not self.sub_stuff['run_rst'].strip().endswith('#'),
            "Container is not automatically attched!")
