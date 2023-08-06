"""A LRUish cache / disk backed  (via a database) dictionary
implementation


TODO:
shelve OR sqlite3
document backend requirements
finish LRU option
"""

import collections
import os
import shutil
import sys
import time

# for SqliteBackend
try:
    import cPickle as pickle
except ImportError:
    import pickle
import sqlite3


IS_WIN = sys.platform == 'win32'


class SqliteBackend(object):
    """Stole the query / update scheme from Erez Shinan's filedict project.
    Thanks!
    """

    def __init__(self, db_file=None, db_table='sql_dict_table',
        unlink_old_db=False):
        """Create the db and tables"""
        # TODO: this should handle the file creation more gracefully.
        if db_file is None:
            db_file = 'db_file_{0}.dict'.format(int(time.time()))
        if unlink_old_db and os.path.exists(db_file):
            os.unlink(db_file)
        self._db_file = db_file
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.table = db_table
        self.conn.execute('create table if not exists {0} (id integer primary '
            'key, hash integer, key blob, value blob);'.format(self.table))
        self.conn.execute(
            'create index if not exists {0}_index ON {0}(hash);'.format(
                self.table, self.table))
        self.conn.commit()
        self._commit_needed = False

    def _get_key_id(self, key):
        """The indirection allows for hash collisions needed for add and
        delete -- makes contains a bit faster"""
        cursor = self.conn.execute(
            'select key,id from {0} where hash=?;'.format(self.table),
            (hash(key), ))
        for k, key_id in cursor:
            if self._load(k) == key:
                return key_id
        # not in the db
        raise KeyError(key)

    def __getitem__(self, key):
        cursor = self.conn.execute(
            'select key,value from {0} where hash=?;'.format(self.table),
            (hash(key), ))
        for k, v in cursor:
            if self._load(k) == key:
                return self._load(v)
        # not in the db
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._insert(key, value)
        self.commit()

    def __delitem__(self, key):
        db_id = self._get_key_id(key)
        self.conn.execute('delete from {0} where id=?;'.format(
            self.table), (db_id,))
        self.commit()

    def __iter__(self):
        """Generator of keys"""
        return (self._load(k[0]) for k in
            self.conn.execute('select key from {0};'.format(self.table)))

    def __len__(self):
        return self.conn.execute('select count(*) from {0};'.format(
            self.table)).fetchone()[0]

    def __contains__(self, key):
        try:
            self._get_key_id(key)
            return True
        except KeyError:
            return False

    def _dump(self, value, version=-1):
        return sqlite3.Binary(pickle.dumps(value, version))

    def _load(self, value):
        return pickle.loads(str(value))

    def _insert(self, key, value):
        """This kinda stinks, check for existence, and then do the work"""
        try:
            db_id = self._get_key_id(key)
            self.conn.execute(
                'update {0} set value=? where id=?;'.format(self.table),
                (self._dump(value), db_id))
        except KeyError:
            self.conn.execute(
                'insert into {0} (hash, key, value) values (?, ?, ?);'.format(
                    self.table),
                (hash(key), self._dump(key), self._dump(value)))

    def pop(self, key):
        """Not atomic, kinda a deal breaker for thread safety."""
        value = self[key]
        del self[key]
        return value

    def keys(self):
        return iter(self)

    def values(self):
        return [self._load(x[0]) for x in
            self.conn.execute('select value from {0};'.foramt(self.table))]

    def items(self):
        return [(self._load(items[0]), self._load(items[1])) for items in
            self.conn.execute('select key,value from {0};'.format(self.table))]

    def commit(self, force=False):
        if self._commit_needed or force:
            self.conn.commit()
        self._commit_needed = False

    def db_file_path(self):
        return self._db_file

    def save(self, db_file=None, remove_old_db=False):
        """Commit the data, close the connection, move file into place"""
        self.commit(force=True)
        self.conn.close()
        if db_file is not None and db_file != self._db_file:
            shutil.copy(self._db_file, db_file)
            if remove_old_db:
                os.unlink(self._db_file)
        self.__init__(db_file=db_file)

    def load(self, db_file=None):
        self.commit(force=True)
        self.conn.close()
        db_file = db_file or self._db_file
        self.__init__(db_file=db_file)


# Container stuff
class CacheDict(collections.MutableMapping):
    """Acts like a normal dictionary until we hit a maximum size, and then
    items are stored in a backing database in LRU or random fashion.

    There are no guarantees around thread safety, so be careful.

    Items are removed from DB when pulled into cache, and written back when
    they fall out of the cache. TODO: allow for remain in db style caching?
    """

    def __init__(self, max_size=100000, db_file=None, backend=None, lru=False,
        current_dictionary=None):
        self._evict_lock_held = False
        self._cache = {}
        self._db_file = db_file
        if backend:
            self._db = backend
        else:
            self._db = SqliteBackend(db_file)
        self.max_size = max_size
        self.lru = lru
        if lru:
            self._key_order = collections.deque([], max_size)
        else:
            self._key_order = None
        # this is a performance yuck, create a batched option
        if current_dictionary:
            for key, value in current_dictionary.iteritems():
                self[key] = value

    def __contains__(self, key):
        """Check for existence in local cache, fall back to db.
        TODO: fault or not fault on contains?  -- currently all db hits fault
        """
        local = key in self._cache
        if not local:
            return key in self._db
        return local

    def __len__(self):
        """Sum the len of every mapping"""
        return len(self._cache) + len(self._db)

    def __iter__(self):
        """Get the keys from local and the db"""
        # this method must account for items faulting in and out of cache
        # in the iteritems case. While iterating, the cache is frozen.
        try:
            self._evict_lock_held = True
            for x in self._cache:
                yield x
            for x in self._db:
                yield x
        finally:
            self._evict_lock_held = False

    def __getitem__(self, key):
        """Returns the stored item at key from a sub mapping or
        raises KeyError"""
        value = None
        if key in self._cache:
            value = self._cache[key]
        else:
            # no fault if we can't evict
            if self._evict_lock_held:
                return self._db[key]
            else:
                value = self._fault(key)
        if self.lru:
            if key in self._key_order:
                self._key_order.remove(key)
            self._key_order.append(key)
        return value

    def __setitem__(self, key, value):
        """Put an items into the mappings, if key doesn't exist, create it"""
        if key not in self._cache and key in self._db:
            # no fault if we can't evict, just update db
            if self._evict_lock_held:
                self._db[key] = value
                return
            # dump the db value and assign in cache
            del self._db[key]
        if key not in self._cache:
            if self._evict_lock_held:
                self._db[key] = value
                return
            else:
                self._evict()
        self._cache[key] = value
        if self._evict_lock_held:
            return
        if self.lru:
            if key in self._key_order:
                self._key_order.remove(key)
            self._key_order.append(key)

    def __delitem__(self, key):
        """Remove item, raise KeyError if does not exist"""
        if key in self._cache:
            del self._cache[key]
        else:
            del self._db[key]
        if self.lru and key in self._key_order:
            self._key_order.remove(key)

    def _fault(self, key):
        """Bring key in from db or raise KeyError, trigger evict if over
        size constraints"""
        # fetch from db and put in local cache
        value = self._db.pop(key)
        # make room in local cache
        self._evict()
        self._cache[key] = value
        return value

    def _evict(self):
        """Push oldest key out of local cache to db if exceeding size limit"""
        if len(self._cache) < self.max_size:
            return
        if self.lru:
            # pop gets the oldest key
            key = self._key_order.popleft()
        else:
            # dump a semi-random key
            view_iter = iter(self._cache.viewkeys())
            key = view_iter.next()
        # take the key out of cache and put in in db
        value = self._cache.pop(key)
        self._db[key] = value

    def get(self, key, default):
        if not self.__contains__(key):
            return default
        else:
            return self.__getitem__(key)

    def has_key(self, key):
        return self.__contains__(key)

    def copy(self, db_file=None):
        """Returns a dictionary as a shallow from the cache dict"""
        newcd = CacheDict(max_size=self.max_size, backend=self.backend,
            lru=self.lru, db_file=db_file)
        newcd.update(self)
        return newcd

    def fromkeys(self, keys, default=None, db_file=None):
        newcd = CacheDict(max_size=self.max_size, backend=self.backend,
            lru=self.lru, db_file=db_file)
        for key in keys:
            newcd[key] = default
        return newcd

    def db_file_path(self):
        """Return the db file path if there is one"""
        return self._db.db_file_path()

    def load(self, db_file=None):
        """Load from a db instance"""
        # clear out local cache so we're correctly in sync
        self._cache.clear()
        if self.lru:
            self._key_order = collections.deque([], self.max_size)
        self._db.load(db_file=db_file)

    def save(self, db_file=None, remove_old_db=False):
        """Dump all to database"""
        for key, value in self._cache.iteritems():
            self._db[key] = value
        if self.lru:
            self._key_order = collections.deque([], self.max_size)
        # clear out local cache so we're correctly in sync
        self._db.save(db_file=db_file or self._db_file,
            remove_old_db=remove_old_db)
        self._cache.clear()


class DefaultCacheDict(CacheDict):

    def __init__(self, default_factory=None, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        if (default_factory is not None and
            not hasattr(default_factory, '__call__')):
            raise TypeError('the factory must be callable')
        super(DefaultCacheDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return super(DefaultCacheDict, self).__getitem__(key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def setdefault(self, key, default):
        if not super(DefaultCacheDict, self).__contains__(key):
            self[key] = default
            return default
        else:
            return self[key]

    def copy(self, db_file=None):
        """Returns a dictionary as a shallow from the cache dict"""
        new_kwargs = {}
        for key, value in self._kwargs.iteritems():
            new_kwargs[key] = value
        new_kwargs['db_file'] = db_file
        newcd = DefaultCacheDict(default_factory=self.default_factory,
            *self._args, **new_kwargs)
        newcd.update(self)
        return newcd

    def fromkeys(self, keys, default=None, db_file=None):
        new_kwargs = {}
        for origkey, origvalue in self._kwargs.iteritems():
            new_kwargs[origkey] = origvalue
        new_kwargs['db_file'] = db_file
        newcd = DefaultCacheDict(default_factory=self.default_factory,
            *self._args, **new_kwargs)
        for key in keys:
            newcd[key] = default
        return newcd


# TODO:
# helper for cleaning up of dictionary file if it shouldn't be stored
