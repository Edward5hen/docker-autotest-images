r"""
Summary
---------

Operational Detail
----------------------
#. Check if net-snmp has been pulled or not.
#. If not, pull it.
#. Remove the image in cleanup.

Prerequisites
---------------

*   Clean host without net-snmp container ever installed
"""
import re

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages


class net_snmp(SubSubtestCaller):

    config_section = 'images/net_snmp'


class net_snmp_base(SubSubtest):

    def initialize(self):
        super(net_snmp_base, self).initialize()
        self.sub_stuff['img_name'] = None
        self.regx = '[0-9]{1,3}'

    def load_image(self):
        if not self.check_loaded():
            cmd = (
                'sudo docker pull '
                'brew-pulp-docker01.web.prod.ext.phx2.redhat.com:8888/'
                'rhel7/net-snmp:{}-{}'.format(self.config['ver'], self.config['rls_ver'])
                )
            utils.run(cmd, timeout=10 * 60)
            self.loginfo('Image is pulled successfully')
            # Check it again and make self.sub_stuff['img_name'] have value.
            self.check_loaded()
        else:
            self.loginfo('Image does not need to load')

    def check_loaded(self):
        images = DockerImages(self)
        cmd = 'sudo docker inspect %s | grep -i "\\"release\\":" | head -1'
        for image_name in images.list_imgs_full_name():
            if 'net-snmp' in image_name:
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
