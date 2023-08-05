# -*- coding: utf-8 -*-
import unittest
from requests_proxy import Proxy
from webtest import TestApp
from webtest.debugapp import debug_app
from webtest.http import StopableWSGIServer


class TestProxy(unittest.TestCase):

    def setUp(self):
        self.server = StopableWSGIServer.create(debug_app)
        self.app = TestApp(Proxy(self.server.application_url))

    def test_form(self):
        resp = self.app.get('/form.html')
        resp.mustcontain('</form>')
        form = resp.form
        form['name'] = 'gawel'
        resp = form.submit()
        resp.mustcontain('name=gawel')

    def test_status(self):
        resp = self.app.get('/?status=404', status='*')
        self.assertEqual(resp.status_int, 404)

    def tearDown(self):
        self.server.shutdown()
