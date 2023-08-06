# File: zone_update_soa.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-02-15

import os
import os.path
import sys
import re
import datetime

soa_regex = re.compile(r"@\s+(?P<record_ttl>[0-9]+[a-z]*)?\s+IN\s+SOA\s+(?P<ns>[\w\.]+)\s+(?P<hostmaster>[\w\.]+)\s+\(\s*(?P<serial>\d+)\D*(?P<refresh>\d+)\D*(?P<retry>\d+)\D*(?P<expire>\d+)\D*(?P<minttl>\d+)\D*\)", re.MULTILINE)
serial_regex = re.compile(r"(?P<date>[0-9]{8})(?P<inc>[0-9]{2})")

soa_record = """@ {record_ttl} IN SOA {ns} {hostmaster} (
    {serial} \t; Serial number
    {refresh} \t; Refresh
    {retry} \t; Retry
    {expire} \t; Expiration
    {minttl} \t; Min TTL
    )"""

def yes_or_no(text):
    y = [ 'y', 't', '1' ]
    inp = raw_input('{text} (y/n): '.format(text=text))

    if inp.lower()[0] in y:
        return True

    return False


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <zonename>\n'
          '(example: "%s example.net/example.net.zone")' % (cmd, cmd))


def main(argv=sys.argv):
    """Create a new zone"""

    if len(argv) < 2:
        usage(argv)
        exit(-1)

    if ".zone" not in argv[1]:
        argv[1] = argv[1] + '.zone'

    print('Domain name: {domain}'.format(domain=argv[1][:-5]))

    if os.path.isfile(argv[1]) is False:
        print('Zonefile "{zf}" doesn\'t exist'.format(zf=argv[1]))
        exit(-1)

    with open(argv[1], "r+") as zonefile:
        zone = zonefile.read()
        soa = soa_regex.search(zone).groupdict()

        if soa['record_ttl'] is None:
            soa['record_ttl'] = '1d'

        print('Current SOA record:')
        print(soa_record.format(**soa))

        cur_date = datetime.datetime.utcnow().strftime("%Y%m%d")
        serial = serial_regex.match(soa['serial']).groupdict()
        
        if serial['date'] == cur_date:
            print('The SOA record has already been updated today... incrementing')
            serial['inc'] = int(serial['inc']) + 1
        else:
            serial['inc'] = int(serial['inc'])
        
        serial['date'] = cur_date
        serial = '{date}{inc:0=2d}'.format(**serial)
        soa['serial'] = serial

        print('')
        print('New SOA record:')
        print(soa_record.format(**soa))

        print('')
        if yes_or_no('Write new SOA record to zone') is False:
            print('Not writing zone to disk.')
            exit(0)

        new_zone = soa_regex.sub(soa_record.format(**soa), zone)
        zonefile.seek(0)
        zonefile.truncate(0)
        zonefile.write(new_zone)

        print('')
        print('Zone has been updated.')
