from thirtycli.actions.common import Action
from thirtycli import utils


class RestoreAction(Action):
    """Restore a database from a dump."""
    positional = 'resource'
    RESOURCE_COMMAND = True

    ##
    # Deploy app resources
    ##
    @utils.arg('location',
            metavar='<location>',
            help=("The location that contains the dump of the database."))
    def do_app_postgres(self, args, global_args):
        """Restore a postgres database from a dump."""
        cmd = {'action': 'restore', 'options': {}}
        cmd['options']['location'] = args.location

        self._restore(args, global_args, cmd)
