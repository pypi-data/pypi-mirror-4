#coding=utf-8
from sqlalchemy import (
    create_engine, engine_from_config,
    Column, Integer, ForeignKey, String, DateTime, event, Table, Boolean, Enum, Float, Text)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref, class_mapper, mapper, relationship, configure_mappers
from sqlalchemy.schema import Table
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta, _as_declarative, declared_attr, declarative_base
from sqlalchemy.types import TypeDecorator, String

from zope.sqlalchemy import ZopeTransactionExtension

from datetime import datetime
from types import MethodType

import collections
import inspect
import json
import re

__title__ = 'sqlmagic'
__author__ = "Christopher König"
__version__ = "0.0.2"
__license__ = 'Apache Software License 2.0'

"""
   Copyright 2012 Christopher König

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

class JsonType(TypeDecorator):
    '''Dumps simple python data structures to json format and stores them as string
    Convert the data back to original python data structures when read.
    Differences from sqlalchemy PickleType: PickleType only supports python, JsonType supports a lot of languages
        Think that you might want to read the data out of Magic using Java or PHP(or C#...etc).
    '''
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

def string(size):
    """Convenience macro, return a Column with String."""
    return Column(String(size))

def int():
    """Convenience macro, return a Column with Integer."""
    return Column(Integer)

def bool():
    """Convenience macro, return a Column with Boolean."""
    return Column(Boolean)

def datetime():
    return Column(DateTime)

def enum(*vals):
    return Column(Enum(*vals))

def float():
    return Column(Float)

def json():
    return Column(JsonType)

def text(length=None):
    return Column(Text(length=length))

class DeferredProp(object):
    """A class attribute that generates a mapped attribute
    after mappers are configured."""

    def _config(self, cls, mapper, key):
        raise NotImplementedError

    def _setup_reverse(self, key, rel, target_cls):
        """Setup bidirectional behavior between two relationships."""

        reverse = self.kw.get('reverse')
        if reverse:
            reverse_attr = getattr(target_cls, reverse)
            if not isinstance(reverse_attr, DeferredProp):
                reverse_attr.property._add_reverse_property(key)
                rel._add_reverse_property(reverse)

class FKRelationship(DeferredProp):
    """Generates a one to many or many to one relationship."""

    def __init__(self, target, fk_col, **kw):
        self.target = target
        self.fk_col = fk_col
        self.kw = kw

    def _config(self, cls, key):
        """Create a Column with ForeignKey as well as a relationship()."""

        target_cls = cls._decl_class_registry[self.target]

        pk_target, fk_target = self._get_pk_fk(cls, target_cls)
        pk_table = pk_target.__table__
        pk_col = list(pk_table.primary_key)[0]

        if hasattr(fk_target, self.fk_col):
            fk_col = getattr(fk_target, self.fk_col)
        else:
            fk_col = Column(self.fk_col, pk_col.type, ForeignKey(pk_col))
            setattr(fk_target, self.fk_col, fk_col)

        rel = relationship(target_cls,
                primaryjoin=fk_col==pk_col,
                collection_class=self.kw.get('collection_class', set)
            )
        setattr(cls, key, rel)
        self._setup_reverse(key, rel, target_cls)
        
    def _get_pk_fk(self, cls, target_cls):
        raise NotImplementedError

class one_to_many(FKRelationship):
    """Generates a one to many relationship."""

    def _get_pk_fk(self, cls, target_cls):
        return cls, target_cls

class many_to_one(FKRelationship):
    """Generates a many to one relationship."""

    def _get_pk_fk(self, cls, target_cls):
        return target_cls, cls

class many_to_many(DeferredProp):
    """Generates a many to many relationship."""

    def __init__(self, target, tablename, local, remote, **kw):
        self.target = target
        self.tablename = tablename
        self.local = local
        self.remote = remote
        self.kw = kw

    def _config(self, cls, key):
        """Create an association table between parent/target
        as well as a relationship()."""

        target_cls = cls._decl_class_registry[self.target]
        local_pk = list(cls.__table__.primary_key)[0]
        target_pk = list(target_cls.__table__.primary_key)[0]

        t = Table(
                self.tablename,
                cls.metadata,
                Column(self.local, ForeignKey(local_pk), primary_key=True),
                Column(self.remote, ForeignKey(target_pk), primary_key=True),
                keep_existing=True
            )
        rel = relationship(target_cls,
                secondary=t,
                collection_class=self.kw.get('collection_class', set)
            )
        setattr(cls, key, rel)
        self._setup_reverse(key, rel, target_cls)

class Magic(object):
    """Base class which auto-generates tablename, surrogate
    primary key column.

    Also includes a scoped session and a database generator.
    """

    @staticmethod
    def before_insert_listener(mapper, connection, target):
        target.created_at = datetime.now()

    @staticmethod
    def before_update_listener(mapper, connection, target):
        target.updated_at = datetime.now()

    @event.listens_for(mapper, "mapper_configured")
    @staticmethod
    def _setup_deferred_properties(mapper, class_):
        """Listen for finished mappers and apply DeferredProp
        configurations."""

        for key, value in class_.__dict__.items():
            if isinstance(value, DeferredProp):
                value._config(class_, mapper, key)
    
    first_cap_pattern = re.compile(r'(.)([A-Z][a-z]+)')
    all_cap_pattern = re.compile(r'([a-z0-9])([A-Z])')
    @classmethod
    def camel_to_snake(cls, camel):
        """Convert CamelCase to camel_case"""
        temp = cls.first_cap_pattern.sub(r'\1_\2', name)
        return cls.all_cap_pattern.sub(r'\1_\2', temp).lower()

    @classmethod
    def cast(cls, url=None, settings=None, prefix="sqlalchemy.", create=False, echo=False):
        """'Setup everything' method for the ultra lazy."""

        configure_mappers()

        if url is not None:
            cls.engine = create_engine(url, convert_unicode = True, encoding = 'utf-8', echo=echo)
        elif settings is not None:
            cls.engine = engine_from_config(settings, prefix)
        else:
            raise RuntimeError("No engine specified")

        if create:
            cls.metadata.create_all(cls.engine)

        cls._session = scoped_session(sessionmaker(cls.engine, extension=ZopeTransactionExtension))

    @declared_attr
    def __tablename__(cls):
        """Convert CamelCase class name to underscores_between_words
        table name."""
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "name"):
            return cls.Meta.name

        name = cls.__name__
        return cls.camel_to_snake(name)

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self):
        self.session = self._session()
        event.listen(self, 'before_insert', self.before_insert_listener)
        event.listen(self, 'before_update', self.before_update_listener)

    def save(self):
        self.session.add(self)

    def delete(self):
        self.session.delete(self)

Spell = declarative_base(cls=Magic)
