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

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.images import DockerImages
import time


class run_options(SubSubtest):

    def initialize(self):
        super(run_options, self).initialize()
        self.sub_stuff['img_name'] = ''
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
        dcr_exec_cmd = 'sudo docker exec rsyslog-docker '
        etc_pki_rsyslog_cmd = 'ls -go /etc/pki/rsyslog'
        self.sub_stuff['etc_pki_rsyslog_rst_ctn'] = utils.run(
                dcr_exec_cmd + etc_pki_rsyslog_cmd)
        self.sub_stuff['etc_pki_rsyslog_rst_host'] = utils.run(
                etc_pki_rsyslog_cmd)

        etc_rsyslog_conf_cmd = 'ls -go /etc/rsyslog.conf'
        self.sub_stuff['etc_rsyslog_conf_rst_ctn'] = utils.run(
                dcr_exec_cmd + etc_rsyslog_conf_cmd)
        self.sub_stuff['etc_rsyslog_conf_rst_host'] = utils.run(
                etc_rsyslog_conf_cmd)

        etc_rsyslog_d_cmd = 'ls -go /etc/rsyslog.d'
        self.sub_stuff['etc_rsyslog_d_rst_ctn'] = utils.run(
                dcr_exec_cmd + etc_rsyslog_d_cmd)
        self.sub_stuff['etc_rsyslog_d_rst_host'] = utils.run(etc_rsyslog_d_cmd)

        var_log_cmd = 'ls -go /var/log'
        self.sub_stuff['var_log_rst_ctn'] = utils.run(
                dcr_exec_cmd + var_log_cmd)
        self.sub_stuff['var_log_rst_host'] = utils.run(var_log_cmd)

        var_lib_rsyslog_cmd = 'ls -go /var/lib/rsyslog'
        self.sub_stuff['var_lib_rsyslog_rst_ctn'] = utils.run(
                dcr_exec_cmd + var_lib_rsyslog_cmd)
        self.sub_stuff['var_lib_rsyslog_rst_host'] = utils.run(
                var_lib_rsyslog_cmd)

        dir_run_cmd = 'ls -go /run'
        self.sub_stuff['run_rst_ctn'] = utils.run(dcr_exec_cmd + dir_run_cmd)
        self.sub_stuff['run_rst_host'] = utils.run(dir_run_cmd)

        etc_machine_id_cmd = 'ls -go /etc/machine-id'
        self.sub_stuff['etc_machine_id_rst_ctn'] = utils.run(
                dcr_exec_cmd + etc_machine_id_cmd)
        self.sub_stuff['etc_machine_id_rst_host'] = utils.run(
                etc_machine_id_cmd)

    def echo_env_virs(self):
        dcr_exec_cmd = 'docker exec rsyslog-docker '
        echo_name_cmd = "bash -c 'echo $NAME'"
        echo_image_cmd = "bash -c 'echo $IMAGE'"

        self.sub_stuff['env_vir_name'] = utils.run(
                dcr_exec_cmd + echo_name_cmd).stdout.strip()
        self.sub_stuff['env_vir_image'] = utils.run(
                dcr_exec_cmd + echo_image_cmd).stdout.strip()

    def check_env_vir(self):
        # If testing by loading the image, NAME viriable is rsyslog-docker
        self.failif(not self.sub_stuff['env_vir_name'].startswith('rsyslog'),
                    'Env viriable NAME is set wrongly!')
        # If testing by loading the image, IMAGE
        self.failif('rsyslog' not in self.sub_stuff['env_vir_image'],
                    'Env viriable IMAGE is set wrongly!')

    def check_mounted_dir(self):
        self.failif_ne(self.sub_stuff['etc_pki_rsyslog_rst_ctn'].stdout,
                       self.sub_stuff['etc_pki_rsyslog_rst_host'].stdout,
                       '/etc/pki/rsyslog mounted failed!')
        self.failif_ne(self.sub_stuff['etc_rsyslog_conf_rst_ctn'].stdout,
                       self.sub_stuff['etc_rsyslog_conf_rst_host'].stdout,
                       '/etc/rsyslog.conf mounted failed!')
        self.failif_ne(self.sub_stuff['etc_rsyslog_d_rst_ctn'].stdout,
                       self.sub_stuff['etc_rsyslog_d_rst_host'].stdout,
                       '/etc/rsyslog.d mounted failed!')
        self.failif_ne(self.sub_stuff['var_lib_rsyslog_rst_ctn'].stdout,
                       self.sub_stuff['var_lib_rsyslog_rst_host'].stdout,
                       '/var/lib/rsyslog mounted failed!')
        self.failif_ne(self.sub_stuff['var_log_rst_ctn'].stdout,
                       self.sub_stuff['var_log_rst_host'].stdout,
                       '/var/log mounted failed!')
        self.failif_ne(self.sub_stuff['run_rst_ctn'].stdout,
                       self.sub_stuff['run_rst_host'].stdout,
                       '/run mounted failed!')
        self.failif_ne(self.sub_stuff['etc_machine_id_rst_ctn'].stdout,
                       self.sub_stuff['etc_machine_id_rst_host'].stdout,
                       '/etc/machine-id mounted failed!')

    def run_once(self):
        """
        Called to run test
        """
        super(run_options, self).run_once()
        imgs = DockerImages(self)
        for img_name in imgs.list_imgs_full_name():
            if 'rsyslog' in img_name:
                self.sub_stuff['img_name'] = img_name
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        self.sub_stuff['run_result'] = utils.run(run_cmd, timeout=10)
        time.sleep(5)

        ctn_name_cmd = "sudo docker ps | grep rsyslog | awk '{print $10}'"
        self.sub_stuff['ctn_name_rst'] = utils.run(ctn_name_cmd, timeout=3)

        self.list_mounted_dir()
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

        self.check_mounted_dir()
        self.check_env_vir()
