# -*- coding: utf-8 -*- -
"""dhmanager.py

Manage your DNS Records at DreamHost.

1) Read first the (rather limited) API documentation from:
    http://wiki.dreamhost.com/API
2) Then register an API key via:
    https://panel.dreamhost.com/?tree=home.api
3) Store the api key in this folder in file called KEYFILE
4) run: python dhmanager.py

Created by: risto.haukioja@gmail.com
"""
import uuid
import requests
import argparse
import logging

f = open('KEYFILE', 'r')
key = f.readline().strip()
f.close()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class DnsManager(object):

    """manage dns through DreamHost"""

    def __init__(self, key):
        self.key = key
        self.base_url = 'https://api.dreamhost.com/?key=%s&unique_id=%s&cmd=%s'

    def _get_resource(self, resource):
        r = requests.get(resource)
        if r.status_code == 200:
            return r.text
        else:
            print '%s - %s' % (r.status_code, r.text)

    def dns_list_records(self):
        cmd = 'dns-list_records'
        resource = self.base_url % (self.key, uuid.uuid4(), cmd)
        print self._get_resource(resource)

    def dns_add_record(self, record, r_type, value, comment=None):
        cmd = 'dns-add_record'
        resource_url = self.base_url + '&record=%s&type=%s&value=%s&comment=%s'
        resource = resource_url % (self.key, uuid.uuid4(), cmd, record, r_type,
                                   value, comment)
        print self._get_resource(resource)

    def dns_remove_record(self, record, r_type, value):
        cmd = 'dns-remove_record'
        resource_url = self.base_url + '&record=%s&type=%s&value=%s'
        resource = resource_url % (self.key, uuid.uuid4(), cmd, record, r_type,
                                   value)
        print self._get_resource(resource)


def get_parser():
    parser = argparse.ArgumentParser(description='DreamHost DNS Manager')
    parser.add_argument('-l', '--dns-list-records', action='store_true',
                        help='List DNS records from your account')
    parser.add_argument('-a', '--dns-add-record', action='store_true',
                        help="Add anew dns record")
    parser.add_argument('-r', '--dns-remove-record', action='store_true',
                        help='Remove a dns record')
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
    logging.debug(args.keys())
    manager = DnsManager(key)
    if args['dns_list_records']:
        manager.dns_list_records()
    else:
        record = args['record']
        r_type = args['type']
        value = args['value']
        comment = args['comment']
        if not record or not r_type or not value:
            raise ValueError('you need to define record, type and value')
        if args['dns_add_record']:
            manager.dns_add_record(record, r_type, value, comment)
        if args['dns_remove_record']:
            manager.dns_remove_record(record, r_type, value)


if __name__ == '__main__':
    cmd_line_runner()