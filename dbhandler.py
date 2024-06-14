import sqlite3
import time

class dbhandler:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query, params=None, retries=2, delay=1):
        for attempt in range(retries):
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                if params:
                    c.execute(query, params)
                else:
                    c.execute(query)
                conn.commit()
                conn.close()
                return
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    print(f"Database is locked, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Error executing query: {e}")
                    break

    def create_table(self, table_definition):
        self.execute_query(table_definition)
        print(f"Table created with definition: {table_definition}")

    def insert_data(self, table, columns, data):
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        self.execute_query(query, data)
        print(f"Data inserted into {table}: {data}")

    def select_data(self, table, columns='*', where_clause=None, where_params=None):
        query = f"SELECT {', '.join(columns)} FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            if where_params:
                c.execute(query, where_params)
            else:
                c.execute(query)
            rows = c.fetchall()
            conn.close()
            return rows
        except sqlite3.OperationalError as e:
            print(f"Error selecting data: {e}")
            return None

    def update_data(self, table, updates, where_clause, where_params):
        update_clause = ', '.join([f"{col} = ?" for col in updates.keys()])
        params = list(updates.values()) + list(where_params)
        query = f"UPDATE {table} SET {update_clause} WHERE {where_clause}"
        self.execute_query(query, params)
        print(f"Data updated in {table} where {where_clause}: {updates}")

    def delete_data(self, table, where_clause, where_params):
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.execute_query(query, where_params)
        print(f"Data deleted from {table} where {where_clause}")
 
# Example usage
if __name__ == "__main__":
    db = dbhandler("/Users/macjianfeng/Dropbox/github/python/xample_dbhandler/data/example.db")
    
    # Create table
    create_table_sql = """CREATE TABLE IF NOT EXISTS tab (
                            row TEXT PRIMARY KEY, 
                            content TEXT)"""
    db.create_table(create_table_sql)
    
    # Insert data
    db.insert_data("tab", ["row", "content"], ["row1", "This is a row"])
    
    # Select data
    rows = db.select_data("tab")
    print("Selected rows:", rows)
    
    # Update data
    db.update_data("tab", {"content": "Updated content"}, "row = ?", ["row1"])
    
    # Select data again to see the update
    rows = db.select_data("tab")
    print("Selected rows after update:", rows)
    
    # Delete data
    db.delete_data("tab", "row = ?", ["row1"])
    
    # Select data again to see the deletion
    rows = db.select_data("tab")
    print("Selected rows after deletion:", rows)
