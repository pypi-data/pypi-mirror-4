# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from mediagoblin.init import setup_global_and_app_config


def migrate_parser_setup(subparser):
    pass


def _print_started_migration(migration_number, migration_func):
    sys.stdout.write(
        "Running migration %s, '%s'... " % (
            migration_number, migration_func.func_name))
    sys.stdout.flush()


def _print_finished_migration(migration_number, migration_func):
    sys.stdout.write("done.\n")
    sys.stdout.flush()


def migrate(args):
    run_migrate(args.conf_file)


def run_migrate(conf_file):
    # This MUST be imported so as to set up the appropriate migrations!
    from mediagoblin.db.mongo import migrations

    from mediagoblin.db.mongo import util as db_util
    from mediagoblin.db.mongo.open import setup_connection_and_db_from_config

    global_config, app_config = setup_global_and_app_config(conf_file)

    connection, db = setup_connection_and_db_from_config(
        app_config, use_pymongo=True)
    migration_manager = db_util.MigrationManager(db)

    # Clear old indexes
    print "== Clearing old indexes... =="
    removed_indexes = db_util.remove_deprecated_indexes(db)

    for collection, index_name in removed_indexes:
        print "Removed index '%s' in collection '%s'" % (
            index_name, collection)

    # Migrate
    print "\n== Applying migrations... =="
    migration_manager.migrate_new(
        pre_callback=_print_started_migration,
        post_callback=_print_finished_migration)

    # Add new indexes
    print "\n== Adding new indexes... =="
    new_indexes = db_util.add_new_indexes(db)

    for collection, index_name in new_indexes:
        print "Added index '%s' to collection '%s'" % (
            index_name, collection)
