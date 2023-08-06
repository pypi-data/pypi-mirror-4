'''
django-keyval/management/commands/keyval.py

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

from django.core.management.base import BaseCommand, make_option

from django_keyval.models import KeyVal


class Command(BaseCommand):
    help = "Manipulate key-value table - only intended for testing purposes"
    option_list = BaseCommand.option_list + (
            make_option('--command', '-c',
                dest='command',
                type = 'str',
                help='Command to execute, options are: set, get and del.'
            ),
            make_option('--store_name', '-n',
                dest='store_name',
                type = 'str',
                help='Set the name of the store for this command'
            ),
            make_option('--ke', '-k',
                dest='key',
                type='str',
                help='Name of the key'
            ),
            make_option('--value', '-V',
                dest='value',
                type='string',
                help='value to store, note: this will be stored as a string'
            ),)

    def handle(self, **options):
        command = options.get('command')
        if not command:
            raise SystemExit('Error: you must specify a command')
        store_name = options.get('store_name')
        if not store_name:
            raise SystemExit('Error: you must specify a store name')
        key = options.get('key')
        if not key:
            raise SystemExit('Error: you must specify a key')
        kv = KeyVal(store_name)
        if command == 'set':
            value = options.get('value')
            if not value:
                raise SystemExit('Error: you must specify a value')
            created = kv.set(key, value)
            if created:
                print('New key {} set to {}.'.format(key, value))
            else:
                print('Existing key {} overwritten to {}.'.format(key, value))
        elif command == 'get':
            try:
                value = kv.get_default(key, None)
            except NameError:
                raise SystemExit('Error: store_name {} does not exist'.format(
                        store_name))
            if value is None:
                print('Warning: Key {} does not exist in {}.'.format(key, 
                        store_name))
            else:
                print('Value for key {} is {}'.format(key, value))
        elif command == 'del':
            try:
                deleted = kv.delete(key, ignore_keyerror=True)
            except NameError:
                raise SystemExit('Error: store_name {} does not exist'.format(
                        store_name))
            if deleted:
                print('Key {} deleted'.format(key))
            else:
                print('Warning: Key {} does not exist in {}.'.format(key, 
                        store_name))
        else:
            raise SystemExit('Error: command {} is invalid'.format(command))
