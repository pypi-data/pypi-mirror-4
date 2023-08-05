# -*- coding: utf-8 -*-
import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk

log = logging.getLogger(__name__)


@view_config(route_name='clientlogs')
def log_view(request):
    try:
        # TODO use the 'ignore' or 'replace' error handler
        # XXX check if Pyramid does not already decode
        message = unicode(request.body, request.charset)
    except UnicodeDecodeError:
        message = request.body
    logger_name = request.matchdict['logger_name']
    log_level = request.matchdict['log_level']
    logger = logging.getLogger(logger_name)
    # checking for valid log level is already done by the route
    getattr(logger, log_level)(message)
    return HTTPOk()
