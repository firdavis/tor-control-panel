#!/usr/bin/python3 -su

## Copyright (C) 2018 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

import os, subprocess, fcntl
from stem.control import Controller

if os.path.exists('/usr/share/anon-gw-base-files/gateway'):
    whonix=True
else:
    whonix=False

## TODO: code duplication
## Should use same variable as in anon_connection_wizard.py.
torrc_file_path = '/etc/torrc.d/20_default_torrc.conf'


def tor_status():
    print("tor_status was called.")

    # output = self.tor_enabled_check()  #subprocess.check_output('/usr/libexec/helper-scripts/tor_enabled_check')
    # output = output.decode("UTF-8").strip()

    def tor_enabled_check():
        # if os.path.exists(torrc_file_path):
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

'''Unlike tor_status() function which only shows the current state of the anon_connection_wizard.conf,
set_enabled() and set_disabled() function will try to repair the missing torrc or DisableNetwork line.
This makes sense because when we call set_enabled() or set_disabled() we really want Tor to work.

set_enabled() will return a tuple with two value: a string of error type and an int of error code.
'''

'''set_enabled() is specified as follows:
set_enabled() will:
1. guarantee the existence of 40_tor_control_panel.conf
2. guarantee the final value of DisableNetwork is 0 in the file
3. guarantee Tor uses DisableNetwork 0
'''
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
        # if os.path.exists(torrc_file_path):
        with open(torrc_file_path,'r') as f:
            content = f.read() + '\n' + 'DisableNetwork 0' + '\n'

    subprocess.run(
        ["sudo", "tee", torrc_file_path],
        input=content.encode(),
        check=True
    )

    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.set_conf("DisableNetwork", "0")

    return 'tor_enabled'

def set_disabled():
    print("set_disabled was called.")

    content = ''

    # if os.path.exists(torrc_file_path):
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

