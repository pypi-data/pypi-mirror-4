import sqlite3
import os
from datetime import datetime
from model import Model
from photo import Photo


class Album(Model):

    DB_TABLE_NAME = "albums"

    photo_id = None
    name = None
    updated_at = None
    created_at = None

    __photos = None
    __undownloaded_photos = None

    @property
    def undownloaded_photos(self):
        if self.__undownloaded_photos is None:
            self.__undownloaded_photos = Photo.where([{"key": "album_id", "value": self.album_id}, {"key": "downloaded", "value": 0}])

        return self.__undownloaded_photos

    @property
    def photos(self):
        if self.__photos is None:
            self.__photos = Photo.where("album_id", self.album_id)
        return self.__photos

    def __init__(self):
        pass

    @staticmethod
    def fromPicasa(picasa_album):
        album = Album()
        album.album_id = picasa_album.gphoto_id.text
        album.name = picasa_album.title.text
        album.updated_at = datetime.now()
        album.created_at = datetime.now()
        return album

    @staticmethod
    def fromDict(row):
        album = Album()
        album.album_id = row["id"]
        album.name = row["name"]
        album.updated_at = row["updated_at"]
        album.created_at = row["created_at"]
        return album

    def save(self):
        db = sqlite3.connect(os.path.join(os.getcwd(), Album.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.execute("""INSERT OR REPLACE INTO %s (id, name, updated_at, created_at)
                      VALUES (:id, :name, :updated_at, :created_at)""" % Album.DB_TABLE_NAME,
                      {"id": self.album_id,
                       "name": self.name,
                       "updated_at": self.updated_at,
                       "created_at": self.created_at})
        db.commit()
        db.close()

    @staticmethod
    def create_db(path=None):
        if path is None:
            path = os.getcwd()

        # Connect to and init table
        db = sqlite3.connect(os.path.join(path, Album.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS %s (
                     id VARCHAR PRIMARY KEY,
                     name VARCHAR,
                     updated_at TIMESTAMP,
                     created_at TIMESTAMP)
                  ''' % Album.DB_TABLE_NAME)

        db.commit()
        c.close()
        db.close()
