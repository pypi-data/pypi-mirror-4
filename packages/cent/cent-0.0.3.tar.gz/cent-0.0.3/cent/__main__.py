#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import sys

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

try:
    import simplejson as json
except ImportError:
    import json

from .client import Client


def run():

    parser = argparse.ArgumentParser(description='Centrifuge client')

    parser.add_argument(
        'section', metavar='SECTION', type=str, help='section key from cent configuration file'
    )
    parser.add_argument(
        'category', metavar='CATEGORY', type=str, help='category name'
    )
    parser.add_argument(
        'key', metavar='KEY', type=str, help='event key'
    )
    parser.add_argument(
        '--data', type=str, help='event data', default='{}'
    )
    parser.add_argument(
        '--tag', action='append', help='event tags'
    )
    parser.add_argument(
        '--unique', action='append', help='unique event data keys'
    )
    parser.add_argument(
        '--config', type=str, default="~/.centrc", help='cent configuration file'
    )

    options = parser.parse_args()

    config_file = os.path.expanduser(options.config)
    config = ConfigParser.ConfigParser()
    config.read(config_file)

    if not options.section in config.sections():
        print(
            "Section {0} not found in {1} configuration file".format(
                options.section, options.config
            )
        )
        sys.exit(1)

    try:
        address = config.get(options.section, 'address')
        project = config.get(options.section, 'project')
        public_key = config.get(options.section, 'public_key')
        secret_key = config.get(options.section, 'secret_key')
        try:
            timeout = config.getint(options.section, 'timeout')
        except:
            timeout = 2
    except Exception as e:
        print(e)
        sys.exit(1)

    if not sys.stdin.isatty():
        json_data = sys.stdin.read().strip()
    else:
        json_data = options.data

    try:
        data = json.loads(json_data)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not data:
        print("no event data, nothing to do")
        sys.exit(1)

    client = Client(
        address,
        project,
        public_key,
        secret_key,
        timeout=timeout
    )

    if not isinstance(data, dict):
        print("event data must be valid JSON object")
        sys.exit(1)

    event = {
        'category': options.category,
        'key': options.key,
        'data': data
    }
    if options.unique:
        event['unique_keys'] = options.unique
    if options.tag:
        event['tags'] = options.tag

    to_send = [event]
    response = client.send(to_send)
    result, error = response
    if error:
        print(error)
        sys.exit(1)
    else:
        print(result)


if __name__ == '__main__':
    run()