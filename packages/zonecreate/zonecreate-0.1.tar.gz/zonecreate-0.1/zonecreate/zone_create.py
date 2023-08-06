# File: zone_create.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-02-15

import os
import sys
import pkg_resources

import datetime
from collections import defaultdict

from mako.template import Template

def yes_or_no(text):
    y = [ 'y', 't', '1' ]
    inp = raw_input('{text} (y/n): '.format(text=text))

    if inp.lower()[0] in y:
        return True

    return False


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <zonename> [output file]\n'
          '(example: "%s example.net")' % (cmd, cmd))


def main(argv=sys.argv):
    """Create a new zone"""
    if len(argv) < 2:
        usage(argv)
        exit(-1)

    if argv[1][-1] != ".":
        argv[1] = argv[1] + '.'

    # I know ... add it, and then remove it, but only if we need to
    strip_domain = argv[1][:-1]

    print strip_domain

    print('Domain name: {domain}'.format(domain=argv[1]))

    zone = defaultdict(defaultdict)
    zone['root'] = argv[1]
    zone['serial'] = datetime.datetime.utcnow().strftime("%Y%m%d") + "00"
    zone['types']['NS'] = []
    zone['types']['A'] = []
    zone['types']['AAAA'] = []

    count_ns = 1
    print('Name servers for domain. Leave blank to continue ...')
    while True:
        record = raw_input('Name server [{count}]: '.format(count=count_ns))
        if len(record) == 0:
            if count_ns == 1:
                print('At least one name server must be supplied!')
                continue
            break

        entry = {} 
        entry['resource'] = "@"
        entry['record'] = record

        zone['types']['NS'].append(entry)

        if strip_domain in entry['record'] or entry['record'][-1] != '.':
            if yes_or_no('Is {record} a fqdn'.format(record=entry['record'])):
                entry['record'] = entry['record'] + '.'
            else:
                while True:
                    record = raw_input('Enter IP for name server: ')

                    if len(record) == 0:
                        break

                    ipentry = {}
                    ipentry['resource'] = entry['record']
                    ipentry['record'] = record

                    if ":" in record:
                        zone['types']['AAAA'].append(ipentry)
                    if "." in record:
                        zone['types']['A'].append(ipentry)
        count_ns = count_ns + 1

    foutput = argv[2] if 2 in argv else '{domain}.zone'.format(domain=strip_domain)

    with open(foutput, "w") as outfile:
        soa = pkg_resources.resource_string(__name__, "templates/SOA.template")
        outfile.write(Template(soa).render(zone=zone))

        generic = pkg_resources.resource_string(__name__, "templates/GENERIC.template")

        for record in zone['types']['NS']:
            outfile.write(Template(generic).render(type="NS", **record))

        for (key, records) in zone['types'].items():
            if key == "NS":
                continue
            for record in records:
                outfile.write(Template(generic).render(type=key, **record))
