#!/usr/bin/env python

__VERSION__ = '0.1.0'

import sys
import os
import re
import time

from urllib import urlencode
import urllib2

from urlparse import urlparse, urljoin

try:
    import simplejson as json
except ImportError:
    import json

from optparse import OptionParser

def main():

    p = OptionParser(
        version=__VERSION__,
    )

    p.add_option(
        '-k', '--keystone',
        action = 'store',
        type = 'str',
        dest='keystone',
        metavar='keystone-url',
        help='keystone url'
    )

    p.add_option(
        '-t', '--tenant',
        action = 'store',
        type = 'str',
        dest='tenant',
        metavar='tenant',
        help='tenant name'
    )

    p.add_option(
        '-u', '--user',
        action = 'store',
        type = 'str',
        dest='user',
        metavar='user',
        help='user name'
    )

    p.add_option(
        '-p', '--password',
        action = 'store',
        type = 'str',
        dest='password',
        metavar='password',
        help='password'
    )

    p.add_option(
        '-r', '--region',
        action = 'store',
        type = 'str',
        dest='region',
        metavar='region',
        help='region',
        default='RegionOne'
    )

    p.add_option(
        '-f', '--file-name',
        action = 'store',
        type = 'str',
        dest='file',
        metavar='file_name',
        help='object name for put into container',
        default='zabbix_check.txt'
    )

    p.add_option(
        '-m', '--max',
        action = 'store',
        type = 'int',
        dest='max_containers',
        metavar='max_number_of_container',
        help='max number of existing container',
        default=10
    )

    opts, args = p.parse_args()

    if opts.keystone == None:
        p.print_help()
        return 1

    if opts.tenant == None:
        p.print_help()
        return 1

    if opts.user == None:
        p.print_help()
        return 1

    if opts.password == None:
        p.print_help()
        return 1

    # set sleep time for interval
    sleeping = 0.3

    # container name for test
    hash = os.urandom(16).encode('hex')
    container_name = '_zabbix_{0}'.format(hash)

    # get authtoken and endpoint url from keystone
    ks = _get_authtoken(
            opts.keystone,
            opts.tenant,
            opts.user,
            opts.password,
            opts.region,
            )

    # check get authtoken
    if ks['url_path'] == None or ks['authtoken'] == None:
        return 2

    ks['auth_url'] = urljoin(args[0], ks['url_path'])

    # check number of container
    result = _list_container(ks)
    if result > opts.max_containers:
        return 3

    # create container
    result = _create_container(ks, container_name)
    if not result == 201:
        return 4

    time.sleep(sleeping)

    # put file into container
    result = _put_file(ks, container_name, opts.file)
    if not result == 201:
        return 5

    time.sleep(sleeping)

    # delete file from container
    result = _delete_file(ks, container_name, opts.file)
    if not result == 204:
        return 6

    time.sleep(sleeping)

    # delete container
    result = _delete_container(ks, container_name)
    if not result == 204:
        return 7

    # ALL OK
    return 0

def _get_authtoken(url, tenant, user, password, region):

    _result = {}
    _result['authtoken'] = None
    _result['url_path'] = None

    if not re.search('/$', url):
        url = url + '/'
    token_url = urljoin(url, 'tokens')

    headers = {
        'Content-Type': 'application/json',
    }

    body = dict()
    body['auth'] = {}
    body['auth']['tenantName'] = tenant
    body['auth']['passwordCredentials'] = {}
    body['auth']['passwordCredentials']['username'] = user
    body['auth']['passwordCredentials']['password'] = password

    request = urllib2.Request(token_url, data=json.dumps(body), headers=headers)

    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        return _result

    if not response.code == 200:
        return _result

    res_body = response.read()
    res_json = json.loads(res_body)

    _result['authtoken'] = res_json['access']['token']['id']

    for endpoints_links in res_json['access']['serviceCatalog']:
        if endpoints_links['type'] == 'object-store':
            for endpoint in endpoints_links['endpoints']:
                if endpoint['region'] == region:
                    up = urlparse(endpoint['internalURL'])
                    _result['url_path'] = up.path

    return _result

def _list_container(ks):

    headers = {'X-Auth-Token': ks['authtoken']}

    request = urllib2.Request(ks['auth_url'], headers=headers)

    try:
        response = urllib2.urlopen(request)
        return len(list(response))
    except urllib2.HTTPError, e:
        return None

def _create_container(ks, container):

    headers = {'X-Auth-Token': ks['authtoken']}
    url = '{0}/{1}'.format(ks['auth_url'], container)

    request = urllib2.Request(url, headers=headers)
    request.get_method = lambda: 'PUT'

    try:
        response = urllib2.urlopen(request)
        return response.code
    except urllib2.HTTPError, e:
        return None

def _delete_container(ks, container):

    headers = {'X-Auth-Token': ks['authtoken']}
    url = '{0}/{1}'.format(ks['auth_url'], container)

    request = urllib2.Request(url, headers=headers)
    request.get_method = lambda: 'DELETE'

    try:
        response = urllib2.urlopen(request)
        return response.code
    except urllib2.HTTPError, e:
        return None

def _put_file(ks, container, file):

    headers = {'X-Auth-Token': ks['authtoken']}
    url = '{0}/{1}/{2}'.format(ks['auth_url'], container, file)
    file_contents = 'this is check file'

    request = urllib2.Request(url, data=file_contents, headers=headers)
    request.get_method = lambda: 'PUT'

    try:
        response = urllib2.urlopen(request)
        return response.code
    except urllib2.HTTPError, e:
        return None

def _delete_file(ks, container, file):

    headers = {'X-Auth-Token': ks['authtoken']}
    url = '{0}/{1}/{2}'.format(ks['auth_url'], container, file)

    request = urllib2.Request(url, headers=headers)
    request.get_method = lambda: 'DELETE'

    try:
        response = urllib2.urlopen(request)
        return response.code
    except urllib2.HTTPError, e:
        return None

if __name__ == '__main__':

    # return code
    # 0 : success
    # 1 : syntax error
    # 2 : failed to get authtoken
    # 3 : number of containers reached max
    # 3 : failed to create container
    # 5 : failed to put object in container
    # 6 : failed to delete object in container
    # 7 : failed to delete container

    print main()
    sys.exit()
