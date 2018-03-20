r"""
Summary
---------

Test rpms on net-snmp container are signed correctly

Operational Detail
----------------------
#. Load image net-snmp
#. Run it
#. List all the rpms on container
#. Check every rpm is signed with gold key

Prerequisites
---------------

*   Clean host without rhel7-atomic container ever installed
"""

from autotest.client import utils
from net_snmp import net_snmp_base

GOLD_KEY = '199e2f91fd431d51'


class rpms_signatures(net_snmp_base):

    def initialize(self):
        super(rpms_signatures, self).initialize()
        self.load_image()

    def run_once(self):
        super(rpms_signatures, self).run_once()

        # Run a container which sleep 2m to execute the test
        utils.run('sudo docker run -d --name=rt_sig %s sleep 120' %
                  self.sub_stuff['img_name'])

        qa_cmd = 'sudo docker exec rt_sig rpm -qa'
        query_cmd = 'sudo docker exec rt_sig rpm -qi %s'
        rst_qa = utils.run(qa_cmd).stdout
        rpm_list = rst_qa.split('\n')
        fake_list = []
        self.loginfo(rpm_list)
        for rpm in rpm_list:
            # skip the null item
            if len(rpm.strip()) > 0:
                self.loginfo('Checking %s.....' % rpm.strip())
                rst_query = utils.run(query_cmd % rpm.strip()).stdout
                query_list = rst_query.split('\n')
                for line in query_list:
                    if line.strip().startswith('Signature'):
                        items = line.split(' ')
                        self.loginfo('rpm is signed with key %s' % items[-1])
                        if not rpm.strip().lower().startswith('gpg-pubkey'):
                            self.failif_ne(items[-1].strip(), GOLD_KEY,
                                           'rpm is not signed with gold key!')
                        else:
                            fake_list.append(rpm)
        self.loginfo('Fake rpm(s) is/are found:' + str(fake_list))

    def cleanup(self):
        cmd_stop = 'sudo docker stop rt_sig'
        cmd_rm = 'sudo docker rm rt_sig'

        self.loginfo('CLEANUP: {}'.format(cmd_stop))
        utils.run(cmd_stop, timeout=30)

        self.loginfo('CLEANUP: {}'.format(cmd_rm))
        utils.run(cmd_rm)
