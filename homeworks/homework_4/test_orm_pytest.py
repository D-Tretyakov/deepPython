from orm import *
from fields import *
from database import *
import pytest


@pytest.fixture(scope='session', autouse=True)
def setup():
    config = {}

    db = Database(**config)
    db_name = 'test'
    db.command.execute('CREATE DATABASE %s;' % db_name)
    db.command.execute('USE %s;' % db_name)

    # Helper functions
    def get_tables_names():
        db.command.execute('SHOW TABLES;')
        return [item['Tables_in_%s' % db_name].decode('UTF-8') for item in db.command]
    def get_fields_names():
        db.command.execute('DESCRIBE Person;')
        return [(item['Field'], item['Type'].decode())for item in db.command]

    class Person(Model):
        num = Integer()
        name = Char(100)
        surname = Char(50)

    Person.bind_db(db)

    p = Person(num=1, name='Ivan', surname='Ivanov')
    print(Person.db)
    Person.all()

    yield db, db_name, Person, p, get_fields_names, get_tables_names

    db.command.execute('DROP DATABASE %s' % db_name)
    db.command.close()
    db.close()

# TESTS
def test_table_creation(setup):
    db, db_name, Person, p, get_fields_names, get_tables_names = setup
    db.create_table(Person)
    assert 'Person' in get_tables_names()
    assert [('num', 'int'),
            ('name', 'varchar(100)'),
            ('surname', 'varchar(50)')] == get_fields_names()

def test_row_creation(setup):
    db, db_name, Person, p, get_fields_names, get_tables_names = setup
    print(p.db)
    p.create()
    db.command.execute('SELECT * FROM Person WHERE num=1 AND name="Ivan" AND surname="Ivanov";')
    assert {'num': 1, 'name': 'Ivan', 'surname': 'Ivanov'} == list(db.command)[0]

def test_row_update(setup):
    db, db_name, Person, p, get_fields_names, get_tables_names = setup
    p.num=10
    p.save()
    db.command.execute('SELECT * FROM Person WHERE num=10 AND name="Ivan" AND surname="Ivanov";')
    assert {'num': 10, 'name': 'Ivan', 'surname': 'Ivanov'} == list(db.command)[0]
    
    p.num=1
    p.save()
    db.command.execute('SELECT * FROM Person WHERE num=1 AND name="Ivan" AND surname="Ivanov";')
    assert {'num': 1, 'name': 'Ivan', 'surname': 'Ivanov'} == list(db.command)[0]

def test_all_selection(setup):
    db, db_name, Person, p, get_fields_names, get_tables_names = setup
    testers = [Person(num=20+i, name=f'TestName_{i}', surname=f'TestSurname_{i}') for i in range(1, 11)]
    for tester in testers:
        tester.create()
    
    assert [{'num': 1, 'name': 'Ivan', 'surname': 'Ivanov'},
            {'num': 21, 'name': 'TestName_1', 'surname': 'TestSurname_1'},
            {'num': 22, 'name': 'TestName_2', 'surname': 'TestSurname_2'},
            {'num': 23, 'name': 'TestName_3', 'surname': 'TestSurname_3'},
            {'num': 24, 'name': 'TestName_4', 'surname': 'TestSurname_4'},
            {'num': 25, 'name': 'TestName_5', 'surname': 'TestSurname_5'},
            {'num': 26, 'name': 'TestName_6', 'surname': 'TestSurname_6'},
            {'num': 27, 'name': 'TestName_7', 'surname': 'TestSurname_7'},
            {'num': 28, 'name': 'TestName_8', 'surname': 'TestSurname_8'},
            {'num': 29, 'name': 'TestName_9', 'surname': 'TestSurname_9'},
            {'num': 30, 'name': 'TestName_10', 'surname': 'TestSurname_10'}] == Person.all()

def test_get_selection(setup):
    db, db_name, Person, p, get_fields_names, get_tables_names = setup
    assert [{'num': 23, 'name': 'TestName_3', 'surname': 'TestSurname_3'}] == Person.get(num=23)

def test_delete(setup):
    db, db_name, Person, p, get_fields_names, get_tables_names = setup
    p.delete()
    assert [{'num': 21, 'name': 'TestName_1', 'surname': 'TestSurname_1'},
            {'num': 22, 'name': 'TestName_2', 'surname': 'TestSurname_2'},
            {'num': 23, 'name': 'TestName_3', 'surname': 'TestSurname_3'},
            {'num': 24, 'name': 'TestName_4', 'surname': 'TestSurname_4'},
            {'num': 25, 'name': 'TestName_5', 'surname': 'TestSurname_5'},
            {'num': 26, 'name': 'TestName_6', 'surname': 'TestSurname_6'},
            {'num': 27, 'name': 'TestName_7', 'surname': 'TestSurname_7'},
            {'num': 28, 'name': 'TestName_8', 'surname': 'TestSurname_8'},
            {'num': 29, 'name': 'TestName_9', 'surname': 'TestSurname_9'},
            {'num': 30, 'name': 'TestName_10', 'surname': 'TestSurname_10'}] == Person.all()
