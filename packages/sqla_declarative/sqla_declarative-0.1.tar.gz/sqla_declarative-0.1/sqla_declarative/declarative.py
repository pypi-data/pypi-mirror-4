from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import class_mapper

_marker = object()

class ExtendedBase(object):

    _pk_name_cached = _marker

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def _pk_name(cls):
        if cls._pk_name_cached is _marker:
            mapper = class_mapper(cls)
            pkeys = []
            for prop in mapper._props.values():
                if [c for c in getattr(prop, 'columns', []) if c.primary_key]:
                    pkeys += [prop.key]
            if len(pkeys) == 0:
                # Should never arrive!
                raise Exception('No primary key found')
            if len(pkeys) != 1:
                raise Exception('Too many primary keys to use this function')
            cls._pk_name_cached = pkeys[0]
        return cls._pk_name_cached

    @property
    def pk_id(self):
        return getattr(self, self._pk_name())


def extended_declarative_base(db_session, **kw):
    Base = declarative_base(cls=ExtendedBase, **kw)
    Base.query = db_session.query_property()
    return Base
