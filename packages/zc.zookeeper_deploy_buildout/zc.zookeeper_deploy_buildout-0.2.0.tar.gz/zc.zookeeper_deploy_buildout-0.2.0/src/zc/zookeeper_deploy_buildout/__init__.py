##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import subprocess
import sys
import tempfile

install_template = """\
[buildout]
directory = %(directory)s
installed = %(installed)s
parts = %(part)s
[%(part)s]
recipe = %(recipe)s
"""

uninstall_template = """\
[buildout]
directory = %(directory)s
installed = %(installed)s
parts =
"""

def main(app, recipe, *extra):
    if not app:
        app = os.path.basename(os.path.dirname(os.path.dirname(sys.argv[0])))
    args = sys.argv[1:]
    template = install_template
    if args[0] == '-u':
        template = uninstall_template
        args.pop(0)
    elif args[0] == '-r':
        args.pop(0)
        if ':' in recipe:
            print "-r isn't allowed for this script"
            sys.exit(1)
        recipe += ':'+args.pop(0)

    path = args.pop(0)
    n = args.pop(0)
    directory = os.path.dirname(os.path.dirname(sys.argv[0]))
    part = '%s.%s' % (path[1:].replace('/', ','), n)
    fd, cpath = tempfile.mkstemp('.cfg')
    os.write(fd, template % dict(
        directory = directory,
        installed = '/etc/%s/%s.deployed' % (app, part),
        part = part,
        recipe = recipe,
        ))
    os.close(fd)

    sys.exit(
        subprocess.call(
            ['%s/bin/buildout' % directory, '-oUc'+cpath] + list(extra) + args
            )
        )
