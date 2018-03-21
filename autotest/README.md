> I'm using [docker-autotest](https://github.com/autotest/autotest-docker) to test atomic host providing container images: rhel7/rhel-tools, rhel7/syslog, rhel7/sadc, rhel7-atomic, rhel7-init, rhel7/support-tools, rhel7/net-snmp...

### Executing command:
`cd ..../autotest/client`
`sudo ./autotest-local run docker --args images --args images/$image_to_test`

### Init files location:
`...../autotest/client/tests/docker/config_custom/subtests/images/$image_to_test.ini`

### Scripts location:
`...../autotest/client/tests/docker/subtests/images/$image_to_test/$TC_scripts`
