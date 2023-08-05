from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import class_mapper
from tw2.sqla import AutoViewGrid, AutoTableForm

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

    def db_session_add(self):
        self.query.session.add(self)


# TODO: See why we need to do '.req()' on the form and make sure it's not
# time/ressource consumming
class MixinForm(object):

    @classmethod
    def view_all(cls):
        c = type('%sAutoViewGrid' % cls.__name__,
                    (AutoViewGrid,),
                    {'entity': cls})
        form = c().req()
        form.value = cls.query.all()
        return form.display()

    @classmethod
    def edit_form(cls):
        c = type('%sAutoTableForm' % cls.__name__,
                 (AutoTableForm,),
                 {'entity': cls})
        return c().req()


class FormBase(ExtendedBase, MixinForm): pass

def extended_declarative_base(db_session, forms=True, **kw):
    if forms:
        Base = declarative_base(cls=FormBase, **kw)
    else:
        Base = declarative_base(cls=ExtendedBase, **kw)
    Base.query = db_session.query_property()
    return Base
