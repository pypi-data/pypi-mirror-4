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

"""
TODO: indexes on foreignkeys, where useful.
"""


import datetime
import sys

from sqlalchemy import (
    Column, Integer, Unicode, UnicodeText, DateTime, Boolean, ForeignKey,
    UniqueConstraint, PrimaryKeyConstraint, SmallInteger)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.expression import desc
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.util import memoized_property

from mediagoblin.db.sql.extratypes import PathTupleWithSlashes, JSONEncoded
from mediagoblin.db.sql.base import Base, DictReadAttrProxy
from mediagoblin.db.mixin import UserMixin, MediaEntryMixin, MediaCommentMixin
from mediagoblin.db.sql.base import Session

# It's actually kind of annoying how sqlalchemy-migrate does this, if
# I understand it right, but whatever.  Anyway, don't remove this :P
#
# We could do migration calls more manually instead of relying on
# this import-based meddling...
from migrate import changeset


class SimpleFieldAlias(object):
    """An alias for any field"""
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __get__(self, instance, cls):
        return getattr(instance, self.fieldname)

    def __set__(self, instance, val):
        setattr(instance, self.fieldname, val)


class User(Base, UserMixin):
    """
    TODO: We should consider moving some rarely used fields
    into some sort of "shadow" table.
    """
    __tablename__ = "core__users"

    id = Column(Integer, primary_key=True)
    username = Column(Unicode, nullable=False, unique=True)
    email = Column(Unicode, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    pw_hash = Column(Unicode, nullable=False)
    email_verified = Column(Boolean, default=False)
    status = Column(Unicode, default=u"needs_email_verification", nullable=False)
    # Intented to be nullable=False, but migrations would not work for it
    # set to nullable=True implicitly.
    wants_comment_notification = Column(Boolean, default=True)
    verification_key = Column(Unicode)
    is_admin = Column(Boolean, default=False, nullable=False)
    url = Column(Unicode)
    bio = Column(UnicodeText)  # ??
    fp_verification_key = Column(Unicode)
    fp_token_expire = Column(DateTime)

    ## TODO
    # plugin data would be in a separate model

    _id = SimpleFieldAlias("id")


class MediaEntry(Base, MediaEntryMixin):
    """
    TODO: Consider fetching the media_files using join
    """
    __tablename__ = "core__media_entries"

    id = Column(Integer, primary_key=True)
    uploader = Column(Integer, ForeignKey(User.id), nullable=False, index=True)
    title = Column(Unicode, nullable=False)
    slug = Column(Unicode)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now,
        index=True)
    description = Column(UnicodeText) # ??
    media_type = Column(Unicode, nullable=False)
    state = Column(Unicode, default=u'unprocessed', nullable=False)
        # or use sqlalchemy.types.Enum?
    license = Column(Unicode)

    fail_error = Column(Unicode)
    fail_metadata = Column(JSONEncoded)

    transcoding_progress = Column(SmallInteger)

    queued_media_file = Column(PathTupleWithSlashes)

    queued_task_id = Column(Unicode)

    __table_args__ = (
        UniqueConstraint('uploader', 'slug'),
        {})

    get_uploader = relationship(User)

    media_files_helper = relationship("MediaFile",
        collection_class=attribute_mapped_collection("name"),
        cascade="all, delete-orphan"
        )
    media_files = association_proxy('media_files_helper', 'file_path',
        creator=lambda k, v: MediaFile(name=k, file_path=v)
        )

    attachment_files_helper = relationship("MediaAttachmentFile",
        cascade="all, delete-orphan",
        order_by="MediaAttachmentFile.created"
        )
    attachment_files = association_proxy("attachment_files_helper", "dict_view",
        creator=lambda v: MediaAttachmentFile(
            name=v["name"], filepath=v["filepath"])
        )

    tags_helper = relationship("MediaTag",
        cascade="all, delete-orphan"
        )
    tags = association_proxy("tags_helper", "dict_view",
        creator=lambda v: MediaTag(name=v["name"], slug=v["slug"])
        )

    ## TODO
    # media_data
    # fail_error

    _id = SimpleFieldAlias("id")

    def get_comments(self, ascending=False):
        order_col = MediaComment.created
        if not ascending:
            order_col = desc(order_col)
        return MediaComment.query.filter_by(
            media_entry=self.id).order_by(order_col)

    def url_to_prev(self, urlgen):
        """get the next 'newer' entry by this user"""
        media = MediaEntry.query.filter(
            (MediaEntry.uploader == self.uploader)
            & (MediaEntry.state == u'processed')
            & (MediaEntry.id > self.id)).order_by(MediaEntry.id).first()

        if media is not None:
            return media.url_for_self(urlgen)

    def url_to_next(self, urlgen):
        """get the next 'older' entry by this user"""
        media = MediaEntry.query.filter(
            (MediaEntry.uploader == self.uploader)
            & (MediaEntry.state == u'processed')
            & (MediaEntry.id < self.id)).order_by(desc(MediaEntry.id)).first()

        if media is not None:
            return media.url_for_self(urlgen)

    #@memoized_property
    @property
    def media_data(self):
        session = Session()

        return session.query(self.media_data_table).filter_by(
            media_entry=self.id).first()

    def media_data_init(self, **kwargs):
        """
        Initialize or update the contents of a media entry's media_data row
        """
        session = Session()

        media_data = session.query(self.media_data_table).filter_by(
            media_entry=self.id).first()

        # No media data, so actually add a new one
        if media_data is None:
            media_data = self.media_data_table(
                media_entry=self.id,
                **kwargs)
            session.add(media_data)
        # Update old media data
        else:
            for field, value in kwargs.iteritems():
                setattr(media_data, field, value)

    @memoized_property
    def media_data_table(self):
        # TODO: memoize this
        models_module = self.media_type + '.models'
        __import__(models_module)
        return sys.modules[models_module].DATA_MODEL

    def __repr__(self):
        safe_title = self.title.encode('ascii', 'replace')

        return '<{classname} {id}: {title}>'.format(
                classname=self.__class__.__name__,
                id=self.id,
                title=safe_title)


class FileKeynames(Base):
    """
    keywords for various places.
    currently the MediaFile keys
    """
    __tablename__ = "core__file_keynames"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)

    def __repr__(self):
        return "<FileKeyname %r: %r>" % (self.id, self.name)

    @classmethod
    def find_or_new(cls, name):
        t = cls.query.filter_by(name=name).first()
        if t is not None:
            return t
        return cls(name=name)


class MediaFile(Base):
    """
    TODO: Highly consider moving "name" into a new table.
    TODO: Consider preloading said table in software
    """
    __tablename__ = "core__mediafiles"

    media_entry = Column(
        Integer, ForeignKey(MediaEntry.id),
        nullable=False)
    name_id = Column(SmallInteger, ForeignKey(FileKeynames.id), nullable=False)
    file_path = Column(PathTupleWithSlashes)

    __table_args__ = (
        PrimaryKeyConstraint('media_entry', 'name_id'),
        {})

    def __repr__(self):
        return "<MediaFile %s: %r>" % (self.name, self.file_path)

    name_helper = relationship(FileKeynames, lazy="joined", innerjoin=True)
    name = association_proxy('name_helper', 'name',
        creator=FileKeynames.find_or_new
        )


class MediaAttachmentFile(Base):
    __tablename__ = "core__attachment_files"

    id = Column(Integer, primary_key=True)
    media_entry = Column(
        Integer, ForeignKey(MediaEntry.id),
        nullable=False)
    name = Column(Unicode, nullable=False)
    filepath = Column(PathTupleWithSlashes)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)

    @property
    def dict_view(self):
        """A dict like view on this object"""
        return DictReadAttrProxy(self)


class Tag(Base):
    __tablename__ = "core__tags"

    id = Column(Integer, primary_key=True)
    slug = Column(Unicode, nullable=False, unique=True)

    def __repr__(self):
        return "<Tag %r: %r>" % (self.id, self.slug)

    @classmethod
    def find_or_new(cls, slug):
        t = cls.query.filter_by(slug=slug).first()
        if t is not None:
            return t
        return cls(slug=slug)


class MediaTag(Base):
    __tablename__ = "core__media_tags"

    id = Column(Integer, primary_key=True)
    media_entry = Column(
        Integer, ForeignKey(MediaEntry.id),
        nullable=False, index=True)
    tag = Column(Integer, ForeignKey(Tag.id), nullable=False, index=True)
    name = Column(Unicode)
    # created = Column(DateTime, nullable=False, default=datetime.datetime.now)

    __table_args__ = (
        UniqueConstraint('tag', 'media_entry'),
        {})

    tag_helper = relationship(Tag)
    slug = association_proxy('tag_helper', 'slug',
        creator=Tag.find_or_new
        )

    def __init__(self, name=None, slug=None):
        Base.__init__(self)
        if name is not None:
            self.name = name
        if slug is not None:
            self.tag_helper = Tag.find_or_new(slug)

    @property
    def dict_view(self):
        """A dict like view on this object"""
        return DictReadAttrProxy(self)


class MediaComment(Base, MediaCommentMixin):
    __tablename__ = "core__media_comments"

    id = Column(Integer, primary_key=True)
    media_entry = Column(
        Integer, ForeignKey(MediaEntry.id), nullable=False, index=True)
    author = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    content = Column(UnicodeText, nullable=False)

    get_author = relationship(User)

    _id = SimpleFieldAlias("id")


MODELS = [
    User, MediaEntry, Tag, MediaTag, MediaComment, MediaFile, FileKeynames,
    MediaAttachmentFile]


######################################################
# Special, migrations-tracking table
#
# Not listed in MODELS because this is special and not
# really migrated, but used for migrations (for now)
######################################################

class MigrationData(Base):
    __tablename__ = "core__migrations"

    name = Column(Unicode, primary_key=True)
    version = Column(Integer, nullable=False, default=0)

######################################################


def show_table_init(engine_uri):
    if engine_uri is None:
        engine_uri = 'sqlite:///:memory:'
    from sqlalchemy import create_engine
    engine = create_engine(engine_uri, echo=True)

    Base.metadata.create_all(engine)


if __name__ == '__main__':
    from sys import argv
    print repr(argv)
    if len(argv) == 2:
        uri = argv[1]
    else:
        uri = None
    show_table_init(uri)
