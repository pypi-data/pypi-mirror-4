# coding: utf-8
from pymongo import Connection

from mongofixtures import conf


class PyMongoBackend(object):
    def __init__(self):
        self.settings = conf.SETTINGS
        self.connect()

    def connect(self):
        connection = Connection(self.settings.HOST, self.settings.PORT)
        self.db = connection[self.settings.DB]

    def insert(self, collection, documents):
        self.db[collection].insert(documents)

    def empty(self, collection):
        self.db[collection].drop()
