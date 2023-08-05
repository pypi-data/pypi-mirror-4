# Copyright 2012 Rackspace
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cliff.command import Command

from service_registry import Client


class BaseCommand(Command):
    def get_parser(self, prog_name):
        parser = super(BaseCommand, self).get_parser(prog_name=prog_name)
        parser.add_argument('--username', dest='username')
        parser.add_argument('--api-key', dest='api_key')
        parser.add_argument('--api-url', dest='api_url')
        parser.add_argument('--region', dest='region')
        return parser


class BaseListCommand(BaseCommand):
    def get_parser(self, prog_name):
        parser = super(BaseListCommand, self).get_parser(prog_name=prog_name)
        parser.add_argument('--limit', dest='limit')
        parser.add_argument('--marker', dest='marker')
        parser.add_argument('--tag', dest='tag')
        return parser


class BaseShowCommand(BaseCommand):
    def get_parser(self, prog_name):
        parser = super(BaseShowCommand, self).get_parser(prog_name=prog_name)
        parser.add_argument('--id', dest='object_id')
        return parser


def get_client(parsed_args):
    username = parsed_args.username
    api_key = parsed_args.api_key
    api_url = parsed_args.api_url
    region = parsed_args.region

    if not username:
        raise ValueError('Missing required argument: username')

    if not api_key:
        raise ValueError('Missing required argument: api_key')

    kwargs = {}

    if api_url is not None:
        kwargs['base_url'] = api_url

    if region is not None:
        kwargs['region'] = region

    c = Client(username=username, api_key=api_key, **kwargs)

    return c


def format_metadata(metadata_dict):
    metadata_str = ""
    for key, value in metadata_dict.items():
        metadata_str += '%s: %s,\n' % (key, value)
    metadata_str = metadata_str.strip(',\n')

    return metadata_str


# TODO
def format_event_payload(event_response):
    event_payload_str = ''
    event_payload = event_response['payload']
    if event_payload == []:
        event_payload_str = '[]'
        return event_payload_str
    if event_response['type'] in ['service.join', 'services.timeout']:
        if event_response['type'] == 'service.join':
            event_payload = [event_payload]

        for service in event_payload:
            for key, value in service.iteritems():
                if key == 'metadata':
                    metadata_str = format_metadata(value)
                    event_payload_str += 'metadata: %s\n' % (metadata_str)
                else:
                    event_payload_str += '%s: %s\n' % (key, value)
    else:
        for key, value in event_payload.iteritems():
            event_payload_str += '%s: %s\n' % (key, value)
        event_payload_str = event_payload_str.strip(',\n')

    return event_payload_str
