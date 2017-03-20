r"""
Summary
---------

Test SPC rhel7/sadc according to redhat customer portal

Operational Detail
----------------------
#. Load image sadc
#. Install it with atomic command
#. Check /etc/cron.d/sysstat file on host
#. Check /etc/sysconfig/sysstat file on host
#. Check /etc/sysconfig/sysstat.ioconf file on host
#. Check /usr/local/bin/sysstat.sh file on host

Prerequisites
---------------

*   Clean host without sadc container ever installed
"""

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages


class sadc(SubSubtestCaller):

    config_section = 'images/sadc'


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
        self.sub_stuff['etc_crond_sysstat_exists'] = None
        self.sub_stuff['etc_sysconfig_sysstat_exists'] = None
        self.sub_stuff['etc_sysconfig_sysstat_ioconf_exists'] = None
        self.sub_stuff['usr_local_bin_sysstat_sh_exists'] = None

    def run_once(self):
        super(install, self).run_once()
        imgs = DockerImages(self)
        for img_name in imgs.list_imgs_full_name():
            if 'sadc' in img_name:
                break
        ins_result = utils.run('sudo atomic install %s' % img_name,
                               timeout=60, ignore_status=True)
        self.sub_stuff['install_result'] = ins_result

        # List /etc/cron.d/sysstat
        cmd1 = 'ls /etc/cron.d/sysstat'
        cmd1_result = utils.run(cmd1, ignore_status=True)
        self.sub_stuff['etc_crond_sysstat_exists'] = cmd1_result.exit_status

        # List /etc/sysconfifg/sysstat
        cmd2 = 'ls /etc/sysconfig/sysstat'
        cmd2_result = utils.run(cmd2, ignore_status=True)
        self.sub_stuff['etc_sysconfig_sysstat_exists'] = \
            cmd2_result.exit_status

        # list /etc/sysconfig/sysstat.ioconf
        cmd3 = 'ls /etc/sysconfig/sysstat.ioconf'
        cmd3_result = utils.run(cmd3, ignore_status=True)
        self.sub_stuff['etc_sysconfig_sysstat_ioconf_exists'] = \
            cmd3_result.exit_status

        # list /usr/local/bin/sysstat.sh
        cmd4 = 'ls /usr/local/bin/sysstat.sh'
        cmd4_result = utils.run(cmd4, ignore_status=True)
        self.sub_stuff['usr_local_bin_sysstat_sh_exists'] = \
            cmd4_result.exit_status

    def check_etc_crond_sysstat(self):
        self.failif_ne(self.sub_stuff['etc_crond_sysstat_exists'], 0,
                       '/etc/cron.d/sysstat does not exist on host!')

    def check_etc_sysconfig_sysstat(self):
        self.failif_ne(self.sub_stuff['etc_sysconfig_sysstat_exists'], 0,
                       '/etc/sysconfig/sysstat does not exist on host!')

    def check_etc_sysconfig_sysstat_ioconf(self):
        self.failif_ne(
            self.sub_stuff['etc_sysconfig_sysstat_ioconf_exists'], 0,
            '/etc/sysconfig/sysstat.ioconf does not exist on host!')

    def check_usr_local_bin_sysstat_sh(self):
        self.failif_ne(self.sub_stuff['usr_local_bin_sysstat_sh_exists'], 0,
                       '/usr/local/bin/sysstat.sh does not exist on host!')

    def postprocess(self):
        super(install, self).postprocess()
        self.failif_ne(self.sub_stuff['install_result'].exit_status, 0,
                       'Atomic install command failed!')
        self.check_etc_crond_sysstat()
        self.check_etc_sysconfig_sysstat()
        self.check_etc_sysconfig_sysstat_ioconf()
        self.check_usr_local_bin_sysstat_sh()
