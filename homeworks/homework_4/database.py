import mysql.connector
from mysql.connector import connection
from mysql.connector import errorcode
from functools import wraps

def db_error_handle(function):
    @wraps(function)
    def inner(*args, **kwargs):
        try:
            res = function(*args, **kwargs)
        except mysql.connector.Error as err:
            print(err)
        else:
            return res
    return inner

def quotes(value, prefix=None):
    if prefix is None:
        return f"{value}" if isinstance(value, int) else f"'{value}'"
    else:
        return f"{prefix}{value}" if isinstance(value, int) else f"{prefix}'{value}'"

class Database(connection.MySQLConnection):
    def __init__(self, **config):
        try:
            super().__init__(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            self.command = self.cursor(dictionary=True)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.command.close()
        self.close()
        if exc_val:
            raise

    @db_error_handle
    def create_table(self, table):
        self.command.execute(table.sql_repr())
        table.bind_db(self)
    
    @db_error_handle
    def add_row(self, instance):
        items = instance.fields_values()
        names = ', '.join(items.keys())
        values = ', '.join([quotes(value) for value in items.values()])
        self.command.execute(f'INSERT INTO {instance._name} ({names}) VALUES ({values});')
        self.commit()

    @db_error_handle
    def query_all(self, table):
        self.command.execute(f'SELECT * FROM {table.__name__};')
        return list(self.command)

    @db_error_handle
    def query_get(self, table, **kwargs):
        condition = ' AND '.join(
            quotes(value, prefix=f'{column}=') for column, value in kwargs.items())
        self.command.execute(f'SELECT * FROM {table.__name__} WHERE {condition};')
        return list(self.command)
    
    @db_error_handle
    def modify_and_save(self, instance):
        previous_items = instance.get_changes()
        items = instance.fields_values()
        values = ', '.join(quotes(value, prefix=f'{column}=') for column, value in items.items())
        condition = ' AND '.join(
            quotes(value, prefix=f'{column}=') for column, value in previous_items.items())
        self.command.execute(f'UPDATE {instance._name} SET {values} WHERE {condition};')
        self.commit()
    
    @db_error_handle
    def delete(self, instance):
        items = instance.fields_values()
        condition = ' AND '.join(
            quotes(value, prefix=f'{column}=') for column, value in items.items())
        self.command.execute(f'DELETE FROM {instance._name} WHERE {condition};')
        self.commit()
