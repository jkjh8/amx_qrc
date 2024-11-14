import sqlite3

class Database:
    def __init__(self, db_name = None):
        if not db_name:
            self.conn = sqlite3.connect("file::memory:?cache=shared")
        else:
            self.conn = sqlite3.connect(f"{db_name}.db")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def excute(self, query):
        self.cursor.execute(query)
        self.conn.commit()
        
    def create_table(self, table_name, columns):
        try:
            # columns key value pair of column name and data type
            # example: columns = {'name': 'TEXT', 'age': 'INTEGER'}
            columns = [f'{key} {value}' for key, value in columns.items()]
            columns = ', '.join(columns)
            query = f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, {columns})'
            self.excute(query)
        except Exception as e:
            print(f"Create Table Error: {e}")

    def insert(self, table_name, data):
        try:
            # data key value pair of column name and value
            # example: data = {'name': 'John', 'age': 25}
            columns = ', '.join(data.keys())
            values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in data.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            print(query)
            self.excute(query)
        except Exception as e:
            print(f"Insert Data Error: {e}")
    
    def exists(self, table_name, condition):
        try:
            condition = {key: f"'{value}'" if isinstance(value, str) else value for key, value in condition.items()}
            query = f"SELECT EXISTS" + f"(SELECT 1 FROM {table_name} WHERE {' AND '.join([f'{key}={value}' for key, value in condition.items()])})"
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Exists Data Error: {e}")
    
    def find(self, table_name, condition):
        try:
            condition = {key: f"'{value}'" if isinstance(value, str) else value for key, value in condition.items()}
            query = f"SELECT * FROM {table_name} WHERE {' AND '.join([f'{key}={value}' for key, value in condition.items()])}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Search Data Error: {e}")
            
    def find_one(self, table_name, condition):
        try:
            condition = {key: f"'{value}'" if isinstance(value, str) else value for key, value in condition.items()}
            query = f"SELECT * FROM {table_name} WHERE {' AND '.join([f'{key}={value}' for key, value in condition.items()])}"
            self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Search Data Error: {e}")
            
    def search_or(self, table_name, data):
        try:
            query = f"SELECT * FROM {table_name} WHERE {' OR '.join([f'{key}={value}' for key, value in data.items()])}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Search Data Error: {e}")
            
    def search_like(self, table_name, data):
        try:
            query = f"SELECT * FROM {table_name} WHERE {' AND '.join([f'{key} LIKE {value}' for key, value in data.items()])}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Search Data Error: {e}")
            
    def update(self, table_name, data, condition, upsert = False):
        try:
            if upsert:
                if self.exists(table_name, condition) == 0:
                    self.insert(table_name, {**condition, **data})
                    return
            data = {key: f"'{value}'" if isinstance(value, str) else value for key, value in data.items()}
            condition = {key: f"'{value}'" if isinstance(value, str) else value for key, value in condition.items()}
            query = f"UPDATE {table_name} SET {', '.join([f'{key}={value}' for key, value in data.items()])} WHERE {' AND '.join([f'{key}={value}' for key, value in condition.items()])}"
            self.excute(query)
        except Exception as e:
                print(f"Update Data Error: {e}")
            
    def delete(self, table_name, condition):
        try:
            # condition key value pair of column name and value
            # example: condition = {'id': 1}
            query = f"DELETE FROM {table_name} WHERE {' AND '.join([f'{key}={value}' for key, value in condition.items()])}"
            self.excute(query)
        except Exception as e:
            print(f"Delete Data Error: {e}")
            
    def delete_by_id(self, table_name, id):
        try:
            query = f"DELETE FROM {table_name} WHERE id = {id}"
            self.excute(query)
        except Exception as e:
            print(f"Delete Data Error: {e}")
    
    def delete_by_data(self, table_name, data):
        try:
            query = f"DELETE FROM {table_name} WHERE {' AND '.join([f'{key}={value}' for key, value in data.items()])}"
            self.excute(query)
        except Exception as e:
            print(f"Delete Data Error: {e}")
            
    def fetch(self, table_name):
        try:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Fetch Data Error: {e}")
    
    def fetch_data_by_id(self, table_name, id):
        try:
            query = f"SELECT * FROM {table_name} WHERE id = {id}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Fetch Data Error: {e}")
            
    def join(self, table_name1, table_name2, column_name):
        try:
            query = f"SELECT * FROM {table_name1} JOIN {table_name2} ON {table_name1}.{column_name} = {table_name2}.{column_name}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Join Data Error: {e}")
            
    def __del__(self):
        self.conn.close()

    def close(self):
        self.conn.close()