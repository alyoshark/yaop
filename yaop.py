import sqlite3
import uuid


config = {"__conn": sqlite3.connect("database.db")}
config["__cursor"] = config["__conn"].cursor()


class YaopSqlException(Exception):
    pass


def code_to_command(x):
    if type(x) == str:
        return "\"%s\"" % x
    else:
        return str(x)


class Attribute(object):
    def __init__(self, tp, value=None, unique=False):
        # assert(tp in (int, str))
        self.tp = tp
        self.foreign = None
        if tp is int:
            self.sqldef = " INTEGER"
        elif tp is str:
            self.sqldef = " TEXT"
        elif tp is float:
            self.sqldef = " REAL"
        else:
            # Can only reference to a type inherits Model
            assert issubclass(tp, Model)
            self.sqldef = " INTEGER"
            self.foreign = tp.__name__
        self.value = value
        if unique:
            self.sqldef += " NOT NULL UNIQUE"

    def update(self, value):
        self.value = value


class ModelFac(type):
    def __init__(cls, name, bases, dct):
        table_name = cls.__name__
        base = bases[0]
        base_attributes = dir(base)
        # All the attributes in the base type
        attribute_dict = dict([(k, getattr(base, k)) for k in base_attributes
            if type(getattr(base, k)) is Attribute])
        # Overwrite the attributes with new information (if exists)
        attribute_dict.update(dct)
        attribute_pairs = [(k,v) for k,v in attribute_dict.items() if type(v) is Attribute]
        # Check if there are any foreign keys
        foreign_keys = [(i[0], i[1].foreign) for i in attribute_pairs if i[1].foreign]
        attributes = [i[0] + i[1].sqldef for i in attribute_pairs]
        if dct.get("cursor", None) is None:
            dct["cursor"] = config["__cursor"]
            dct["conn"] = config["__conn"]
        if attributes:
            # Getting the column information from database (if exists)
            db_cols = ModelFac.table_exists(dct["cursor"], table_name)
            if db_cols:
                # Should ideally insert/delete columns, will throw error
                # if the definition is not the same as column defines
                if set(db_cols)-set(["Id",]) != set(i[0] for i in attribute_pairs):
                    raise YaopSqlException("Class definition and table column don't match")
            ModelFac.__register(dct["cursor"], dct["conn"], table_name,
                    attributes, foreign_keys)
            super(ModelFac, cls).__init__(name, bases, dct)

    @staticmethod
    def table_exists(cursor, table):
        cursor.execute("select name from sqlite_master where \
                        type=\"table\" and name=\"%s\"" % (table,))
        tables = cursor.fetchall()
        if tables:
            cursor.execute("PRAGMA table_info(%s)" % table)
            return [row[1] for row in cursor.fetchall()]
        else:
            return None

    @staticmethod
    def __register(cursor, conn, table, attributes, foreign_keys=None):
        """
            Create a table with given name and attribute list
        """
        foreign_key_parse = lambda x: "foreign key(" + x[0] + ") references " + x[1] + "(Id)"
        cmd = "create table if not exists %s(Id INTEGER PRIMARY KEY AUTOINCREMENT,%s" \
                % (table, ','.join(attributes))
        if foreign_keys:
            cmd += ',' + ','.join([foreign_key_parse(x) for x in foreign_keys])
        cmd += ")"
        cursor.execute(cmd)
        conn.commit()


class Model(object):
    __metaclass__ = ModelFac
    cursor = config["__cursor"]
    conn = config["__conn"]

    def __init__(self, **args):
        # __data should NOT contain Id field
        self.__data = {}
        self.__data.update(args)
        for k, v in args.items():
            attribute = getattr(self, k, None)
            if attribute:
                attribute.update(v)
            else:  # Can only be "Id"
                self.Id = v

    def update(self, **args):
        assert reduce(lambda x, y: x and y, [x in dir(self) for x in args])
        self.__data.update(args)

    def save(self):
        name = type(self).__name__
        if not self.Id:
            cmd = "insert into %s(%s) values(%s)" % \
                  (name, ",".join(self.__data.keys()),
                         ",".join(code_to_command(x) for x in self.__data.values()))
        else:
            set_str = ",".join([k+"="+code_to_command(v) for k,v in __data.items()])
            cmd = "update %s set %s where id=%d" % (name, set_str, self.Id)
        print "Executed: " + cmd
        self.cursor.execute(cmd)
        self.conn.commit()
        self.Id = self.cursor.lastrowid
        return self.Id

    def remove(self):
        cmd = "delete from %s where Id=%s" % (type(self).__name__, str(self.Id))
        self.cursor.execute(cmd)
        self.conn.commit()

    @classmethod
    def search(cls, **args):
        if not getattr(cls, "__attributes", None):
            cls.cursor.execute("PRAGMA table_info(%s)" % cls.__name__)
            cls.__attributes = [row[1] for row in cls.cursor.fetchall()]
        if args:
            cmd = "select * from %s where " % cls.__name__
            cmd += ",".join([k+"="+code_to_command(v) for k,v in args.items()])
        else:
            cmd = "select * from %s" % cls.__name__
        cls.cursor.execute(cmd)
        return [cls(**dict(zip(cls.__attributes, e))) \
                for e in cls.cursor.fetchall()]
