from thirtycli.actions.common import Action


class RestartAction(Action):
    """Restart processes."""
    positional = 'resource'
    RESOURCE_COMMAND = True

    ##
    # Restart processes
    ##
    def do_app(self, args, global_args):
        """Restart all app processes."""
        cmd = {'action': 'restart'}

        self._run_command(args, global_args, cmd)

    ##
    # Scale worker instances
    ##
    def do_app_worker(self, args, global_args):
        """Restart all worker processes."""
        cmd = {'action': 'restart'}

        self._run_command(args, global_args, cmd)
