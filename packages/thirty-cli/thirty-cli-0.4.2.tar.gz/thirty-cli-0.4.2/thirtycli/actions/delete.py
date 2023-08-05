from thirtycli.actions.common import Action


class DeleteAction(Action):
    """Delete a resource."""
    RESOURCE_COMMAND = True
    positional = 'resource'

    ##
    # Delete resources
    ##
    def do_app(self, args, global_args):
        """Delete an app."""

        self._delete_resource(args, global_args)

    def do_app_worker(self, args, global_args):
        """Delete a worker."""

        self._delete_resource(args, global_args)

    def do_app_mongodb(self, args, global_args):
        """Delete a MongoDB database."""

        self._delete_resource(args, global_args)

    def do_app_postgres(self, args, global_args):
        """Delete a PostgreSQL database."""

        self._delete_resource(args, global_args)

    def do_app_repository(self, args, global_args):
        """Delete a repository."""

        self._delete_resource(args, global_args)
