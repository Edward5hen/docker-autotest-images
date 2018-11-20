r"""
Summary
---------
before and after subscription

Operational Detail
----------------------
#. before and after subscription
Setup:
1. The atomic host should be without registration.
   If it's registered before, just unregister it.
2. check if rhel-atomic image is loaded, if not,
   do "cat $img.tar.gz | sudo docker load"
3. sudo docker run --name=rhel7-atomic $img_full_name /bin/sleep 1000
Steps:
1. sudo docker exec rhel7-atomic microdnf install \
   --enablerepo=$rpms_repo traceroute
2. sudo docker exec rhel7-atomic test -s /etc/yum.repo/redhat.repo
3. subscribe on host with correct confidentiality
4. stop and rm rhel7-atomic, then create rhel7-atomic
5. sudo docker exec rhel7-atomic microdnf install \
   --enablerepo=$rpms_repo traceroute"
6. sudo docker exec rhel7-atomic test -s /etc/yum.repo/redhat.repo
Expectations:
1. some error is raised up that tells that repo is not found
2. size of redhat.repo file is zero
3. successfully subscribed
4. rhel7-atomic can be successfully stopped and removed.
   new rhel7-atomic container can be created
5. traceroute is successfully installed
6. redhat.repo file is non-zero
Teardown:
sudo docker stop rhel7-atomic
sudo docker rm rhel7-atomic

Prerequisites
---------------
"""
from autotest.client import utils
from rhel7_atomic import rhel7_atomic_base


class specific_sm(rhel7_atomic_base):

    def initialize(self):
        super(specific_sm, self).initialize()
        self.sub_stuff['install_b4'] = None
        self.sub_stuff['test_repo_b4'] = None
        self.sub_stuff['install_after'] = None
        self.sub_stuff['test_repo_after'] = None

        self.load_image()
        if self.check_registration():
            self.unregister()
        self.run_detached_img()

    def run_once(self):
        super(specific_sm, self).run_once()
        self.loginfo(
            ('1. sudo docker exec rhel7-atomic microdnf install '
             '--enablerepo=%s traceroute' % self.rpms_repo)
            )
        cmd_install = ('sudo docker exec rhel7-atomic microdnf install'
                       ' --enablerepo=%s traceroute' % self.rpms_repo)
        self.sub_stuff['install_b4'] = utils.run(
            cmd_install, timeout=30, ignore_status=True
            )

        self.loginfo('2. sudo docker exec rhel7-atomic test -s /etc/yum.repo/redhat.repo')
        cmd_test = ('sudo docker exec rhel7-atomic test -s '
                    '/etc/yum.repos.d/redhat.repo')
        self.sub_stuff['test_repo_b4'] = utils.run(
            cmd_test, timeout=10, ignore_status=True
            )

        self.loginfo('3. subscribe on host with correct confidentiality')
        self.subscribe()

        self.loginfo('4. stop and rm rhel7-atomic, then create rhel7-atomic')
        self.stop_rm_ctn()
        self.run_detached_img()

        self.loginfo(
            ('5. sudo docker exec rhel7-atomic microdnf install '
             '--enablerepo=%s traceroute' % self.rpms_repo)
            )
        self.sub_stuff['install_after'] = utils.run(
            cmd_install, timeout=900
            )

        self.loginfo('6. sudo docker exec rhel7-atomic test -s /etc/yum.repo/redhat.repo')
        self.sub_stuff['test_repo_after'] = utils.run(
            cmd_test, timeout=10
            )

    def postprocess(self):
        super(specific_sm, self).postprocess()
        self.loginfo('1. some error is raised up that tells that repo is not found')
        self.failif(self.sub_stuff['install_b4'].exit_status == 0,
                    'microdnf install does NOT fail before host registers')
        self.loginfo('microdnf install FAILs before host registers')

        self.loginfo('2. size of redhat.repo file is zero')
        self.failif(self.sub_stuff['test_repo_b4'].exit_status == 0,
                    'repo file is NOT empty')
        self.loginfo('repo file is empty')

        self.loginfo('4. container is stopped and removed successfully')
        self.failif_ne(self.sub_stuff['stop_rst'].exit_status, 0,
                       'cant stop container rhel7-atomic')
        self.failif_ne(self.sub_stuff['rm_rst'].exit_status, 0,
                       'cant remove container rhel7-atomic')

        self.loginfo('5. traceroute is successfully installed')
        self.failif_ne(self.sub_stuff['install_after'].exit_status, 0,
                       'microdnf install FAILS after host registers')
        self.loginfo('microdnf install PASSes after host registers')

        self.loginfo('6. redhat.repo file is non-zero')
        self.failif_ne(self.sub_stuff['test_repo_after'].exit_status, 0,
                       'repo file is empty')
        self.loginfo('repo file is not empty now')

    def cleanup(self):
        # Sometimes images_obj.clean_all() just doesn't work
        self.stop_rm_ctn()
