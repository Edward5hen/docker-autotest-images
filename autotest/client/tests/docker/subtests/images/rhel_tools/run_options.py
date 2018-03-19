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
#. Check CVEs via atomic scan command

Prerequisites
---------------

*   rhel-tools container is installed
"""

from autotest.client import utils
from dockertest.images import DockerImages
from rhel_tools import rhel_tools_base
from dockertest.containers import DockerContainers
from autotest.client.shared import error


class run_options(rhel_tools_base):

    def initialize(self):
        super(run_options, self).initialize()
        self.sub_stuff['img_name'] = ''
        self.sub_stuff['ctn_name_rst'] = None
        self.sub_stuff['run_dir_rst_ctn'] = None
        self.sub_stuff['run_dir_rst_host'] = None
        self.sub_stuff['var_log_rst_ctn'] = None
        self.sub_stuff['var_log_rst_host'] = None
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
        self.load_image()

        # If container is not started, run the image.
        ctns = DockerContainers(self)
        run_cmd = "sudo atomic run %s" % self.sub_stuff['img_name']
        if 'rhel-tools' not in ctns.list_container_names():
            self.loginfo('Container rhel-tools is not found')
            self.loginfo('Start the container...')
            try:
                utils.run(run_cmd, timeout=30)
            except error.CmdError, exc:
                err = exc.result_obj.stdout
                if err.strip().endswith('#'):
                    self.loginfo('Container is being started!')

    def list_mounted_dir(self):
        dcr_exec_cmd = 'sudo docker exec rhel-tools '
        ls_run_cmd = 'ls -go /run'
        self.sub_stuff['run_dir_rst_ctn'] = set(self.format_output(
            utils.run(dcr_exec_cmd + ls_run_cmd).stdout)[1:])
        self.sub_stuff['run_dir_rst_host'] = set(self.format_output(
            utils.run(ls_run_cmd).stdout)[1:])

        var_log_cmd = 'ls -go /var/log'
        self.sub_stuff['var_log_rst_ctn'] = set(self.format_output(
            utils.run(dcr_exec_cmd + var_log_cmd).stdout))
        self.sub_stuff['var_log_rst_host'] = set(self.format_output(
            utils.run(var_log_cmd).stdout))

        # The proc line is diffrent
        root_host_cmd = 'ls -go / | grep -v proc'
        host_ctn_cmd = 'ls -go /host | grep -v proc'
        self.sub_stuff['root_rst_host'] = set(self.format_output(
            utils.run(root_host_cmd).stdout))
        self.sub_stuff['host_rst_ctn'] = set(self.format_output(
            utils.run(dcr_exec_cmd + host_ctn_cmd).stdout))

    def echo_env_virs(self):
        dcr_exec_cmd = 'docker exec rhel-tools '
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
        self.loginfo('Env virable NAME is %s' % self.sub_stuff['env_vir_name'])
        # If testing by loading the image, NAME viriable is rhel-tools
        self.failif(
                not self.sub_stuff['env_vir_name'].startswith('rhel-tools'),
                'Env viriable NAME is set wrongly!'
        )
        self.loginfo('Env virable IMAGE is %s'
                     % self.sub_stuff['env_vir_image'])
        self.loginfo('Env virable HOST is %s'
                     % self.sub_stuff['env_vir_host'])
        # If testing by loading the image, IMAGE viriable is bit complex,
        # but definitely includes *rhel-tools*
        self.failif('rhel-tools' not in self.sub_stuff['env_vir_image'],
                    'Env viriable IMAGE is set wrongly!')
        self.failif_ne('/host', self.sub_stuff['env_vir_host'],
                       'Env viriable HOST is set wrongly!')

    def check_mounted_dir(self):
        can_pass = 0
        diff0 = self.sub_stuff['run_dir_rst_ctn'] -\
            self.sub_stuff['run_dir_rst_host']
        diff1 = self.sub_stuff['run_dir_rst_host'] -\
            self.sub_stuff['run_dir_rst_ctn']
        # Only secrets folder is different
        if len(diff0) == len(diff1) == 1 and\
           'secrets' in ''.join(tuple(diff0)[0]) and\
           'secrets' in ''.join(tuple(diff1)[0]):
            can_pass = 1
        self.failif_ne(can_pass, 1, '/run mounted failed!')
        self.loginfo('/run mounted successfully')

        self.failif_ne(self.sub_stuff['var_log_rst_ctn'],
                       self.sub_stuff['var_log_rst_host'],
                       '/var/log mounted failed!')
        self.loginfo('/var/log mounted successfully')

        self.failif_ne(self.sub_stuff['root_rst_host'],
                       self.sub_stuff['host_rst_ctn'],
                       'Host root dir mounted failed!')
        self.loginfo('Host root dir mounted successfully')

    def check_ipc(self):
        cmd_ctn = 'sudo docker exec rhel-tools ipcs -u'
        cmd_host = 'ipcs -u'
        self.sub_stuff['ipc_rst_ctn'] =\
            self.format_output(utils.run(cmd_ctn).stdout)
        self.sub_stuff['ipc_rst_host'] =\
            self.format_output(utils.run(cmd_host).stdout)
        self.failif_ne(self.sub_stuff['ipc_rst_ctn'],
                       self.sub_stuff['ipc_rst_host'],
                       'Different result of ipcs from host and container')
        self.loginfo('Container IPC is same as host')

    def check_net(self):
        cmd_ctn = 'sudo docker exec rhel-tools ifconfig'
        cmd_host = 'ifconfig'
        self.sub_stuff['net_rst_ctn'] =\
            self.format_output(utils.run(cmd_ctn).stdout)
        self.sub_stuff['net_rst_host'] =\
            self.format_output(utils.run(cmd_host).stdout)
        self.failif_ne(self.sub_stuff['net_rst_ctn'],
                       self.sub_stuff['net_rst_host'],
                       'Different result of ifconfig from host and container')
        self.loginfo('Container net interfaces are same as host')

    def check_process(self):
        cmd_ctn = 'sudo docker exec rhel-tools ps -Ao pid,fname'
        cmd_host = 'ps -Ao pid,fname'
        can_pass = 0
        self.sub_stuff['pid_rst_ctn'] =\
            set(self.format_output(utils.run(cmd_ctn).stdout))
        self.sub_stuff['pid_rst_host'] =\
            set(self.format_output(utils.run(cmd_host).stdout))
        diff = self.sub_stuff['pid_rst_host'] - self.sub_stuff['pid_rst_ctn']
        # Only process diff from host to container is the "ps".
        if len(diff) == 1 and 'ps' in tuple(diff)[0][0]:
            can_pass = 1
        # Count of process in container is always one more than on host
        self.failif_ne(can_pass, 1, 'Different result of process listing\
            from host and container')
        self.loginfo('Container process table is same as host')

    def check_name(self):
        cmd = 'sudo docker ps --format {{.Image}}hope-not-exist{{.Names}}\
               | grep %s' % self.sub_stuff['img_name']
        result = utils.run(cmd).stdout.split('hope-not-exist')[-1]
        self.loginfo('Container name is %s' % result.strip())
        self.failif(result.strip() not in ['rhel-tools-docker', 'rhel-tools'],
                    'Container name is not rhel-tools-docker or rhel-tools')

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
        self.list_mounted_dir()
        self.echo_env_virs()

    def postprocess(self):
        super(run_options, self).postprocess()
        self.check_mounted_dir()
        self.check_name()
        self.check_env_vir()
        self.check_ipc()
        self.check_net()
        self.check_process()
        self.check_cves()
