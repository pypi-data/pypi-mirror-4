from thirtycli.actions.common import Action
from thirtycli import utils
from argparse import REMAINDER


class DjangocmdAction(Action):
    """Run a Django management command."""
    positional = 'resource'
    RESOURCE_COMMAND = True

    ##
    # run a Django command on an app
    ##
    @utils.arg('command',
            default=None,
            nargs=REMAINDER,
            metavar="<command>",
            help="Command to run.")
    @utils.arg('--occurrence',
            default=1,
            help=('Number of app instances to run the command on '
                '(use "all" for all instances)'),
            type=utils.occurrence)
    def do_app(self, args, global_args):
        """Run a Django command on one or more app instances."""
        cmd = {'action': 'djangocommand', 'options': {}}
        cmd['options']['command'] = " ".join(args.command)
        cmd['options']['occurrence'] = args.occurrence

        self._run_command(args, global_args, cmd)

    ##
    # run a Django command on a worker
    ##
    @utils.arg('command',
            default=None,
            nargs=REMAINDER,
            metavar="<command>",
            help="Command to run.")
    @utils.arg('--occurrence',
            default=1,
            help=('Number of worker instances to run the command on '
                '(use "all" for all instances)'),
            type=utils.occurrence)
    def do_app_worker(self, args, global_args):
        """Run a Django command on one or more worker instances."""
        cmd = {'action': 'djangocommand', 'options': {}}
        cmd['options']['command'] = " ".join(args.command)
        cmd['options']['occurrence'] = args.occurrence

        self._run_command(args, global_args, cmd)
