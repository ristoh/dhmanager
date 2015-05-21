# -*- coding: utf-8 -*- -
"""dhmanager.py

Library for managing DreamHost DNS Records. See README.md for more details.
Created by: risto.haukioja@gmail.com
"""
import uuid
import requests
import argparse
import urllib
import urlparse
import logging
import os
from os.path import expanduser

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_key():
    try:
        file_name = os.path.join(expanduser('~'), '.dhkeyfile')
        with open(file_name, 'r') as f:
            return f.readline().strip()
    except IOError:
        exit('~/.dhkeyfile could not be found')


class DnsManager(object):

    """manage dns through DreamHost"""

    def __init__(self, key):
        self.key = key
        self.base_url = 'https://api.dreamhost.com/?'

    def _resource_url(self, **kwargs):
        query = {
            'id': str(uuid.uuid4()),
            'key': self.key
        }
        keys = ['cmd', 'record', 'type', 'value', 'comment']
        for key in keys:
            if kwargs.get(key, None):
                query.update({key: kwargs[key]})

        url_parts = list(urlparse.urlparse(self.base_url))
        url_parts[4] = urllib.urlencode(query)
        logging.debug(url_parts)

        return urlparse.urlunparse(url_parts)

    def _get_resource(self, resource):
        r = requests.get(resource)
        if r.status_code == 200:
            return r.text
        else:
            print '%s - %s' % (r.status_code, r.text)

    def get_current_ip(self):
        r = requests.get(r'http://jsonip.com')
        self.public_ip = r.json()['ip']
        return self.public_ip

    def dns_set_dynamic_ip(self, record):
        r_type = 'A'
        value = self.get_current_ip()
        self.dns_add_record(record, r_type, value)

    def dns_list_records(self):
        cmd = 'dns-list_records'
        resource = self._resource_url(cmd=cmd)
        print self._get_resource(resource)

    def dns_add_record(self, record, type, value, comment=None):
        cmd = 'dns-add_record'
        resource = self._resource_url(cmd=cmd, record=record,
                                      type=type, value=value,
                                      comment=comment)
        print self._get_resource(resource)
        self.dns_list_records()

    def dns_remove_record(self, record, type, value):
        cmd = 'dns-remove_record'
        resource = self._resource_url(cmd=cmd, record=record, type=type,
                                      value=value)
        print self._get_resource(resource)
        self.dns_list_records()


def get_parser():
    parser = argparse.ArgumentParser(description='DreamHost DNS Manager')
    parser.add_argument('-l', '--dns-list-records', action='store_true',
                        help='List DNS records from your account')
    parser.add_argument('-a', '--dns-add-record', action='store_true',
                        help="Add anew dns record")
    parser.add_argument('-r', '--dns-remove-record', action='store_true',
                        help='Remove a dns record')
    parser.add_argument('-d', '--dns-set-dynamic-ip', action='store_true',
                        help='Set a record to your dynamic IP')
    parser.add_argument('--key',
                        help='DreamHost API key')
    parser.add_argument('--record',
                        help='Record to be changed e.g. my.foo.bar')
    parser.add_argument('--type',
                        help='A,CNAME,NS,PTR,NAPTR,SRV,TXT,SPF, or AAAA')
    parser.add_argument('--value',
                        help='the DNS record value e.g. 98.100.101.55')
    parser.add_argument('--comment',
                        help='want to add a comment to your record')
    return parser


def cmd_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())
    if not args['key']:
        key = get_key()
    else:
        key = args['key']
    logging.debug(key)
    manager = DnsManager(key)
    logging.debug(manager)
    if args['dns_list_records']:
        manager.dns_list_records()
    else:
        record = args['record']
        r_type = args['type']
        value = args['value']
        comment = args['comment']
        if args['dns_add_record']:
            manager.dns_add_record(record, r_type, value, comment)
        if args['dns_remove_record']:
            manager.dns_remove_record(record, r_type, value)
        if args['dns_set_dynamic_ip']:
            manager.dns_set_dynamic_ip(record)


if __name__ == '__main__':
    cmd_line_runner()
