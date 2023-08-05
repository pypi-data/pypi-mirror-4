import json
import sys

from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.logs import LogsHandler
from libthirty.exceptions import HttpReturnError


class LogsAction(Action):
    """View the logs of your application."""

    @utils.arg('app',
            default=None,
            metavar='<app>',
            help='The name of the app.')
    @utils.arg('--process',
            default=None,
            help=("Specify the process to get the logs from "
                "(default: gunicorn,nginx)."))
    @utils.arg('--limit',
            default=None,
            help="The number of entries to return (default: 10).")
    def do_logs(self, args, global_args):
        """View the logs of your application."""
        params = {}
        if args.process:
            params['process'] = args.process
        if args.limit:
            params['limit'] = args.limit

        logs = LogsHandler(
                args.app,
                'app',
                **params)
        try:
            logs.fetch()
        except HttpReturnError as e:
            #FIXME: push this into its own formatting method
            error = {
                    "code": e[0],
                    "message": e[1]
                    }
            sys.stderr.write(json.dumps(error, indent=4))
            sys.stderr.flush()
            sys.exit(1)

        if global_args.raw:
            sys.stdout.write(logs.response.content)
        else:
            sys.stdout.write(utils._format_logoutput(
               json.loads(logs.response.content)))
