# -*- coding: utf-8 -*-
import os
import logging

import mongokit

from pyramid.events import NewRequest

from zope.interface import implementer
from zope.interface import Interface

log = logging.getLogger(__name__)

__all__ = ['register_document', 'mongo_db', 'mongo_connection',
           'IMongoConnection']


def includeme(config):
    log.info('Configure mongo...')
    if 'MONGO_DB_NAME' not in os.environ:
        raise KeyError('No MONGO_DB_NAME os.environ.')
    connection = MongoConnection(
        os.environ['MONGO_URI'],
        auto_start_request=False,
        tz_aware=True,
        )
    config.registry.registerUtility(connection)
    config.add_request_method(
        mongo_connection,
        'mongo_connection',
        reify=True,
        )
    config.add_request_method(mongo_db, 'mongo_db', reify=True)
    config.add_subscriber(begin_request, NewRequest)
    log.info('Mongo configured...')


def register_document(registry, document_cls):
    registry.getUtility(IMongoConnection).register(document_cls)


class IMongoConnection(Interface):
    pass


@implementer(IMongoConnection)
class MongoConnection(mongokit.Connection):
    pass


def mongo_connection(request):
    return request.registry.getUtility(IMongoConnection)


def mongo_db(request):
    return getattr(request.mongo_connection, os.environ['MONGO_DB_NAME'])


def begin_request(event):
    event.request.mongo_connection.start_request()
    event.request.add_finished_callback(end_request)


def end_request(request):
    request.mongo_connection.end_request()
