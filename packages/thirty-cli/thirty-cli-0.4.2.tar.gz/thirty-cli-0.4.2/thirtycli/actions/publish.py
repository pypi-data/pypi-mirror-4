from thirtycli.actions.common import Action
from thirtycli import utils


class PublishAction(Action):
    """Publish an app."""

    ##
    # Publish an application
    ##
    @utils.arg('app',
        metavar="<app>",
        help="The app to publish.")
    def do_publish(self, args, global_args):
        """Publish an app (upgrade to paid)."""
        cmd = {
                'action': 'publish',
                }
        args.appname = args.app
        args.service = None

        self._run_command(args, global_args, cmd)
