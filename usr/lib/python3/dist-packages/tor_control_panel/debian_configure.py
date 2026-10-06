#!/usr/bin/sudo /usr/bin/python3 -su

import os
import subprocess

from PyQt5.QtWidgets import QMessageBox
from pathlib import Path
from . import info


def configure():
    info.configuration_info()

    ## Create groups for sudoers.d, using the real user name.
    username = os.environ["USER"]

    subprocess.run(
        ['sudo', '/usr/sbin/groupadd', '--system', 'tor-admin'],
        check=True
    )

    subprocess.run(
        ['sudo', '/usr/sbin/usermod', '-aG', 'tor-admin', username],
        check=True
    )


    ## Write /etc/profile.d/torbrowser..sh,
    ## which force Tor Browser to use system tor
    ## instead of it's own bundled tor.
    if not os.path.exists("/etc/profile.d/torbrowser.sh"):
        path = "/etc/profile.d/torbrowser.sh"
        content = "export TOR_SKIP_LAUNCH=1\n"
        subprocess.run(
            ['sudo', '/usr/bin/tee', path],
            input=content.encode(),
            check=True
        )


    ## If installed, reinstall tor to get te latest version.
    if os.path.exists('/usr/bin/tor'):
        subprocess.run(
            ['sudo', '/usr/bin/apt', 'install', '-y', '--reinstall', 'tor'],
            check=True
        )

    else:
        ## Install tor.
        subprocess.run(
            ['sudo', '/usr/bin/apt', 'install', '-y', 'tor'],
            check=True
        )

    # We create our own torrc.
    torrc_path = "/etc/tor/torrc"

    subprocess.run(
        ['sudo', '/usr/bin/rm', torrc_path],
        check=True
    )
    content = info.torrc_text()
    subprocess.run(
        ['sudo', '/usr/bin/tee', torrc_path],
        input=content.encode(),
        check=True
    )


    ## Write apparmor local system_tor.
    system_tor_path = "/etc/apparmor.d/local/system_tor"
    content = info.local_system_tor()
    subprocess.run(
        ['sudo', '/usr/bin/tee', system_tor_path],
        input = content.encode(),
        check=True
    )

    ## Reload apparmor
    subprocess.run(
        ['sudo' , '/usr/sbin/apparmor_parser', '-r', '/etc/apparmor.d/system_tor'],
        check=True
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
            ['sudo', '/usr/bin/tee', path],
            input=content.encode(),
            check=True
        )
        subprocess.run(
            ['sudo', '/usr/bin/apt', 'update'],
            check=True
        )
        subprocess.run(
            ['sudo', '/usr/bin/apt', 'install', '-y', 'webtunnel'],
            check=True
        )
        subprocess.run(
            ['sudo', '/usr/bin/rm', path],
            check=True
        )


    # ## Check if Tor Browser is installed.
    # path = None
    #
    # def find_folder(folder_name):
    #     ## Search the whole file system in case Tor Browser
    #     ## is intalled in an exotic folder.
    #     for path in Path('/').rglob(folder_name):
    #         print(path)
    #         return(path)
    #
    # path = find_folder('tor-browser')
    #
    # if path is None:
    #     ## Install torbrowser-launcher with flatpak.
    #     if not os.path.exists("/usr/bin/flatpak"):
    #         subprocess.run(
    #             ['sudo', 'apt', 'install', 'flatpak'],
    #             check=True
    #         )
    #         subprocess.run(
    #             ['sudo', 'flatpak', 'remote-add', '--if-not-exists', 'flathub', \
    #                 'https://dl.flathub.org/repo/flathub.flatpakrepo'],
    #             check=True
    #         )
    #
    #
    # else:
    #     print("Tor Browser is intallled. OK. Finishing configuration...")
    #

    ## Configuration is done.
    path = "/etc/tor/configuration_done"
    subprocess.run(
        ['sudo', '/usr/bin/tee', path],
        input='',
        check=True
    )

    ## We have to reboot the system.
    ## Let the user know.
    reply= QMessageBox(QMessageBox.NoIcon, 'Resart requested.',
'''<p>In order to take into acccount some of the changes listed in "First run configuration",
you MUST reboot your system. ''', QMessageBox.Ok)
    reply.exec_()

    subprocess.run(
        ['sudo', '/usr/sbin/reboot'],
        check=True
    )
