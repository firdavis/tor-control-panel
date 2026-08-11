#!/usr/bin/python3 -su

import os
import subprocess

def configure():
    if not os.path.exists("usr/bin/tor"):
        command = "pkexec apt install tor -y"
        subprocess.call(command, shell=True)
        # subprocess.run(
        #     ['sudo', 'apt', 'install', 'tor']
        #     check=True
        # )

        ## Add the %include directive to /etc/tor/torrc
        path = "/etc/tor/torrc"
        line_to_add = "%include /etc/torrc.d/*.conf"
        with open(path, 'r') as f:
            content = f.read()  + line_to_add + '\n'
            print(content)

        with open(path , 'r' , encoding="utf-8") as f:
            subprocess.run(
                ["sudo", "tee", path],
                input=content.encode(),
                check=True
            )

    ## Configuration is done.
    path = "/etc/tor/configuration_done"
    subprocess.run(
        ["sudo", "tee", path],
        input='',
        check=True
    )


