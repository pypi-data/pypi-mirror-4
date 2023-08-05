from datetime import datetime

from blazeutils.helpers import tolist
from blazeutils.strings import randchars
from blazeweb.globals import ag
import savalidation as saval
import sqlalchemy as sa
import sqlalchemy.ext.declarative as sadec
import sqlalchemy.orm as saorm
import sqlalchemy.sql as sasql
from sqlalchemy.util import classproperty

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.columns import SmallIntBool
from compstack.sqlalchemy.lib.decorators import one_to_none, transaction, \
    ignore_unique

class DefaultColsMixin(object):
    id = sa.Column(sa.Integer, primary_key=True)
    createdts = sa.Column(sa.DateTime, nullable=False, default=datetime.now, server_default=sasql.text('CURRENT_TIMESTAMP'))
    updatedts = sa.Column(sa.DateTime, onupdate=datetime.now)

class MethodsMixin(object):
    # the object that the SA session should be pulled from
    mm_db_global = db
    # the name of the attribute representing the SA session
    mm_db_sess_attr = 'sess'

    @classmethod
    def _sa_sess(cls):
        return getattr(cls.mm_db_global, cls.mm_db_sess_attr)

    @classmethod
    def query(cls, *args):
        if args:
            entities = [getattr(cls, aname) for aname in args]
        else:
            entities = [cls]
        return cls._sa_sess().query(*entities)


    @transaction
    def add(cls, **kwargs):
        o = cls()
        o.from_dict(kwargs)
        cls._sa_sess().add(o)
        return o

    @ignore_unique
    def add_iu(cls, **kwargs):
        """
            Add a record and ignore unique constrainted related
            exceptions if encountered
        """
        return cls.add(**kwargs)

    @transaction
    def edit(cls, oid=None, **kwargs):
        try:
            oid = oid or kwargs.pop('id')
        except KeyError:
            raise ValueError('the id must be given to edit the record')
        o = cls.get(oid)
        o.from_dict(kwargs)
        return o

    @classmethod
    def update(cls, oid=None, **kwargs):
        """
            Add or edit depending on presence if 'id' field from oid or kwargs
        """
        oid = oid or kwargs.pop('id', None)
        if oid:
            return cls.edit(oid, **kwargs)
        return cls.add(**kwargs)

    @classmethod
    def get(cls, oid):
        return cls._sa_sess().query(cls).get(oid)

    @one_to_none
    def get_by(cls, **kwargs):
        """
        Returns the instance of this class matching the given criteria or None
        if there is no record matching the criteria.

        If multiple records are returned, an exception is raised.
        """
        return cls._sa_sess().query(cls).filter_by(**kwargs).one()

    @one_to_none
    def get_where(cls, clause, *extra_clauses):
        """
        Returns the instance of this class matching the given clause(s) or None
        if there is no record matching the criteria.

        If multiple records are returned, an exception is raised.
        """
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls._sa_sess().query(cls).filter(where_clause).one()

    @classmethod
    def first(cls, order_by=None):
        return cls.order_by_helper(cls._sa_sess().query(cls), order_by).first()

    @classmethod
    def first_by(cls, order_by=None, **kwargs):
        return cls.order_by_helper(cls._sa_sess().query(cls), order_by).filter_by(**kwargs).first()

    @classmethod
    def first_where(cls, clause, *extra_clauses, **kwargs):
        order_by = kwargs.pop('order_by', None)
        if kwargs:
            raise ValueError('order_by is the only acceptable keyword arg')
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls.order_by_helper(cls._sa_sess().query(cls), order_by).filter(where_clause).first()

    @classmethod
    def list(cls, order_by=None):
        return cls.order_by_helper(cls._sa_sess().query(cls), order_by).all()

    @classmethod
    def list_by(cls, order_by=None, **kwargs):
        return cls.order_by_helper(cls._sa_sess().query(cls), order_by).filter_by(**kwargs).all()

    @classmethod
    def list_where(cls, clause, *extra_clauses, **kwargs):
        order_by = kwargs.pop('order_by', None)
        if kwargs:
            raise ValueError('order_by is the only acceptable keyword arg')
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls.order_by_helper(cls._sa_sess().query(cls), order_by).filter(where_clause).all()

    @classmethod
    def pairs(cls, fields, order_by=None, _result=None):
        """
            Returns a list of two element tuples.
            [
                (1, 'apple')
                (2, 'banana')
            ]

            fields: string with the name of the fields you want to pair with
                a ":" seperating them.  I.e.:

                Fruit.pairs('id:name')

            order_by = order_by clause or iterable of order_by clauses
        """
        key_field_name, value_field_name = fields.split(':')
        if _result is None:
            _result = cls.list(order_by)
        retval = []
        for obj in _result:
            retval.append((
                  getattr(obj, key_field_name),
                  getattr(obj, value_field_name)
                ))
        return retval

    @classmethod
    def pairs_by(cls, fields, order_by=None, **kwargs):
        result = cls.list_by(order_by, **kwargs)
        return cls.pairs(fields, _result=result)

    @classmethod
    def pairs_where(cls, fields, clause, *extra_clauses, **kwargs):
        result = cls.list_where(clause, *extra_clauses, **kwargs)
        pairs = cls.pairs(fields, _result=result)
        return pairs

    @transaction
    def delete(cls, oid):
        o = cls.get(oid)
        if o is None:
            return False

        cls._sa_sess().delete(o)
        return True

    @transaction
    def delete_where(cls, clause, *extra_clauses):
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls._sa_sess().query(cls).filter(where_clause).delete()

    @transaction
    def delete_all(cls):
        return cls._sa_sess().query(cls).delete()

    @classmethod
    def count(cls):
        return cls._sa_sess().query(cls).count()

    @classmethod
    def count_by(cls, **kwargs):
        return cls._sa_sess().query(cls).filter_by(**kwargs).count()

    @classmethod
    def count_where(cls, clause, *extra_clauses):
        where_clause = cls.combine_clauses(clause, extra_clauses)
        return cls._sa_sess().query(cls).filter(where_clause).count()

    def to_dict(self, exclude=[]):
        col_prop_names = self.sa_column_names()
        data = dict([(name, getattr(self, name))
                     for name in col_prop_names if name not in exclude])
        return data

    def from_dict(self, data):
        """
        Update a mapped class with data from a JSON-style nested dict/list
        structure.
        """
        # surrogate can be guessed from autoincrement/sequence but I guess
        # that's not 100% reliable, so we'll need an override

        mapper = saorm.object_mapper(self)

        for key, value in data.iteritems():
            if isinstance(value, dict):
                dbvalue = getattr(self, key)
                rel_class = mapper.get_property(key).mapper.class_
                pk_props = rel_class._descriptor.primary_key_properties

                # If the data doesn't contain any pk, and the relationship
                # already has a value, update that record.
                if not [1 for p in pk_props if p.key in data] and \
                   dbvalue is not None:
                    dbvalue.from_dict(value)
                else:
                    record = rel_class.update_or_create(value)
                    setattr(self, key, record)
            elif isinstance(value, list) and \
                 value and isinstance(value[0], dict):

                rel_class = mapper.get_property(key).mapper.class_
                new_attr_value = []
                for row in value:
                    if not isinstance(row, dict):
                        raise Exception(
                                'Cannot send mixed (dict/non dict) data '
                                'to list relationships in from_dict data.')
                    record = rel_class.update_or_create(row)
                    new_attr_value.append(record)
                setattr(self, key, new_attr_value)
            else:
                setattr(self, key, value)

    @classmethod
    def order_by_helper(cls, query, order_by):
        if order_by is not None:
            return query.order_by(*tolist(order_by))
        return query.order_by(cls.id)

    @classmethod
    def combine_clauses(cls, clause, extra_clauses):
        if not extra_clauses:
            return clause
        return sasql.and_(clause, *extra_clauses)

    @classmethod
    def sa_column_names(self):
        return [p.key for p in self.__mapper__.iterate_properties \
                                      if isinstance(p, saorm.ColumnProperty)]

class DefaultMixin(saval.ValidationMixin, DefaultColsMixin, MethodsMixin):
    pass

def declarative_base(*args, **kwargs):
    """
        creates a Base class for declarative objects or returns the class that
        has allready been created for the current application instance.
    """
    if not hasattr(ag, 'sabwp_declarative_base'):
        kwargs.setdefault('metadata', db.meta)
        ag.sabwp_declarative_base = sadec.declarative_base(*args, **kwargs)
    return ag.sabwp_declarative_base

###
### Lookup Functionality
###
class LookupMixin(DefaultMixin):
    @classproperty
    def label(cls):
        return sa.Column(sa.Unicode(255), nullable=False, unique=True)
    active_flag = sa.Column(SmallIntBool, nullable=False, server_default=sasql.text('1'))

    @classmethod
    def testing_create(cls, label=None, active=True):
        if label is None:
            label = u'%s %s' % (cls.__name__, randchars(5))
        return cls.add(label=label, active_flag=active)

    @classmethod
    def list_active(cls, include_ids=None, order_by=None):
        if order_by is None:
            order_by = cls.label
        if include_ids:
            include_ids = tolist(include_ids)
            clause = sasql.or_(
                cls.active_flag == 1,
                cls.id.in_(include_ids)
            )
        else:
            clause = cls.active_flag == 1
        return cls.list_where(clause, order_by=order_by)

    @classmethod
    def pairs_active(cls, include_ids=None, order_by=None):
        result = cls.list_active(include_ids, order_by=order_by)
        return cls.pairs('id:label', _result=result)

    @classmethod
    def get_by_label(cls, label):
        return cls.get_by(label=label)

    def __repr__(self):
        return '<%s %s:%s>' % (self.__class__.__name__, self.id, self.label)
