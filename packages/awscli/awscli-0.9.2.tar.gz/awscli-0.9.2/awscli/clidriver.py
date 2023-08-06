# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import argparse
import sys
import os
import traceback
import json
import six
import botocore.session
from botocore.compat import copy_kwargs
from awscli import EnvironmentVariables, __version__
from .help import get_provider_help, get_service_help, get_operation_help
from .formatter import get_formatter
from .paramfile import get_paramfile


def split_list(s):
    l = []
    depth = 0
    item = ''
    for c in s:
        if c == '[':
            depth += 1
            if depth > 1:
                item += c
        elif c == ']':
            if depth > 1:
                item += c
            depth -= 1
        elif c == ',':
            if depth == 1:
                l.append(item)
                item = ''
            elif depth > 1:
                item += c
        else:
            item += c
    l.append(item)
    return l


class CLIDriver(object):

    Formatter = argparse.RawTextHelpFormatter

    type_map = {
        'structure': str,
        'map': str,
        'timestamp': str,
        'list': str,
        'string': str,
        'float': float,
        'integer': str,
        'long': int,
        'boolean': bool,
        'double': float,
        'blob': str}

    def __init__(self):
        self.session = botocore.session.get_session(EnvironmentVariables)
        self.session.user_agent_name = 'aws-cli'
        self.session.user_agent_version = __version__
        self.args = None
        self.service = None
        self.region = None
        self.endpoint = None
        self.operation = None

    def create_choice_help(self, choices):
        help_str = ''
        for choice in sorted(choices):
            help_str += '* %s\n' % choice
        return help_str

    def create_main_parser(self):
        """
        Create the main parser to handle the global arguments.
        """
        self.cli_data = self.session.get_data('cli')
        description = self.cli_data['description']
        self.parser = argparse.ArgumentParser(formatter_class=self.Formatter,
                                              description=description,
                                              add_help=False,
                                              conflict_handler='resolve')
        for option_name in self.cli_data['options']:
            option_data = copy_kwargs(self.cli_data['options'][option_name])
            if 'choices' in option_data:
                choices = option_data['choices']
                if not isinstance(choices, list):
                    provider = self.session.get_variable('provider')
                    choices_path = choices.format(provider=provider)
                    choices = self.session.get_data(choices_path)
                if isinstance(choices, dict):
                    choices = list(choices.keys())
                option_data['help'] = self.create_choice_help(choices)
                option_data['choices'] = choices + ['help']
            self.parser.add_argument(option_name, **option_data)
        self.parser.add_argument('--version', action="version",
                                 version=self.session.user_agent())

    def create_service_parser(self, remaining):
        """
        Create the subparser to handle the Service arguments.

        :type remaining: list
        :param remaining: The list of command line parameters that were
            not recognized by upstream parsers.
        """
        if self.args.profile:
            self.session.profile = self.args.profile
        prog = '%s %s' % (self.parser.prog,
                          self.service.cli_name)
        parser = argparse.ArgumentParser(formatter_class=self.Formatter,
                                         add_help=False, prog=prog)
        operations = [op.cli_name for op in self.service.operations]
        operations.append('help')
        parser.add_argument('operation', help='The operation',
                            metavar='operation',
                            choices=operations)
        args, remaining = parser.parse_known_args(remaining)
        if args.operation == 'help':
            get_service_help(self.service)
            return 0
        self.operation = self.service.get_operation(args.operation)
        return self.create_operation_parser(remaining)

    def create_operation_parser(self, remaining):
        """
        Create the subparser to handle the Operation arguments.

        :type remaining: list
        :param remaining: The list of command line parameters that were
            not recognized by upstream parsers.
        """
        prog = '%s %s %s' % (self.parser.prog,
                             self.service.cli_name,
                             self.operation.cli_name)
        parser = argparse.ArgumentParser(formatter_class=self.Formatter,
                                         add_help=False, prog=prog)
        for param in self.operation.params:
            if param.type == 'list':
                parser.add_argument(param.cli_name,
                                    help=param.documentation,
                                    nargs='*',
                                    type=self.type_map[param.type],
                                    required=param.required,
                                    dest=param.py_name)
            elif param.type == 'boolean':
                if param.required:
                    dest = param.cli_name[2:].replace('-', '_')
                    mutex = parser.add_mutually_exclusive_group(required=True)
                    mutex.add_argument(param.cli_name,
                                       help=param.documentation,
                                       dest=dest,
                                       action='store_true')
                    false_name = '--no-' + param.cli_name[2:]
                    mutex.add_argument(false_name,
                                       help=param.documentation,
                                       dest=dest,
                                       action='store_false')
                else:
                    parser.add_argument(param.cli_name,
                                        help=param.documentation,
                                        action='store_true',
                                        required=param.required,
                                        dest=param.py_name)
            else:
                parser.add_argument(param.cli_name,
                                    help=param.documentation,
                                    nargs=1,
                                    type=self.type_map[param.type],
                                    required=param.required,
                                    dest=param.py_name)
        if self.operation.is_streaming():
            parser.add_argument('outfile', metavar='output_file',
                                help='Where to save the content')
        if 'help' in remaining:
            get_operation_help(self.operation)
            return 0
        args, remaining = parser.parse_known_args(remaining)
        if remaining:
            print('Something is wrong.  We have leftover options')
            print(remaining)
            return -1
        return args

    def unpack_cli_arg(self, param, s):
        """
        Parses and unpacks the encoded string command line parameter
        and returns native Python data structures that can be passed
        to the Operation.
        """
        if param.type == 'integer':
            if isinstance(s, list):
                s = s[0]
            return int(s)
        elif param.type == 'float' or param.type == 'double':
            # TODO: losing precision on double types
            if isinstance(s, list):
                s = s[0]
            return float(s)
        elif param.type == 'structure' or param.type == 'map':
            if isinstance(s, list) and len(s) == 1:
                s = s[0]
            if s[0] == '{':
                d = json.loads(s)
            else:
                msg = 'Structure option value must be JSON or path to file.'
                raise ValueError(msg)
            return d
        elif param.type == 'list':
            if isinstance(s, six.string_types):
                if s[0] == '[':
                    return json.loads(s)
            elif isinstance(s, list) and len(s) == 1:
                if s[0][0] == '[':
                    return json.loads(s[0])
            return [self.unpack_cli_arg(param.members, v) for v in s]
        elif param.type == 'blob' and param.payload and param.streaming:
            if isinstance(s, list) and len(s) == 1:
                file_path = s[0]
            file_path = os.path.expandvars(file_path)
            file_path = os.path.expanduser(file_path)
            if not os.path.isfile(file_path):
                msg = 'Blob values must be a path to a file.'
                raise ValueError(msg)
            return open(file_path, 'rb')
        else:
            if isinstance(s, list):
                s = s[0]
            return str(s)

    def build_call_parameters(self, args, param_dict):
        for param in self.operation.params:
            value = getattr(args, param.py_name)
            if value is not None:
                # Don't include non-required boolean params whose
                # values are False
                if param.type == 'boolean' and not param.required and value is False:
                    continue
                if not hasattr(param, 'no_paramfile'):
                    if isinstance(value, list) and len(value) == 1:
                        temp = value[0]
                    else:
                        temp = value
                    temp = get_paramfile(self.session, temp)
                    if temp:
                        value = temp
                param_dict[param.py_name] = self.unpack_cli_arg(param, value)

    def display_error_and_exit(self, ex):
        if self.args.debug:
            traceback.print_exc()
        elif isinstance(ex, Exception):
            print(ex)
        elif self.args.output != 'json':
            print(ex)
        return 1

    def get_error_code_and_message(self, response):
        code = 'Unknown'
        message = 'Unknown'
        if 'Response' in response:
            if 'Errors' in response['Response']:
                if 'Error' in response['Response']['Errors']:
                    if 'Message' in response['Response']['Errors']['Error']:
                        message = response['Response']['Errors']['Error']['Message']
                    if 'Code' in response['Response']['Errors']['Error']:
                        code = response['Response']['Errors']['Error']['Code']
        return (code, message)

    def save_output(self, body_name, response_data, path):
        buffsize = 32768
        with open(path, 'wb') as fp:
            data = response_data[body_name].read(buffsize)
            while data:
                fp.write(data)
                data = response_data[body_name].read(buffsize)
        del response_data[body_name]

    def call(self, args):
        try:
            params = {}
            self.build_call_parameters(args, params)
            self.endpoint = self.service.get_endpoint(
                self.args.region, endpoint_url=self.args.endpoint_url)
            self.endpoint.verify = not self.args.no_verify_ssl
            if self.operation.can_paginate:
                pages = self.operation.paginate(self.endpoint, **params)
                self._display_response(self.operation, pages)
                # TODO: need to handle http error responses.  I believe
                # this will be addressed with the plugin refactoring,
                # but the other alternative is going to be that we'll need
                # to cache the fully buffered response.
            else:
                http_response, response_data = self.operation.call(
                    self.endpoint, **params)
                response_data = response_data
                streaming_param = self.operation.is_streaming()
                if streaming_param:
                    self.save_output(streaming_param, response_data,
                                     args.outfile)
                self._display_response(self.operation, response_data)
                return self._handle_http_response(http_response, response_data)
        except Exception as ex:
            return self.display_error_and_exit(ex)

    def _handle_http_response(self, http_response, response_data):
        if http_response.status_code >= 500:
            msg = self.session.get_data('messages/ServerError')
            code, message = self.get_error_code_and_message(response_data)
            print(msg.format(error_code=code,
                                error_message=message))
            return http_response.status_code - 399
        if http_response.status_code >= 400:
            msg = self.session.get_data('messages/ClientError')
            code, message = self.get_error_code_and_message(response_data)
            print(msg.format(error_code=code,
                                error_message=message))
            return http_response.status_code - 399

    def _display_response(self, operation, response_data):
        try:
            self.formatter(operation, response_data)
        finally:
            # flush is needed to avoid the "close failed in file object
            # destructor" in python2.x (see http://bugs.python.org/issue11380).
            sys.stdout.flush()

    def test(self, cmdline):
        """
        Useful for unit tests.  Pass in a command line as you would
        type it on the command line (e.g.):

        ``aws ec2 describe-instances --instance-id i-12345678``

        and this method will return the
        dictionary of parameters that will be passed to the operation.

        :type cmdline: str
        :param cmdline: The command line.
        """
        self.create_main_parser()
        self.args, remaining = self.parser.parse_known_args(cmdline.split()[1:])
        self.service = self.session.get_service(self.args.service_name)
        output = self.args.output
        if output is None:
            output = self.session.get_variable('output')
        self.formatter = get_formatter(output, self.args)
        args = self.create_service_parser(remaining)
        params = {}
        self.build_call_parameters(args, params)
        return self.operation.build_parameters(**params)

    def main(self):
        self.create_main_parser()
        self.args, remaining = self.parser.parse_known_args()
        if self.args.service_name == 'help':
            provider = self.session.get_variable('provider')
            get_provider_help(provider=provider)
            return 0
        else:
            if self.args.debug:
                from six.moves import http_client
                http_client.HTTPConnection.debuglevel = 2
                self.session.set_debug_logger()
            output = self.args.output
            if output is None:
                output = self.session.get_variable('output')
            self.formatter = get_formatter(output, self.args)
            self.service = self.session.get_service(self.args.service_name)
            args = self.create_service_parser(remaining)
            return self.call(args)
