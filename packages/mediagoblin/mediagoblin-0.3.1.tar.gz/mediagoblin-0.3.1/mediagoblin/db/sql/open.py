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


from sqlalchemy import create_engine
import logging

from mediagoblin.db.sql.base import Base, Session

_log = logging.getLogger(__name__)


class DatabaseMaster(object):
    def __init__(self, engine):
        self.engine = engine

        for k, v in Base._decl_class_registry.iteritems():
            setattr(self, k, v)

    def commit(self):
        Session.commit()

    def save(self, obj):
        Session.add(obj)
        Session.flush()

    def check_session_clean(self):
        for dummy in Session():
            _log.warn("STRANGE: There are elements in the sql session. "
                      "Please report this and help us track this down.")
            break

    def reset_after_request(self):
        Session.rollback()
        Session.remove()


def load_models(app_config):
    import mediagoblin.db.sql.models

    if True:
        for media_type in app_config['media_types']:
            _log.debug("Loading %s.models", media_type)
            __import__(media_type + ".models")


def setup_connection_and_db_from_config(app_config):
    engine = create_engine(app_config['sql_engine'])
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    Session.configure(bind=engine)

    return "dummy conn", DatabaseMaster(engine)


def check_db_migrations_current(db):
    pass
