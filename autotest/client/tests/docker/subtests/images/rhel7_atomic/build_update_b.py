r"""
Summary
---------
Test microdnf update works well while building container.

Operational Detail
----------------------
cat << EOF > build/Dockerfile-2b

# docker build --rm --no-cache --force-rm -f Dockerfile-2b -t microdnf-test2b .
# docker rmi microdnf-test2b

FROM registry.access.stage.redhat.com/rhel7-atomic
MAINTAINER Martin Jenner "mjenner@redhat.com"

# We will run update twice to test the case where there are no rpms to update
RUN microdnf update --enablerepo=$rpms_repo && microdnf clean all
# Second run should have no rpms to update but not cause build failure
RUN microdnf update --enablerepo=$rpms_repo && microdnf clean all

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
            'rhel7_atomic', 'files', 'Dockerfile-2b']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 40 * 60


class build_update_b(rhel7_atomic_base):

    def initialize(self):
        super(build_update_b, self).initialize()

        self.load_image()
        if not self.check_registration():
            self.subscribe()
        # Replace FROM line in dockerfile
        self.replace_line(WORK_DIR, self.sub_stuff['img_name'])

        self.sub_stuff['build'] = 0

    def run_once(self):
        super(build_update_b, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t microdnf-test2b {}'.format(WORK_DIR, BUILD_DIR))

        self.loginfo('1. {}'.format(build_cmd))
        self.sub_stuff['build'] = utils.run(build_cmd, timeout=TIMEOUT_LONG).exit_status

    def postprocess(self):
        super(build_update_b, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 0, 'Build failed!!!!!')

    def cleanup(self):
        cmd = 'sudo docker rmi microdnf-test2b'
        self.loginfo(cmd)
        utils.run(cmd, timeout=30)
