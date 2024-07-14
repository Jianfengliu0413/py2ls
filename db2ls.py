import sqlite3
import pandas as pd
import json
from typing import Optional, List, Union, Tuple
import os
from pprint import pp
class db2ls:
    @classmethod
    def cheatsheet(cls, command: str = None, verbose:bool=False):
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, "data/db2ls_sql_chtsht.json")
        try:
            with open(json_path) as file:
                cheatsheets = json.load(file)
            if command:
                command_lower = command.lower()
                if command_lower in cheatsheets:
                    print(cheatsheets[command_lower])
                elif command_lower in ["list", 'all']:
                    pp(list(cheatsheets.keys()))
                else:
                    print("Command not found. Available commands are: create, insert, select, update, delete, drop.")
            else:
                print("no 'command'")
        except FileNotFoundError:
            print(f"db2ls_sql_chtsht.json cannot be found at {json_path}")
        if verbose:
            pp(list(cheatsheets.keys()))

    def __init__(self, db_path: str):
        self.db_path = db_path
        # # self.logger = logging.getLogger(__name__)
        self.connection: Optional[sqlite3.Connection] = None
    def __enter__(self) -> 'db2ls':
        """
        Establishes a context for the db2ls object, opening a connection to the database.
        This method is automatically called when entering a 'with' statement.
        """
        self.connection = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Closes the database connection when exiting a 'with' statement.
        if self.connection:
            self.connection.close()
            print("Connection closed")

    @classmethod
    def connect(cls, db_path: str) -> 'db2ls':
        instance = cls(db_path)
        instance.connection = sqlite3.connect(db_path)
        return instance 
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        # Execute a SQL query with optional parameters.
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                # self.log_change('EXECUTE', query, params)
                # print("Query executed successfully.")
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            pass

    def tables(self) -> List[str]:
        # Retrieve the names of all tables in the database.
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        rows = self.fetchall(query)
        if rows:
            tab_= [row[0] for row in rows]
        else:
            tab_= []
        if len(tab_)==1:
            return tab_[0]
        else:
            return tab_

    def fetchall(self, query: str, params: Optional[Tuple] = None) -> Optional[List[Tuple]]:
        # Execute a SQL query and return all results.
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                rows = cursor.fetchall()
                return rows
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None

    def fetchmany(self, query: str, params: Optional[Tuple] = None,n:int=5) -> Optional[List[Tuple]]:
        # Execute a SQL query and return all results.
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                rows = cursor.fetchmany(n)
                return rows
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None

    def create(self, table: str,columns:Union[str, List[str]],exist_ok:bool=True) -> None:
        # Create a table in the database. 
        if isinstance(columns, list):
            columns_=', '.join(columns)
        else:
            columns_=columns
        if exist_ok:
            query = f"CREATE TABLE IF NOT EXISTS {table} ({columns_})"
        else:
            query = f"CREATE TABLE {table} ({columns_})"
        self.execute(query)
        print(f"Table created with definition: {query}")
    
    def insert(self, table: str = None, columns: List[str] = None, data: List[Union[str, int, float]] = None) -> None:
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        # Insert data into a table.
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        self.execute(query, data)
        print(f"Data inserted into {table}: {data}")

    def select(self, table: str=None, columns: Union[str, List[str]] = '*', where: Optional[str] = None, where_params: Optional[Tuple] = None, verbose: bool=False) -> Optional[List[Tuple]]:
        # Select data from a table. 
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables()       
        if isinstance(columns, list):
            columns_=', '.join(columns)
        else:
            columns_=columns
        query = f"SELECT {columns_} FROM {table}"
        if where:
            query += f" WHERE {where}"
        rows = self.fetchall(query, where_params)
        if verbose:
            for row in rows:
                print(row)
        return rows
    
    def print(self, table: str = None, columns: Union[str, List[str]] = ['*'], where: Optional[str] = None, where_params: Optional[Tuple] = None, n:int=5) -> Optional[List[Tuple]]:
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        rows = self.select(table=table,columns=columns,where=where,where_params=where_params)
        if rows:
            if len(rows) <= n:
                rows_=rows
            else:
                rows_=rows[:n]
            for row in rows_:
                print(row)
    def update(self, table: str=None, set_clause: Union[str, List[str]] = None, where: Union[str, List[str]] = None, where_params: Tuple=None) -> None:
            """
            Update data in a table.
            Usage:
                option1: 
                    with db2ls(db_path) as db:
                        db.update(table, "postcode = '72076'", "postcode = '69181'")
                option2: 
                db2ls.connect(db_path).execute("update germany set city='Tübingen' where city = 'Leimen'")
            """
            if table is None:
                if isinstance(self.tables(),list):
                    table=self.tables()[0]
                else:
                    table=self.tables() 
            if isinstance(set_clause, list):
                set_clause = ', '.join([f"{col} = ?" for col in set_clause])
            
            if isinstance(where, list):
                where_clause = ' AND '.join(where)
            else:
                where_clause = where
            
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            print(query)
            if where_params is None:
                self.execute(query)
                # print(f"Data updated in {table} where {where_clause}")
            else:
                self.execute(query, where_params)
                # print(f"Data updated in {table} where {where_clause}: {where_params}")

    def drop(self, table:str=None):
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        self.execute("DROP TABLE {table}")
        print(f"Warning: {table} got removed from DataBase")
    def remove(self, table:str=None):
        self.drop(self, table)
        
    def delete(self, table: str=None, where: str = None, where_params: Tuple = None) -> None:
        # Delete data from a table. 
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        query = f"DELETE FROM {table} WHERE {where}"
        self.execute(query, where_params)
        print(f"Data deleted from {table} where {where}")

    def begin(self) -> None:
        """
        Begin a transaction.
        """
        try:
            self.connection.execute('BEGIN')
            print("Transaction started")
        except sqlite3.Error as e:
            print(f"Error starting transaction: {e}")
            pass

    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        try:
            self.connection.commit()
            print("Transaction committed")
        except sqlite3.Error as e:
            print(f"Error committing transaction: {e}")
            pass

    def rollback(self) -> None:
        """
        Rolls back the current transaction to undo changes.
        """
        try:
            self.connection.rollback()
            print("Transaction rolled back")
        except sqlite3.Error as e:
            pass
            print(f"Error rolling back transaction: {e}")
    def undo(self) -> None:
        """
        Rolls back the current transaction to undo changes.
        """
        try:
            self.connection.rollback()
            print("Transaction rolled back")
        except sqlite3.Error as e:
            pass
            print(f"Error rolling back transaction: {e}")

    def columns(self, table: str=None) -> List[str]:
        """
        Retrieve column names of a table.
        usage: db.connect(db_path).columns('germany')
        """
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        query = f"PRAGMA table_info({table})"
        rows = self.fetchall(query)
        if rows:
            return [row[1] for row in rows]
        else:
            return []

    def vacuum(self) -> None:
        """
        Run the VACUUM command to rebuild the database file.
        - Executes the VACUUM command to optimize the database file.
        """
        self.execute("VACUUM")
        print("Database vacuumed")

    def to_df(self, table: str=None, query: Optional[str] = None) -> pd.DataFrame:
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        if query is None:
            query = f"SELECT * FROM {table}"
        try:
            return pd.read_sql_query(query, self.connection)
        except pd.DatabaseError as e:
            print(f"Error converting query result to DataFrame: {e}")
            return pd.DataFrame()
    def to_sql(self, table:str=None, df = None, if_exists='fail',index=False,**kwargs):
        """
        to_sql 
            DataFrame.to_sql(name, con, *, schema=None, if_exists='fail', 
            index=True, index_label=None, chunksize=None, dtype=None, method=None)[source]
        args:
            if_exists: ‘fail’(default), ‘replace’, ‘append’
            index: bool, default True
            index_labelstr or sequence, default None

            method{None, ‘multi’, callable}, optional Controls the SQL insertion clause used:
                'None': Uses standard SQL INSERT clause (one per row).
                ‘multi’: Pass multiple values in a single INSERT clause. 
                'callable': with signature (pd_table, conn, keys, data_iter).
        """
        if table is None:
            if isinstance(self.tables(),list):
                table=self.tables()[0]
            else:
                table=self.tables() 
        conn = self.connection
        df.to_sql(table, conn, if_exists=if_exists, index=index, **kwargs)

    # +++++++++ to add redo() function +++++++++ 
    def log_change(self, operation: str, query: str, params: Optional[Tuple] = None):
            """
            Log the database operation to the change_log table.
            
            Args:
            - operation (str): The type of operation (e.g., 'INSERT', 'UPDATE', 'DELETE').
            - query (str): The SQL query executed.
            - params (tuple, optional): Parameters used in the query.
            """
            log_query = "INSERT INTO change_log (operation, query, params) VALUES (?, ?, ?)"
            params_str = json.dumps(params) if params else None
            self.execute(log_query, (operation, query, params_str))

    def redo(self):
        """
        Reapply the changes from the change_log.
        """
        logs = self.fetchall("SELECT operation, query, params FROM change_log ORDER BY timestamp")
        for log in logs:
            operation, query, params_str = log
            params = json.loads(params_str) if params_str else None
            self.execute(query, params)
    # +++++++++ to add redo() function +++++++++ 
 
if __name__ == "__main__":
    pass
