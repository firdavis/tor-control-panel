#!/usr/bin/python3 -su

import os
import subprocess

from PyQt5.QtWidgets import QMessageBox
from . import info


def configure():
    info.configuration_info()

    ## Create user debian-tor.
    subprocess.run(
        ['sudo', 'usermod', '-aG', 'debian-tor', 'user']
    )

    # ## Install missing dependencies
    # if /usr/bin/apt-cache policy python3-pyqt5 | grep "Installed: (none)":
    #     subprocess.run(
    #         ['sudo', 'apt', 'install', 'python3-pyqt5', '-y']
    #     )
    # if /usr/bin/apt-cache policy python3-stem | grep "Installed: (none)":
    #     subprocess.run(
    #         ['sudo', 'apt', 'install', 'python3-stem', '-y']
    #     )


    ## Write /etc/profile.d/torbrowser..sh,
    ## which force Tor Browser to use system tor
    ## instead of it's own bundled tor.
    if not os.path.exists("/etc/profile.d/torbrowser.sh"):
        path = "/etc/profile.d/torbrowser.sh"
        content = "export TOR_SKIP_LAUNCH=1"
        subprocess.run(
            ['sudo', 'tee', path],
            input=content.encode(),
            check=True
        )


    torrc_path ='/etc/tor/torrc'

    ## If installed, remove tor.
    if os.path.exists('/usr/bin/tor'):
        subprocess.run(
            ['sudo', 'apt', 'purge', 'tor', '-y']
        )

    ## Install tor.
    subprocess.run(
        ['sudo', 'apt', 'install', 'tor', '-y']
    )
    ## We create our own torrc.
    subprocess.run(
        ['sudo', 'rm', torrc_path]
    )
    content = info.torrc_text()
    print(content)
    subprocess.run(
        ['sudo', 'tee', torrc_path],
        input=content.encode(),
        check=True
    )


    ## Write apparmor local system_tor.
    system_tor_path = "/etc/apparmor.d/local/system_tor"
    content = info.local_system_tor()
    subprocess.run(
        ['sudo', 'tee', system_tor_path],
        input = content.encode(),
        check=True
    )

    ## Reload apparmor
    subprocess.run(
        ['sudo' , 'apparmor_parser', '-r', '/etc/apparmor.d/system_tor']
    )


    ## onioncircuits
    subprocess.run(
        ['sudo', 'apt', 'install', 'onioncircuits', '-y']
    )


    ## Instal pluggable transport.
    subprocess.run(
        ['sudo', 'apt', 'install', 'obfs4proxy', '-y']
    )
    subprocess.run(
        ['sudo', 'apt', 'install', 'snowflake-client', '-y']
    )

    ## webtunnel not in stable repo yet.
    ## Install  from testing.
    if not os.path.exists("/usr/bin/webtunnel-client"):
        path = "/etc/apt/sources.list.d/debian-testing.sources"
        content = '''Types: deb
URIs: http://deb.debian.org/debian
Suites: testing
Components: main
Enabled: yes
'''
        subprocess.run(
            ['sudo', 'tee', path],
            input=content.encode(),
            check=True
        )
        subprocess.run(
            ['sudo', 'apt', 'update']
        )
        subprocess.run(
            ['sudo', 'apt', 'install', 'webtunnel', '-y']
        )
        subprocess.run(
            ['sudo', 'rm', path]
        )

    subprocess.run(
        ['sudo', 'systemctl', 'reload', 'tor@default.service']
    )


    ## Configuration is done.
    path = "/etc/tor/configuration_done"
    subprocess.run(
        ['sudo', 'tee', path],
        input='',
        check=True
    )

    ## We have to reboot the system.
    ## Let the user know.
    reply= QMessageBox(QMessageBox.NoIcon, 'Resart requested.',
'''<p>In order to take into acccount the changes listed in "First run configuration",
you MUST reboot your system. ''', QMessageBox.Ok)
    reply.exec_()

    subprocess.run(
        ['sudo', 'reboot']
    )
