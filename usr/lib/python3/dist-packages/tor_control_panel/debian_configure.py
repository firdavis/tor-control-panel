#!/usr/bin/python3 -su

import os
import subprocess

from PyQt5.QtWidgets import QMessageBox
from . import info


def configure():
    info.configuration_info()

    ## Write /etc/profile.d/torbrowser..sh,
    ## which force Tor Browser to use system tor
    ## instead of it'w own bundled tor.'
    if not os.path.exists("/etc/profile.d/torbrowser.sh"):
        path = "/etc/profile.d/torbrowser.sh"
        content = "export TOR_SKIP_LAUNCH=1\n"
        subprocess.run(
            ["sudo", "/usr/bin/tee", path],
            input=content.encode(),
            check=True
        )

    ## Create user/group debian-tor.
    ## No consequences if it's already exists.
    subprocess.run(
        ['sudo', 'usermod', '-a', '-G', 'debian-tor', 'debian-tor']
    )

    ## Install tor if missing.
    if not os.path.exists("/us/bin/tor"):
        subprocess.run(
            ['sudo', '/usr/bin/apt', 'install', 'tor', '-y']
        )
        ## Add the %include directive to /etc/tor/torrc
        path = "/etc/tor/torrc"
        line_to_add = "%include /etc/torrc.d/*.conf"
        with open(path, 'r') as f:
            content = f.read()  + line_to_add + '\n'
        with open(path , 'r' , encoding="utf-8") as f:
            subprocess.run(
                ["sudo", "/usr/bin/tee", path],
                input=content.encode(),
                check=True
            )



    ## Configuration is done.
    path = "/etc/tor/configuration_done"
    subprocess.run(
        ["sudo", "/usr/bin/tee", path],
        input='',
        check=True
    )

    reply= QMessageBox(QMessageBox.NoIcon, 'Resart requested.',
'''<p>In order to take into acccount the changes listed in "First run configuration",
you MUST reboot your system. ''', QMessageBox.Ok)
    reply.exec_()

    subprocess.run(
        ['sudo', '/usr/sbin/reboot']
    )
