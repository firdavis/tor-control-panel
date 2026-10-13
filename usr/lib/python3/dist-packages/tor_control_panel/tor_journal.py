#!/usr/bin/python3 -su

'''
There is no way to write a polkit rule to allow a log or any single command
passworrdless. unless using systemd-journal, which would give access to
to ALL the systemd logs.

Consequently, we write a separate module for 'jounalctl' without sudo.
We change its ownership to root is postinst.
'''

from subprocess import Popen, PIPE

def show_tor_journal():
    journal_command = ['/usr/bin/journalctl', '-n', '200', '-u', 'tor@default.service']

    p = Popen(journal_command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    ## Journal content is untrusted; decode defensively (a
    ## malformed byte must not crash the log view) then strip
    ## control characters, escape sequences and markup.
    # text = sanitize_string(stdout.decode(errors='replace'))
    text = stdout.decode(errors='replace')
    return text
