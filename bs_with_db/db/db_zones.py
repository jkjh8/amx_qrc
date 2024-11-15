from modules.db import Database

def db_zones_init():
    db = Database()
    db.create_table('zones', { 'Name': 'TEXT', 'Gain': 'REAL', 'Mute': 'BOOLEAN', 'Active': 'BOOLEAN', 'Barix': 'TEXT', 'Sel': 'BOOLEAN' })
    print("DB Zones Started")
    return db

def db_zones_find(condition = None):
    db = Database()
    if condition:
        return db.find('zones', condition)
    else:
        return db.fetch('zones')

def db_zones_find_one(condition):
    db = Database()
    return db.find_one('zones', condition)

def db_zones_update(data, condition, upsert = False):
    db = Database()
    return db.update('zones', data, condition, upsert)

def db_zones_exists(condition):
    db = Database()
    return db.exists('zones', condition)