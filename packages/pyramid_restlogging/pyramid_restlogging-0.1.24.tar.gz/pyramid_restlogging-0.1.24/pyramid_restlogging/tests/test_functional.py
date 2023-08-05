# encoding: utf-8
import unittest

import webtest


class TestLogView(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        from pyramid_restlogging import main
        self.app = webtest.TestApp(main(None))

    def test_basic(self):
        body = 'Error: no more spam'
        self.app.post('/clientlogs/spam/error', body, status=200)

    def test_wrong_encoding(self):
        body = u'Unknown user: Éric'.encode('latin-1')
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        self.app.post('/clientlogs/spam/error', body, headers, status=200)

    def test_invalid_loglevel(self):
        body = 'Error: too much ham'
        self.app.post('/clientlogs/spam/impossible', body, status=404)
