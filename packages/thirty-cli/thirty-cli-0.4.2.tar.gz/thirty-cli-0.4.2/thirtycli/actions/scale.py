from thirtycli.actions.common import Action
from thirtycli import utils


class ScaleAction(Action):
    """Scale a resource."""
    positional = 'resource'
    RESOURCE_COMMAND = True

    ##
    # Scale app instances
    ##
    @utils.arg('instances',
            type=int,
            default=None,
            metavar='<instances>',
            help=("Number of app instances to scale to. This is the final "
                 "number of app instances."))
    def do_app(self, args, global_args):
        """Scale the number of app instances."""
        cmd = {
                'action': 'scale',
                'options': {
                    'instances': args.instances
                    }
                }

        self._run_command(args, global_args, cmd)

    ##
    # Scale worker instances
    ##
    @utils.arg('instances',
            type=int,
            default=None,
            metavar='<instances>',
            help=("Number of worker instances to scale to. This is the final "
                "number of worker instances."))
    def do_app_worker(self, args, global_args):
        """Scale the number of worker instances."""
        cmd = {
                'action': 'scale',
                'options': {
                    'instances': args.instances
                    }
                }

        self._run_command(args, global_args, cmd)
