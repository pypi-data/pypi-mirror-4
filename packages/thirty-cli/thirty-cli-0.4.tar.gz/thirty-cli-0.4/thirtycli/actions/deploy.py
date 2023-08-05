from thirtycli.actions.common import Action
from thirtycli import utils


class DeployAction(Action):
    """Deploy an app."""

    ##
    # Deploy app resources
    ##
    @utils.arg('app',
            metavar="<app>",
            help="The name of the app to deploy.")
    @utils.arg('--clean',
            '-c',
            action='store_true',
            help=("Do a clean deploy. This installs fresh from scratch, "
                "but is a bit slower."))
    def do_deploy(self, args, global_args):
        """Deploy an app."""
        cmd = {'action': 'deploy'}

        if args.clean:
            cmd['options'] = {'clean': True}

        args.appname = args.app
        args.service = None

        self._run_command(args, global_args, cmd)
