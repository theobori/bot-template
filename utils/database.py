"""database controller"""

import logging
import mariadb

from configparser import ConfigParser
from typing import Any, List, Dict

LOG = logging.getLogger(__name__)
CONFIG = ConfigParser()
CONFIG.read("config.ini")

DBCONFIG = {
    "host": CONFIG.get("DATABASE", "HOST"),
    "user": CONFIG.get("DATABASE", "USER"),
    "passwd": CONFIG.get("DATABASE", "PASSWORD"),
    "database": CONFIG.get("DATABASE", "DB_NAME")
}

class CursorDB:
    """
        This class contains some basics mariadb features
        
        It represents a connection to a database
    """

    def __init__(self):
        LOG.info("[+] A connection to the database has been created")

        try:
            self.conn = mariadb.connect(
                pool_name = "pool",
                **DBCONFIG
            )
        except mariadb.Error as error:
            LOG.error(error)
            return

        self.cursor = self.conn.cursor(buffered=True, dictionary=True)
        self.conn.autocommit = True
        self.conn.auto_reconnect = True

    def execute(self, req: str):
        """
            It will execute a SQL request
        """

        try:
            self.cursor.execute(req)
        except mariadb.Error as error:
            LOG.error(error)

    def get_cursor(self):
        """
            Return the outputs after executing a request
        """

        return self.cursor

class LogRequest(CursorDB):
    """
        Some pre made requests to manage the logs in the database
    """

    def __init__(self):
        super().__init__()

    def resolve(self, _id: str, category: str) -> Any:
        """
            Log category -> channel id
        """

        query = f"""SELECT {category} FROM guild_log_channel WHERE
            guild_id = {_id}"""

        self.execute(query)
        channel = self.cursor.fetchone()

        return channel[category]
    
    def get_permission(self, _id: str, permission: str) -> bool:
        """
            Return if the event is allowed to be logged
        """

        ret = True
        query = f"""SELECT {permission} FROM guild_log_permission WHERE
            guild_id = {_id}"""

        self.execute(query)
        response = self.cursor.fetchone()

        try:
            return response[permission]
        except:
            ret = False
        
        return ret

    def get_permissions(self, _id: str) -> List[Dict]:
        """
            Return permissions values (booleans)
        """

        query = f"""SELECT message_delete, message_edit, role_create,
            role_update, role_delete FROM guild_log_permission 
            WHERE guild_id={_id}"""

        self.execute(query)
        response = self.cursor.fetchone()

        return response

    def get_channels(self, _id: str) -> List[Dict]:
        """
            Return linked channels ids
        """

        query = f"""SELECT messages, roles
            FROM guild_log_channel WHERE guild_id={_id}"""

        self.execute(query)
        response = self.cursor.fetchone()

        return response
