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

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages


class rsyslog(SubSubtestCaller):

    config_section = 'images/rsyslog'


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


class install(SubSubtest):

    def initialize(self):
        super(install, self).initialize()
        self.sub_stuff['install_result'] = None
        self.sub_stuff['dir_exists'] = None
        self.sub_stuff['cfg_exists'] = None
        self.sub_stuff['sys_cfg_exists'] = None

    def run_once(self):
        super(install, self).run_once()
        imgs = DockerImages(self)
        img_name = imgs.list_imgs_full_name()[0]
        ins_result = utils.run('sudo atomic install %s' % img_name,
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

    def postprocess(self):
        super(install, self).postprocess()
        self.failif_ne(self.sub_stuff['install_result'].exit_status, 0,
                       'Atomic install command failed!')
        self.check_cfg()
        self.check_sys_cfg()
        self.check_dir()
