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

import os
import logging
import sys

import libcloud.security
from cliff.app import App

from service_registry_cli.command_manager import CommandManager
from service_registry_cli.commands.help import HelpAction
from service_registry_cli import __version__

CA_CERT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'data/cacert.pem')
libcloud.security.CA_CERTS_PATH.insert(0, CA_CERT_PATH)


class ServiceRegistryApp(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(ServiceRegistryApp, self).__init__(
            description='Rackspace Cloud Service Registry Command Line Interface',
            version=__version__,
            command_manager=CommandManager('service_registry'),
        )

    def build_option_parser(self, description, version):
        # Replace HelpAction with the one which supports sub-commands
        argparse_kwargs = {'conflict_handler': 'resolve'}
        parser = super(ServiceRegistryApp, self).\
            build_option_parser(description,
                                version,
                                argparse_kwargs=argparse_kwargs)
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit",
        )
        return parser

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = ServiceRegistryApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
