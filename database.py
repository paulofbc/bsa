import sqlite3
from datetime import datetime
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "websocket_clients.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connected_clients (
                    client_id INTEGER PRIMARY KEY,
                    address TEXT NOT NULL,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Database initialized successfully")
    
    def add_client(self, client_id: int, address: str):
        """Add a new connected client to the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO connected_clients (client_id, address, connected_at, last_activity)
                    VALUES (?, ?, ?, ?)
                """, (client_id, address, datetime.now(), datetime.now()))
                logger.info(f"Client {client_id} added to database")
        except sqlite3.IntegrityError:
            logger.warning(f"Client {client_id} already exists in database")
    
    def remove_client(self, client_id: int):
        """Remove a disconnected client from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM connected_clients WHERE client_id = ?", (client_id,))
            logger.info(f"Client {client_id} removed from database")
    
    def get_all_clients(self):
        """Retrieve all currently connected clients"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM connected_clients")
            return cursor.fetchall()
    
    def update_activity(self, client_id: int):
        """Update last activity timestamp for a client"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE connected_clients 
                SET last_activity = ? 
                WHERE client_id = ?
            """, (datetime.now(), client_id))
    
    def get_client_count(self):
        """Get the number of connected clients"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM connected_clients")
            return cursor.fetchone()[0]
