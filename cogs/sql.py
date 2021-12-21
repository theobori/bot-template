import mysql.connector, time
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

dbconfig = {
    "host": config.get("DATABASE", "HOST"),
    "user": config.get("DATABASE", "USER"),
    "passwd": config.get("DATABASE", "PASSWORD"),
    "database": config.get("DATABASE", "DB_NAME"),
    "auth_plugin": "mysql_native_password"
}

class SQLCursor:
    def __init__(self):
        self.conn = mysql.connector.connect(
            pool_name = "pool",
            **dbconfig
            )
        self.cursor = self.conn.cursor(buffered=True, dictionary=True)
    
    def reconnect(self, wait: float = 1.5):
        if self.conn.is_connected() == False:
            self.conn.reconnect(attempts = 1, delay = 0)
            time.sleep(wait)
        self.conn.commit()
    
    def execute(self, req: str):
        # Reconnect if the connection has timed out
        self.reconnect()
        self.cursor.execute(req)