r"""
Summary
---------
Test microdnf disable switch work well while building container.

Operational Detail
----------------------
mkdir -p build
cat << EOF > build/Dockerfile-5
# docker build --rm --no-cache --force-rm -f Dockerfile-5 -t microdnf-test5 .
# docker run --rm -it microdnf-test5 rpm -q htop traceroute
# docker rmi microdnf-test5

FROM registry.access.stage.redhat.com/rhel7-atomic
MAINTAINER Martin Jenner "mjenner@redhat.com"

RUN rpm -i http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-9.noarch.rpm

RUN microdnf install --disablerepo=epel --enablerepo=rhel-7-server-rpms traceroute htop
&& microdnf clean all

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
            'rhel7_atomic', 'files', 'Dockerfile-5']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 20 * 60


class build_disable_switch(rhel7_atomic_base):

    def initialize(self):
        super(build_disable_switch, self).initialize()

        self.load_image()
        if not self.check_registration:
            self.subscribe()
        # Replace FROM line in dockerfile
        self.replace_line(WORK_DIR, self.sub_stuff['img_name'])

        self.sub_stuff['build'] = 0

    def run_once(self):
        super(build_disable_switch, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t microdnf-test5 {}'.format(WORK_DIR, BUILD_DIR))

        self.loginfo('1. {}'.format(build_cmd))
        self.sub_stuff['build'] = utils.run(
            build_cmd, timeout=TIMEOUT_LONG,
            ignore_status=True).exit_status

    def postprocess(self):
        super(build_disable_switch, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 1, 'Should fail with 1!!!!')

    def cleanup(self):
        pass
