# coding: utf-8
import json

from bson import json_util

from mongofixtures.conf import SETTINGS


class FixtureMixin(object):
    # Must be overriden from subclasses
    FIXTURES = None

    _COLLECTIONS_LOADED = set()

    def fixtures_load(self):
        assert self.FIXTURES is not None, "Attribute FIXTURES should be defined"
        self._load_backend_module()

        for fixture in self.FIXTURES:
            data = self._load_fixture_data(fixture)
            for collection, documents in data.iteritems():
                self._COLLECTIONS_LOADED.add(collection)
                self.db.insert(collection, documents)

    def fixtures_cleanup(self):
        for collection in self._COLLECTIONS_LOADED:
            self.db.empty(collection)

    def _load_fixture_data(self, filename):
        content = open(filename, 'rb').read()
        return json.loads(content, object_hook=json_util.object_hook)

    def _load_backend_module(self):
        assert hasattr(SETTINGS, 'BACKEND'), "Missing BACKEND configuration"

        temp = SETTINGS.BACKEND.split('.')
        backend_module = __import__('.'.join(temp[:-1]), globals(), locals(), [temp[-1]])
        backend = getattr(backend_module, temp[-1])
        self.db = backend()
