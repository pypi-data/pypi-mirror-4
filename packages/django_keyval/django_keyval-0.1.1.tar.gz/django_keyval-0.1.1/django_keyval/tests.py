'''
django_keyval/tests

Copyright (C) 2013 Edwin van Opstal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see `<http://www.gnu.org/licenses/>`.
'''

from __future__ import division
from __future__ import absolute_import

from django import test

from django_keyval.models import KeyVal


class KeyValTestCase(test.TestCase):
    '''
    #TODO: put values in database fixture instead or relying on kv1.set

    Until a database fixture is used, KeyVal.set is used in all tests.
    KeyVal.exists is not explicitly tested, because it is used in most tests
    anyway.
    '''


    def setUp(self):
        self.kv1 = KeyVal('kv1')
        self.kv2 = KeyVal.connect('kv2')
        self.values1 = (12, 'ab', 1.2, (1,2), [1,2], {'a': 1.2})
        self.values2 = (123, 'abc', 12.3, (1,2,3), [1,2,3],
                {'a': 1, 'b': 2.3})
        self.keys = ['key{}'.format(i) for i, unused in enumerate(
                self.values1)]
        self.nokeys = ['nokey{}'.format(i) for i, unused in enumerate(
                self.values1)]


    def test_set_get(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values2):
            self.assertTrue(self.kv1.set(key, value))
        # overwrite kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertFalse(self.kv1.set(key, value))

        # get (nonexistent) values in kv1
        for key in self.nokeys:
            self.assertRaises(KeyError, self.kv1.get, key)
        # get (nonexistent) values in *empty* kv2
        for key in self.keys:
            self.assertRaises(KeyError, self.kv2.get, key)

        # generate new kv's in kv2
        for key, value in zip(self.keys, self.values2):
            self.assertTrue(self.kv2.set(key, value))

        # check values in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertEqual(self.kv1.get(key), value)
        # check values in kv2
        for key, value in zip(self.keys, self.values2):
            self.assertEqual(self.kv2.get(key), value)


    def test_delete(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))

        # delete (nonexistent) kvs
        for key in self.nokeys:
            self.assertRaises(KeyError, self.kv1.delete, key)
            self.assertFalse(self.kv1.delete(key, ignore_keyerror=True))

        # delete kv1 keys:
        for key in self.keys:
            self.assertTrue(self.kv1.delete(key))

        # check if they are gone:
        for key in self.keys:
            self.assertFalse(self.kv1.exists(key))

        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))

        # delete kv1 keys:
        for key in self.keys:
            self.assertTrue(self.kv1.delete(key, ignore_keyerror=True))

        # check if they are gone:
        for key in self.keys:
            self.assertFalse(self.kv1.exists(key))


    def test_pop(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))

        # pop (nonexistent) kvs
        for key in self.nokeys:
            self.assertRaises(KeyError, self.kv1.pop, key)

        # pop kv1 keys:
        for key, value in zip(self.keys, self.values1):
            self.assertEqual(self.kv1.pop(key), value)

        # check if they are gone:
        for key in self.keys:
            self.assertFalse(self.kv1.exists(key))


    def test_pop_default(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))

        # pop (nonexistent) kvs
        for key in self.nokeys:
            self.assertEqual(self.kv1.pop_default(key, 5), 5)

        # pop kv1 keys:
        for key, value in zip(self.keys, self.values1):
            self.assertEqual(self.kv1.pop_default(key, 5), value)

        # check if they are gone:
        for key in self.keys:
            self.assertFalse(self.kv1.exists(key))


    def test_get_default(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))

        # get (nonexistent) kvs
        for key in self.nokeys:
            self.assertEqual(self.kv1.get_default(key, 5), 5)

        # pop kv1 keys:
        for key, value in zip(self.keys, self.values1):
            self.assertEqual(self.kv1.get_default(key, 5), value)


    def test_flush(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))
        # generate new kv's in kv2
        for key, value in zip(self.keys, self.values2):
            self.assertTrue(self.kv2.set(key, value))

        # flush kv1:
        self.assertIsNone(self.kv1.flush())

        # kv1 should be empty
        for key in self.keys:
            self.assertFalse(self.kv1.exists(key))

        # kv2 should be full
        for key in self.keys:
            self.assertTrue(self.kv2.exists(key))


    def test_flush_all(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))
        # generate new kv's in kv2
        for key, value in zip(self.keys, self.values2):
            self.assertTrue(self.kv2.set(key, value))

        # the following is equivalent to KeyVal.flush_all()
        self.assertIsNone(self.kv1.flush_all())

        # kv1 should be empty
        for key in self.keys:
            self.assertFalse(self.kv1.exists(key))

        # kv2 should be empty
        for key in self.keys:
            self.assertFalse(self.kv2.exists(key))

    def test_disconnect(self):
        # generate new kv's in kv1
        for key, value in zip(self.keys, self.values1):
            self.assertTrue(self.kv1.set(key, value))
        # generate new kv's in kv2
        for key, value in zip(self.keys, self.values2):
            self.assertTrue(self.kv2.set(key, value))

        self.assertIsNone(self.kv1.disconnect())

        # any operation on kv1 should raise an error, but kv2 should be ok
        for key, value in zip(self.keys, self.values2):
            #exists
            self.assertRaises(NameError, self.kv1.exists, key)
            self.assertTrue(self.kv2.exists(key))
            #get
            self.assertRaises(NameError, self.kv1.get, key)
            self.assertEqual(self.kv2.get(key), value)
            #set
            self.assertRaises(NameError, self.kv1.set, key, value)
            self.assertFalse(self.kv2.set(key, value))
            #pop
            self.assertRaises(NameError, self.kv1.pop, key)
            self.assertEqual(self.kv2.pop(key), value)
            # further tests on kv2 are pointless
            #delete
            self.assertRaises(NameError, self.kv1.delete, key)
            #pop_default
            self.assertRaises(NameError, self.kv1.pop_default, key, 0)
            #get_default
            self.assertRaises(NameError, self.kv1.get_default, key, 0)
            #flush
            self.assertRaises(NameError, self.kv1.flush)

        # check if values in kv1 are still there
        new_kv1 = KeyVal('kv1')
        for key, value in zip(self.keys, self.values1):
            self.assertEqual(new_kv1.get(key), value)

        #flush_all should work!!
        self.assertIsNone(self.kv1.flush_all())
