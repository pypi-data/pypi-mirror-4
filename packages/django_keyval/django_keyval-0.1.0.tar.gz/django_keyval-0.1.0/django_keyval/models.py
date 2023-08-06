'''
django_keyval/models

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

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class KeyVal(object):

    def __init__(self, name):
        '''
        Connect to name
        '''
        self.name = name

    @classmethod
    def connect(cls, name):
        '''
        Just an alias for __init__ for code readability
        '''
        return cls(name)

    @staticmethod
    def flush_all():
        '''
        Delete all key-value pairs of all names
        '''
        _KvStore.objects.all().delete()

    def _get_name(self):
        '''
        Return self.name if it exists, else generate an exception
        '''
        try:
            return self.name
        except AttributeError:
            raise NameError('Name is not set')

    def _get(self, key):
        '''
        Return object if it exists.
        '''
        try:
            return _KvStore.objects.get(name=self._get_name(), key=key)
        except ObjectDoesNotExist:
            raise KeyError('key {} does not exist in {}'.format(key,
                    self.name))

    def set(self, key, value):
        value = pickle.dumps(value)
        kv, created = _KvStore.objects.get_or_create(name=self._get_name(),
                key=key, defaults={'value': value})
        if not created:
            # silently overwrite the value
            kv.value = value
            kv.save()
        return created

    def exists(self, key):
        try:
            self._get(key)
            return True
        except KeyError:
            return False

    def get(self, key):
        return pickle.loads(str(self._get(key).value))

    def get_default(self, key, default_value):
        try:
            return self.get(key)
        except KeyError:
            return default_value

    def pop(self, key):
        '''
        Return the value of key and delete the key-value pair
        '''
        value = self.get(key)
        self.delete(key)
        return value

    def pop_default(self, key, default_value):
        try:
            return self.pop(key)
        except KeyError:
            return default_value

    def delete(self, key, ignore_keyerror=False):
        try:
            self._get(key).delete()
        except KeyError:
            if ignore_keyerror:
                return False
            else:
                raise
        return True

    def flush(self):
        '''
        Delete all key-value pairs in the current name
        '''
        _KvStore.objects.filter(name=self._get_name()).delete()

    def disconnect(self):
        del self.name


class _KvStore(models.Model):
    '''
    The key-value pairs are stored here. This class is not meant to be used
    directly, but only through the KeyVal class.
    '''
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        unique_together = (('name', 'key'),)
