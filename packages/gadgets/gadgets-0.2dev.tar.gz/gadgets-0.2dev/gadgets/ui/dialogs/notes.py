import curses, time, datetime
from gadgets.ui.window import Window

class Notes(Window):
    """take some notes"""

    _table = '''CREATE TABLE if not exists notes
             (method_id integer, timestamp integer, notes text)'''

    _insert = '''INSERT INTO notes VALUES(?, ?, ?)'''

    def __init__(self, socket, lock, db):
        self._socket = socket
        self._lock = lock
        db.ensure_table(self._table)
        self._db = db
        self._width = 40
        self._height = 18

    def _save(self, notes, method_id):
        timestamp=datetime.datetime.now()
        self._db.save(self._insert, (method_id, int(timestamp.strftime('%s')), notes))

    def __call__(self, screen, data, method_id=None):
        self._lock.acquire()
        win = self._get_subwin(screen)
        self._add_title(win, self.__doc__)
        curses.echo()
        curses.curs_set(1)
        notes = ''
        row = 2
        while not notes.endswith('\n\n'):
            win.move(row ,1)
            notes += win.getstr() + '\n'
            row += 1
        curses.noecho()
        curses.curs_set(0)
        if notes != '':
            self._save(notes, method_id)
        self._lock.release()
        
