# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import sys
import subprocess

from acrylamid import log, __version__
from acrylamid.tasks import argument, task
from acrylamid.errors import AcrylamidException


@task('log', [argument("version", nargs=1, default=None)], help="show Acrylamid's changelog")
def run(conf, env, options):

    if options.version is None:
        options.version = 1

    try:
        # args stolen fron git source, see `man less`
        pager = subprocess.Popen(['less', '-F', '-R', '-S', '-X', '-K'], stdin=subprocess.PIPE, stdout=sys.stdout)
        for num in range(1000):
            pager.write('This is output line %s\n' % num)
        pager.stdin.close()
        pager.wait()
    except KeyboardInterrupt:
        # let less handle this, -K will exit cleanly
        pass
