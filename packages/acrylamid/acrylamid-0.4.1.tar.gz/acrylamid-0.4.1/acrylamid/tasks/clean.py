# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import os

from os.path import join

from acrylamid import log, commands, readers
from acrylamid.tasks import task, argument
from acrylamid.helpers import event

tracked = set([])

arguments = [
    argument("-f", "--force", action="store_true", dest="force",
             help="remove all files generated by Acrylamid", default=False),
    argument("-n", "--dry-run", dest="dryrun", action='store_true',
             help="show what would have been deleted", default=False)
]


def track(path, **kw):
    global tracked
    tracked.add(path)


@task(['clean', 'rm'], arguments, help="remove abandoned files")
def run(conf, env, options):
    """Attention: this function may eat your data!  Every create, changed
    or skip event call tracks automatically files. After generation,
    ``acrylamid clean`` will call this function and remove untracked files.

    - with OUTPUT_IGNORE you can specify a list of patterns which are ignored.
    - you can use --dry-run to see what would have been removed
    - by default acrylamid does NOT call this function
    - it removes silently every empty directory

    :param conf: user configuration
    :param env: acrylamid environment
    :param force: remove all tracked files, too
    :param dryrun: don't delete, just show what would have been done
    """
    force=options.force
    dryrun=options.dryrun

    # we don't bother the user here
    log.setLevel(env.options.verbosity+5)
    env.options.ignore = True

    # register our track function to events
    event.register(track, to=['create', 'update', 'skip', 'identical'])

    # run a silent compile
    commands.compile(conf, env, dryrun=True, force=False)

    log.setLevel(env.options.verbosity)

    global tracked
    for root, dirs, files in os.walk(conf['output_dir'], topdown=True):
        found = set([join(root, p) for p in files
                     if not readers.ignored(root, p, conf['output_ignore'], conf['output_dir'])])

        for p in found.difference(tracked):
            if not dryrun:
                os.remove(p)
            event.remove(p)

        if force:
            for p in found.intersection(tracked):
                if not dryrun:
                    os.remove(p)
                event.remove(p)

        # don't visit excluded dirs
        for dir in dirs[:]:
            if readers.ignored(root, dir+'/', conf['output_ignore'], conf['output_dir']):
                dirs.remove(dir)

    # remove empty directories
    for root, dirs, files in os.walk(conf['output_dir'], topdown=True):
        for p in (join(root, k) for k in dirs):
            try:
                os.rmdir(p)
            except OSError:
                pass
