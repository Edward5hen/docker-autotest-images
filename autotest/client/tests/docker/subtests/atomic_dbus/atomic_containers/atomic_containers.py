r"""
Summary
---------

Test atomic dbus service

Operational Detail
----------------------
#. atomic containers list
Setup:
1. sudo docker pull rhel7/rsyslog
2. sudo docker atomic install rhel7/rsyslog
3. sudo atomic run rhel7/rsyslog

Step1: create a dbus client that gets a system dbus object as dbus_object with
        the path/org/atomic/object and the well-known name org.atomic
Expectation: dbus_object has been successfully obtained
Step2: print dbus_object.ContainersList(dbus_interface="org.atomic")
        in the client
Expectation: the output is same as sudo atomic containers list

Teardown:
1. sudo docker stop rsyslog
2. sudo docker rm rsyslog
3. sudo docker rmi rhel7/rsyslog

#. atomic containers delete
Setup:
1. sudo docker pull rhel7/rsyslog
2. sudo atomic install rhel7/rsyslog
3. sudo atomic run rhel7/rsyslog
4. sudo docker stop rsyslog

Step1: create a dbus client that gets a system dbus object as dbus_object with
        the path/org/atomic/object and the well-known name org.atomic
Expectation:  dbus_object has been successfully obtained
Step2: run dbus_object.ContainersDelete(['rsyslog'], False, False,
        '', dbus_interface='org.atomic') in client
Expectation: rsyslog container has been successfully deleted
Step3: sudo atomic run rhel7/rsyslog
Expectation: rsyslog container is started again
Step4: run dbus_object.ContainersDelete(['rsyslog'], False, True, '',
        dbus_interface='org.atomic') in client
Expectation: rsyslog container has been successfully deleted
Step5: sudo atomic run rhel7/rsyslog & docker pull rhel7/sadc &
       atomic install rhel7/sadc & atomic run rhel7/sadc
Expectation: rsyslog and sadc container are successfully started
Step6: docker stop rsyslog & docker stop sadc
Expectation: make containers' status not running
Step7: run dbus_object.ContainersDelete(None, True, False, '',
        dbus_interface='org.atomic') in client
Expectation: both containers are successfully deleted
Step8: sudo atomic run rhel7/rsyslog & sudo docker pull rhel7/sadc &
        sudo atomic install rhel7/sadc & sudo atomic run rhel7/sadc
Expectation: rsyslog and sadc container are successfully started
Step9: run dbus_object.ContainersDelete(None, True, True, '',
        dbus_interface='org.atomic') in client
Expectatoin: both containers are successfully deleted

---------------

"""

from dbus_client import AtomicDBusClient
from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from dockertest.containers import DockerContainers


DBUS_OBJ = AtomicDBusClient()


class atomic_containers(SubSubtestCaller):

    config_section = 'atomic_dbus/atomic_containers'

    def clean_up(self):
        super(atomic_containers, self).clean_up()
        imgs = DockerImages(self)
        imgs.clean_all(['rhel7/rsyslog', 'rhel7/sadc'])


class containers_list(SubSubtest):

    def initialize(self):
        super(containers_list, self).initialize()
        utils.run('sudo docker pull rhel7/rsyslog')
        utils.run('sudo atomic install rhel7/rsyslog')
        utils.run('sudo atomic run rhel7/rsyslog')

        self.sub_stuff['dbus_rst'] = ''
        self.sub_stuff['host_rst'] = ''

    def run_once(self):
        super(containers_list, self).run_once()
        self.sub_stuff['dbus_rst'] = DBUS_OBJ.containers_list()
        self.sub_stuff['host_rst'] = \
            utils.run('sudo atomic containers list')

    def postprocess(self):
        super(containers_list, self).postprocess()
        self.failif_ne(self.sub_stuff['dbus_rst'],
                       self.sub_stuff['host_rst'].stdout,
                       'Dbus failed to list containers')


class containers_delete_base(SubSubtest):

    def postprocess(self, dscp, ctns=['rsyslog']):
        super(containers_delete_base, self).postprocess()
        _ctns = DockerContainers(self)
        ctn_names = _ctns.list_containers_with_name()
        self.failif(ctns[0] in ctn_names,
                    'Dbus failed to delete container %s' % dscp)


class containers_delete(containers_delete_base):

    def initialize(self):
        super(containers_delete, self).initialize()
        utils.run('sudo docker stop rsyslog')

    def run_once(self):
        super(containers_delete, self).run_once()
        DBUS_OBJ.containers_delete(['rsyslog'], False, False)

    def postprocess(self):
        super(containers_delete, self).postprocess(dscp='')


class containers_delete_force(containers_delete_base):

    def initialize(self):
        super(containers_delete_force, self).initialize()
        utils.run('sudo atomic run rhel7/rsyslog')

    def run_once(self):
        super(containers_delete_force, self).run_once()
        DBUS_OBJ.containers_delete(['rsyslog'], False, True)

    def postprocess(self):
        super(containers_delete_force, self).postprocess(dscp='forcely')


class containers_delete_all(containers_delete_base):

    def initialize(self):
        super(containers_delete_all, self).initialize()
        utils.run('sudo atomic run rhel7/rsyslog')
        utils.run('sudo docker pull rhel7/sadc')
        utils.run('sudo atomic install rhel7/sadc')
        utils.run('sudo atomic run rhel7/sadc')
        utils.run('sudo docker stop rhel7/rsyslog')
        utils.run('sudo docker stop rhel7/sadc')

    def run_once(self):
        super(containers_delete_all, self).run_once()
        DBUS_OBJ.containers_delete(None, True, False)

    def postprocess(self):
        super(containers_delete_all, self).postprocess(
            ctns=['rsyslog', 'sadc'], dscp='all')


class containers_delete_all_force(containers_delete_base):

    def initialize(self):
        super(containers_delete_base, self).initialize()
        utils.run('sudo atomic run rhel7/rsyslog')
        utils.run('sudo docker pull rhel7/sadc')
        utils.run('sudo atomic install rhel7/sadc')
        utils.run('sudo atomic run rhel7/sadc')

    def run_once(self):
        super(containers_delete_base, self).initialize()
        DBUS_OBJ.containers_delete(None, True, True)

    def postprocess(self):
        super(containers_delete_base, self).postprocess(
            ctns=['rsyslog', 'sadc'], dscp='all')
