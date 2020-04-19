import mysql.connector
from mysql.connector import connection
from mysql.connector import errorcode
from functools import wraps

from fields import *
from database import *

class MetaBase(type):
    def __new__(cls, name, bases, attrs):
        attrs['_data'] = {}
        attrs['_fields'] = {}
        for field_name, field in attrs.items():
            if issubclass(type(field), Field):
                attrs['_fields'][field_name] = field
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=MetaBase):
    db = None
    def __init__(self, **kwargs):
        self._name = type(self).__name__
        self._previous_state = {}
        self._is_modifying = False

        for field in kwargs:
            setattr(self, field, kwargs[field])
        self.clear_changes()
    
    def __setattr__(self, name, value):
        if name in self._fields and not self._is_modifying:
            self._previous_state = self.fields_values()
            self._is_modifying = True
        return super().__setattr__(name, value)

    def clear_changes(self):
        self._previous_state.clear()
        self._is_modifying = False

    def create(self):
        self.db.add_row(self)

    @classmethod
    def sql_repr(cls):
        fields_repr = [f'{field_name} {field.get_repr()}' for field_name, field in cls._fields.items()]
        table_repr = f"CREATE TABLE IF NOT EXISTS {cls.__name__} \
            ({', '.join(fields_repr)}, PRIMARY KEY ({fields_repr[0].split()[0]}));"
        return table_repr

    @classmethod
    def bind_db(cls, db):
        cls.db = db

    @classmethod
    def all(cls):
        return cls.db.query_all(cls)
    
    @classmethod
    def get(cls, **kwargs):
        return cls.db.query_get(cls, **kwargs)

    @classmethod
    def from_all(cls):
        rows = cls.db.query_all(cls)
        return [cls(**values) for values in rows]
    
    def fields_values(self):
        return {field_name: getattr(self, field_name, None) for field_name in self._fields}
    
    def get_changes(self):
        return self._previous_state
    
    def save(self):
        self.db.modify_and_save(self)
        self.clear_changes()

    def delete(self):
        self.db.delete(self)
    
