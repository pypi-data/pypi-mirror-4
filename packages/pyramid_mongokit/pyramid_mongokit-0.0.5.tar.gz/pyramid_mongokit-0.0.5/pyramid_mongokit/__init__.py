# -*- coding: utf-8 -*-
import os
import logging

import mongokit

from pyramid.decorator import reify
from pyramid.events import NewRequest

from zope.interface import Interface, implementer

log = logging.getLogger(__name__)

__all__ = ['register_document', 'generate_index', 'get_mongo_connection']


def includeme(config):
    log.info('Configure mongokit connection...')
    db_prefix = os.environ.get('MONGO_DB_PREFIX', '')

    if 'MONGO_DB_NAME' in os.environ:
        connection = SingleDbConnection(
            os.environ['MONGO_DB_NAME'],
            db_prefix,
            '%s' % os.environ['MONGO_URI'],
            auto_start_request=False,
            tz_aware=True,
            )
        config.add_request_method(mongo_db, 'mongo_db', reify=True)
    else:
        connection = MongoConnection(
            db_prefix,
            os.environ['MONGO_URI'],
            auto_start_request=False,
            tz_aware=True,
            )
        config.add_request_method(mongo_db, 'get_mongo_db')

    config.registry.registerUtility(connection)

    config.add_request_method(mongo_connection, 'mongo_connection',
                              reify=True)

    config.add_subscriber(begin_request, NewRequest)
    log.info('Mongo connection configured...')


class IMongoConnection(Interface):
    pass


@implementer(IMongoConnection)
class MongoConnection(mongokit.Connection):

    def __init__(self, db_prefix, *args, **kwargs):
        super(MongoConnection, self).__init__(*args, **kwargs)
        self.db_prefix = db_prefix

    def get_db(self, db_name=None):
        return getattr(self, '%s%s' % (self.db_prefix, db_name))

    def generate_index(self, document_cls, db_name=None, collection=None):
        collection = collection if collection else document_cls.__collection__
        document_cls.generate_index(self.get_db(db_name)[collection])


@implementer(IMongoConnection)
class SingleDbConnection(MongoConnection):

    def __init__(self, db_name, db_prefix, *args, **kwargs):
        super(SingleDbConnection, self).__init__(db_prefix, *args, **kwargs)
        self.db_name = db_name

    @reify
    def db(self):
        return self.get_db(self.db_name)

    def get_db(self, db_name=None):
        return super(SingleDbConnection, self).get_db(self.db_name)

    def generate_index(self, document_cls, db_name=None, collection=None):
        super(SingleDbConnection, self).generate_index(document_cls,
                                                       self.db_name,
                                                       collection)


def generate_index(registry, document_cls, db_name='', collection=None):
    mongo_connection = get_mongo_connection(registry)
    mongo_connection.generate_index(document_cls, db_name=db_name,
                                    collection=collection)


def register_document(registry, document_cls):
    mongo_connection = get_mongo_connection(registry)
    mongo_connection.register(document_cls)


def get_mongo_connection(registry):
    return registry.getUtility(IMongoConnection)


def mongo_connection(request):
    return get_mongo_connection(request.registry)


def mongo_db(request, db_name=False):
    conn = request.mongo_connection
    if db_name:
        return conn.get_db(db_name)
    return conn.db


def begin_request(event):
    event.request.mongo_connection.start_request()
    event.request.add_finished_callback(end_request)


def end_request(request):
    request.mongo_connection.end_request()
