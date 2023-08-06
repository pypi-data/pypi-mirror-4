#!/usr/bin/env python

from __future__ import print_function
import sys
import getpass
import subprocess
import os
from os import path

def exit_error(error):
    print(error, file=sys.stderr)
    exit(1)

def horseshit_to_array(horseshit_file):
    if os.path.exists(horseshit_file):
        horseshit = open(horseshit_file)
        return [line.split()[0] for line in horseshit if line.split() != []]
    else:
        return []

if "linux" in sys.platform:
    hosts_file = "/etc/hosts"
    horseshits = [
        "./horseshits",
        "/etc/horseshits",
        path.expanduser(path.join("~", ".config/horseshits")),
    ]
    restart_network_commands = [
        ["/etc/init.d/networking", "restart"],
        ["/etc/init.d/nscd", "restart"],
        ["/etc/rc.d/nscd", "restart"],
        ["/etc/rc.d/init.d/nscd", "restart"],
    ]

elif "darwin" in sys.platform:
    hosts_file = "/etc/hosts"
    horseshits = [
        "./horseshits",
        "/etc/horseshits",
        path.expanduser(path.join("~", ".config/horseshits")),
    ]
    restart_network_commands = [
        ["dscacheutil", "-flushcache"],
    ]

elif "win32" in sys.platform:
    hosts_file = "/Windows/System32/drivers/etc/hosts"
    horseshits = [
        "./horseshits",
        path.expanduser(path.join("~", ".config/horseshits")),
    ]
    restart_network_commands = [
        ["ipconfig", "/flushdns"],
    ]

else:
    message = '"Please contribute DNS cache flush command on GitHub."'
    restart_network_commands = [
        ["echo", message],
    ]

start_token = "## Start of horseshits"
end_token = "## End of horseshits"

site_list = []
for horseshit in horseshits:
    site_list += horseshit_to_array(horseshit)

def rehash():
    try:
        subprocess.check_call(restart_network_command)
    except:
        return

def work():
    hFile = open(hosts_file, "r+")
    contents = hFile.read()
    if start_token in contents and end_token in contents:
        exit_error("Work mode already set.")
    
    print(start_token, file=hFile)
    for site in set(site_list):
        print("127.0.0.1\t" + site, file=hFile)
        print("127.0.0.1\twww." + site, file=hFile)
    print(end_token, file=hFile)
    
    rehash()

def play():
    hosts_file_handle = open(hosts_file, "r+")
    lines = hosts_file_handle.readlines()
    
    startIndex = -1
    
    for index, line in enumerate(lines):
        if line.strip() == start_token:
            startIndex = index
    
    if startIndex > -1:
        lines = lines[0:startIndex]
        
        hosts_file_handle.seek(0)
        hosts_file_handle.write(''.join(lines))
        hosts_file_handle.truncate()
        
        rehash()

def main():
    if getpass.getuser() != "root" and "win32" not in sys.platform:
        exit_error("Please run script as root.")
    if len(sys.argv) != 2:
        exit_error("Usage: " + sys.argv[0] + " [work|play]")
    try:
        {"work": work, "play": play}[sys.argv[1]]()
    except KeyError:
        exit_error("Usage: " + sys.argv[0] + " [work|play]")	

if __name__ == "__main__":
    main()
