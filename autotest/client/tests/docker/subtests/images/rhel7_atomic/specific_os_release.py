r"""
Summary
---------
/etc/os-release file correctness

Operational Detail
----------------------
#. /etc/os-release file correctness
Setup:
1. check if rhel-atomic image is pulled, if not,
   do "sudo docker pull registry.access.redhat.com/rhel7-atomic"
2. sudo docker run --name=rhel7-atomic registry.access.redhat.com/rhel7-atomic /bin/sleep 1000

Steps:
1. check file /etc/os-release existence
2. check parameter NAME
3. check parameter PRETTY_NAME
4. check parameter CPE_NAME
Expectations:
1. file does exist
2. Red Hat Enterprise Linux Server
3. Red Hat Enterprise Linux Server 7.$sub_version ($nickname)
4. cpe:/o:redhat:enterprise_linux:7.$sub_version:GA:server
Teardown:
sudo docker stop rhel7-atomic
sudo docker rm rhel7-atomic

Prerequisites
---------------

"""
from rhel7_atomic import rhel7_atomic_base
from autotest.client import utils


class specific_os_release(rhel7_atomic_base):

    def initialize(self):
        super(specific_os_release, self).initialize()

        self.sub_stuff['file_existance'] = 0
        self.sub_stuff['cat_output'] = ''
        self.sub_stuff['para_name'] = ''
        self.sub_stuff['para_pretty'] = ''
        self.sub_stuff['para_cpe'] = ''

        self.load_image()
        self.run_detached_img()

    def run_once(self):
        super(specific_os_release, self).run_once()

        self.loginfo('1. check file /etc/os-release existence')
        cmd_check = 'sudo docker exec rhel7-atomic test -f /etc/os-release && echo $?'
        self.sub_stuff['file_existance'] = utils.run(cmd_check).exit_status

        cmd_cat = 'sudo docker exec rhel7-atomic cat /etc/os-release'
        self.sub_stuff['cat_output'] = self.format_output(utils.run(cmd_cat).stdout)

    def postprocess(self):
        super(specific_os_release, self).postprocess()

        self.loginfo('1. file does exist')
        self.failif_ne(self.sub_stuff['file_existance'], 0,
                       'File /etc/os-release does not exist!!!')

        for para in self.sub_stuff['cat_output']:
            if para[0].startswith('NAME='):
                name_para = para[0][5:].strip('"')
            elif para[0].startswith('PRETTY_NAME='):
                name_pretty = para[0][12:].strip('"')
            elif para[0].startswith('CPE_NAME='):
                name_cpe = para[0][9:].strip('"')

        self.loginfo('2. check parameter NAME')
        self.loginfo(name_para)
        self.failif_ne(name_para, 'Red Hat Enterprise Linux Server',
                       'Parameter NAME is wrong!!!')

        self.loginfo('3. check parameter PRETTY_NAME')
        self.loginfo(name_pretty)
        self.failif(
            not name_pretty.startswith(
                'Red Hat Enterprise Linux Server {}'.format(str(self.config['ver']))),
            'Parameter PRETTY_NAME is wrong!!!'
            )

        self.loginfo('4. check parameter CPE_NAME')
        self.loginfo(name_cpe)
        self.failif_ne(
            name_cpe,
            'cpe:/o:redhat:enterprise_linux:{}:GA:server'.format(str(self.config['ver'])),
            'Parameter CPE_NAME is wrong'
            )

    def cleanup(self):
        super(specific_os_release, self).cleanup()
