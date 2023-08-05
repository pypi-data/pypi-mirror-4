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


class ListCommand(BaseListCommand, Lister):
    """
    Return a list of services.
    """
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        client = get_client(parsed_args)
        if parsed_args.tag:
            values = client.services.list_for_tag(parsed_args.tag)['values']
        else:
            values = client.services.list()['values']
        service_tuples = [(value['id'],
                          value['session_id'],
                          ', '.join(value['tags']))
                          for value in values]
        return (('Service ID', 'Session ID', 'Tags'),
                service_tuples)
