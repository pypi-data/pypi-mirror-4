import sqlite3
import os
from datetime import datetime
from model import Model


class Photo(Model):

    DB_TABLE_NAME = "photos"

    photo_id = None
    album_id = None
    file_name = None
    url = None
    current_version = None
    downloaded = None
    updated_at = None
    created_at = None

    __album = None

    def __init__(self):
        pass

    @property
    def album(self):
        if self.__album is None:
            self.__album = Album.find(self.album_id)
        return self.__album

    @staticmethod
    def fromPicasa(picasa_photo):
        photo = Photo()
        photo.photo_id = picasa_photo.gphoto_id.text
        photo.album_id = picasa_photo.albumid.text
        photo.file_name = picasa_photo.content.src.split('/')[-1].split('#')[0].split('?')[0]
        photo.url = picasa_photo.media.content[0].url
        photo.current_version = int(picasa_photo.version.text)
        photo.downloaded = False
        photo.updated_at = datetime.now()
        photo.created_at = datetime.now()
        return photo

    @staticmethod
    def fromDict(_dict):
        photo = Photo()
        photo.photo_id = _dict["id"]
        photo.album_id = _dict["album_id"]
        photo.file_name = _dict["file_name"]
        photo.url = _dict["url"]
        photo.current_version = _dict["current_version"]
        photo.downloaded = bool(_dict["downloaded"])
        photo.updated_at = _dict["updated_at"]
        photo.created_at = _dict["created_at"]
        return photo

    def save(self):
        db = sqlite3.connect(os.path.join(os.getcwd(), Photo.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        db.execute("""INSERT OR REPLACE INTO %s (id, album_id, file_name, url, current_version, downloaded, updated_at, created_at)
                      VALUES (:id, :album_id, :file_name, :url, :current_version, :downloaded, :updated_at, :created_at)""" % Photo.DB_TABLE_NAME,
                      {"id": self.photo_id,
                       "album_id": self.album_id,
                       "file_name": self.file_name,
                       "url": self.url,
                       "current_version": self.current_version,
                       "downloaded": self.downloaded,
                       "updated_at": self.updated_at,
                       "created_at": self.created_at})
        db.commit()
        db.close()

    @staticmethod
    def create_db(path=None):
        if path is None:
            path = os.getcwd()

        # Connect to and init table
        db = sqlite3.connect(os.path.join(path, Photo.DB), detect_types=sqlite3.PARSE_DECLTYPES)
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS %s (
                     id VARCHAR PRIMARY KEY,
                     album_id VARCHAR,
                     file_name VARCHAR,
                     url VARCHAR,
                     current_version Integer,
                     downloaded Integer,
                     updated_at TIMESTAMP,
                     created_at TIMESTAMP)
                  ''' % Photo.DB_TABLE_NAME)

        db.commit()
        c.close()
        db.close()
