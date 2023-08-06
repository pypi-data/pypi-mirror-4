import sqlite3
import os
import time
import datetime
import tempfile

class CannotRun(Exception):
    pass

class JustMe(object):
    """Prohibit to run two process/instance at same time.
    to use a transaction behavior via sqlite3.
    """

    TABLE_NAME = 'just_me'
    CREATE_TABLE = '''
        CREATE TABLE {}(
            id integer primary key autoincrement unique not null
            ,
            moment text not null # when do you call lock() or unlock() ?
            ,
            type text not null # "lock" or "unlock"
            ,
            pid integer not null # process id
        );
    '''.format(TABLE_NAME)
    LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), 'just_me.lock')

    def __init__(self,
                 script_name='"JustMe"',
                 db_path=LOCK_FILE_PATH,
                 ):
        """initilize attributes and create database to lock database."""

        self.script_name = script_name
        self._db_path = db_path
        self._pid = os.getpid()

        # for transaction
        self._conn = sqlite3.connect(self._db_path,
                                     timeout=0,
                                     isolation_level='IMMEDIATE')
        self._cur = self._conn.cursor()
        self._create_db()

    def lock(self):
        """see method name"""
        self._lock()

    def unlock(self):
        """see method name"""
        self._unlock()

    def clean(self):
        """delete lock file"""
        os.remove(self._db_path)

    def dump_db(self):
        """see method name"""
        rows = self._cur.execute('select * from {}'.format(JustMe.TABLE_NAME))
        column_names = tuple(map(lambda x: x[0], self._cur.description))
        print(column_names)
        for row in rows.fetchall():
            print(row)

    def _create_db(self):
        """see method name"""
        try:
            self._cur.execute(JustMe.CREATE_TABLE)
        except sqlite3.OperationalError as raiz:
            message = 'table {} already exists'.format(JustMe.TABLE_NAME)
            if raiz.args[0] != message:
                raise raiz

    def _lock(self):
        """acquire lock instance.
           if you cannot lock, raise CannotRun()
        """

        error_message = ''
        sql, values = self._make_sql('lock')
        try:
            self._cur.execute(sql, values)
            # NEVER self._conn.commit() in _lock()
        except sqlite3.OperationalError as raiz:
            if raiz.args[0] == 'database is locked':
                error_message = \
                    ('Another process/instance of '
                     '{0} is already running.'.format(self.script_name))
            else:
                raise raiz

        if error_message:
            raise CannotRun(error_message)

    def _unlock(self):
        """release lock instance"""
        sql, values = self._make_sql('unlock')
        self._cur.execute(sql, values)
        self._conn.commit()

    def _make_sql(self, type_):
        """make sql sentence for lock/unlock"""
        now = datetime.datetime.now().isoformat()
        d = {
            'id': None,
            'moment': now,
            'type': type_,
            'pid': self._pid,
        }
        keys = tuple(d.keys())
        values = tuple(d.values())
        hatenas = ', '.join('?' * len(values))
        d_sql = {
            'KEYS': keys,
            'VALUES': '({})'.format(hatenas),
        }

        fmt = 'insert into {0}{KEYS} values{VALUES}'
        sql = fmt.format(JustMe.TABLE_NAME, **d_sql)
      # print('sql =')
      # print(sql)

        return sql, values

if __name__ == '__main__':

    class MyJustMe(JustMe):
        """how to inherit the JustMe class"""

        def lock(self):
            """you should change this method in inherited class.
            """
            now = datetime.datetime.now().isoformat()
            print('{0} pid={1} trying lock().'.format(now, self._pid))

            super().lock()

            now = datetime.datetime.now().isoformat()
            print('{0} pid={1} locked.'.format(now, self._pid))

        def unlock(self):
            """you should change this method in inherited class.
            """
            now = datetime.datetime.now().isoformat()
            print('{0} pid={1} trying unlock().'.format(now, self._pid))

            super().unlock()

            now = datetime.datetime.now().isoformat()
            print('{0} pid={1} unlocked.'.format(now, self._pid))

    my_just_me = MyJustMe(script_name='MyJustMe')
    my_just_me.lock()
    time.sleep(5)
    my_just_me.unlock()

    my_just_me.dump_db()

  # my_just_me.clean() # if need.
