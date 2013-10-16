import sqlite3


# Dirty hack to prevent uninitialized cursor
# if globals().get("__cursor", None) is None:
#     __cursor = sqlite3.connect("database.db").cursor()
#     print __cursor
#     globals().update({"__cursor": __cursor})

config = {"__conn": sqlite3.connect("database.db")}
config["__cursor"] = config["__conn"].cursor()


class Attribute(object):
    def __init__(self, tp, primary=False):
        assert(tp in (int, str))
        self.tp = tp
        self.sqldef = (tp is int) and " INTEGER" or " TEXT"
        if primary:
            self.sqldef += " PRIMARY KEY"


class ModelFac(type):
    def __init__(cls, name, bases, dct):
        table_name = cls.__name__
        attributes = [k + v.sqldef for k,v in dct.items() if type(v) is Attribute]
        if dct.get("cursor", None) is None:
            dct["cursor"] = config["__cursor"]
            dct["conn"] = config["__conn"]
        if attributes:
            ModelFac.__register(dct["cursor"], dct["conn"], table_name, attributes)
            super(ModelFac, cls).__init__(name, bases, dct)

    @staticmethod
    def __register(cursor, conn, table, attributes):
        """
            Create a table with given name and attribute list
        """
        cmd = "create table if not exists " + table
        cmd += "(" + ','.join(attributes) + ")"
        cursor.execute(cmd)
        conn.commit()


class Model(object):
    __metaclass__ = ModelFac
    cursor = config["__cursor"]
    conn = config["__conn"]

    def __init__(self, **args):
        self.data = {}
        self.data.update(args)

    def update(self, **args):
        self.data.update(args)

    def save(self):
        def code_to_command(x):
            if type(x) == str:
                return "\"%s\"" % x
            else:
                return str(x)
        name = type(self).__name__
        cmd = "insert into %s(%s) values(%s)" % \
            (name, ",".join(self.data.keys()),
                   ",".join(code_to_command(x) for x in self.data.values()))
        print "Executed: " + cmd
        self.cursor.execute(cmd)
        self.conn.commit()


class Database(object):
    def __init__(self):
        self.cursor = config["__cursor"]
 
    def __get_columns(self, name):
        self.sql_rows = 'select * from %s' % name
        # SQLite specific call to get column information of a table
        sql_columns = "PRAGMA table_info(%s)" % name
        self.cursor.execute(sql_columns)
        return [row[1] for row in self.cursor.fetchall()]
 
    def Table(self, name):
        # TODO: Once called, create a class for the table with correct
        # attributes as described by PRAGMA
        columns = self.__get_columns(name)
        return Query(self.cursor, self.sql_rows, columns, name)
 
 
class Query(object):
    def __init__(self, cursor, sql_rows, columns, name):
        self.cursor = cursor
        self.sql_rows = sql_rows
        self.columns = columns
        self.name = name
 
    def filter(self, criteria):
        key_word = "AND" if "WHERE" in self.sql_rows else "WHERE"
        sql = self.sql_rows + " %s %s" % (key_word, criteria)
        return Query(self.cursor, sql, self.columns, self.name)
 
    def order_by(self, criteria):
        return Query(self.cursor, self.sql_rows + " ORDER BY %s" % criteria, self.columns, self.name)
 
    def group_by(self, criteria):
        return Query(self.cursor, self.sql_rows + " GROUP BY %s" % criteria, self.columns, self.name)
 
    def get_rows(self):
        print self.sql_rows
        self.cursor.execute(self.sql_rows)
        return [Row(zip(self.columns, fields), self.name) for fields in self.cursor.fetchall()]
    rows = property(get_rows)
 
 
class Row(object):
    def __init__(self, fields, table_name):
        """
           fields: A list of tuple(column_name : value of column)
           table_name: the name of the table
        """
        self.__class__.__name__ = table_name + "_Row"
        for name, value in fields:
            setattr(self, name, value)
