r"""
Summary
---------
Test microdnf install httpd works fine while building container.

Operational Detail
----------------------
cat << EOF > build/Dockerfile-8
# BEFORE YOU START: this Dockerfile requires your host subscribed to either a
# Red Hat Server or Free Developer subscription prior to building/running
# yum install oci-register-machine and oci-systemd-hook on server
#
# docker build --rm --no-cache --force-rm -t httpd-systemd .
# docker run -d -p 80:80 --name httpd httpd-systemd
# curl localhost

FROM registry.access.stage.redhat.com/rhel7-atomic
MAINTAINER Martin Jenner "mjenner@redhat.com"

RUN microdnf install --enablerepo=rhel-7-server-rpms httpd;
microdnf clean all; systemctl enable httpd.service
RUN echo "hello from httpd systemd container" > /var/www/html/index.html

STOPSIGNAL SIGRTMIN+3
EXPOSE 80
CMD ["/usr/sbin/init"]

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
            'rhel7_atomic', 'files', 'Dockerfile-8']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 20 * 60


class build_httpd(rhel7_atomic_base):

    def initialize(self):
        super(build_httpd, self).initialize()

        self.load_image()
        if not self.check_registration():
            self.subscribe()
        # Replace FROM line in dockerfile
        self.replace_line(WORK_DIR, self.sub_stuff['img_name'])

        self.sub_stuff['build'] = 0
        self.sub_stuff['run'] = 0
        self.sub_stuff['curl'] = ''

    def run_once(self):
        super(build_httpd, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t httpd-systemd {}'.format(WORK_DIR, BUILD_DIR))
        run_cmd = 'sudo docker run -d -p 80:80 --name httpd httpd-systemd'
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
        super(build_httpd, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 0, 'Build failed!!!')

        self.loginfo('2. Check run result')
        self.failif_ne(self.sub_stuff['run'], 0, 'Run failed!!!')

        self.loginfo('3. Check curl result')
        self.failif_ne(self.sub_stuff['curl'], 'hello from httpd systemd container',
            'Curl failed!!!')

    def cleanup(self):
        self.loginfo('CLEANUP: stop httpd')
        cmd_stop = 'sudo docker stop httpd'
        utils.run(cmd_stop)

        self.loginfo('CLEANUP: rm httpd')
        cmd_rm = 'sudo docker rm httpd'
        utils.run(cmd_rm)

        self.loginfo('CLEANUP: remove httpd-systemd')
        cmd = 'sudo docker rmi httpd-systemd'
        utils.run(cmd)
