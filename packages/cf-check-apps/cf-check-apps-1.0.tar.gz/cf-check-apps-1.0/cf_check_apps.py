import getpass
import itertools
import json
import os
import sys

import grequests
import requests

__doc__ = '''cf-check-apps

Usage:
    cf-check-apps <host>

Options:
    -h --help       Show this screen.
'''

def get_token(host):
    cache = os.path.expanduser('~/.vmc_token')
    if os.path.exists(cache):
        with open(cache) as fobj:
            data = json.load(fobj)
            if host in data:
                return data[host]
    else:
        data = {}
    username = raw_input('Username: ')
    password = getpass.getpass()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = json.dumps({'password': password})
    response = requests.post('%s/users/%s/tokens' % (host, username), data=data, headers=headers)
    if response.ok:
        token = response.json['token']
    else:
        print "Login failed"
        sys.exit(1)
    data[host] = token
    with open(cache, 'w') as fobj:
        json.dump(data, fobj)
    return token

def check(host, token):
    apps = requests.get('%s/apps' % host, headers={'Authorization': token}).json
    urls = ['http://%s' % url for url in itertools.chain(*(app['uris'] for app in apps)) if url]
    result = {
        'ok': [],
        'fail': [],
        'apps': apps,
        'urls': urls,
    }
    for response in grequests.map(grequests.get(url) for url in urls):
        if response.ok:
            result['ok'].append(response.url)
        else:
            result['fail'].append(response.url)
    return result


def main(host, token=None):
    token = token or get_token(host)
    result = check(host, token)
    print "SUMMARY"
    print "-------"
    print ""
    print "Apps: %s" % len(result['apps'])
    print "URLs: %s" % len(result['urls'])
    print "OK:   %s" % len(result['ok'])
    print "FAIL: %s" % len(result['fail'])
    print ""
    print "Failed URLs"
    print "-----------"
    print ""
    for url in result['fail']:
        print url

def cli():
    import docopt
    args = docopt.docopt(__doc__)
    main(args['<host>'])


if __name__ == '__main__':
    cli()
