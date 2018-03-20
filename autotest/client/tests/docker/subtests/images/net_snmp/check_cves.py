r"""
Summary
---------
Check CVE via atom scan command

Operational Detail
----------------------

Prerequisites
---------------
"""
from autotest.client import utils
from net_snmp import net_snmp_base


class check_cves(net_snmp_base):

    def initialize(self):
        super(check_cves, self).initialize()

        self.load_image()

    def check(self):
        cmd = 'sudo atomic scan %s | grep -i pass' % self.sub_stuff['img_name']
        result = utils.run(cmd, timeout=900)
        self.failif_ne(result.exit_status, 0, 'atomic scan failed!')
        self.loginfo('No CVEs found by atomic scan')

    def postprocess(self):
        super(check_cves, self).postprocess()

        self.check()

    def cleanup(self):
        pass
