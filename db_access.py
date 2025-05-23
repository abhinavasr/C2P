import sqlite3
import time
import uuid
import json
import random, string

# --- Configuration Constants ---
DEFAULT_DB_PATH = 'temporary_data_storage.db'
DEFAULT_LINK_DURATION_SECONDS = 10 * 60  # 10 minutes

class Storage:
    """
    A helper class to store data temporarily in an SQLite database with an expiry time.
    """
    def __init__(self, db_path=DEFAULT_DB_PATH, link_duration=DEFAULT_LINK_DURATION_SECONDS):
        """
        Initializes the Stogare instance.

        Args:
            db_path (str): The path to the SQLite database file.
            link_duration (int): The duration in seconds for which the data should be stored.
        """
        self.db_path = db_path
        self.link_duration = link_duration
        self._init_db_schema()

    def _get_db_connection(self):
        """Establishes and returns a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def _execute_db(self, query, args=()):
        """
        Executes a database query (INSERT, UPDATE, DELETE).

        Args:
            query (str): The SQL query to execute.
            args (tuple): The arguments to pass to the query.
        
        Raises:
            sqlite3.Error: If a database error occurs.
        """
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Stogare - Database execution error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _query_db(self, query, args=(), one=False):
        """
        Executes a SELECT database query.

        Args:
            query (str): The SQL query to execute.
            args (tuple): The arguments to pass to the query.
            one (bool): If True, returns a single record, otherwise a list of records.

        Returns:
            dict or list or None: The query result.
        
        Raises:
            sqlite3.Error: If a database error occurs.
        """
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, args)
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
        except sqlite3.Error as e:
            print(f"Stogare - Database query error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _init_db_schema(self):
        """Initializes the database schema if the 'links' table doesn't exist."""
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='links';")
            if cursor.fetchone() is None:
                schema_content = """
                CREATE TABLE links (
                  id TEXT PRIMARY KEY,
                  data TEXT NOT NULL,
                  expires_at INTEGER NOT NULL
                );
                """
                cursor.executescript(schema_content)
                conn.commit()
                print(f"Stogare - Database table 'links' initialized in '{self.db_path}'.")
            else:
                print(f"Stogare - Database table 'links' already exists in '{self.db_path}'.")
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Stogare - Database schema initialization error: {e}")
            # Not raising here to allow app to potentially continue if table exists
            # but other error occurred. Or, re-raise if critical.
        finally:
            if conn:
                conn.close()

    
    def store_data(self, consumer_data):
        """
        Stores the provided data and returns a unique ID and expiry time.

        Args:
            consumer_data (dict): The data to store.

        Returns:
            dict: A dictionary containing 'link_id' and 'expires_at_unix' on success,
                  or 'error' and 'details' on failure.
        """
        
        link_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        expires_at = int(time.time()) + self.link_duration
        
        try:
            # Store data as a JSON string
            data_json = json.dumps(consumer_data)
        except TypeError as e:
            print(f"Stogare - Error serializing data to JSON: {e}")
            return "Invalid data for JSON serialization"

        try:
            self._execute_db("INSERT INTO links (id, data, expires_at) VALUES (?, ?, ?)",
                             [link_id, data_json, expires_at])
            return  link_id
        except sqlite3.Error as e:
            return "Could not store data in database"

    def retrieve_data(self, link_id):
        """
        Retrieves data associated with the given link_id if not expired.
        Expired links are cleaned up.

        Args:
            link_id (str): The unique ID of the data to retrieve.

        Returns:
            dict: A dictionary containing the retrieved 'data' on success,
                  or 'error' and 'details' on failure/expiry/not found.
        """
        try:
            link_data_row = self._query_db("SELECT * FROM links WHERE id = ?", [link_id], one=True)
        except sqlite3.Error as e:
            return {"error": "Database query failed during retrieval", "details": str(e)}

        if link_data_row is None:
            return {"error": "Data not found or already expired/used."}

        current_time = int(time.time())
        
        # Convert sqlite3.Row to dict for easier access and modification
        link_data = dict(link_data_row)

        if current_time > link_data['expires_at']:
            try:
                self._execute_db("DELETE FROM links WHERE id = ?", [link_id])
                print(f"Stogare - Cleaned up expired link: {link_id}")
            except sqlite3.Error as e:
                # Log error but still return expired message
                print(f"Stogare - Error deleting expired link {link_id}: {e}")
            return {"error": "Data link has expired."}

        try:
            retrieved_data = json.loads(link_data['data'])
        except json.JSONDecodeError as e:
            print(f"Stogare - Error decoding JSON data for link_id {link_id}: {e}")
            return {"error": "Failed to parse stored data", "details": str(e)}
        
        return  retrieved_data

    
    def cleanup_expired_links(self):
        """
        Manually triggers a cleanup of all expired links from the database.

        Returns:
            dict: A dictionary with 'cleaned_count' on success, or 'error' on failure.
        """
        current_time = int(time.time())
        try:
            # To count, we can select IDs first, then delete.
            # Or, use cursor.rowcount after DELETE if the SQLite version supports it well.
            # For simplicity and clarity, let's select IDs first.
            expired_ids_rows = self._query_db("SELECT id FROM links WHERE expires_at < ?", [current_time])
            expired_ids = [row['id'] for row in expired_ids_rows]
            
            if not expired_ids:
                print("Stogare - No expired links to clean up.")
                return {"cleaned_count": 0, "message": "No expired links found."}

            # Using a placeholder for a list of IDs
            placeholders = ','.join('?' for _ in expired_ids)
            self._execute_db(f"DELETE FROM links WHERE id IN ({placeholders})", expired_ids)
            
            print(f"Stogare - Cleaned up {len(expired_ids)} expired links.")
            return {"cleaned_count": len(expired_ids), "message": f"Successfully cleaned {len(expired_ids)} links."}
        except sqlite3.Error as e:
            print(f"Stogare - Error during cleanup of expired links: {e}")
            return {"error": "Cleanup failed", "details": str(e)}
            
