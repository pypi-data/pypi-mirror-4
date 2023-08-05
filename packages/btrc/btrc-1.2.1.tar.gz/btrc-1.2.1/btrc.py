#!/usr/bin/env python
import sys
import json
from optparse import OptionParser

import requests


class CouchbaseClient(object):

    """Simplified couchbase client
    """

    def __init__(self, host_port, bucket):
        self.base_url = 'http://{0}'.format(host_port)
        self.bucket = bucket

    def _get_list_of_nodes(self):
        """Yield CAPI host:port names"""
        url = self.base_url + '/pools/default/'
        try:
            r = requests.get(url).json
        except requests.exceptions.ConnectionError:
            sys.exit(
                'Cannot establish connection with specified [host:port] node')
        if r is not None:
            for node in r['nodes']:
                hostname, port = node['hostname'].split(':')
                if port == '8091':
                    yield hostname + ':8092'
                else:
                    yield hostname + ':9500'
        else:
            sys.exit('Node has no buckets/misconfigured')

    def _get_list_of_ddocs(self):
        """Yield names of design documents in specified bucket"""
        url = self.base_url + \
            '/pools/default/buckets/{0}/ddocs'.format(self.bucket)
        r = requests.get(url).json
        if r is not None:
            return (row['doc']['meta']['id'] for row in r['rows'])
        else:
            sys.exit('Wrong bucket name')

    def get_btree_stats(self):
        """Yield view btree stats"""
        for node in self._get_list_of_nodes():
            for ddoc in self._get_list_of_ddocs():
                url = 'http://{0}'.format(node) + \
                    '/_set_view/{0}/{1}/_btree_stats'.format(self.bucket, ddoc)
                yield node, ddoc, requests.get(url).json


class CliArgs(object):

    """CLI options and args handler
    """

    def __init__(self):
        usage = 'usage: %prog -n node:port [-b bucket]\n\n' +\
                'Example: %prog -n 127.0.0.1:8091 -b default'

        parser = OptionParser(usage)

        parser.add_option('-n', dest='node',
                          help='Node address', metavar='127.0.0.1:8091')
        parser.add_option('-b', dest='bucket', default='default',
                          help='Bucket name', metavar='default')

        self.options, self.args = parser.parse_args()

        if not self.options.node:
            parser.print_help()
            sys.exit(1)


def main():
    """Save all view btree stats to *.json files"""
    ca = CliArgs()
    cb = CouchbaseClient(ca.options.node, ca.options.bucket)
    for node, ddoc, stat in cb.get_btree_stats():
        filename = node.replace(':', '_') + ddoc.replace('/', '_') + '.json'
        with open(filename, 'w') as fh:
            print 'Saving btree stats to: ' + filename
            fh.write(json.dumps(stat, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
