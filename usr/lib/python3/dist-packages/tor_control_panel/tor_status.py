#!/usr/bin/python3 -su

## Copyright (C) 2018 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

import subprocess
from stem.control import Controller

torrc_file_path = '/etc/torrc.d/20_default_torrc.conf'


def tor_status():
    print("tor_status was called.")

    def tor_enabled_check():
        with open(torrc_file_path, 'r') as f:
            content = f.readlines()
            for line in content:
                if  "DisableNetwork 1" in line:
                    return False
                elif "DisableNetwork 0" in line:
                    return True

    if tor_enabled_check():
        print("tor_status status: tor_enabled")
        return "tor_enabled"
    else:
        print("tor_status status: tor_disabled")
        return "tor_disabled"


def set_enabled():
    print("set_enabled was called.")

    content = ''

    with open(torrc_file_path, 'r', encoding="utf-8") as f:
        content = f.readlines()

    disable_network_found = False
    for line in content:
        if 'DisableNetwork' in line:
            disable_network_found = True
            break

    if disable_network_found:
        with open(torrc_file_path,'r', encoding="utf-8") as f:
            content = f.read().replace('DisableNetwork 1', 'DisableNetwork 0')

    else:
        with open(torrc_file_path,'r') as f:
            content = f.read() + '\n' + 'DisableNetwork 0' + '\n'

    ## Write torrc as root.
    ## No need to change file permissions.
    subprocess.run(
        ["sudo", "tee", torrc_file_path],
        input=content.encode(),
        check=True
    )

    ## When using system tor, the DisableNetwork line is ignored in torrc.
    ## It is managed with SETCONF in the bundled Tor in Tor Browser,
    ## switching ftom 1 to 0 when connecting to the network.
    ## So, the use of stem.set_conf seems the simpest way to overcome the isssue.
    ## Whonix does it a different way that was not explored.
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.set_conf("DisableNetwork", "0")

    return 'tor_enabled'


def set_disabled():
    print("set_disabled was called.")

    content = ''

    with open(torrc_file_path, 'r',  encoding="utf-8") as f:
        content = f.readlines()

    disable_network_found = False
    for line in content:
        if 'DisableNetwork' in line:
            disable_network_found = True
            break

    if disable_network_found:
        with open(torrc_file_path,'r', encoding="utf-8") as f:
            content = f.read().replace('DisableNetwork 0', 'DisableNetwork 1')

    else:
        with open(torrc_file_path,'r', encoding="utf-8") as f:
            content = f.read() + '\n' + 'DisableNetwork 1' + '\n'

    subprocess.run(
        ["sudo", "tee", torrc_file_path],
        input=content.encode(),
        check=True
    )

    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.set_conf("DisableNetwork", "1")

    return 'tor_disabled'

