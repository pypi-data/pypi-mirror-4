import curses, time, datetime, json
from gadgets.ui.window import Window
from gadgets.ui.dialogs.prompt import Prompt


class Method(Window):
    """run a method"""

    _table = '''CREATE TABLE if not exists methods
             (id integer primary key, timestamp integer, title text, method text)'''

    _insert = '''INSERT INTO methods VALUES(null, ?, ?, ?)'''

    _delete = '''DELETE FROM methods WHERE id=?'''

    def __init__(self, socket, lock, db):
        self._socket = socket
        self._lock = lock
        db.ensure_table(self._table)
        self._db = db
        self._width = 40
        self._height = 18
        self._return_val = []
        self._dialogs = {
            'c': self._create_method,
            'r': self._run_method,
            'd': self._delete_method,
            }

    def _save(self, title, method):
        timestamp=datetime.datetime.now()
        self._db.connection.execute(self._insert, (int(timestamp.strftime('%s')), title, method))
        self._db.connection.commit()


    def _create_method(self, win):
        win.clear()
        win.border()
        self._add_title(win, 'enter method, end with 2 newlines')
        curses.echo()
        method = ''
        row = 2
        while not method.endswith('\n\n'):
            win.move(row ,1)
            method += win.getstr() + '\n'
            row += 1
        prompt = Prompt('method title', str)
        title = prompt(win)
        curses.noecho()
        if method != '':
            self._save(title, method)

    def _get_methods(self):
        cursor = self._db.connection.cursor()
        cursor.execute('SELECT * FROM methods')
        return dict([
            (str(m[0]), dict(
                id=m[0],
                title=m[2],
                method=m[3])) for m in cursor.fetchall()])

    def _print_methods(self, win, row, methods):
        for method in methods.itervalues():
            win.addstr(row, 1, '{0}: {1}'.format(method['id'], method['title']))
            row += 1
        return row

    def _run_method(self, win):
        win.clear()
        win.border()
        self._add_title(win, 'select a method')
        methods = self._get_methods()
        row = 2
        row = self._print_methods(win, row, methods)
        curses.echo()
        win.move(row, 1)
        _id = win.getstr()
        if _id != '':
            method = methods[_id]
            method = method['method'].split('\n')
            self._return_val = method
            self._socket.send('method', {'method': method})
        curses.noecho()

    def _delete_method(self, win):
        win.clear()
        win.border()
        self._add_title(win, 'select a method')
        methods = self._get_methods()
        row = 2
        row = self._print_methods(win, row, methods)
        win.move(row, 1)
        curses.echo()
        _id = win.getstr()
        if _id != '':
            self._db.connection.execute(self._delete, (_id))
            self._db.connection.commit()
        curses.noecho()

    def _ask_user(self, win):
        x = ''
        while x != 'x' and x != 'r':
            win.clear()
            self._add_title(win, self.__doc__)
            win.addstr(2, 1, 'c: create a method')
            win.addstr(3, 1, 'd: delete a method')
            win.addstr(4, 1, 'r: run a method')
            win.addstr(5, 1, 'x: exit')
            win.move(7,1)
            x = chr(win.getch())
            if x in self._dialogs:
                method = self._dialogs[x]
                method(win)

    def __call__(self, screen, data):
        self._lock.acquire()
        win = self._get_subwin(screen)
        self._ask_user(win)
        self._lock.release()
        return self._return_val
        
