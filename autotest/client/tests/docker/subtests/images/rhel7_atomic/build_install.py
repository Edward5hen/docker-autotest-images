r"""
Summary
---------
Test microdnf install  works well while building container.

Operational Detail
----------------------
cat << EOF > build/Dockerfile-1
# docker build --rm --no-cache --force-rm -f Dockerfile-1 -t microdnf-test1 .
# docker run --rm -it microdnf-test1
# docker rmi microdnf-test1

FROM registry.access.stage.redhat.com/rhel7-atomic
MAINTAINER Martin Jenner "mjenner@redhat.com"

RUN microdnf install --enablerepo=rhel-7-server-rpms traceroute && microdnf clean all

CMD ["/bin/traceroute","google.com"]
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
            'rhel7_atomic', 'files', 'Dockerfile-1']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 20 * 60


class build_install(rhel7_atomic_base):

    def initialize(self):
        super(build_install, self).initialize()

        self.load_image()
        if not self.check_registration():
            self.subscribe()
        # Replace FROM line in dockerfile
        self.replace_line(WORK_DIR, self.sub_stuff['img_name'])

        self.sub_stuff['build'] = 0
        self.sub_stuff['run'] = 0

    def run_once(self):
        super(build_install, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t microdnf-test1 {}'.format(WORK_DIR, BUILD_DIR))
        run_cmd = 'docker run --rm -it microdnf-test1'

        self.loginfo('1. {}'.format(build_cmd))
        self.sub_stuff['build'] = utils.run(build_cmd, timeout=TIMEOUT_LONG).exit_status

        self.loginfo('2. {}'.format(run_cmd))
        self.sub_stuff['run'] = utils.run(run_cmd)
        self.loginfo(self.sub_stuff['run'].stdout)

    def postprocess(self):
        super(build_install, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 0, 'Build failed!!!!!')

        self.loginfo('2. Check run result')
        self.failif_ne(self.sub_stuff['run'].exit_status, 0, 'Run failed!!!!')

    def cleanup(self):
        pass
