import json
import sys

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from libthirty.logbook import LogBookHandler
from libthirty.exceptions import HttpReturnError
from thirtycli.utils import format_logbook_message


class LogbookAction(Action):
    """View the actions logbook."""
    ##
    # View logbook
    ##
    @utils.arg('uuid',
            default=None,
            metavar="<uuid>",
            help="The UUID of the logbook.")
    def do_logbook(self, args, global_args):
        """Poll the logbook for an action."""
        env.username = global_args.username
        env.password = global_args.password

        lbh = LogBookHandler(args.uuid)
        try:
            messages = lbh.fetch()
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e.args[0],
                    "message": e.args[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        if global_args.raw:
            sys.stdout.write(lbh.response.content)
        else:
            for msg in messages:
                sys.stdout.write(format_logbook_message(msg))
