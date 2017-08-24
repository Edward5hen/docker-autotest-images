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
import re

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from autotest.client.shared import error


class sadc(SubSubtestCaller):

    config_section = 'images/sadc'


class sadc_base(SubSubtest):

    def initialize(self):
        super(sadc_base, self).initialize()
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
            if 'sadc' in image_name:
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

    def get_installed(self):
        """ Have to be used after load_image """
        cmd = 'sudo atomic install %s' % self.sub_stuff['img_name']
        utils.run(cmd, timeout=120, ignore_status=True)
        self.loginfo('Image is successfully installed')

    def get_run(self):
        cmd_ps = 'sudo docker ps --format={{.Names}}'
        cmd_run = 'sudo atomic run %s' % self.sub_stuff['img_name']
        self.get_installed()
        if 'sadc' not in utils.run(cmd_ps).stdout:
            utils.run(cmd_run, timeout=120)

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


class install(sadc_base):

    def initialize(self):
        super(install, self).initialize()
        self.sub_stuff['install_result'] = None
        self.sub_stuff['etc_crond_sysstat_exists'] = None
        self.sub_stuff['etc_sysconfig_sysstat_exists'] = None
        self.sub_stuff['etc_sysconfig_sysstat_ioconf_exists'] = None
        self.sub_stuff['usr_local_bin_sysstat_sh_exists'] = None

        self.load_image(self.config['img_stored_location'])
        # Uninstall the image first, if there was some older version installed
        try:
            self.loginfo('Uninstall the image first')
            utils.run('sudo atomic uninstall %s' % self.sub_stuff['img_name'],
                      timeout=30)
        except error.CmdError:
            self.loginfo('Uninstall failed!')

    def run_once(self):
        super(install, self).run_once()
        ins_result = utils.run(
            'sudo atomic install %s' % self.sub_stuff['img_name'],
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
        self.loginfo('/etc/cron.d/sysstat is created')

    def check_etc_sysconfig_sysstat(self):
        self.failif_ne(self.sub_stuff['etc_sysconfig_sysstat_exists'], 0,
                       '/etc/sysconfig/sysstat does not exist on host!')
        self.loginfo('/etc/sysconfig/sysstat is created')

    def check_etc_sysconfig_sysstat_ioconf(self):
        self.failif_ne(
            self.sub_stuff['etc_sysconfig_sysstat_ioconf_exists'], 0,
            '/etc/sysconfig/sysstat.ioconf does not exist on host!')
        self.loginfo('/etc/sysconfig/sysstat.ioconf is created')

    def check_usr_local_bin_sysstat_sh(self):
        self.failif_ne(self.sub_stuff['usr_local_bin_sysstat_sh_exists'], 0,
                       '/usr/local/bin/sysstat.sh does not exist on host!')
        self.loginfo('/usr/local/bin/sysstat.sh is created')

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
        self.loginfo('Greater than %f, lower than %f' % (min_size, max_size))
        if min_size < actual_size < max_size:
            can_pass = 1
        self.failif_ne(can_pass, 1, "Size is not Correct")

    def postprocess(self):
        super(install, self).postprocess()
        self.failif_ne(self.sub_stuff['install_result'].exit_status, 0,
                       'Atomic install command failed!')
        self.check_etc_crond_sysstat()
        self.check_etc_sysconfig_sysstat()
        self.check_etc_sysconfig_sysstat_ioconf()
        self.check_usr_local_bin_sysstat_sh()
        self.check_size()
