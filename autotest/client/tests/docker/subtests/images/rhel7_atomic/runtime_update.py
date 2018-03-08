r"""
Summary
---------
Test microdnf works well while in running container.

Operational Detail
----------------------
#. microdnf update
Setup:
1. The atomic host should be registered with correct confidentiality.
2. check if rhel-atomic image is pulled, if not,
   do "sudo docker pull registry.access.redhat.com/rhel-atomic"
3. sudo docker run -d --name=rhel7-atomic /bin/sleep 1000
Steps:
1. run "sudo docker exec rhel7-atomic microdnf update
    --enablerepo=rhel-7-server-rpms" twice
Expectations:
1. each time of run succeeds with exit code 0.
Teardown:
sudo docker stop rhel7-atomic
sudo docker rm rhel7-atomic

Prerequisites
---------------
"""
from autotest.client import utils
from rhel7_atomic import rhel7_atomic_base


TIME_OUT_LONG = 10 * 60


class runtime_update(rhel7_atomic_base):

    def initialize(self):
        super(runtime_update, self).initialize()

        self.load_image()
        if not self.check_registration:
            self.subscribe()
        self.run_detached_img()

        self.sub_stuff['update_1st'] = 0
        self.sub_stuff['update_2nd'] = 0

    def run_once(self):
        super(runtime_update, self).run_once()

        self.loginfo(
            ('1. run "sudo docker exec rhel7-atomic microdnf'
             'update --enablerepo=rhel-7-server-rpms" twice')
            )
        self.loginfo('Run it 1st time')
        cmd = ('sudo docker exec rhel7-atomic microdnf update'
               ' --enablerepo=rhel-7-server-rpms')
        self.sub_stuff['update_1st'] =\
            utils.run(cmd, timeout=TIME_OUT_LONG).exit_status

        self.loginfo('Run it 2nd time')
        self.sub_stuff['update_2nd'] =\
            utils.run(cmd, timeout=TIME_OUT_LONG).exit_status

    def postprocess(self):
        super(runtime_update, self).postprocess()

        self.loginfo('Check 1st time update')
        self.failif_ne(self.sub_stuff['update_1st'],
                       0, 'Update 1st time failed!!!')
        self.loginfo('Check 2nd time update')
        self.failif_ne(self.sub_stuff['update_2nd'],
                       0, 'Update 2nd time failed!!!')

    def cleanup(self):
        super(runtime_update, self).cleanup()
