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

import logging

from cliff.lister import Lister

from service_registry_cli.utils import BaseListCommand, get_client
from service_registry_cli.utils import format_metadata, format_timestamp


class ListCommand(BaseListCommand, Lister):
    """
    Return a list of the available sessions.
    """
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        client = get_client(parsed_args)
        marker = parsed_args.marker if parsed_args.marker else None
        limit = parsed_args.limit if parsed_args.limit else None

        result = client.sessions.list(marker=marker, limit=limit)
        values = result['values']
        metadata = result['metadata']

        parsed_args.returned_metadata = metadata

        session_tuples = [(value['id'],
                          value['heartbeat_timeout'],
                          format_timestamp(value['last_seen']),
                          format_metadata(value['metadata']))
                          for value in values]
        return (('Session ID', 'Heartbeat Timeout', 'Last Seen', 'Metadata'),
                session_tuples)
