class Field:
    def __get__(self, obj, type=None):
        return obj._data.setdefault((obj, self), None)

    def __set__(self, obj, value):
        obj._data[(obj, self)] = value

    def get_repr(self):
        return 'TEXT NOT NULL'

class Integer(Field):
    def __set__(self, instance, value):
        if not isinstance(value, int):
            errmessage = f'Invalid value for {type(self).__name__}: "{value}"({type(value)})'
            raise TypeError(errmessage)
        super().__set__(instance, value)

    def get_repr(self):
        return 'INT NOT NULL' 

class Char(Field):
    def __init__(self, maxsize):
        self.maxsize = maxsize
    def __set__(self, instance, value):
        if not isinstance(value, str):
            if len(value) > self.maxsize:
                errmessage = f'Invalid length for {type(self).__name__}: {len(value)} (max is {self.maxsize})'
                raise BufferError(errmessage)
            errmessage = f'Invalid value for {type(self).__name__}: "{value}"({type(value)})'
            raise TypeError(errmessage)
        super().__set__(instance, value)

    def get_repr(self):
        return f'VARCHAR({self.maxsize}) NOT NULL'
