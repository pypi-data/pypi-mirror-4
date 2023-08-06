import sqlite3
import os
import time
import datetime
import tempfile
import gettext

path_ = os.path.join(os.path.dirname(__file__), 'locale')
# print('path_ =', path_)
gettext.install('just_me', path_)

class CannotRun(Exception):
    pass

class JustMe(object):
    """Prohibit to run two process/instance at same time.
    To use a transaction behavior via sqlite3.
    Developver DO change lock_db_path, table_name.
    Developver DO NOT change just_me table structure.
    """

    # 難しく考えすぎだった。失敗。
    __doc__ = _(__doc__)
#   __doc__ = __doc__ * 100
#   print('dir() =', dir())
#   print(__class__)
#   print(__name__)
#   print(__module__.__class__)
#   print(dir(__locals__))
#   print(dir(__module__))

    TABLE_NAME = 'just_me'
    _CREATE_TABLE = '''
        CREATE TABLE if NOT EXISTS {table_name} (
            id integer primary key autoincrement unique not null
            ,
            moment text not null -- when do you call lock() or unlock() ?
            ,
            type text not null check(type in ("lock", "unlock", "prelock"))
            ,
            pid integer not null -- process id
        );
    '''
    _SQL = '''
        insert into {table_name}
        (id, moment, type, pid)
        values(:id, :moment, :type, :pid)
    '''

    # JustMe._make_lock_db_path() combine DIR_NAME and BASE_NAME.
    # of course you can change above two xxx_NAME.
    DIR_NAME = tempfile.gettempdir()
    BASE_NAME = 'just_me_lock.db'

    def __init__(self,
                 script_name='"JustMe"',
                 lock_db_path='',
                 ):
        """initilize attributes and create database to lock database."""

        self.script_name = script_name
        if not lock_db_path:
            lock_db_path = self._make_lock_db_path()
        self.lock_db_path = lock_db_path
        self.pid = os.getpid()

        self._sql = self._SQL.format(**{'table_name': self.TABLE_NAME})

        # for transaction
        self._conn = sqlite3.connect(self.lock_db_path,
                                     timeout=0,
                                     isolation_level='IMMEDIATE')
        self._cur = self._conn.cursor()
        self._create_db()

    def lock(self):
        """see method name."""
        self._lock()

    def unlock(self):
        """see method name."""
        self._unlock()

    def clean(self):
        """delete lock db."""
        os.remove(self.lock_db_path)

    def exercise(self, remains=10):
        """reduce record to remains of num."""
        self._delete(remains)
        self._vacuum()

    def dump_db(self, limit=0, where=''):
        """dump db order by id desc.
        And set limit records of number.
        And you can write a where clause.
        """
        sql = 'select * from {} '.format(self.TABLE_NAME)
        if where:
            sql += 'where {} '.format(where)
        sql += 'order by id desc'
        if limit:
            sql += ' limit {} '.format(limit)

        dumped = []
      # print('sql =')
      # print(sql)
        rows = self._cur.execute(sql)
        column_names = tuple(map(lambda x: x[0], self._cur.description))
        dumped.append(column_names)
        for row in rows.fetchall():
            dumped.append(row)

        return dumped

    def _create_db(self):
        """see method name."""

        sql = JustMe._CREATE_TABLE.format(**{'table_name': self.TABLE_NAME})
        try:
            self._cur.execute(sql)
        except sqlite3.OperationalError as raiz:
            message = 'table {0} already exists'.format(self.TABLE_NAME)
            if raiz.args[0] != message:
                raise raiz

    def _lock(self):
        """acquire lock instance.
        if you cannot lock, raise CannotRun().
        """

        self._insert_to_lock('prelock')
        self._insert_to_lock('lock')

    def _insert_to_lock(self, type_):
        if type_ == 'lock':
            self._conn.isolation_level = 'IMMEDIATE'
        elif type_ == 'prelock':
            # auto commit
            self._conn.isolation_level = None
        else:
            ValueError(_('unkown type_ "{}".').format(type_))

        error_message = ''
        parameters = self._make_parameters(type_)
        try:
            self._cur.execute(self._sql, parameters)
            # NEVER self._conn.commit() in _lock()
        except sqlite3.OperationalError as raiz:
            if raiz.args[0] == 'database is locked':
                error_message = \
                    (_('Another process/instance of '
                       '{0} is already running.\n').format(self.script_name))
            else:
                raise raiz

        if error_message:
            dumped = \
                my_just_me.dump_db(limit=10, where='type = \'prelock\'')
            dumped_str = '\n'.join([str(row) for row in dumped])
            raise CannotRun(error_message + dumped_str)

    def _unlock(self):
        """release lock instance."""
        self._conn.isolation_level = 'IMMEDIATE'
        parameters = self._make_parameters('unlock')
        self._cur.execute(self._sql, parameters)
        self._conn.commit()

    def _make_parameters(self, type_):
        """make sql sentence for lock/unlock."""
        now = datetime.datetime.now().isoformat()
        parameters = {
            'id': None,
            'moment': now,
            'type': type_,
            'pid': self.pid,
        }

      # sql = self._sql
      # print('sql =')
      # print(sql)

      # print('parameters =')
      # print(parameters)

        return parameters

    def _make_lock_db_path(self):
        lock_db_path = os.path.join(self.DIR_NAME, self.BASE_NAME)
        return lock_db_path

    def _delete(self, remains):
        self._conn.execute('''
            delete from {0} where id
                not in (select id from {0} order by id desc limit {1});
        '''.format(self.TABLE_NAME, remains))

    def _vacuum(self):
        """vacuum lock db."""
        self._conn.execute('vacuum')

    def __enter__(self):
        """automatic lock()."""
        self.lock()

    def __exit__(self, *args):
        """automatic unlock()."""
        self.unlock()

#   class JustMe(builtins.object)
#    ...
#    |
#    |  Methods defined here:
#    ...
#    |  lock(self)
#    |      日本語で上書き
#    ...
#    できたっ！
# JustMe.lock.__doc__ = '日本語で上書き'

# 現在の __doc__ を msgid として引っ張ってきておいて、
# _(msgid) として、gettext()経由の文字列にしてから、
# __doc__を上書きする。
# これで、docstringを国際化することが出来る。
# for I18N docstring

def I18N(attr):
    if callable(attr):
        msgid = getattr(attr, '__doc__')
        msgstr = _(msgid)
        setattr(attr, '__doc__', msgstr)

for attr in JustMe.__dict__.values():
    I18N(attr)

del attr, path_, I18N

if __name__ == '__main__':

    class MyJustMe(JustMe):
        """How to inherit the JustMe class."""

        TABLE_NAME = 'my_just_me'
        DIR_NAME = os.path.expanduser('~')
        BASE_NAME = 'my_just_me_lock.db'
        # If MyJustMe(lock_db_path=''), JustMe._make_lock_db_path() combine
        # DIR_NAME and BASE_NAME

        def lock(self):
            """you should change this method in inherited class.
            """
            now = datetime.datetime.now().isoformat()
            print(_('{0} pid={1} trying lock().').format(now, self.pid))

            super().lock()

            now = datetime.datetime.now().isoformat()
            print(_('{0} pid={1} locked.').format(now, self.pid))

        def unlock(self):
            """you should change this method in inherited class.
            """
            now = datetime.datetime.now().isoformat()
            print(_('{0} pid={1} trying unlock().').format(now, self.pid))

            super().unlock()

            now = datetime.datetime.now().isoformat()
            print(_('{0} pid={1} unlocked.').format(now, self.pid))

    # MyJustMe(script_name='MyJustMe', lock_db_path='/path/to/dir/lock.db')
    my_just_me = MyJustMe(script_name='MyJustMe')

    with my_just_me:
        time.sleep(5)

  # my_just_me.lock()   # equal to above with sentence.
  # time.sleep(5)       #
  # my_just_me.unlock() #

    dumped = my_just_me.dump_db(limit=10)
    for row in dumped:
        print(row)

  # my_just_me.exercise(remains=5) # if need.
  # my_just_me.clean() # if need.

  # reproduction.
  # for i in `seq 30` ; do
  #     echo i=$i;
  #     python3 ./justme/justme.py;
  # done
