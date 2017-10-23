import dbus
import sys


class AtomicDBusClient(object):
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.dbus_object = self.bus.get_object("org.atomic",
                                               "/org/atomic/object")

    def images_info(self, image, remote):
        return self.dbus_object.ImagesInfo(image, remote,
                                           dbus_interface="org.atomic")

    def images_prune(self):
        self.dbus_object.ImagesPrune(dbus_interface="org.atomic")

    def images_list(self):
        return self.dbus_object.ImagesList(dbus_interface="org.atomic")

    def images_delete(self, image, force, remote):
        self.dbus_object.ImagesDelete(image, force, remote,
                                      dbus_interface="org.atomic")

    def images_help(self, image):
        return self.dbus_object.ImagesHelp(image, dbus_interface="org.atomic")

    def containers_list(self):
        return self.dbus_object.ContainersList(dbus_interface="org.atomic")

    def containers_delete(self, containers,
                          all_containers=False, force=False,
                          storage=''):
        self.dbus_object.ContainersDelete(containers, all_containers,
                                          force, storage,
                                          dbus_interface="org.atomic")

    def top(self, containers, optional):
        return self.dbus_object.Top(containers, optional,
                                    dbus_interface='org.atomic')


if __name__ == "__main__":
    dbus_client = AtomicDBusClient()

    if (sys.argv[1], sys.argv[2]) == ("images", "info"):
        info_remote = False if sys.argv[-1] == "--remote" else True
        print dbus_client.images_info(sys.argv[3], info_remote)
    elif (sys.argv[1], sys.argv[2]) == ("images", "prune"):
        dbus_client.images_prune()
    elif (sys.argv[1], sys.argv[2]) == ("images", "list"):
        print dbus_client.images_list()
    elif (sys.argv[1], sys.argv[2]) == ("images", "delete"):
        delete_image = sys.argv[3] if sys.argv[3] != "-f" else sys.argv[4]
        delete_force = True if sys.argv[3] == "-f" else False
        delete_remote = True if sys.argv[-1] == "--remote" else False
        dbus_client.images_delete(delete_image, delete_force, delete_remote)
    elif (sys.argv[1], sys.argv[2]) == ("images", "help"):
        print dbus_client.images_help(sys.argv[3])
    elif (sys.argv[1], sys.argv[2]) == ("containers", "list"):
        print dbus_client.containers_list()
    elif (sys.argv[1], sys.argv[2]) == ("containers", "delete"):
        ctns = []
        force = False
        all_del = False
        for arg in sys.argv[3:]:
            if not arg.startswith('-'):
                ctns.append(arg)
            if arg in ('-a', '--all'):
                all_del = True
            if arg in ('-f', '--force'):
                force = True
        dbus_client.containers_delete(ctns, all_del, force)
