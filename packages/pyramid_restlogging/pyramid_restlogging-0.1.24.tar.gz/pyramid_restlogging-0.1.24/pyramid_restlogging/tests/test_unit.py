# -*- coding: utf-8 -*-
import unittest

import mock
from pyramid.testing import DummyRequest


class TestIncludeme(unittest.TestCase):

    def test_basic(self):
        from pyramid_restlogging import includeme
        config = mock.Mock()

        includeme(config)

        config.add_route.assert_called_with('clientlogs', mock.ANY,
                                            request_method='POST')
        config.scan.assert_called_with('pyramid_restlogging.views')
        config.commit.assert_called_with()


class TestLogView(unittest.TestCase):

    def test_nominal_case(self):
        from pyramid_restlogging.views import log_view
        req = DummyRequest()
        req.matchdict = {
            'logger_name': 'com.ludia:Application',
            'log_level': 'debug',
            }
        req.body = 'beware of the dog.'

        log_view(req)
