#!/usr/bin/python3 -su

import os
import subprocess

from PyQt5.QtWidgets import QMessageBox
from . import info


def configure():
    info.configuration_info()

    ## Add pkexec passwordless.
    path = "/etc/polkit-1/rules.d/50-nopasswd-pkexec.rules"
    content = info.pkexec_noauth()
    subprocess.run(
        ['sudo', '/usr/bin/tee', path],
        input=content.encode(),
        check=True
    )


    ## Create user debian-tor.
    subprocess.run(
        ['pkexec', '/usr/sbin/usermod', '-aG', 'debian-tor', 'user']
    )


    ## Write /etc/profile.d/torbrowser..sh,
    ## which force Tor Browser to use system tor
    ## instead of it's own bundled tor.
    if not os.path.exists("/etc/profile.d/torbrowser.sh"):
        path = "/etc/profile.d/torbrowser.sh"
        content = "export TOR_SKIP_LAUNCH=1"
        subprocess.run(
            ['pkexec', '/usr/bin/tee', path],
            input=content.encode(),
            check=True
        )


    torrc_path ='/etc/tor/torrc'

    ## If installed, remove tor.
    if os.path.exists('/usr/bin/tor'):
        subprocess.run(
            ['pkexec', '/usr/bin/apt', 'purge', 'tor', '-y']
        )

    ## Install tor.
    subprocess.run(
        ['pkexec', '/usr/bin/apt', 'install', 'tor', '-y']
    )
    ## We create our own torrc.
    subprocess.run(
        ['pkexec', 'rm', torrc_path]
    )
    content = info.torrc_text()
    print(content)
    subprocess.run(
        ['pkexec', '/usr/bin/tee', torrc_path],
        input=content.encode(),
        check=True
    )


    ## Write apparmor local system_tor.
    system_tor_path = "/etc/apparmor.d/local/system_tor"
    content = info.local_system_tor()
    subprocess.run(
        ['pkexec', '/usr/bin/tee', system_tor_path],
        input = content.encode(),
        check=True
    )

    ## Reload apparmor
    subprocess.run(
        ['pkexec' , '/usr/sbin/apparmor_parser', '-r', '/etc/apparmor.d/system_tor']
    )


    ## onioncircuits
    subprocess.run(
        ['pkexec', '/usr/bin/apt', 'install', 'onioncircuits', '-y']
    )


    ## Instal pluggable transport.
    subprocess.run(
        ['pkexec', '/usr/bin/apt', 'install', 'obfs4proxy', '-y']
    )
    subprocess.run(
        ['pkexec', '/usr/bin/apt', 'install', 'snowflake-client', '-y']
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
            ['pkexec', '/usr/bin/tee', path],
            input=content.encode(),
            check=True
        )
        subprocess.run(
            ['pkexec', '/usr/bin/apt', 'update']
        )
        subprocess.run(
            ['pkexec', '/usr/bin/apt', 'install', 'webtunnel', '-y']
        )
        subprocess.run(
            ['pkexec', 'rm', path]
        )

    subprocess.run(
        ['pkexec', '/usr/bin/systemctl', 'reload', 'tor@default.service']
    )


    ## Configuration is done.
    path = "/etc/tor/configuration_done"
    subprocess.run(
        ['pkexec', '/usr/bin/tee', path],
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
        ['pkexec', '/usr/sbin/reboot']
    )
