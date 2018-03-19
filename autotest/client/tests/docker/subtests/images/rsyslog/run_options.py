r"""
Summary
---------

Test SPC rhel7/rsyslog according to redhat customer portal

Operational Detail
----------------------
#. atomic run $image host
#. docker ps on host to check container name
#. Check below dirs/files mounted correctly:
    * /etc/pki/rsyslog
    * /etc/rsyslog.d
    * /etc/rsyslog.conf
    * /var/log
    * /var/lib/rsyslog
    * /run
    * /etc/machine-id
#. Check env virables $NAME & $IMAGE are set correctly.

Prerequisites
---------------

*   rsyslog container is installed
"""
import time

from autotest.client import utils
from rsyslog import rsyslog_base


class run_options(rsyslog_base):

    def initialize(self):
        super(run_options, self).initialize()
        # Make sure image is loaded and installed
        self.load_image()
        self.get_installed()

        self.sub_stuff['run_result'] = None
        self.sub_stuff['ctn_name_rst'] = None
        self.sub_stuff['etc_pki_rsyslog_rst_ctn'] = None
        self.sub_stuff['etc_pki_rsyslog_rst_host'] = None
        self.sub_stuff['etc_rsyslog_conf_rst_ctn'] = None
        self.sub_stuff['etc_rsyslog_conf_rst_host'] = None
        self.sub_stuff['etc_rsyslog_d_rst_ctn'] = None
        self.sub_stuff['etc_rsyslog_d_rst_host'] = None
        self.sub_stuff['var_lib_rsyslog_rst_ctn'] = None
        self.sub_stuff['var_lib_rsyslog_rst_host'] = None
        self.sub_stuff['var_log_rst_ctn'] = None
        self.sub_stuff['var_log_rst_host'] = None
        self.sub_stuff['run_rst_ctn'] = None
        self.sub_stuff['run_rst_host'] = None
        self.sub_stuff['etc_machine_id_rst_ctn'] = None
        self.sub_stuff['etc_machine_id_rst_host'] = None

        self.sub_stuff['env_vir_name'] = ''
        self.sub_stuff['env_vir_image'] = ''

    def list_mounted_dir(self):
        dcr_exec_cmd = 'sudo docker exec rsyslog '
        etc_pki_rsyslog_cmd = 'ls -go /etc/pki/rsyslog'
        self.sub_stuff['etc_pki_rsyslog_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + etc_pki_rsyslog_cmd).stdout)
        self.sub_stuff['etc_pki_rsyslog_rst_host'] = self.format_output(
            utils.run(etc_pki_rsyslog_cmd).stdout)

        etc_rsyslog_conf_cmd = 'ls -go /etc/rsyslog.conf'
        self.sub_stuff['etc_rsyslog_conf_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + etc_rsyslog_conf_cmd).stdout)
        self.sub_stuff['etc_rsyslog_conf_rst_host'] = self.format_output(
            utils.run(etc_rsyslog_conf_cmd).stdout)

        etc_rsyslog_d_cmd = 'ls -go /etc/rsyslog.d'
        self.sub_stuff['etc_rsyslog_d_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + etc_rsyslog_d_cmd).stdout)
        self.sub_stuff['etc_rsyslog_d_rst_host'] = self.format_output(
            utils.run(etc_rsyslog_d_cmd).stdout)

        # Sometimes the order is different
#        var_log_cmd = 'ls -go /var/log'
#        self.sub_stuff['var_log_rst_ctn'] = set(self.format_output(
#            utils.run(dcr_exec_cmd + var_log_cmd).stdout))
#        self.sub_stuff['var_log_rst_host'] = set(self.format_output(
#            utils.run(var_log_cmd).stdout))

        var_lib_rsyslog_cmd = 'ls -go /var/lib/rsyslog'
        self.sub_stuff['var_lib_rsyslog_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + var_lib_rsyslog_cmd).stdout)
        self.sub_stuff['var_lib_rsyslog_rst_host'] = self.format_output(
            utils.run(var_lib_rsyslog_cmd).stdout)

        dir_run_cmd = 'ls -go /run'
        self.sub_stuff['run_rst_ctn'] = set(self.format_output(
            utils.run(dcr_exec_cmd + dir_run_cmd).stdout)[1:])
        self.sub_stuff['run_rst_host'] = set(self.format_output(
            utils.run(dir_run_cmd).stdout)[1:])

        etc_machine_id_cmd = 'ls -go /etc/machine-id'
        self.sub_stuff['etc_machine_id_rst_ctn'] = self.format_output(
            utils.run(dcr_exec_cmd + etc_machine_id_cmd).stdout)
        self.sub_stuff['etc_machine_id_rst_host'] = self.format_output(
            utils.run(etc_machine_id_cmd).stdout)

    def echo_env_virs(self):
        dcr_exec_cmd = 'docker exec rsyslog '
        echo_name_cmd = "bash -c 'echo $NAME'"
        echo_image_cmd = "bash -c 'echo $IMAGE'"

        self.sub_stuff['env_vir_name'] = utils.run(
            dcr_exec_cmd + echo_name_cmd).stdout.strip()
        self.sub_stuff['env_vir_image'] = utils.run(
            dcr_exec_cmd + echo_image_cmd).stdout.strip()
        self.loginfo('Env virable NAME is %s' %
                     self.sub_stuff['env_vir_name'])
        self.loginfo('Env virable IMAGE is %s' %
                     self.sub_stuff['env_vir_image'])

    def check_env_vir(self):
        # If testing by loading the image, NAME viriable is rsyslog
        self.failif(not self.sub_stuff['env_vir_name'].startswith('rsyslog'),
                    'Env viriable NAME is set wrongly!')
        # If testing by loading the image, IMAGE
        self.failif('rsyslog' not in self.sub_stuff['env_vir_image'],
                    'Env viriable IMAGE is set wrongly!')

    def check_mounted_dir(self):
        self.failif_ne(self.sub_stuff['etc_pki_rsyslog_rst_ctn'],
                       self.sub_stuff['etc_pki_rsyslog_rst_host'],
                       '/etc/pki/rsyslog mounted failed!')
        self.loginfo('/etc/pki/rsyslog mounted successfully')
        self.failif_ne(self.sub_stuff['etc_rsyslog_conf_rst_ctn'],
                       self.sub_stuff['etc_rsyslog_conf_rst_host'],
                       '/etc/rsyslog.conf mounted failed!')
        self.loginfo('/etc/rsyslog.conf mounted successfully')
        self.failif_ne(self.sub_stuff['etc_rsyslog_d_rst_ctn'],
                       self.sub_stuff['etc_rsyslog_d_rst_host'],
                       '/etc/rsyslog.d mounted failed!')
        self.loginfo('/etc/rsyslog.d mounted successfully')
        self.failif_ne(self.sub_stuff['var_lib_rsyslog_rst_ctn'],
                       self.sub_stuff['var_lib_rsyslog_rst_host'],
                       '/var/lib/rsyslog mounted failed!')
        self.loginfo('/var/lib/rsyslog mounted successfully')
        self.failif_ne(self.sub_stuff['var_log_rst_ctn'],
                       self.sub_stuff['var_log_rst_host'],
                       '/var/log mounted failed!')
        self.loginfo('/var/log mounted successfully')
        self.failif_ne(self.sub_stuff['etc_machine_id_rst_ctn'],
                       self.sub_stuff['etc_machine_id_rst_host'],
                       '/etc/machine-id mounted failed!')
        self.loginfo('/etc/machine-id mounted successfully')

        # Check mounted dir /run
        can_pass = 0
        diff0 = self.sub_stuff['run_rst_ctn'] -\
            self.sub_stuff['run_rst_host']
        diff1 = self.sub_stuff['run_rst_host'] -\
            self.sub_stuff['run_rst_ctn']
        # Only secrets folder is different
        if len(diff0) == len(diff1) == 1 and\
           'secrets' in ''.join(tuple(diff0)[0]) and\
           'secrets' in ''.join(tuple(diff1)[0]):
            can_pass = 1
        self.failif_ne(can_pass, 1, '/run mounted failed!')

    def check_cves(self):
        cmd = 'sudo atomic scan %s | grep -i pass' % self.sub_stuff['img_name']
        result = utils.run(cmd, timeout=900)
        self.failif_ne(result.exit_status, 0, 'atomic scan failed!')
        self.loginfo('No CVEs found by atomic scan')

    def run_once(self):
        """
        Called to run test
        """
        super(run_options, self).run_once()
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        self.loginfo('1. {}'.format(run_cmd))
        self.sub_stuff['run_result'] = utils.run(run_cmd, timeout=10)
        time.sleep(5)

        ctn_name_cmd = "sudo docker ps | grep rsyslog | awk '{print $10}'"
        self.sub_stuff['ctn_name_rst'] = utils.run(ctn_name_cmd, timeout=3)
        self.loginfo('Container name is %s' %
                     self.sub_stuff['ctn_name_rst'].stdout.strip())

        self.loginfo('List mounted directories...')
        self.list_mounted_dir()
        self.loginfo('Echo environment virables...')
        self.echo_env_virs()

    def postprocess(self):
        super(run_options, self).postprocess()
        # If it's tested by loading the image, container name is rsyslog-docker
        # If it's tested by pulling the image, container name is rsyslog
        self.failif_ne(self.sub_stuff['run_result'].exit_status, 0,
                       "image runs failed with atomic commands!")
        self.failif_not_in(self.sub_stuff['ctn_name_rst'].stdout.strip(),
                           ['rsyslog', 'rsyslog-docker'],
                           "Container is wrongly named!")

        self.loginfo('Check mounted directories...')
        self.check_mounted_dir()
        self.loginfo('Check evironment viriables...')
        self.check_env_vir()
        self.loginfo('Check CVEs by atomic scan...')
        self.check_cves()
