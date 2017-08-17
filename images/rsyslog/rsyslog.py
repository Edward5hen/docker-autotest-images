r"""
Summary
---------

Test SPC rhel7/rsyslog according to redhat customer portal

Operational Detail
----------------------
Steps:
#. Load image rsyslog
#. Install it with atomic command
#. Check /etc/pki/rsyslog directory on host
#. Check /etc/rsyslog.conf file on host
#. Check /etc/sysconfig/rsyslog file on host

Expectations:
#. Image is loaded successfully
#. command runs successfully with correct output
#. Directory is successfully created on host
#. Config file is successfully created on host

Prerequisites
---------------

*   Clean host without rsyslog container ever installed
"""
import re

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from autotest.client.shared import error


class rsyslog(SubSubtestCaller):

    config_section = 'images/rsyslog'


class rsyslog_base(SubSubtest):

    def initialize(self):
        super(rsyslog_base, self).initialize()
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
            if 'rsyslog' in image_name:
                release_line = utils.run(cmd % image_name, timeout=30)
                rst = re.search(self.regx, release_line.stdout)
                if rst is not None:
                    if str(self.config['rls_ver']) == rst.group():
                        self.sub_stuff['img_name'] = image_name
                        return True
                else:
                    raise ValueError('No digital release info found!')
        return False

    def get_installed(self):
        """ Have to be used after load_image """
        cmd = 'sudo atomic install %s' % self.sub_stuff['img_name']
        utils.run(cmd, timeout=120)

    def get_run(self):
        cmd_ps = 'sudo docker ps --format={{.Names}}'
        cmd_run = 'sudo atomic run %s' % self.sub_stuff['img_name']
        self.get_installed()
        if 'rsyslog' not in utils.run(cmd_ps).stdout:
            utils.run(cmd_run, timeout=120)

    def format_output(self, output):
        """
        Output of a linux command often includes tabs and spaces,
        this method tries to convert output to a python list
        """
        converted = []
        tmp = []
        for eachLine in output.split('\n'):
            tmp = re.split('\s\s+|\t+', eachLine)
            # Sometimes returned list need to change to set
            tmp = tuple(tmp)
            converted.append(tmp)
        return converted


class install(rsyslog_base):

    def initialize(self):
        super(install, self).initialize()
        self.load_image(self.config['img_stored_location'])
        # Uninstall the image first, if there was some older version installed
        try:
            utils.run('sudo atomic uninstall %s' % self.sub_stuff['img_name'],
                      timeout=30)
        except error.CmdError:
            self.loginfo('Uninstall failed!')

        self.loginfo(self.sub_stuff['img_name'])
        self.sub_stuff['install_result'] = None
        self.sub_stuff['dir_exists'] = None
        self.sub_stuff['cfg_exists'] = None
        self.sub_stuff['sys_cfg_exists'] = None

    def run_once(self):
        super(install, self).run_once()
        ins_result = utils.run(
            'sudo atomic install %s' % self.sub_stuff['img_name'],
            timeout=60, ignore_status=True)
        self.sub_stuff['install_result'] = ins_result

        # List /etc/pki/rsyslog dir
        cmd1 = 'ls /etc/pki/rsyslog'
        cmd1_result = utils.run(cmd1, ignore_status=True)
        self.sub_stuff['dir_exists'] = cmd1_result.exit_status

        # List /etc/rsyslog.conf
        cmd2 = 'ls /etc/rsyslog.conf'
        cmd2_result = utils.run(cmd2, ignore_status=True)
        self.sub_stuff['cfg_exists'] = cmd2_result.exit_status

        # list /etc/sysconfig/rsyslog
        cmd3 = 'ls /etc/sysconfig/rsyslog'
        cmd3_result = utils.run(cmd3, ignore_status=True)
        self.sub_stuff['sys_cfg_exists'] = cmd3_result.exit_status

    def check_dir(self):
        self.failif_ne(self.sub_stuff['dir_exists'], 0,
                       '/etc/pki/rsyslog does not exist on host!')

    def check_cfg(self):
        self.failif_ne(self.sub_stuff['cfg_exists'], 0,
                       '/etc/rsyslog.conf does not exist on host!')

    def check_sys_cfg(self):
        self.failif_ne(self.sub_stuff['sys_cfg_exists'], 0,
                       '/etc/sysconfig/rsyslog does not exist on host!')

    def check_size(self):
        """
        This method is to check image's size.
        The correct size must be between 90%-110% of 208 MB.
        """
        can_pass = 0
        min_size = 0.9 * 208
        max_size = 1.1 * 208
        cmd = "sudo docker images --format={{.Repository}}:{{.Tag}}\
hope-not-exist{{.Size}} | grep %s" % self.sub_stuff['img_name']
        rst = utils.run(cmd).stdout.split('hope-not-exist')[-1]
        actual_size = float(rst[:-3])
        self.loginfo('Image size is %s' % actual_size)
        if min_size < actual_size < max_size:
            can_pass = 1
        self.failif_ne(can_pass, 1, "Size is not Correct")

    def postprocess(self):
        super(install, self).postprocess()
        self.failif_ne(self.sub_stuff['install_result'].exit_status, 0,
                       'Atomic install command failed!')
        self.check_cfg()
        self.check_sys_cfg()
        self.check_dir()
        self.check_size()
