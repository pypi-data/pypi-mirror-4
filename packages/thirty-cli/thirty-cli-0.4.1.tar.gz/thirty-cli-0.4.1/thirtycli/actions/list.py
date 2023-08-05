from thirtycli.actions.common import Action
from libthirty.app import AppManager
from libthirty.exceptions import HttpReturnError
# from docar.fields import ForeignDocument


class ListAction(Action):
    """List apps."""

    ##
    # List app resources
    ##
    def do_list(self, args, global_args):
        """List all application resources."""
        self._output_formatter(global_args)

        rm = AppManager()

        try:
            rm.list()
        except HttpReturnError as e:
            self.out.error(e)
            sys.exit(1)

        # FIXME: The formatting should not happen here I guess
        for item in rm._collection.collection_set:
            self.out.info(item.name)
