#==========================================================================
# Copyright 2012 Lucidel, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==========================================================================

import sys
import os
import gzip
import zipfile
from optparse import make_option
import traceback

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import (connections, router, transaction, DEFAULT_DB_ALIAS,
                       IntegrityError, DatabaseError)
from django.db.models import get_apps
from django.utils.itercompat import product

try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False

class Command(BaseCommand):
    """
    This code is based off the loaddata command within django1.4.1. It is then modified to serve the moma-django modification, allowing:
    1. Fast import using bulk insert
    2. Remove validation against sql DBs
    """

    help = 'Installs the named fixture(s) in the mongo database.'
    args = "fixture [fixture ...]"

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to load '
                                           'fixtures into. Defaults to the "default" database.'),
        )

    def handle(self, *fixture_labels, **options):
        using = options.get('database')

        connection = connections[using]
        self.style = no_style()

        if not len(fixture_labels):
            self.stderr.write(
                self.style.ERROR("No database fixture specified. Please provide the path of at least one fixture in the command line.\n")
            )
            return

        verbosity = int(options.get('verbosity'))
        show_traceback = options.get('traceback')

        # commit is a stealth option - it isn't really useful as
        # a command line option, but it can be useful when invoking
        # loaddata from within another script.
        # If commit=True, loaddata will use its own transaction;
        # if commit=False, the data load SQL will become part of
        # the transaction in place when loaddata was invoked.
        commit = options.get('commit', True)

        # Keep a count of the installed objects and fixtures
        fixture_count = 0
        loaded_object_count = 0
        fixture_object_count = 0
        models = set()

        humanize = lambda dirname: "'%s'" % dirname if dirname else 'absolute path'

        # Get a cursor (even though we don't need one yet). This has
        # the side effect of initializing the test database (if
        # it isn't already initialized).
        cursor = connection.cursor()

        # Start transaction management. All fixtures are installed in a
        # single transaction to ensure that all references are resolved.
        if commit:
            transaction.commit_unless_managed(using=using)
            transaction.enter_transaction_management(using=using)
            transaction.managed(True, using=using)

        class SingleZipReader(zipfile.ZipFile):
            def __init__(self, *args, **kwargs):
                zipfile.ZipFile.__init__(self, *args, **kwargs)
                if settings.DEBUG:
                    assert len(self.namelist()) == 1, "Zip-compressed fixtures must contain only one file."
            def read(self):
                return zipfile.ZipFile.read(self, self.namelist()[0])

        compression_types = {
            None:   open,
            'gz':   gzip.GzipFile,
            'zip':  SingleZipReader
        }
        if has_bz2:
            compression_types['bz2'] = bz2.BZ2File

        app_module_paths = []
        for app in get_apps():
            if hasattr(app, '__path__'):
                # It's a 'models/' subpackage
                for path in app.__path__:
                    app_module_paths.append(path)
            else:
                # It's a models.py module
                app_module_paths.append(app.__file__)

        app_fixtures = [os.path.join(os.path.dirname(path), 'fixtures') for path in app_module_paths]

        try:
            with connection.constraint_checks_disabled():
                for fixture_label in fixture_labels:
                    parts = fixture_label.split('.')

                    if len(parts) > 1 and parts[-1] in compression_types:
                        compression_formats = [parts[-1]]
                        parts = parts[:-1]
                    else:
                        compression_formats = compression_types.keys()

                    if len(parts) == 1:
                        fixture_name = parts[0]
                        formats = serializers.get_public_serializer_formats()
                    else:
                        fixture_name, format = '.'.join(parts[:-1]), parts[-1]
                        if format in serializers.get_public_serializer_formats():
                            formats = [format]
                        else:
                            formats = []

                    if formats:
                        if verbosity >= 2:
                            self.stdout.write("Loading '%s' fixtures...\n" % fixture_name)
                    else:
                        self.stderr.write(
                            self.style.ERROR("Problem installing fixture '%s': %s is not a known serialization format.\n" %
                                             (fixture_name, format)))
                        if commit:
                            transaction.rollback(using=using)
                            transaction.leave_transaction_management(using=using)
                        return

                    if os.path.isabs(fixture_name):
                        fixture_dirs = [fixture_name]
                    else:
                        fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

                    for fixture_dir in fixture_dirs:
                        if verbosity >= 2:
                            self.stdout.write("Checking %s for fixtures...\n" % humanize(fixture_dir))

                        label_found = False
                        for combo in product([using, None], formats, compression_formats):
                            database, format, compression_format = combo
                            file_name = '.'.join(
                                p for p in [
                                    fixture_name, database, format, compression_format
                                ]
                                    if p
                            )

                            if verbosity >= 3:
                                self.stdout.write("Trying %s for %s fixture '%s'...\n" %\
                                                  (humanize(fixture_dir), file_name, fixture_name))
                            full_path = os.path.join(fixture_dir, file_name)
                            open_method = compression_types[compression_format]
                            try:
                                fixture = open_method(full_path, 'r')
                            except IOError:
                                if verbosity >= 2:
                                    self.stdout.write("No %s fixture '%s' in %s.\n" %\
                                                      (format, fixture_name, humanize(fixture_dir)))
                            else:
                                try:
                                    if label_found:
                                        self.stderr.write(self.style.ERROR("Multiple fixtures named '%s' in %s. Aborting.\n" %
                                                                           (fixture_name, humanize(fixture_dir))))
                                        if commit:
                                            transaction.rollback(using=using)
                                            transaction.leave_transaction_management(using=using)
                                        return

                                    fixture_count += 1
                                    objects_in_fixture = 0
                                    loaded_objects_in_fixture = 0
                                    if verbosity >= 2:
                                        self.stdout.write("Installing %s fixture '%s' from %s.\n" %\
                                                          (format, fixture_name, humanize(fixture_dir)))

                                    objects = serializers.deserialize(format, fixture, using=using)

                                    object_write_buffer = {}
                                    for obj in objects:
                                        objects_in_fixture += 1
                                        if router.allow_syncdb(using, obj.object.__class__):
                                            loaded_objects_in_fixture += 1
                                            models.add(obj.object.__class__)
                                            try:
                                                obj.save(using=using)
                                                #todo The commented code below (and after the except) should activate an alternative save that is done in bulk. Not working yet...
#                                                the_model = type(obj.object)
#                                                if the_model not in object_write_buffer:
#                                                    object_write_buffer.update({the_model:[]})
#                                                item = {}
#                                                item.update( {'account':obj.object.account})
#                                                for field in obj.object._meta.fields:
#                                                    item.update( {field.attname : getattr(obj.object, field.attname ) } )
#                                                object_write_buffer[the_model].append(item)
#                                                if len(object_write_buffer[the_model]) > 500:
#                                                    the_model.objects.bulk_insert(object_write_buffer[the_model])
#                                                    object_write_buffer[the_model]=[]
                                            except (DatabaseError, IntegrityError), e:
                                                msg = "Could not load %(app_label)s.%(object_name)s(pk=%(pk)s): %(error_msg)s" % {
                                                    'app_label': obj.object._meta.app_label,
                                                    'object_name': obj.object._meta.object_name,
                                                    'pk': obj.object.pk,
                                                    'error_msg': e
                                                }
                                                raise e.__class__, e.__class__(msg), sys.exc_info()[2]

#                                    for the_model in object_write_buffer.keys():
#                                        if len(object_write_buffer[the_model]) > 0:
#                                            the_model.objects.bulk_insert(object_write_buffer[the_model])
#                                            object_write_buffer[the_model]=[]


                                    loaded_object_count += loaded_objects_in_fixture
                                    fixture_object_count += objects_in_fixture
                                    label_found = True
                                finally:
                                    fixture.close()

                                # If the fixture we loaded contains 0 objects, assume that an
                                # error was encountered during fixture loading.
                                if objects_in_fixture == 0:
                                    self.stderr.write(
                                        self.style.ERROR("No fixture data found for '%s'. (File format may be invalid.)\n" %
                                                         (fixture_name)))
                                    if commit:
                                        transaction.rollback(using=using)
                                        transaction.leave_transaction_management(using=using)
                                    return


        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            if commit:
                transaction.rollback(using=using)
                transaction.leave_transaction_management(using=using)
            if show_traceback:
                traceback.print_exc()
            else:
                self.stderr.write(
                    self.style.ERROR("Problem installing fixture '%s': %s\n" %
                                     (full_path, ''.join(traceback.format_exception(sys.exc_type,
                                         sys.exc_value, sys.exc_traceback)))))
            return


        # If we found even one object in a fixture, we need to reset the
        # database sequences.
        if loaded_object_count > 0:
            sequence_sql = connection.ops.sequence_reset_sql(self.style, models)
            if sequence_sql:
                if verbosity >= 2:
                    self.stdout.write("Resetting sequences\n")
                for line in sequence_sql:
                    cursor.execute(line)

        if commit:
            transaction.commit(using=using)
            transaction.leave_transaction_management(using=using)

        if verbosity >= 1:
            if fixture_object_count == loaded_object_count:
                self.stdout.write("Installed %d object(s) from %d fixture(s)\n" % (
                    loaded_object_count, fixture_count))
            else:
                self.stdout.write("Installed %d object(s) (of %d) from %d fixture(s)\n" % (
                    loaded_object_count, fixture_object_count, fixture_count))

        # Close the DB connection. This is required as a workaround for an
        # edge case in MySQL: if the same connection is used to
        # create tables, load data, and query, the query can return
        # incorrect results. See Django #7572, MySQL #37735.
        if commit:
            connection.close()
