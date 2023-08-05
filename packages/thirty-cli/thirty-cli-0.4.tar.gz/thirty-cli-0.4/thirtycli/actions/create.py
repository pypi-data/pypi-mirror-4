import sys
import json

from thirtycli import utils
from thirtycli.actions.common import Action
from docar.exceptions import HttpBackendError, BackendDoesNotExist
from libthirty.state import env


class CreateAction(Action):
    """Create a new resource."""
    positional = 'resource'

    RESOURCE_COMMAND = True

    #     return resource
    ##
    # Create an application
    ##
    @utils.arg('location',
            metavar="<location>",
            help="This is the URI of the repository that will be used for this app.")
    @utils.arg('--cname',
            default=None,
            action="append",
            help="Connect a CNAME record to this app. Specify multiple times if needed.")
    @utils.arg('--region',
            default=None,
            help="The region of this app (defaults to ams1).")
    @utils.arg('--instances',
            default=1,
            type=int,
            help="The number of instances to deploy your app on.")
    @utils.arg('--variant',
            default='python',
            help="The variant of this app (default: python).")
    def do_app(self, args, global_args):
        """Create a new app."""
        App = utils._get_document("App")
        app = App({'name': args.appname})

        env.appname = app.name

        app.instances = args.instances

        if args.cname:
            Cname = utils._get_document('CnameRecord')
            for c in args.cname:
                cname = Cname({'record': c})
                app.cnames.add(cname)

        if args.location:
            app.repository.location = args.location
            app.repository.variant = "git"
            app.repository.name = args.appname
        else:
            sys.stderr.write("You have to specify a location or an existing repository")
            sys.exit(1)

        if args.region:
            app.region = args.region

        if args.variant:
            app.variant = args.variant

        self._create_resource(args, global_args, app)

    ##
    # Create a worker
    ##
    @utils.arg('--instances',
            default=1,
            help="The number of worker instances to deploy.")
    def do_app_worker(self, args, global_args):
        """Create a new worker."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        env.appname = app.name
        env.service = args.service

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except (BackendDoesNotExist, HttpBackendError) as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        Worker = utils._get_document("Worker")
        worker = Worker({'name': args.appname})
        worker.region = app.region

        if args.instances:
            worker.instances = args.instances

        # app.worker = worker
        self._update_resource(args, global_args, worker)

    ##
    # Create a mongodb database
    ##
    def do_app_mongodb(self, args, global_args):
        """Create a new mongodb database."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        env.appname = app.name
        env.service = args.service

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except (BackendDoesNotExist, HttpBackendError) as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        Mongodb = utils._get_document(args.service.capitalize())
        mongodb = Mongodb({'name': args.appname})

        # app.mongodb = mongodb
        self._update_resource(args, global_args, mongodb)

    ##
    # Create a postgresql database
    ##
    @utils.arg('--variant',
        default='postgres_micro',
        help="The variant of this database (default: postgres_micro).")
    @utils.arg('--template',
        default='template1',
        help="The template to create this database from (default: template1).")
    def do_app_postgres(self, args, global_args):
        """Create a new postgresql database."""
        if global_args.raw:
            out = utils.RawOutputFormatter()
        else:
            out = utils.ResourceOutputFormatter()

        App = utils._get_document("App")
        app = App({'name': args.appname})

        env.appname = app.name
        env.service = args.service

        try:
            app.fetch(username=global_args.username, password=global_args.password)
        except (BackendDoesNotExist, HttpBackendError) as e:
            out.error(json.loads(e[1]))
            sys.exit(1)

        Postgres = utils._get_document(args.service.capitalize())
        postgres = Postgres({'name': args.appname})

        # app.postgres = postgres
        self._update_resource(args, global_args, postgres)
