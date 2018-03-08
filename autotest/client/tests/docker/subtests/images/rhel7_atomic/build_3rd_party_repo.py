r"""
Summary
---------
Test microdnf install from 3rd party repo file works fine  while building container.

Operational Detail
----------------------
mkdir -p build
cat << EOF > build/private.repo
[private-repo-rpms]
baseurl = http://download-node-02.eng.bos.redhat.com/rel-eng/RHEL-7.4-RC-1.2/compose/Server/x86_64/os
name = Private test repo
enabled = 1
gpgcheck = 0
EOF

cat << EOF > build/Dockerfile-6
# docker build --rm --no-cache --force-rm -f Dockerfile-6 -t microdnf-test6 .
# docker rmi microdnf-test6
FROM registry.access.stage.redhat.com/rhel7-atomic
MAINTAINER Martin Jenner "mjenner@redhat.com"
ADD private.repo /etc/yum.repos.d/private.repo
RUN microdnf install --enablerepo=private-repo-rpms traceroute && microdnf clean all
EOF

Prerequisites
---------------
"""
import os

from autotest.client import utils
from rhel7_atomic import rhel7_atomic_base


# Current dir is ..../autotest/client/results/xxx/docker/subtests/images/rhel7_atomic
HALF_1ST = os.getcwd().split('/')[:-6]
HALF_2ND = ['tests', 'docker', 'subtests', 'images',
            'rhel7_atomic', 'files', 'Dockerfile-6']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 20 * 60


class build_3rd_party_repo(rhel7_atomic_base):

    def initialize(self):
        super(build_3rd_party_repo, self).initialize()

        self.load_image()
        if not self.check_registration:
            self.subscribe()
        # Replace FROM line in dockerfile
        self.replace_line(WORK_DIR, self.sub_stuff['img_name'])

        self.sub_stuff['build'] = 0

    def run_once(self):
        super(build_3rd_party_repo, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t microdnf-test6 {}'.format(WORK_DIR, BUILD_DIR))

        self.loginfo('1. {}'.format(build_cmd))
        self.sub_stuff['build'] = utils.run(
            build_cmd, timeout=TIMEOUT_LONG,
            ignore_status=True).exit_status

    def postprocess(self):
        super(build_3rd_party_repo, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 0, 'Build failed!!!')

    def cleanup(self):
        self.loginfo('CLEANUP: remove microdnf-test6')
        cmd = 'sudo docker rmi microdnf-test6'
        utils.run(cmd)
