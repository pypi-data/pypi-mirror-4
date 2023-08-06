##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
import tempfile
import unittest
import z3c.layer.pagelet.testing


class SystemErrorTests(unittest.TestCase):

    layer = z3c.layer.pagelet.testing.TestLayer

    def setUp(self):
        fd, self.zcml_file = tempfile.mkstemp('.zcml')
        zcml = os.fdopen(fd, 'w')
        zcml.write('''<configure />''')
        zcml.close()

    def tearDown(self):
        from zope.app.appsetup import appsetup
        os.unlink(self.zcml_file)
        appsetup.reset()

    def callVUT(self):
        from z3c.layer.pagelet.browser import SystemErrorPagelet
        from zope.publisher.browser import TestRequest
        view = SystemErrorPagelet(None, TestRequest())
        view.update()
        return view

    def test_does_not_set_HTTP_500_if_devmode_is_not_set(self):
        from zope.app.appsetup import appsetup
        appsetup.config(self.zcml_file, ())
        view = self.callVUT()
        self.assertEqual(599, view.request.response.getStatus())

    def test_sets_HTTP_500_if_config_context_is_empty(self):
        view = self.callVUT()
        self.assertEqual(500, view.request.response.getStatus())

    def test_sets_HTTP_500_if_devmode_is_set(self):
        from zope.app.appsetup import appsetup
        appsetup.config(self.zcml_file, ('devmode',))
        view = self.callVUT()
        self.assertEqual(500, view.request.response.getStatus())

