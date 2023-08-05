from thirtycli.actions.common import Action

import sys
import os
import getpass
import ConfigParser


class SetupAction(Action):
    """Setup the client credentials."""

    ##
    # Setup the client configuration
    ##
    def do_setup(self, args, global_args):
        """Setup of the client credentials."""
        configfile = os.path.expanduser('~/.thirty.cfg')
        config = ConfigParser.ConfigParser()
        config.read(configfile)
        if config.has_section('thirtyloops'):
            sys.stderr.write(
            "Configuration file already exists. If you want to rerun "
            "the setup, please remove {0} first.".format(configfile))
            exit(1)
        account = raw_input("Please enter your accountname: ")
        username = raw_input("Please enter your username: ")
        password = getpass.getpass()

        config.add_section('thirtyloops')
        config.set('thirtyloops', 'account', account)
        config.set('thirtyloops', 'username', username)
        config.set('thirtyloops', 'password', password)

        with open(configfile, 'w') as output:
            config.write(output)

        sys.stdout.write("The configuration file has been created. You can now use the client.")
