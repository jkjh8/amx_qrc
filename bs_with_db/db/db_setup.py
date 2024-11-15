from modules.db import Database

def db_setup_init():
    db = Database()
    db.create_table('setup', { 'key': 'TEXT', 'Value': 'INTEGER', 'String': 'TEXT', 'Bool': 'BOOLEAN' })
    db.insert('setup', {'key': 'serverIpAddr', 'String': '10.20.0.191' })
    db.insert('setup', {'key': 'qsys', 'String': '0.0.0.0' })
    db.insert('setup', {'key': 'chime', 'Bool': True })
    db.insert('setup', {'key': 'pageTime', 'Value': 30 })
    db.insert('setup', {'key': 'powerOnDelay', 'Value': 5 })
    db.insert('setup', {'key': 'pageId', 'Value': 0 })
    db.insert('setup', {'key': 'pageStatus', 'String': '' })
    db.insert('setup', {'key':"onair", 'Bool': False})
    db.insert('setup', {'key':"numOfRelay", 'Value': 8})
    print("DB Setup Started")
    return db

def db_setup_find(condition = None):
    db = Database()
    if condition:
        return db.find('setup', condition)
    else:
        return db.fetch('setup')

def db_setup_find_one(condition):
    db = Database()
    return db.find_one('setup', condition)

def db_setup_update(data, condition, upsert = False):
    db = Database()
    return db.update('setup', data, condition, upsert)
