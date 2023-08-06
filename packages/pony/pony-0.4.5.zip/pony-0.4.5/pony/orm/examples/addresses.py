from pony.orm.core import *

db = Database('sqlite', 'addresses.sqlite', create_db=True)

class User(db.Entity):
    name = Required(unicode)
    addresses = Set("Address")

class Address(db.Entity):
    user = Required(User)
    street = Required(unicode)
    city = Required(unicode)
    state = Required(unicode)
    zip = Required(unicode)

sql_debug(True)  # Output all SQL queries to stdout

db.generate_mapping(create_tables=True)
