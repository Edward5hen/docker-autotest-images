r"""
Summary
---------
Test microdnf works well while in running container.

Operational Detail
----------------------
#. microdnf multiple enabled channels and disable switch
Setup:
1. The atomic host should be registered with correct confidentiality.
2. check if rhel7-atomic image is pulled, if not,
   do "sudo docker pull registry.access.redhat.com/rhel7-atomic"
3. sudo docker run -d --name=rhel7-atomic
   registry.access.redhat.com/rhel7-atomic /bin/sleep 1000
Steps:
1. sudo docker exec rhel7-atomic microdnf install
   --enablerepo=rhel-7-server-rpms --enablerepo=rhel-7-rc-rpms
   traceroute watchdog
2. sudo docker exec rhel7-atomic microdnf remove
   --enablerepo=rhel-7-server-rpms --enablerepo=rhel-7-rcl-rpms
   traceroute watchdog
3. sudo docker exec rhel7-atomic microdnf install
   --enablerepo=rhel-7-server-rpms --disablerepo=rhel-7-rc-rpms
   traceroute watchdog
Expectations:
1. both rpms are successfully installed
2. both rpms are successfully removed
3. exit with non-zero exit code, since the available repo for
   publican is disabled
Teardown:
sudo docker stop rhel7-atomic
sudo docker rm rhel7-atomic

Prerequisites
---------------
"""
from autotest.client import utils
from rhel7_atomic import rhel7_atomic_base


TIME_OUT_LONG = 10 * 60


class runtime_multiple(rhel7_atomic_base):

    def initialize(self):
        super(runtime_multiple, self).initialize()

        self.load_image()
        if not self.check_registration():
            self.subscribe()
        self.run_detached_img()

        self.sub_stuff['install1'] = 0
        self.sub_stuff['remove'] = 0
        self.sub_stuff['install2'] = 0

    def run_once(self):
        super(runtime_multiple, self).run_once()

        cmd_install1 = ('sudo docker exec rhel7-atomic microdnf install '
                        '--enablerepo=rhel-7-server-rpms '
                        '--enablerepo=rhel-7-server-extras-rpms traceroute etcd')
        cmd_remove = ('sudo docker exec rhel7-atomic microdnf remove '
                      '--enablerepo=rhel-7-server-rpms '
                      '--enablerepo=rhel-7-server-extras-rpms traceroute etcd')
        cmd_install2 = ('sudo docker exec rhel7-atomic microdnf install '
                        '--enablerepo=rhel-7-server-rpms '
                        '--disablerepo=rhel-7-server-extras-rpms traceroute etcd')

        self.loginfo('1. {}'.format(cmd_install1))
        self.sub_stuff['intall1'] =\
            utils.run(cmd_install1, timeout=TIME_OUT_LONG).exit_status

        self.loginfo('2. {}'.format(cmd_remove))
        self.sub_stuff['remove'] =\
            utils.run(cmd_remove, timeout=TIME_OUT_LONG).exit_status

        self.loginfo('3. {}'.format(cmd_install2))
        self.sub_stuff['install2'] =\
            utils.run(cmd_install2, timeout=TIME_OUT_LONG, ignore_status=True).exit_status

    def postprocess(self):
        super(runtime_multiple, self).postprocess()

        self.loginfo('1. both rpms are successfully installed')
        self.failif_ne(self.sub_stuff['install1'], 0,
                       'rpms are not installed successfully')

        self.loginfo('2. both rpms are successfully removed')
        self.failif_ne(self.sub_stuff['remove'], 0,
                       'rpms are not successfully removed!!!')

        self.loginfo(
            ('3. exit with non-zero exit code, '
             'since the available repo for etcd is disabled')
            )
        self.failif(self.sub_stuff['install2'] == 0,
                    'rpms are successfully installed.!!!')

    def cleanup(self):
        super(runtime_multiple, self).cleanup()
