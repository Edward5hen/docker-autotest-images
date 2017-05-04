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

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages


class rhel7_atomic(SubSubtestCaller):

    config_section = 'images/rhel7_atomic'


class rhel7_atomic_base(SubSubtest):

    def initialize(self):
        super(rhel7_atomic_base, self).initialize()
        self.sub_stuff['image_name'] = ''
        self.sub_stuff['images_obj'] = DockerImages(self)

        if not self.check_load(self.sub_stuff['images_obj']):
            self.load_image(self.config['img_stored_location'])
            # Get the image name again
            self.check_load(self.sub_stuff['images_obj'])
        self.loginfo('Image rhel7-atomic has been loaded!')

    def check_load(self, img_obj):
        does_load = False
        for img_name in img_obj.list_imgs_full_name():
            if 'rhel7-atomic' in img_name:
                does_load = True
                self.sub_stuff['image_name'] = img_name
        return does_load

    def load_image(self, location):
        cmd = 'cat %s | sudo docker load' % location
        utils.run(cmd, timeout=300)

    def cleanup(self):
        super(rhel7_atomic_base, self).cleanup()
        # Sometimes images_obj.clean_all() just doesn't work
        utils.run('sudo docker stop rhel7-atomic', timeout=20,
                  ignore_status=True)
        utils.run('sudo docker rm rhel7-atomic', timeout=10,
                  ignore_status=True)
        utils.run('sudo docker rmi %s' % self.sub_stuff['image_name'],
                  timeout=10, ignore_status=True)
