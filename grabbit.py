"""
grabbit.py

grabs email/ip(:port) strings from a given file
"""

from __future__ import print_function # pylint needs this for py3k
from socket import inet_aton # non regex ip validation
from os import access, R_OK # file access validation
from sys import stdout # write to stdout if no file specified
import re
import argparse

__author__ = "Vlad <vlad at vlads dot me>"
__version__ = "0.1"
__license__ = "GPL v3"
__description__ = "python script for grabbing email or ip addresses \
(optional with port) from a given file. "

PARSER = argparse.ArgumentParser(description=__description__)
GROUP = PARSER.add_mutually_exclusive_group()

GROUP.add_argument('--email', help='match an email address', action='store_true')
GROUP.add_argument('--ip', help='match an ip address', action='store_true')
GROUP.add_argument('--ip-port', help='match an ip:port', action='store_true')

PARSER.add_argument('-s', '--separator', help='separator used when data is \
                    column separated using one or more characters')
PARSER.add_argument('-w', '--write', help='file to write in (default stdout)')
PARSER.add_argument('file', help='the file to look in')

ARGS = PARSER.parse_args()

if not (ARGS.email or ARGS.ip or ARGS.ip_port):
    print("You have to select an option.")
    exit(1)

if not access(ARGS.file, R_OK):
    print("Can't open the file, exiting.")
    exit(1)

if ARGS.write is not None:
    try:
        OUT = open(ARGS.write, 'w')
    except OSError:
        print("Can't write to file, permission error, exiting.")
        exit(1)
else:
    OUT = stdout

if ARGS.separator is not None:
    SEP = ARGS.separator.encode('utf-8').decode('unicode_escape')
else:
    SEP = None

VALIDMAIL = re.compile(r'^[^@ ]+@[^@]+\.[^@]+$')

def is_valid_ip(ip_address):
    """ Returns the validity of an IP address """
    if not re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_address):
        return False # first we need a valid ip form
    try:
        inet_aton(ip_address) # check if it's a valid ip address
    except OSError:
        return False
    return True

for line in open(ARGS.file, 'rb'):
    line = line.strip().split(SEP.encode('utf-8'))

    if ARGS.email:
        found = [OUT.write(s.decode('utf-8') + '\n') for i, s in enumerate(line)
                 if VALIDMAIL.match(s.decode('utf-8'))]
        OUT.flush()
    else:
        for string in line:
            string = string.decode('utf-8')
            if ARGS.ip_port and len(string.split(':')) == 2: # IP:Port
                ip, port = string.split(':')
                if is_valid_ip(ip) and 0 < int(port) < 65535:
                    OUT.write('{}:{}\n'.format(ip, port))
                    OUT.flush()
            elif ARGS.ip:
                if is_valid_ip(string):
                    OUT.write(string + '\n')
                    OUT.flush()
