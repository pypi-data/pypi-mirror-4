##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.testing import setupstack
import doctest
import mock
import unittest

def side_effect(m):
    return lambda f: setattr(m, 'side_effect', f)

def setup(test):
    setupstack.context_manager(test, mock.patch('sys.argv'))

    @side_effect(
        setupstack.context_manager(test, mock.patch('subprocess.call')))
    def call(args):
        args = args[:]
        cname = args[1][4:]
        args[1] = args[1][:4]+'CFG'
        print 'called:', ' '.join(args)
        print 'CFG:'
        print '-'*60
        with open(cname) as f:
            cfg = f.read()
        print cfg,
        print '-'*60
        return ('BAD' in cfg) and 41 or 0

    @side_effect(setupstack.context_manager(test, mock.patch('sys.exit')))
    def exit(e):
        print 'sys.exit(%r)' % e
    test.globs['side_effect'] = side_effect

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.test',
            setUp=setup, tearDown=setupstack.tearDown,
            ),
        ))

