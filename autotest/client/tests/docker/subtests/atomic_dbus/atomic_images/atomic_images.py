r"""
Summary
---------

Test atomic dbus service

Operational Detail
----------------------
#. atomic images info & delete
setup:
1. sudo docker pull rhel7/rsyslog

Step1: create a dbus client that gets a system dbus object as dbus_object with
        the path/org/atomic/object and the well-known name org.atomic
Expectation: dbus_object has been successfully obtained
Step2: print dbus_object.ImagesInfo("rhel7/rsyslog", False,
        dbus_interface="org.atomic") in the client
Expectation: output is same as running sudo atomic images info rhel7/rsyslog
Step3: print dbus_object.ImagesInfo("rhel7/sadc", True,
        dbus_interface="org.atomic") in the client
Expectation: output is same as running "sudo atomic images info \
        --remote rhel7/sadc"
Step4: run dbus_object.ImagesDelete("rhel7/rsyslog", False, False,
        dbus_interface="org.atomic") in the client
Expectation: image rhel7/rsyslog is successfully deleted
Step5: pull rhel7/rsyslog and install and run it
Expectation: container can be successfully started
Step6: run dbus_object.ImagesDelete("rhel7/rsyslog", True, False,
        dbus_interface="org.atomic") in the client
Expectation: image rhel7/rsyslog is successfully deleted
Step7: run dbus_object.ImagesDelete("some_remote_registry/some_image:some_tag",
        False, True, dbus_interface="org.atomic") in the client
Expectation: some_image in some_remote_registry with some_tag is
        successfully deleted on the registry host

#. atomic images prune
Setup:
1. sudo docker pull rhel7/rsyslog
2. sudo atomic install rhel7/rsyslog
3. sudo atomic run rhel7/rsyslog
4. sudo docker commit $container_id without specifying repo and
   tag to create a dangling image manually

Step1: create a dbus client that gets a system dbus object as dbus_object with
        the path/org/atomic/object and the well-known name org.atomic
Expectation: dbus_object has been successfully obtained
Step2: run dbus_object.ImagesPrune(dbus_interface="org.atomic") in the client
Expectation: the manually created dangling image is successfully pruned

#. atomic images list & help
Setup:
1. sudo docker pull rhel7/rsyslog
2. img_id=`sudo docker images | sed -n 2p | awk '{print $3}'`

Step1: create a dbus client that gets a system dbus object as dbus_object with
        the path /org/atomic/object and the well-known name org.atomic
Expectation: dbus_object has been successfully obtained
Step2: print dbus_object.ImagesList(dbus_interface="org.atomic") in the client
Expectation: the output is the same as sudo atomic images list
Step3: print dbus_object.ImagesHelp(img_id, dbus_interface="org.atomic")
       in the client
Expectation: the output is the same as "sudo atomic images help $img_id"

---------------

"""

import json
from dbus.exceptions import DBusException

from dbus_client import AtomicDBusClient
from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from dockertest.containers import DockerContainers


DBUS_OBJ = AtomicDBusClient()
IMAGE_NAME = 'registry.access.redhat.com/rhel7/rsyslog'


class atomic_images(SubSubtestCaller):

    config_section = 'atomic_dbus/atomic_images'


class images_list(SubSubtest):

    def initialize(self):
        super(images_list, self).initialize()
        utils.run('sudo docker pull %s' % IMAGE_NAME)

        self.sub_stuff['dbus_rst'] = ''

    def run_once(self):
        super(images_list, self).run_once()
        self.sub_stuff['dbus_rst'] = DBUS_OBJ.images_list()

    def postprocess(self):
        super(images_list, self).postprocess()
        decoded_json = json.loads(self.sub_stuff['dbus_rst'])
        length = len(decoded_json)
        _type = isinstance(decoded_json[0], dict)
        name = decoded_json[0]['image_name']
        value = 'yes' if length == 1 and _type and name == IMAGE_NAME else 'no'
        self.failif_ne(value, 'yes', 'Dbus failed to list images')


class images_help(SubSubtest):

    def initialize(self):
        super(images_help, self).initialize()
        self.sub_stuff['img_id'] = utils.run(
                "sudo docker images --format {{.ID}}").stdout.strip()

        self.sub_stuff['dbus_rst'] = ''
        self.sub_stuff['host_rst'] = ''

    # Since I couldn't find any image has the help info, I just use rsyslog.
    # Although the command will fail, but if we got the same error msg via dbus
    # it means that dbus works.
    def run_once(self):
        super(images_help, self).run_once()
        self.sub_stuff['host_rst'] = utils.run(
                'sudo atomic images help %s' % self.sub_stuff['img_id'],
                ignore_status=True).stderr.strip()
        try:
            DBUS_OBJ.images_help(self.sub_stuff['img_id'])
        except DBusException, e:
            self.sub_stuff['dbus_rst'] = str(e)

    def postprocess(self):
        super(images_help, self).postprocess()
        self.failif(
            self.sub_stuff['host_rst'] not in self.sub_stuff['dbus_rst'],
            'DBus failed to help images!'
        )


class images_prune(SubSubtest):

    def initialize(self):
        super(images_prune, self).initialize()
        utils.run('sudo atomic install %s' % IMAGE_NAME)
        utils.run('sudo atomic run %s' % IMAGE_NAME)
        # Create dangling image
        utils.run('sudo docker commit rsyslog')

    def run_once(self):
        super(images_prune, self).run_once()
        DBUS_OBJ.images_prune()

    def postprocess(self):
        super(images_prune, self).postprocess()
        imgs_names = DockerImages(self).list_imgs_full_name()
        self.failif_ne(imgs_names, ['rhel7/rsyslog:lastest'],
                       'Dbus failed to prune dangling images')

    def clean_up(self):
        super(images_prune, self).clean_up()
        ctns = DockerContainers(self)
        ctns.clean_all(['rsyslog'])


class images_info(SubSubtest):

    def initialize(self):
        super(images_info, self).initialize()
        self.sub_stuff['img_info_dbus_rst'] = None
        self.sub_stuff['img_info_host_rst'] = None
        self.sub_stuff['img_info_remote_dbus_rst'] = None
        self.sub_stuff['img_info_remote_host_rst'] = None

    def run_once(self):
        super(images_info, self).run_once()
        self.sub_stuff['img_info_dbus_rst'] = \
            DBUS_OBJ.images_info("rehl7/rsyslog", False)
        self.sub_stuff['img_info_host_rst'] = \
            utils.run('sudo atomic images info rhel7/rsyslog')

        self.sub_stuff['img_info_remote_dbus_rst'] = \
            DBUS_OBJ.images_info('rhel7/sadc', True)
        self.sub_stuff['img_info_remote_host_rst'] = \
            utils.run('sudo atomic images info --remote rhel7/sadc')

    def postprocess(self):
        super(images_info, self).postprocess()
        self.failif_ne(self.sub_stuff['img_info_dbus_rst'],
                       self.sub_stuff['img_info_host_rst'].stdout,
                       'Dbus failed to list rsyslog info')
        self.failif_ne(self.sub_stuff['img_info_remote_dbus_rst'],
                       self.sub_stuff['img_info_remote_host_rst'].stdout,
                       'Dbus failed to list sadc info remotely')


class images_delete(SubSubtest):

    def run_once(self):
        super(images_delete, self).run_once()
        DBUS_OBJ.images_delete('rhel7/rsyslog', False, False)

    def postprocess(self):
        super(images_delete, self).postprocess()
        imgs_names = DockerImages(self).list_imgs_full_name()
        self.failif('rhel7/rsyslog:lastest' in imgs_names,
                    'dbus can not delete image rhel7/rsyslog')


class images_delete_force(SubSubtest):

    def initialize(self):
        super(images_delete_force, self).initialize()
        utils.run('sudo docker pull rhel7/rsyslog')
        utils.run('sudo atomic install rhel7/rsyslog')
        utils.run('sudo atomic run rhel7/rsyslog')

    def run_once(self):
        super(images_delete_force, self).run_once()
        DBUS_OBJ.images_delete('rhel7/rsyslog', True, False)

    def postprocess(self):
        super(images_delete_force, self).postprocess()
        imgs_names = DockerImages(self).list_imgs_full_name()
        self.failif('rhel7/rsyslog:lastest' in imgs_names,
                    'dbus can not delete image rhel7/rsyslog forcely')
