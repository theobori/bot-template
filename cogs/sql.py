import mysql.connector, time, discord
from configparser import ConfigParser
from typing import *
import logging

log = logging.getLogger(__name__)
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
    """Storing conn, cursor"""

    def __init__(self):
        log.info("[+] A connection Bot <--> SQL has been etablished")
        self.conn = mysql.connector.connect(
            pool_name = "pool",
            **dbconfig
        )
        self.cursor = self.conn.cursor(buffered=True, dictionary=True)
    
    def reconnect(self, wait: float = 1.5):
        """Reconnect if self.conn has timed out"""

        if self.conn.is_connected():
            return
        self.conn.reconnect(attempts=1, delay=0)
        time.sleep(wait)
        self.conn.commit()
    
    def execute(self, req: str):
        """Send the request to the server -> execute"""

        self.reconnect()
        self.cursor.execute(req)
        self.conn.commit()

class LogRequest(SQLCursor):
    """Some premade requests for the Log command category"""

    def __init__(self):
        super().__init__()

    def resolve_log(self, _id: str, category: str) -> Any:
        """Log category -> channel id"""

        query = f"""SELECT {category} FROM guild_log_channel WHERE
            guild_id = {_id}"""

        self.execute(query)
        channel = self.cursor.fetchone()
        return (channel[category])
    
    def get_log_permission(self, _id: str, permission: str) -> bool:
        """Return if the event is allowed to be logged"""

        query = f"""SELECT {permission} FROM guild_log_permission WHERE
            guild_id = {_id}"""

        self.execute(query)
        response = self.cursor.fetchone()

        try:
            return (response[permission])
        except:
            return (False)

    def get_log_permissions(self, _id: str) -> List[Dict]:
        """Return permissions values (bools)"""

        query = f"""SELECT message_delete, message_edit, role_create,
            role_update, role_delete FROM guild_log_permission 
            WHERE guild_id={_id}"""
        self.execute(query)
        response = self.cursor.fetchone()
        return (response)

    def get_log_channels(self, _id: str) -> List[Dict]:
        """Return linked channels ids"""

        query = f"""SELECT messages, roles
            FROM guild_log_channel WHERE guild_id={_id}"""
        self.execute(query)
        response = self.cursor.fetchone()
        return (response)