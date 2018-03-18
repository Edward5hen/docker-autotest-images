r"""
Summary
---------
Test microdnf install http24 works fine while building container.

Operational Detail
----------------------
cat << EOF > Dockerfile-7
# docker build --rm --no-cache --force-rm -f Dockerfile-7 -t microdnf-test7 .
# docker run -d -p 80:80 --name http24 microdnf-test7
# curl localhost
# docker stop http24
# docker rm http24
# docker rmi microdnf-test7
FROM registry.access.stage.redhat.com/rhel7-atomic
MAINTAINER Martin Jenner "mjenner@redhat.com"
RUN microdnf install --enablerepo=rhel-7-server-rpms --enablerepo=rhel-server-rhscl-7-rpms
httpd24 && microdnf clean all
# - Missing base rpm should this be added to help out rhscl ?
RUN microdnf install --enablerepo=rhel-7-server-rpms elfutils-libs && microdnf clean all
RUN echo 'Hello, Docker world.' > /opt/rh/httpd24/root/var/www/html/index.html
EXPOSE 80
# Always run with the scl enabled
ENTRYPOINT ["scl", "enable", "httpd24", "--", "bash", "-c"]
# Run the application
CMD ["httpd -DFOREGROUND"]
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
            'rhel7_atomic', 'files', 'Dockerfile-7']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 20 * 60


class build_http24(rhel7_atomic_base):

    def initialize(self):
        super(build_http24, self).initialize()

        self.load_image()
        if not self.check_registration():
            self.subscribe()
        # Replace FROM line in dockerfile
        self.replace_line(WORK_DIR, self.sub_stuff['img_name'])

        self.sub_stuff['build'] = 0
        self.sub_stuff['run'] = 0
        self.sub_stuff['curl'] = ''

    def run_once(self):
        super(build_http24, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t microdnf-test7 {}'.format(WORK_DIR, BUILD_DIR))
        run_cmd = 'sudo docker run -d -p 80:80 --name http24 microdnf-test7'
        curl_cmd = 'curl localhost'

        self.loginfo('1. {}'.format(build_cmd))
        self.sub_stuff['build'] = utils.run(build_cmd, timeout=TIMEOUT_LONG,).exit_status

        self.loginfo('2. {}'.format(run_cmd))
        self.sub_stuff['run'] = utils.run(run_cmd).exit_status

        self.loginfo('Sleep 5s')
        import time
        time.sleep(5)

        self.loginfo('3. {}'.format(curl_cmd))
        self.sub_stuff['curl'] = utils.run(curl_cmd).stdout.strip()
        self.loginfo(self.sub_stuff['curl'])

    def postprocess(self):
        super(build_http24, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 0, 'Build failed!!!')

        self.loginfo('2. Check run result')
        self.failif_ne(self.sub_stuff['run'], 0, 'Run failed!!!')

        self.loginfo('3. Check curl result')
        self.failif_ne(self.sub_stuff['curl'], 'Hello, Docker world.', 'Curl failed!!!')

    def cleanup(self):
        self.loginfo('CLEANUP: stop http24')
        cmd_stop = 'sudo docker stop http24'
        utils.run(cmd_stop)

        self.loginfo('CLEANUP: rm http24')
        cmd_rm = 'sudo docker rm http24'
        utils.run(cmd_rm)

        self.loginfo('CLEANUP: remove microdnf-test7')
        cmd = 'sudo docker rmi microdnf-test7'
        utils.run(cmd)
