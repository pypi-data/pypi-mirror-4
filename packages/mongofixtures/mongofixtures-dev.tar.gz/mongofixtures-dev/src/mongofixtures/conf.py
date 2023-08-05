# coding: utf-8


class Settings(object):
    BACKEND = 'mongofixtures.backend.PyMongoBackend'
    HOST = 'localhost'
    PORT = 27017
    DB = 'test'

SETTINGS = Settings()


def setup(settings):
    global SETTINGS
    for key, value in settings.iteritems():
        if hasattr(SETTINGS, key):
            setattr(SETTINGS, key, value)
