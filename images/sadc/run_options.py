r"""
Summary
---------

Test SPC rhel7/sadc according to redhat customer portal

Operational Detail
----------------------
#. atomic run $image host
#. docker ps on host to check container name
#. Check below dirs/files mounted correctly:
    * /etc/sysconfig/sysstat
    * /etc/sysconfig/sysstat.ioconf
    * /var/log/sa
    * / on host and /host in container
#. Check env virables $NAME & $IMAGE are set correctly.

Prerequisites
---------------

*   sadc container is installed
"""
import time

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.images import DockerImages
from sadc import sadc_base


class run_options(sadc_base):

    def initialize(self):
        super(run_options, self).initialize()
        self.sub_stuff['img_name'] = ''
        self.sub_stuff['run_result'] = None
        self.sub_stuff['ctn_name_rst'] = None
        self.sub_stuff['etc_sysconfig_sysstat_rst_ctn'] = None
        self.sub_stuff['etc_sysconfig_sysstat_rst_host'] = None
        self.sub_stuff['etc_sysconfig_ioconf_rst_ctn'] = None
        self.sub_stuff['etc_sysconfig_ioconf_rst_host'] = None
        self.sub_stuff['var_log_sa_rst_ctn'] = None
        self.sub_stuff['var_log_sa_rst_host'] = None
        self.sub_stuff['host_rst_ctn'] = None
        self.sub_stuff['root_rst_host'] = None

        self.sub_stuff['env_vir_name'] = ''
        self.sub_stuff['env_vir_image'] = ''

        # Make sure image is loaded and installed
        self.load_image(self.config['img_stored_location'])
        self.get_installed()

    def list_mounted_dir(self):
        dcr_exec_cmd = 'sudo docker exec sadc-docker '
        etc_sysconfig_sysstat_cmd = 'ls -go /etc/sysconfig/sysstat'
        self.sub_stuff['etc_sysconfig_sysstat_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + etc_sysconfig_sysstat_cmd).stdout)
        self.sub_stuff['etc_sysconfig_sysstat_rst_host'] = self.format_output(
            utils.run(etc_sysconfig_sysstat_cmd).stdout)

        etc_sysconfig_ioconf_cmd = 'ls -go /etc/sysconfig/sysstat.ioconf'
        self.sub_stuff['etc_sysconfig_ioconf_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + etc_sysconfig_ioconf_cmd).stdout)
        self.sub_stuff['etc_sysconfig_ioconf_rst_host'] = self.format_output(
            utils.run(etc_sysconfig_ioconf_cmd).stdout)

        var_log_sa_cmd = 'ls -go /var/log/sa'
        self.sub_stuff['var_log_sa_rst_ctn'] = set(self.format_output(
            utils.run(dcr_exec_cmd + var_log_sa_cmd).stdout))
        self.sub_stuff['var_log_sa_rst_host'] = set(self.format_output(
            utils.run(var_log_sa_cmd).stdout))

        # The proc line is diffrent
        host_cmd = 'ls -go /host | grep -v proc'
        root_cmd = 'ls -go / | grep -v proc'
        self.sub_stuff['host_rst_ctn'] = set(self.format_output(
            utils.run(dcr_exec_cmd + host_cmd).stdout))
        self.sub_stuff['root_rst_host'] = set(self.format_output(
            utils.run(root_cmd).stdout))

    def echo_env_virs(self):
        dcr_exec_cmd = 'docker exec sadc-docker '
        echo_name_cmd = "bash -c 'echo $NAME'"
        echo_image_cmd = "bash -c 'echo $IMAGE'"

        self.sub_stuff['env_vir_name'] = utils.run(
                dcr_exec_cmd + echo_name_cmd).stdout.strip()
        self.sub_stuff['env_vir_image'] = utils.run(
                dcr_exec_cmd + echo_image_cmd).stdout.strip()

    def check_env_vir(self):
        # If testing by loading the image, NAME viriable is sadc-docker
        self.failif(not self.sub_stuff['env_vir_name'].startswith('sadc'),
                    'Env viriable NAME is set wrongly!')
        self.loginfo('Env NAME is %s' % self.sub_stuff['env_vir_name'])
        # If testing by loading the image, IMAGE viriable is bit complex,
        # but definitely includes *sadc*
        self.failif('sadc' not in self.sub_stuff['env_vir_image'],
                    'Env viriable IMAGE is set wrongly!')
        self.loginfo('Env IMAGE is %s' % self.sub_stuff['env_vir_image'])

    def check_mounted_dir(self):
        self.failif_ne(self.sub_stuff['etc_sysconfig_sysstat_rst_ctn'],
                       self.sub_stuff['etc_sysconfig_sysstat_rst_host'],
                       '/etc/sysconfig/sysstat is mounted failed!')
        self.loginfo('/etc/sysconfig/sysstat is mounted successfully')
        self.failif_ne(self.sub_stuff['etc_sysconfig_ioconf_rst_ctn'],
                       self.sub_stuff['etc_sysconfig_ioconf_rst_host'],
                       '/etc/sysconfig/sysstat.ioconf is mounted failed!')
        self.loginfo('/etc/sysconfig/sysstat.ioconf is mounted successfully')
        self.failif_ne(self.sub_stuff['var_log_sa_rst_ctn'],
                       self.sub_stuff['var_log_sa_rst_host'],
                       '/var/log/sa is mounted failed!')
        self.loginfo('/var/log/sa is mounted successfully')
        self.failif_ne(self.sub_stuff['host_rst_ctn'],
                       self.sub_stuff['root_rst_host'],
                       'root dir is mounted failed!')
        self.loginfo('root dir is mounted successfully')

    def run_once(self):
        """
        Called to run test
        """
        super(run_options, self).run_once()
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        self.sub_stuff['run_result'] = utils.run(run_cmd, timeout=10)
        time.sleep(5)

        ctn_name_cmd = "sudo docker ps | grep sadc | awk '{print $10}'"
        self.sub_stuff['ctn_name_rst'] = utils.run(ctn_name_cmd, timeout=3)

        self.list_mounted_dir()
        self.echo_env_virs()

    def postprocess(self):
        super(run_options, self).postprocess()
        # If it's tested by loading the image, container name is sadc-docker
        # If it's tested by pulling the image, container name is sadc
        self.failif_ne(self.sub_stuff['run_result'].exit_status, 0,
                       "image runs failed with atomic commands!")
        self.loginfo('Image runs successfully')
        self.failif_not_in(self.sub_stuff['ctn_name_rst'].stdout.strip(),
                           ['sadc', 'sadc-docker'],
                           "Container is wrongly named!")
        self.loginfo('Container name %s' % self.sub_stuff['ctn_name_rst'])

        self.check_mounted_dir()
        self.check_env_vir()
