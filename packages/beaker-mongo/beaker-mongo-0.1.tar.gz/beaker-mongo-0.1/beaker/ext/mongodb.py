# -*- coding: utf-8 -*-
import logging
from beaker.util import verify_directory, SyncDict
from beaker.container import OpenResourceNamespaceManager, Container
from beaker.exceptions import InvalidCacheBackendError
from beaker.synchronization import null_synchronizer

try:
    import cPickle as pickle
except ImportError:
    import pickle


log = logging.getLogger(__name__)

MongoReplicaSetClient = None
MongoClient = None
parse_uri = None
bson = None


class MongoDBNamespaceManager(OpenResourceNamespaceManager):
    collections = SyncDict()
    _pickle = True
    _sparse = False

    @classmethod
    def _init_dependencies(cls):
        """Initialize module-level dependent libraries required
        by this :class:`.NamespaceManager`."""
        global MongoClient, MongoReplicaSetClient, parse_uri, bson
        try:
            from pymongo import MongoClient, MongoReplicaSetClient
            from pymongo.uri_parser import parse_uri
            import bson
        except ImportError:
            raise InvalidCacheBackendError("MongoDB cache backend requires the 'pymongo' driver")

    def __init__(self, namespace, uri=None, collection=None, **params):
        super(MongoDBNamespaceManager, self).__init__(namespace)

        if not uri:
            raise InvalidCacheBackendError("MongoDB uri is required")

        uri_params = parse_uri(uri)
        if not len(uri_params['nodelist']):
            raise InvalidCacheBackendError("mongodb hostname and port not configured")

        db_name = uri_params['database']
        if not db_name:
            raise InvalidCacheBackendError("mongodb database name not configured")

        collection_name = collection or uri_params['collection'] or 'beaker'

        options = uri_params['options']
        options.update(dict([(key[8:], params[key]) for key in params if key.startswith('mongodb.')]))

        def make_cache():
            if len(uri_params['nodelist']) > 1:
                client = MongoReplicaSetClient(uri_params['nodelist'], **options)
            else:
                client = MongoClient(uri_params['nodelist'][0][0], uri_params['nodelist'][0][1], **options)

            db = client[db_name]
            if uri_params['username']:
                if not db.authenticate(uri_params['username'], uri_params['password']):
                    raise InvalidCacheBackendError('Cannot authenticate to MongoDB for user: %s' %
                                                   uri_params['username'])
            return db[collection_name]

        self.cache = MongoDBNamespaceManager.collections.get(collection_name, make_cache)
        self.hash = {}
        self._is_new = False
        self.loaded = False
        self.log_debug = logging.DEBUG >= log.getEffectiveLevel()

    def get_access_lock(self):
        return null_synchronizer()

    def get_creation_lock(self, key):
        # this is weird, should probably be present
        return null_synchronizer()

    def do_open(self, flags, replace):
        # If we already loaded the data, don't bother loading it again
        if self.loaded:
            self.flags = flags
            return

        item = self.cache.find_one({'_id': self.namespace})

        if not item:
            self._is_new = True
            self.hash = {}
        else:
            self._is_new = False
            try:
                self.hash = pickle.loads(item['data'].encode('utf-8'))
            except (IOError, OSError, EOFError, pickle.PickleError):
                if self.log_debug:
                    log.debug("Couln't load pickle data, creating new storage")
                self.hash = {}
                self._is_new = True
        self.flags = flags
        self.loaded = True

    def do_close(self):
        if self.flags is not None and (self.flags == 'c' or self.flags == 'w'):
            data =  {
                'data': pickle.dumps(self.hash),
            }
            self.cache.update({"_id": self.namespace}, {'$set': data}, upsert=True, safe=True)
            if self._is_new:
                self._is_new = False
        self.flags = None

    def do_remove(self):
        log.debug('MongoDB backend remove namespace: %s' % self.namespace)
        self.cache.remove({'_id': self.namespace})
        self.hash = {}

        # We can retain the fact that we did a load attempt, but since the
        # file is gone this will be a new namespace should it be saved.
        self._is_new = True

    def __getitem__(self, key):
        return self.hash[key]

    def __contains__(self, key):
        return key in self.hash

    def __setitem__(self, key, value):
        self.hash[key] = value

    def __delitem__(self, key):
        del self.hash[key]

    def keys(self):
        return self.hash.keys()


class MongoDBContainer(Container):
    namespace_manager = MongoDBNamespaceManager
