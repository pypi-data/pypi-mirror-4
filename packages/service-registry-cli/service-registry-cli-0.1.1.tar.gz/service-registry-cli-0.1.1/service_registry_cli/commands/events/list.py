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
from datetime import datetime

from cliff.lister import Lister

from service_registry_cli.utils import (
    BaseListCommand,
    get_client,
    format_metadata,
    format_event_payload
)


class ListCommand(BaseListCommand, Lister):
    """
    Return a list of events.
    """
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        client = get_client(parsed_args)
        marker = parsed_args.marker if parsed_args.marker else None
        values = client.events.list(marker=marker)['values']
        event_tuples = [(value['id'],
                        datetime.fromtimestamp(value['timestamp'] / 1000).strftime('%Y-%m-%d %H:%I:%S'),
                        value['type'],
                        format_event_payload(value))
                        for value in values]
        return (('Event ID', 'Timestamp', 'Event Type', 'Payload'),
                event_tuples)
