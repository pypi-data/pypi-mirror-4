import os
import datetime
import sqlite3

class SQL(object):

    _path = os.path.join(os.path.expanduser('~'), '.gadgets')
    _db_path = os.path.join(_path, 'db')

    def __init__(self):
        self._make_connection()

    def ensure_table(self, command):
        self.connection.execute(command)
        
    def _make_connection(self):
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        self.connection = sqlite3.connect(self._db_path)

    def save(self, insert, args):
        self.connection.execute(insert, args)
        self.connection.commit()

        
class Mongo(object):

    def __init__(self, host, port):
        self._connection = Connection(host, port)
        self._db = self._connection['gadgets']
        
            
        
    
    











