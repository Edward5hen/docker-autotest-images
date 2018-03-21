r"""
Summary
---------
Test httpd container built on rhel7-init works fine

Operational Detail
----------------------
dockerfile:
FROM fkluknav/rhel7-init-docker:extras-rhel-7.3-docker-candidate-20170509121002
MAINTAINER Edward Shen "weshen@redhat.com"

RUN yum install -y httpd && yum clean all && systemctl enable httpd
RUN echo "hello from Edward" > /var/www/html/index.html

EXPOSE 80

1. Build it.
2. Run it.
3. Check processes in container.
4. Check httpd works fine.

Prerequisites
---------------
"""
import os

from autotest.client import utils
from rhel7_init import rhel7_init_base


# Current dir is ..../autotest/client/results/xxx/docker/subtests/images/rhel7_init
HALF_1ST = os.getcwd().split('/')[:-6]
HALF_2ND = ['tests', 'docker', 'subtests', 'images',
            'rhel7_init', 'files', 'Dockerfile-httpd']
WORK_DIR = '/'.join(HALF_1ST + HALF_2ND)
BUILD_DIR = '/'.join(HALF_1ST + HALF_2ND[:-1])

TIMEOUT_LONG = 20 * 60


class build_httpd(rhel7_init_base):

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
        self.sub_stuff['ps_correct'] = 1

    def run_once(self):
        super(build_httpd, self).run_once()

        build_cmd = ('sudo docker build --rm --no-cache --force-rm '
                     '-f {} -t httpd-init {}'.format(WORK_DIR, BUILD_DIR))
        run_cmd = 'sudo docker run -d -p 80:80 --name httpd httpd-init'
        ps_cmd = 'sudo docker exec httpd ps'
        curl_cmd = 'curl localhost'

        self.loginfo('1. {}'.format(build_cmd))
        self.sub_stuff['build'] = utils.run(build_cmd, timeout=TIMEOUT_LONG,).exit_status

        self.loginfo('2. {}'.format(run_cmd))
        self.sub_stuff['run'] = utils.run(run_cmd).exit_status

        self.loginfo('Sleep 5s')
        import time
        time.sleep(5)

        self.loginfo('3. {}'.format(ps_cmd))
        output_ps = utils.run(ps_cmd).stdout
        output_ps = self.format_output(output_ps)
        self.loginfo(output_ps)
        # the correct output must be something like:
        # [('', 'PID TTY', 'TIME CMD'), ('', '1 ?', '00:00:00 systemd'),
        # ('', '16 ?', '00:00:00 systemd-journal'), ('', '24 ?', '00:00:00 httpd'),
        # ('', '44 ?', '00:00:00 ps'), ('',)]
        if len(output_ps) != 6:
            self.sub_stuff['ps_correct'] = 0
            self.loginfo('Length of output is not FOUR!!!')
        elif output_ps[-1] != ('',):
            self.sub_stuff['ps_correct'] = 0
            self.loginfo('Last item is not Null!!!')
        elif output_ps[1][-1].split()[-1] != 'systemd':
            self.sub_stuff['ps_correct'] = 0
            self.loginfo('First process is not systemd!!!')
        elif output_ps[2][-1].split()[-1] != 'systemd-journal':
            self.sub_stuff['ps_correct'] = 0
            self.loginfo('Second process is not systemd-journal')
        elif output_ps[3][-1].split()[-1] != 'httpd':
            self.sub_stuff['ps_correct'] = 0
            self.loginfo('Third process is not httpd')
        elif output_ps[4][-1].split()[-1] != 'ps':
            self.sub_stuff['ps_correct'] = 0
            self.loginfo('Fourth process is not ps')

        self.loginfo('4. {}'.format(curl_cmd))
        self.sub_stuff['curl'] = utils.run(curl_cmd).stdout.strip()
        self.loginfo(self.sub_stuff['curl'])

    def postprocess(self):
        super(build_httpd, self).postprocess()

        self.loginfo('1. Check build result')
        self.failif_ne(self.sub_stuff['build'], 0, 'Build failed!!!')

        self.loginfo('2. Check run result')
        self.failif_ne(self.sub_stuff['run'], 0, 'Run failed!!!')

        self.loginfo('3. Check processes')
        self.failif_ne(self.sub_stuff['ps_correct'], 1, 'Wrong processes situation!!!')

        self.loginfo('4. Check curl result')
        self.failif_ne(self.sub_stuff['curl'], 'hello from Edward',
            'Curl failed!!!')

    def cleanup(self):
        self.loginfo('CLEANUP: stop httpd')
        cmd_stop = 'sudo docker stop httpd'
        utils.run(cmd_stop)

        self.loginfo('CLEANUP: rm httpd')
        cmd_rm = 'sudo docker rm httpd'
        utils.run(cmd_rm)

        self.loginfo('CLEANUP: remove httpd-init')
        cmd = 'sudo docker rmi httpd-init'
        utils.run(cmd)
