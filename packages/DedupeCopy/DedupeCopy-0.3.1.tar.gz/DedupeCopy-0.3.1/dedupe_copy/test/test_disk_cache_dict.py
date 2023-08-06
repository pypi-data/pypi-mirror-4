"""Test suite covering the db backed dictionary"""


import collections
import os
import random
import unittest

import utils

from dedupe_copy import disk_cache_dict

disk_cache_dict.DEBUG = True


class DcdActionSuite(object):

    def setUp(self):
        """Create a new test object"""
        self.cache_size = 10
        self.temp_dir = utils.make_temp_dir('dcd_temp')
        self.db_file = os.path.join(self.temp_dir,
            'dct_test_db_{0}.dict'.format(random.getrandbits(16)))
        self.mirror = collections.defaultdict(list)
        self.backend = None

    def tearDown(self):
        """Remove the db file"""
        self.dcd = None
        utils.remove_dir(self.temp_dir)

    def _spot_check(self, tests=10):
        for _ in range(tests):
            if not self.mirror.keys():
                return
            test_key = random.choice(self.mirror.keys())
            actual = self.dcd[test_key]
            expected = self.mirror[test_key]
            self.assertEqual(actual, expected,
                'Expected {0} for key {1} but got {2}'.format(
                    expected, test_key, actual))

    def _get_all(self):
        for test_key in self.mirror.keys():
            actual = self.dcd[test_key]
            expected = self.mirror[test_key]
            self.assertEqual(actual, expected,
                'Expected {0} for key {1} but got {2}'.format(
                    expected, test_key, actual))

    def test_action_add_read_consistency(self):
        """Add new keys and confirm random gets are consistent below and above
        the memory cache dict's max size.
        """
        for i in range(100):
            if random.random() < .5:
                self.mirror[i]
                self.dcd[i]
            else:
                self.mirror[i] = str(i)
                self.dcd[i] = str(i)
            self._spot_check()
        self._get_all()

    def test_action_add_del_read_consistency(self):
        """Add new keys and delete keys and confirm random gets are consistent
        below and above the memory cache dict's max size. Picks up a few
        updates as well.
        """
        # be sure to re-use deleted keys
        just_removed = None
        for j in range(3):
            for i in range(50):
                if random.random() < .33 and self.mirror.keys():
                    del_key = random.choice(self.mirror.keys())
                    del self.mirror[del_key]
                    del self.dcd[del_key]
                    just_removed = del_key
                else:
                    self.mirror[i] = '{0}_{1}'.format(j, i)
                    self.dcd[i] = '{0}_{1}'.format(j, i)
                    just_removed = None
                self._spot_check()
                if just_removed:
                    self.assertFalse(just_removed in self.dcd,
                        'Found deleted key {0}'.format(just_removed))
        self._get_all()

    def test_updates(self):
        """Update keys that are in out out of cache, check correctness"""
        # half in, half out of cache
        for i in range(self.cache_size * 2):
            self.mirror[i] = str(i)
            self.dcd[i] = str(i)
        for j in range(100):
            self.mirror[j] = '{0}_{1}'.format(self.mirror[j], j)
            self.dcd[j] = '{0}_{1}'.format(self.dcd[j], j)
            self._spot_check()
            self.assertEqual(self.cache_size, len(self.dcd._cache.keys()),
                "Dcd cache is wrong size")
        self._get_all()

    def test_existing_dict_small(self):
        current_dict = dict((i, i) for i in
            range(self.cache_size - int((self.cache_size / 2.0))))
        current_dict['ek_notmod'] = 'an existing key we keep around'
        self.dcd = disk_cache_dict.DefaultCacheDict(default_factory=list,
            max_size=self.cache_size, db_file=self.db_file, lru=self.lru,
            current_dictionary=current_dict, backend=self.backend)
        self.mirror.update(current_dict)
        self.test_updates()

    def test_existing_dict_large(self):
        current_dict = dict((i, i) for i in range(self.cache_size * 2))
        current_dict['ek_notmod'] = 'an existing key we keep around'
        self.dcd = disk_cache_dict.DefaultCacheDict(default_factory=list,
            max_size=self.cache_size, db_file=self.db_file, lru=self.lru,
            current_dictionary=current_dict, backend=self.backend)
        self.mirror.update(current_dict)
        self.test_updates()

    def test_iteritems(self):
        mirror = dict((i, i) for i in range(self.cache_size * 2))
        for key, value in mirror.iteritems():
            self.dcd[key] = value
        for key, value in self.dcd.iteritems():
            self.assertEqual(mirror[key], value,
                "Incorrect value for key {0}. Expected: {1}, Actual: {2}".format(
                    key, mirror[key], value))

    def _populate(self, size=100):
        for i in range(size):
            self.mirror[i] = i
            self.dcd[i] = i

    def _compare(self, mirror, dcd):
        mkeys = sorted(mirror.keys())
        dkeys = sorted(dcd.keys())
        self.assertEqual(mkeys, dkeys,
            'not all keys the same - actual: {0} expected: {1}'.format(
                dkeys, mkeys))
        for mk, mv in mirror.iteritems():
            dcdv = dcd[mk]
            self.assertEqual(mv, dcdv,
                'Value mismatch - actual: {0} expected: {1}'.format(
                    dcdv, mv))

    def test_clear(self):
        self._populate(100)
        self.mirror.clear()
        self.dcd.clear()
        self._compare(self.mirror, self.dcd)

    def test_copy(self):
        self._populate(100)
        mirror_copy = self.mirror.copy()
        new_db_file = '{}_2'.format(self.db_file)
        dcd_copy = self.dcd.copy(db_file=new_db_file)
        self._compare(mirror_copy, dcd_copy)

    def test_fromkeys(self):
        self._populate(100)
        keys = ['a{0}'.format(i) for i in range(30)]
        newmirror = self.mirror.fromkeys(keys, 'a')
        new_db_file = '{}_2'.format(self.db_file)
        newdcd = self.dcd.fromkeys(keys, 'a', db_file=new_db_file)
        self._compare(newmirror, newdcd)

    def test_get(self):
        self._populate(100)
        test_keys = [1, 70, 100, 101, 201]
        for k in test_keys:
            mval = self.mirror.get(k, 'nosuchkey')
            dval = self.dcd.get(k, 'nosuchkey')
            self.assertEqual(mval, dval,
                'Mismatch on get: Expected: {0}, Actual: {1}'.format(
                    mval, dval))

    def test_has_key(self):
        self._populate(100)
        test_keys = [1, 99, 100, 101, 200]
        for k in test_keys:
            mval = self.mirror.has_key(k)
            dval = self.dcd.has_key(k)
            self.assertEqual(mval, dval,
                'Mismatch on has_key: Expected: {0}, Actual: {1}'.format(
                    mval, dval))

    def test_items(self):
        self._populate(100)
        mitems = sorted(self.mirror.items())
        ditems = sorted(self.dcd.items())
        self.assertEqual(mitems, ditems,
            'Mismatch on iterkeys: Expected: {0}, Actual: {1}'.format(
                mitems, ditems))

    def test_itterkeys(self):
        self._populate(100)
        mkey = sorted([v for v in self.mirror.iterkeys()])
        dkey = sorted([v for v in self.dcd.iterkeys()])
        self.assertEqual(mkey, dkey,
            'Mismatch on iterkeys: Expected: {0}, Actual: {1}'.format(
                mkey, dkey))

    def test_itervalues(self):
        self._populate(100)
        mval = sorted([v for v in self.mirror.itervalues()])
        dval = sorted([v for v in self.dcd.itervalues()])
        self.assertEqual(mval, dval,
            'Mismatch on itervalues: Expected: {0}, Actual: {1}'.format(
                mval, dval))

    def test_keys(self):
        self._populate(100)
        mkeys = self.mirror.keys()
        dkeys = self.dcd.keys()
        self._compare(self.mirror, self.dcd)
        self.assertEqual(sorted(mkeys), sorted(dkeys),
            'Did not get correct values - Expected: {0} Actual: {1}'.format(
                mkeys, dkeys))

    def test_pop(self):
        self._populate(100)
        for k in self.mirror.keys():
            mval = self.mirror.pop(k)
            dval = self.dcd.pop(k)
            self.assertEqual(mval, dval,
                'Mismatch on pop: Expected: {0}, Actual: {1}'.format(
                    mval, dval))

    def test_popitem(self):
        self._populate(1)
        item = self.mirror.popitem()
        dcd_item = self.dcd.popitem()
        self._compare(self.mirror, self.dcd)
        self.assertEqual(item, dcd_item,
            'Did not get correct value - Expected: {0} Actual: {1}'.format(
                item, dcd_item))
        self._populate(self.cache_size * 2)
        while True:
            try:
                dcd_item = self.dcd.popitem()
                self.assertEqual(item[0], item[1],
                    'popitem key value mismatch')
            except KeyError as err:
                self.assertEqual(len(self.dcd), 0,
                    'popitem invalid key error {0}'.format(err))
                break

    def test_setdefault(self):
        self.dcd['a'] = 1
        self.mirror['a'] = 1
        self.assertEqual(self.dcd.setdefault('a', 5),
            self.mirror.setdefault('a', 5), 'setdefault existing')
        self.assertEqual(self.dcd.setdefault('b', 5),
            self.mirror.setdefault('b', 5), 'setdefault new')
        self._compare(self.mirror, self.dcd)

    def test_update(self):
        self._populate(100)
        new_values_dict = {}
        new_values_no_keys = []
        for i in range(1, 200):
            new_values_dict[i] = i
        self.mirror.update(new_values_dict)
        self.dcd.update(new_values_dict)
        self._compare(self.mirror, self.dcd)
        for i in range(1, 300):
            new_values_no_keys.append((i, i))
        self.mirror.update(new_values_no_keys)
        self.dcd.update(new_values_no_keys)
        self._compare(self.mirror, self.dcd)

    def test_values(self):
        self._populate(100)
        items = self.mirror.values()
        dcd_items = self.dcd.values()
        self._compare(self.mirror, self.dcd)
        self.assertEqual(sorted(items), sorted(dcd_items),
            'Did not get correct values - Expected: {0} Actual: {1}'.format(
                items, dcd_items))

    def test_save_load(self):
        """Save and continue on file is the expected work flow, what if
         instead the user saved to a new file, continues working, etc"""
        self._populate(100)
        temp_file = os.path.join(self.temp_dir, 'savefile')
        junk_file = os.path.join(self.temp_dir, 'junkfile')
        self.dcd.save(temp_file)
        # target a different scratch space so we don't change temp more.
        self.dcd.save(junk_file)
        self._compare(self.mirror, self.dcd)
        # clear the dict post save to confirm the load
        self.dcd.clear()
        self.assertEqual(len(self.dcd), 0, 'Clear failed')
        self.dcd.load(temp_file)
        print 'Loaded: {0} items'.format(len(self.dcd.keys()))
        self._compare(self.mirror, self.dcd)

    def test_save_load_same_file(self):
        """Save, close, load into new dict."""
        self._populate(100)
        self.dcd.save()
        del self.dcd
        db_file = '{}_2'.format(self.db_file)
        # load into a new object and check
        try:
            self.dcd2 = disk_cache_dict.DefaultCacheDict(default_factory=list,
                max_size=self.cache_size / 2, lru=self.lru,
                current_dictionary=None, db_file=db_file,
                backend=self.backend)
            # load into an empty/new dcd and confirm data
            self.dcd2.load(self.db_file)
            print 'Loaded: {0} items'.format(len(self.dcd2.keys()))
            self._compare(self.mirror, self.dcd2)
        finally:
            del self.dcd2

    def test_save_reopen(self):
        """Save, close, load via db_file argument"""
        try:
            self._populate(self.cache_size + 1)
            self.dcd.save()
            self.assertEqual(len(self.dcd._cache), 0, 'Failed to evict cache')
            # load into a new object and check
            self.dcd2 = disk_cache_dict.DefaultCacheDict(default_factory=list,
                max_size=self.cache_size / 2, lru=self.lru,
                current_dictionary=None, db_file=self.db_file,
                backend=self.backend)
            print 'Opened db with: {0} items'.format(len(self.dcd2.keys()))
            self._compare(self.mirror, self.dcd2)
            self.assertEqual(len(self.dcd2._cache), self.cache_size / 2,
                'Failed to re-warm cache: now size: {0}'.format(
                    len(self.dcd2._cache)))
        finally:
            del self.dcd
            del self.dcd2


class TestDefaultDiskDictFunctional(DcdActionSuite, unittest.TestCase):
    """
    Functional tests around the DefualtDict version of the disk_cache_dict"""

    def setUp(self):
        print 'NON LRU DEFAULT'
        self.lru = False
        super(TestDefaultDiskDictFunctional, self).setUp()
        self.dcd = disk_cache_dict.DefaultCacheDict(default_factory=list,
            max_size=self.cache_size, db_file=self.db_file, lru=False,
            current_dictionary=None)


class TestDefaultDiskDictLruFunctional(DcdActionSuite, unittest.TestCase):
    """Functional tests around the DefualtDict version of the disk_cache_dict"""

    def setUp(self):
        print 'LRU DEFAULT'
        self.lru = True
        super(TestDefaultDiskDictLruFunctional, self).setUp()
        self.dcd = disk_cache_dict.DefaultCacheDict(default_factory=list,
            max_size=self.cache_size, db_file=self.db_file, lru=True,
            current_dictionary=None)

    def test_lru(self):
        cache = collections.deque([], self.cache_size)
        keys = range(self.cache_size * 2)
        for i in keys:
            self.dcd[i] = i
            cache.append(i)
        for i in range(1000):
            test_key = random.choice(keys)
            self.dcd[test_key] = i
            if test_key in cache:
                cache.remove(test_key)
            cache.append(test_key)

            in_cache = self.dcd._cache.keys()
            print in_cache, self.dcd._key_order
            print cache
            print '....'
            self.assertEqual(test_key, self.dcd._key_order[-1], 'not lru')
            self.assertEqual(self.cache_size, len(self.dcd._cache.keys()),
                "Dcd cache is wrong size")
            self.assertFalse(set(in_cache).symmetric_difference(set(cache)),
                'Lru key mismatch')


if __name__ == '__main__':
    unittest.main()
