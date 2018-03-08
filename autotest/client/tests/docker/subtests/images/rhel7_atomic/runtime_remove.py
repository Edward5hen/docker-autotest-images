r"""
Summary
---------
Test microdnf works well while in running container.

Operational Detail
----------------------
#. microdnf remove
Setup:
1. The atomic host should be registered with correct confidentiality.
2. check if rhel7-atomic image is pulled, if not,
   do "sudo docker pull registry.access.redhat.com/rhel7-atomic"
3. sudo docker run -d --name=rhel7-atomic
   registry.access.redhat.com/rhel7-atomic /bin/sleep 1000
Steps:
1. sudo docker exec rhel7-atomic microdnf install
    --enablerepo=rhel-7-server-rpms traceroute
2. sudo docker exec rhel7-atomic microdnf remove
    --enablerepo=rhel-7-server-rpms traceroute
Expectations:
1. traceroute is successfully installed
2. traceroute is successfully removed
Teardown:
sudo docker stop rhel7-atomic
sudo docker rm rhel7-atomic

Prerequisites
---------------
"""
from autotest.client import utils
from rhel7_atomic import rhel7_atomic_base


TIME_OUT_LONG = 10 * 60


class runtime_remove(rhel7_atomic_base):

    def initialize(self):
        super(runtime_remove, self).initialize()

        self.load_image()
        if not self.check_registration:
            self.subscribe()
        self.run_detached_img()

        self.sub_stuff['install'] = 0
        self.sub_stuff['remove'] = 0

    def run_once(self):
        super(runtime_remove, self).run_once()

        cmd_install = ('sudo docker exec rhel7-atomic microdnf install '
                       '--enablerepo=rhel-7-server-rpms traceroute')
        cmd_remove = ('sudo docker exec rhel7-atomic microdnf remove '
                      '--enablerepo=rhel-7-server-rpms traceroute')

        self.loginfo('1. {}'.format(cmd_install))
        self.sub_stuff['install'] = utils.run(
            cmd_install, timeout=TIME_OUT_LONG).exit_status

        self.loginfo('2. {}'.format(cmd_remove))
        self.sub_stuff['remove'] = utils.run(
            cmd_remove, timeout=TIME_OUT_LONG).exit_status

    def postprocess(self):
        super(runtime_remove, self).postprocess()

        self.loginfo('1. tracetoute is successfully installed')
        self.failif_ne(self.sub_stuff['install'], 0,
                       'Install failed!!!')
        self.loginfo('1. tracetoute is successfully removed')
        self.failif_ne(self.sub_stuff['remove'], 0,
                       'Remove failed!!!')

    def cleanup(self):
        super(runtime_remove, self).cleanup()
