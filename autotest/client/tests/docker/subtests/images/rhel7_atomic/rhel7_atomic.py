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
import fileinput

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

    def load_image(self):
        if not self.check_loaded():
            cmd = (
                'sudo docker pull '
                'brew-pulp-docker01.web.prod.ext.phx2.redhat.com:8888/'
                'rhel7-atomic:{}-{}'.format(self.config['ver'], self.config['rls_ver'])
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
        return converted

    def stop_rm_ctn(self, ctn='rhel7-atomic'):
        self.loginfo('sudo docker stop {}....'.format(ctn))
        self.sub_stuff['stop_rst'] = utils.run(
            'sudo docker stop {}'.format(ctn), timeout=50
            )
        self.loginfo('sudo docker rm {}.....'.format(ctn))
        self.sub_stuff['rm_rst'] = utils.run(
            'sudo docker rm {}'.format(ctn), timeout=10
            )

    def rm_image(self, full_name):
        self.loginfo('sudo docker rmi {}....'.format(full_name))
        utils.run('sudo docker rmi {}'.format(full_name), timeout=60)

    def run_detached_img(self):
        cmd = ('sudo docker run -d --name=rhel7-atomic '
               '%s /bin/sleep 1000' % self.sub_stuff['img_name'])
        self.loginfo('running a detached conainer just sleeps 1000s....')
        utils.run(cmd, timeout=10)

    def check_registration(self):
        is_registered = False
        cmd = 'sudo subscription-manager list | grep -i subscribed'
        self.loginfo('Check registration by {}'.format(cmd))
        cmd_rst = utils.run(cmd, timeout=10, ignore_status=True)
        if not cmd_rst.exit_status:
            is_registered = True
        self.loginfo('is_registered: %s' % is_registered)
        return is_registered

    def unregister(self):
        cmd = 'sudo subscription-manager unregister'
        self.loginfo('unregistering.....')
        utils.run(cmd, timeout=30)

    def subscribe(self):
        username = self.config['sm_user']
        password = self.config['sm_pwd']
        cmd = ('sudo subscription-manager register '
               '--username %s --password %s '
               '--serverurl=subscription.rhn.stage.redhat.com '
               '--baseurl=cdn.stage.redhat.com '
               '--auto-attach' % (username, password))
        self.loginfo('subscribing.....')
        utils.run(cmd, timeout=50)

    def replace_line(self, file_dir, full_name):
        for line in fileinput.input(file_dir, inplace=True):
            if line.startswith('FROM '):
                print 'FROM ' + full_name
            else:
                print line

    def cleanup(self):
        super(rhel7_atomic_base, self).cleanup()
        # Sometimes images_obj.clean_all() just doesn't work
        self.stop_rm_ctn()
