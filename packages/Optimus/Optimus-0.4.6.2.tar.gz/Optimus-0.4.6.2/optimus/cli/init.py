# -*- coding: utf-8 -*-
"""
Command line actions
"""
import datetime, logging, os, time

from argh import arg, CommandError

from optimus.conf import import_project_module
from optimus.logs import init_logging
from optimus.utils import initialize, display_settings
from optimus.start_project import ProjectStarter

@arg('-l', '--loglevel', default='info', choices=['debug','info','warning','error','critical'], help="The minimal verbosity level to limit logs output")
@arg('-n', '--name', default=None, help="Project's name to use, must be a valid python module name") # TODO: required
@arg('--logfile', default=None, help="A filepath that if setted, will be used to save logs output")
@arg('-t', '--template', default="optimus.defaults", help="A python path to a 'project template' module to use instead of the default one 'optimus.defaults'.") # TODO: required
@arg('--dry-run', default=False, help="Dry run mode will perform all processus but will not create or modify anything")
def init(args):
    """
    The init action for the commandline
    """
    starttime = datetime.datetime.now()
    # Init, load and builds
    root_logger = init_logging(args.loglevel.upper(), logfile=args.logfile)
    
    if not args.name:
        raise CommandError("'name' argument is required")
    
    if args.dry_run:
        root_logger.warning("'Dry run' mode enabled")
    
    # TODO: optionnal command option
    project_directory = os.path.abspath(os.getcwd())

    loader = ProjectStarter(project_directory, args.name, dry_run=args.dry_run)
    loader.install("optimus.defaults")
    
    endtime = datetime.datetime.now()
    root_logger.info('Done in %s', str(endtime-starttime))
