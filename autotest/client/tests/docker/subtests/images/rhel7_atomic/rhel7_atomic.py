r"""
Summary
---------

Operational Detail
----------------------
#. Check if rhel7-atomic has been loaded or not.
#. If not, load it.
#. Remove the image in cleanup.

Prerequisites
---------------

*   Clean host without rhel7-atomic container ever installed
"""
import re

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages


class rhel7_atomic(SubSubtestCaller):

    config_section = 'images/rhel7_atomic'


class rhel7_atomic_base(SubSubtest):

    def initialize(self):
        super(rhel7_atomic_base, self).initialize()
        self.sub_stuff['images_obj'] = DockerImages(self)
        self.sub_stuff['stop_rst'] = None
        self.sub_stuff['rm_rst'] = None
        self.sub_stuff['img_name'] = None
        self.regx = '[0-9]{1,3}'

    def load_image(self, location):
        if not self.check_loaded():
            cmd = 'cat %s | sudo docker load' % location
            utils.run(cmd, timeout=300, ignore_status=True)
            self.loginfo('Image is loaded successfully')
            self.check_loaded()
        else:
            self.loginfo('Image does not need to load')

    def check_loaded(self):
        images = DockerImages(self)
        cmd = 'sudo docker inspect %s | grep -i "\\"release\\":" | head -1'
        for image_name in images.list_imgs_full_name():
            if 'rhel7-atomic' in image_name:
                release_line = utils.run(cmd % image_name, timeout=30)
                rst = re.search(self.regx, release_line.stdout)
                if rst is not None:
                    if str(self.config['rls_ver']) == rst.group():
                        self.sub_stuff['img_name'] = image_name
                        self.loginfo('Image is loaded and match the version.')
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

    def stop_rm_ctn(self):
        self.loginfo('sudo docker stop rehl7-atomic....')
        self.sub_stuff['stop_rst'] = utils.run(
            'sudo docker stop rhel7-atomic', timeout=50
            )
        self.loginfo('sudo docker rm rhel7-atomic.....')
        self.sub_stuff['rm_rst'] = utils.run(
            'sudo docker rm rhel7-atomic', timeout=10
            )

    def cleanup(self):
        super(rhel7_atomic_base, self).cleanup()
        # Sometimes images_obj.clean_all() just doesn't work
        self.stop_rm_ctn()
