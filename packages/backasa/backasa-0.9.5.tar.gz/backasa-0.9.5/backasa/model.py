import sqlite3
import os
from abc import ABCMeta, abstractmethod


class Model(object):
    __metaclass__ = ABCMeta

    DB_TABLE_NAME = ""
    DB = "backasa.sqlite"

    @abstractmethod
    def save(self):
        """ Provide Save Method """

    @abstractmethod
    def create_db(path):
        """ Make sure database exists and table for given object exists - @staticmethod """

    @abstractmethod
    def fromDict(row):
        """ Construct Instance from Dict - @staticmethod """

    @abstractmethod
    def fromPicasa(picasa_obj):
        """ Construct Instance from Picasa Equivilent - @staticmethod """

    def delete(self):
        db = sqlite3.connect(os.path.join(os.getcwd(), self.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.text_factory = str
        db.execute("DELETE FROM %s WHERE id = :id" % self.DB_TABLE_NAME, {"id": self.id})
        db.commit()
        db.close()

    @classmethod
    def find(cls, thing_id):
        db = sqlite3.connect(os.path.join(os.getcwd(), cls.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.text_factory = str
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute("SELECT * FROM %s WHERE id = :id" % cls.DB_TABLE_NAME, {"id": thing_id})
        row = c.fetchone()
        if row is None:
            c.close()
            db.close()
            return None
        else:
            thing = cls.fromDict(row)
            c.close()
            db.close()
            return thing

    @classmethod
    def where(cls, where_list):
        #build basic where statement
        sql = "SELECT * FROM %s WHERE " % cls.DB_TABLE_NAME
        for item in where_list[:-1]:
            sql += item["key"] + " = '" + item["value"] + "' AND "
        last_item = where_list[-1]
        sql += last_item["key"] + " = '" + str(last_item["value"]) + "'"
        db = sqlite3.connect(os.path.join(os.getcwd(), cls.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.text_factory = str
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute(sql)
        things = [cls.fromDict(row) for row in c]
        c.close()
        db.close()
        return things 

    @classmethod
    def findAll(cls):
        db = sqlite3.connect(os.path.join(os.getcwd(), cls.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.text_factory = str
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute("SELECT * FROM %s" % cls.DB_TABLE_NAME)
        things = [cls.fromDict(row) for row in c]
        c.close()
        db.close()
        return things

    @classmethod
    def findAllIds(cls):
        db = sqlite3.connect(os.path.join(os.getcwd(), cls.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.text_factory = str
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute("SELECT id FROM %s" % cls.DB_TABLE_NAME)
        rows = c.fetchall()
        return [row["id"] for row in rows]
