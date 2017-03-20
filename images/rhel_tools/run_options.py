r"""
Summary
---------

Test SPC rhel7/rhel-tools according to redhat customer portal

Operational Detail
----------------------
#. atomic run $image host
#. docker ps on host to check container name
#. Check below dirs/files mounted correctly:
    * /run
    * /var/log
    * / on host and /host in container
#. Check env virables $HOST & $NAME & $IMAGE are set correctly.
#. Check --ipc=host works
#. Check --net=host works
#. Check --pid=host works

Prerequisites
---------------

*   rhel-tools container is installed
"""

from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.images import DockerImages
import time


class run_options(SubSubtest):

    def initialize(self):
        super(run_options, self).initialize()
        self.sub_stuff['img_name'] = ''
        self.sub_stuff['ctn_name_rst'] = None
        self.sub_stuff['run_dir_rst_ctn'] = None
        self.sub_stuff['run_dir_rst_host'] = None
        self.sub_stuff['var_log_rst_ctn'] = None
        self.sub_stuff['root_rst_host'] = None
        self.sub_stuff['host_rst_ctn'] = None

        self.sub_stuff['env_vir_name'] = ''
        self.sub_stuff['env_vir_image'] = ''
        self.sub_stuff['env_vir_host'] = ''

        self.sub_stuff['ipc_rst_host'] = ''
        self.sub_stuff['ipc_rst_ctn'] = ''
        self.sub_stuff['net_rst_host'] = ''
        self.sub_stuff['net_rst_ctn'] = ''
        self.sub_stuff['pid_rst_host'] = ''
        self.sub_stuff['pid_rst_ctn'] = ''

    def list_mounted_dir(self):
        dcr_exec_cmd = 'sudo docker exec rhel-tools-docker '
        ls_run_cmd = 'ls -go /run'
        self.sub_stuff['run_dir_rst_ctn'] = utils.run(
                dcr_exec_cmd + ls_run_cmd)
        self.sub_stuff['run_dir_rst_host'] = utils.run(ls_run_cmd)

        ls_var_log_cmd = 'ls -go /etc/sysconfig/sysstat.ioconf'
        self.sub_stuff['var_log_rst_ctn'] = utils.run(
                dcr_exec_cmd + ls_var_log_cmd)
        self.sub_stuff['var_log_rst_host'] = utils.run(
                ls_var_log_cmd)

        host_cmd = 'ls -go /host'
        root_cmd = 'ls -go /'
        self.sub_stuff['host_rst_ctn'] = utils.run(dcr_exec_cmd + host_cmd)
        self.sub_stuff['root_rst_host'] = utils.run(root_cmd)

    def echo_env_virs(self):
        dcr_exec_cmd = 'docker exec rhel-tools-docker '
        echo_name_cmd = "bash -c 'echo $NAME'"
        echo_host_cmd = "bash -c 'echo $HOST'"
        echo_image_cmd = "bash -c 'echo $IMAGE'"

        self.sub_stuff['env_vir_name'] = utils.run(
                dcr_exec_cmd + echo_name_cmd).stdout.strip()
        self.sub_stuff['env_vir_image'] = utils.run(
                dcr_exec_cmd + echo_image_cmd).stdout.strip()
        self.sub_stuff['env_vir_host'] = utils.run(
                dcr_exec_cmd + echo_host_cmd).stdout.strip()

    def check_env_vir(self):
        # If testing by loading the image, NAME viriable is rhel-tools-docker
        self.failif(
                not self.sub_stuff['env_vir_name'].startswith('rhel-tools'),
                'Env viriable NAME is set wrongly!'
        )
        # If testing by loading the image, IMAGE viriable is bit complex,
        # but definitely includes *rhel-tools*
        self.failif('rhel-tools' not in self.sub_stuff['env_vir_image'],
                    'Env viriable IMAGE is set wrongly!')
        self.failif_ne('/host', self.sub_stuff['env_vir_host'],
                       'Env viriable HOST is set wrongly!')

    def check_mounted_dir(self):
        self.failif_ne(self.sub_stuff['dir_run_rst_ctn'].stdout,
                       self.sub_stuff['dir_run_rst_host'].stdout,
                       '/run mounted failed!')
        self.failif_ne(self.sub_stuff['var_log_rst_ctn'].stdout,
                       self.sub_stuff['var_log_rst_host'].stdout,
                       '/var/log mounted failed!')
        self.failif_ne(self.sub_stuff['host_rst_ctn'].stdout,
                       self.sub_stuff['root_rst_host'].stdout,
                       '/host mounted failed!')

    def check_ipc(self):
        cmd_ctn = 'sudo docker exec rhel-tools-docker ipcs'
        cmd_host = 'ipcs'
        self.sub_stuff['ipc_rst_ctn'] = utils.run(cmd_ctn)
        self.sub_stuff['ipc_rst_host'] = utils.run(cmd_host)
        self.failif_ne(self.sub_stuff['ipc_rst_ctn'],
                       self.sub_stuff['ipc_rst_host'],
                       'Different result of ipcs from host and container')

    def check_net(self):
        cmd_ctn = 'sudo docker exec rhel-tools-docker ifconfig'
        cmd_host = 'ifconfig'
        self.sub_stuff['net_rst_ctn'] = utils.run(cmd_ctn)
        self.sub_stuff['net_rst_host'] = utils.run(cmd_host)
        self.failif_ne(self.sub_stuff['net_rst_ctn'],
                       self.sub_stuff['net_rst_host'],
                       'Different result of ifconfig from host and container')

    def run_once(self):
        """
        Called to run test
        """
        super(run_options, self).run_once()
        imgs = DockerImages(self)
        for img_name in imgs.list_imgs_full_name():
            if 'sadc' in img_name:
                self.sub_stuff['img_name'] = img_name
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        self.sub_stuff['run_result'] = utils.run(run_cmd, timeout=10)
        time.sleep(5)

        ctn_name_cmd = "sudo docker ps | grep sadc | awk '{print $10}'"
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
                           ['sadc', 'sadc-docker'],
                           "Container is wrongly named!")

        self.check_mounted_dir()
        self.check_env_vir()
        self.check_ipc()
        self.check_net()
