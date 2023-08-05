# Copyright (c) 2011-2012, 30loops.net
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of 30loops.net nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL 30loops.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Command line interface for the 30loops platform.
"""


import os
import sys
import re
from argparse import SUPPRESS
from argparse import ArgumentParser
import ConfigParser
from datetime import datetime, timedelta

from thirtycli import actions, utils
from libthirty.state import env


def ascii_art():
    art = """
    _____ _____ _                                    _
   |____ |  _  | |                                  | |
       / / |/' | | ___   ___  _ __  ___   _ __   ___| |_
       \ \  /| | |/ _ \ / _ \| '_ \/ __| | '_ \ / _ \ __|
   .___/ | |_/ / | (_) | (_) | |_) \__ \_| | | |  __/ |_
   \____/ \___/|_|\___/ \___/| .__/|___(_)_| |_|\___|\__|
                             | |
                             |_|
"""
    return art


class CommandError(Exception):
    pass


class CustomArgumentParser(ArgumentParser):
    """Override the default error method to hint more help to the user."""
    def error(self, message):
        if len(sys.argv) == 1:
            self.print_help()
        else:
            sys.stdout.write("Error: %s\n" % message)
            self.print_help()
        sys.exit(1)

    def print_help(self):
        ret = super(CustomArgumentParser, self).format_help()
        if hasattr(self, 'MANGLE_HELP'):
            p = re.compile(
                    '(?<=usage: thirty update )app|\
(?<=usage: thirty create )app|\
(?<=usage: thirty delete )app|\
(?<=usage: thirty runcmd )app|\
(?<=usage: thirty djangocmd )app|\
(?<=usage: thirty scale )app|\
app(?=.worker)|app(?=.mongodb)|app(?=.database)|app(?=.repository)|\
(?<=\s{4})app')
            ret = p.sub('<app>', ret)
        sys.stderr.write(ret)


class ThirtyCommandShell(object):
    """The shell command dispatcher."""
    subcommands = {}
    actioncommands = {}

    def get_base_parser(self):
        parser = CustomArgumentParser(
                prog="thirty",
                description=__doc__.strip(),
                epilog='See "thirty help COMMAND" \
for help on a specific command.',
                add_help=False
                )

        ###
        # Global arguments
        ###

        # Surpress the -h/--help command option
        parser.add_argument('-h', '--help',
            action='help',
            help=SUPPRESS)

        parser.add_argument("-u", "--username",
                action="store",
                metavar="<username>",
                help="The username that should be used for this request.")

        parser.add_argument("-p", "--password",
                action="store",
                metavar="<password>",
                help="The password to use for authenticating this request.")

        parser.add_argument("-a", "--account",
                action="store",
                metavar="<account>",
                help="The account that this user is a member of.")

        parser.add_argument("-r", "--uri",
                action="store",
                metavar="<uri>",
                default=env.base_uri,
                help=SUPPRESS)

        parser.add_argument("-i", "--api",
                action="store",
                metavar="<api>",
                default=env.api_version,
                help="The version of the api to use, defaults to 0.9.")

        parser.add_argument("-R", "--raw",
                action="store_true",
                default=False,
                help="Output raw JSON messages.")

        return parser

    def get_subcommand_parsers(self, parser, name):
        """Populate the subparsers."""
        parser.subcommands = {}
        subparsers = parser.add_subparsers(metavar="<%s>" % name, dest=name)
        return subparsers

    def _find_subcommands(self, subparsers):
        """Find all subcommand arguments."""
        # load for each subcommands the appropriate shell file
        for action in (a for a in dir(actions) if a.endswith('Action')):
            # make the commands have hyphens in place of underscores
            command = action[:-6].replace('_', '-').lower()
            callback = getattr(actions, action)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]

            subparser = subparsers.add_parser(command,
                    help=help,
                    add_help=False,
                    description=desc)

            self.subcommands[command] = subparser

    def _find_action_targets(self, subparsers, klass):
        """Find all action targets and create subparsers."""
        # load for each action the appropriate command methods
        instance = klass()
        for func in (a for a in dir(klass) if a.startswith('do_')):
            # make the commands have hyphens in place of underscores
            command = func[3:].replace('_', '.').lower()
            callback = getattr(instance, func)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]

            subparser = subparsers.add_parser(command,
                    help=help,
                    add_help=False,
                    description=desc)

            if hasattr(klass, 'RESOURCE_COMMAND'):
                setattr(subparser, 'MANGLE_HELP', None)

            if hasattr(callback, 'arguments'):
                for (args, kwargs) in callback.arguments:
                    subparser.add_argument(*args, **kwargs)

            self.actioncommands[command] = subparser

            subparser.set_defaults(func=callback)

    def get_action_parser(self, klass):
        """Get the parser for a specific action."""
        action = klass.__name__[:-6].lower()
        action_parser = CustomArgumentParser(
                prog='%s %s' % (self.parser.prog, action.lower()),
                description=klass.__doc__.strip(),
                epilog='See "thirty help %s" for more help.' %
                    action.lower(),
                add_help=False,
                )

        if hasattr(klass, 'positional'):
            # If the class defines a positional variable, we handle the class
            # with subparsers
            subparsers = self.get_subcommand_parsers(action_parser,
                    klass.positional)
            self._find_action_targets(subparsers, klass)
        else:
            # Otherwise assume that the class has only one action, and the
            # function to handle this action is named after the action
            instance = klass()
            func = getattr(instance, 'do_%s' % klass.__name__[:-6].lower())

            if hasattr(func, 'arguments'):
                for (args, kwargs) in func.arguments:
                    action_parser.add_argument(*args, **kwargs)

            action_parser.set_defaults(func=func)

        return action_parser

    def _add_help_command(self, subparsers):
        """Add the help action to the parser. We treat help special."""
        callback = getattr(self, 'do_help')
        desc = callback.__doc__ or ''
        help = desc.strip().split('\n')[0]

        subparser = subparsers.add_parser('help',
                help=help,
                add_help=False,
                description=desc)

        subparser.add_argument('-h', '--help',
            action='help',
            help=SUPPRESS,
        )

        for (args, kwargs) in callback.arguments:
            subparser.add_argument(*args, **kwargs)

        subparser.set_defaults(func=callback)

    def main(self, argv):
        """Entry point of the command shell."""
        defaults = {}

        # Before anything, we check for new versions
        now = datetime.now()
        try:
            with open(os.path.expanduser('~/.thirty.update')) as f:
                line = f.readline()
                d = datetime(*map(int, re.split('[^\d]', line)[:-1]))
                if d < (now - timedelta(days=14)):
                    raise IOError
        except IOError:
            with open(os.path.expanduser('~/.thirty.update'), 'w') as f:
                f.write(now.isoformat())
            utils.check_updates()

        # First read out file based configuration
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.thirty.cfg'))
        defaults = {}
        if config.has_section('thirtyloops'):
            for key, value in dict(config.items('thirtyloops')).iteritems():
                defaults[key] = value
        if config.has_section('defaults'):
            for key, value in dict(config.items('defaults')).iteritems():
                defaults[key] = value

        parser = self.get_base_parser()
        self.parser = parser

        # set the configfile as defaults
        parser.set_defaults(**defaults)

        # parse the main option and the action
        subparsers = self.get_subcommand_parsers(parser, 'action')
        self._find_subcommands(subparsers)
        self._add_help_command(subparsers)

        global_args, unknown = parser.parse_known_args(argv)

        # Handle the help before we actually parse the action targets
        if global_args.action == 'help':
            global_args.func(global_args)
            sys.exit(0)

        # Make sure that the required credentials are configured
        creds = ['account', 'username', 'password']
        for item in creds:
            if not getattr(global_args, item) and not global_args.action == 'setup':
                sys.stderr.write(('%s wasn\'t specified. Add it to '
                        'thirty.cfg or specify it as an argument.\n' % item))
                sys.exit(1)
            setattr(env, item, getattr(global_args, item))

        # Handle global arguments
        if global_args.uri:
            env.base_uri = global_args.uri
        if global_args.account:
            env.account = global_args.account
        if global_args.api:
            env.api_version = global_args.api

        # Parse the action relevant arguments
        try:
            klass = getattr(actions, '%sAction' %
                    global_args.action.capitalize())
        except AttributeError:
            raise CommandError("'%s' is not a valid action command" %
                global_args.action.resource)

        action_parser = self.get_action_parser(klass)

        # map appname --> app action
        if hasattr(klass, 'RESOURCE_COMMAND'):
            unknown = klass.map_app_name(unknown, action_parser)
            parser.MANGLE_HELP = True
            action_parser.MANGLE_HELP = True
        # Parse the rest of the argument, using the right subparser
        action_args = action_parser.parse_args(unknown)

        # Call the action method
        action_args.func(action_args, global_args)

    @utils.arg('command', metavar='<command>', nargs='?',
                    help='Display help for <command>.')
    @utils.arg('resource', metavar='<subcommand>', nargs='?',
                    help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display this help."""
        if args.command:
            if args.command in self.subcommands:
                # We add the action subparser here, otherwise we would
                # parse help as its own action class, and that will fail
                try:
                    klass = getattr(actions, '%sAction' %
                        args.command.capitalize())
                except AttributeError:
                    raise CommandError("'%s' is not a valid action command." %
                        args.command)

                if args.resource:
                    pos_arg = [args.resource]
                else:
                    pos_arg = []

                # We create a parser for this command, so that we have the full
                # help for this command available
                action_parser = self.get_action_parser(klass)

                if hasattr(klass, 'RESOURCE_COMMAND'):
                    pos_arg = klass.map_app_name(pos_arg, action_parser)
                    action_parser.MANGLE_HELP = True

                if pos_arg and hasattr(klass, 'positional'):
                    # We determined that this command is called with and action
                    # target. We check for the existence of the subparser and
                    # call its help method
                    if pos_arg[0] in self.actioncommands:
                        self.actioncommands[pos_arg[0]].print_help()
                    else:
                        raise CommandError(
                                "'%s' is not a valid action target." %
                            pos_arg[0])
                else:
                    action_parser.print_help()
            else:
                raise CommandError("'%s' is not a valid action command." %
                    args.command)
        else:
            print(ascii_art())
            self.parser.print_help()


def main():
    try:
        ThirtyCommandShell().main(sys.argv[1:])
    except Exception as e:
        print >> sys.stderr, e
        sys.exit(1)
