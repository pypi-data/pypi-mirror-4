from thirtycli.actions.common import Action
from thirtycli import utils

class UsageAction(Action):
    """Show the usage of a resource"""

    RESOURCE_COMMAND = True

    ##
    # Show resources
    ##
    @utils.arg('resource',
            metavar="<resource>",
            help="The resource to show")
    def do_usage(self, args, global_args):
        """Show the usage of a resource"""

        self._show_usage(args, global_args)
