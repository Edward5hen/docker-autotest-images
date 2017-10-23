r"""
Summary
---------
/etc/os-release file correctness

Operational Detail
----------------------
#. /etc/os-release file correctness
Setup:
1. The atomic host should be without registration.
   If it's registered before, just unregister it.
2. check if rhel-atomic image is pulled, if not,
   do "sudo docker pull registry.access.redhat.com/rhel7-atomic"
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
