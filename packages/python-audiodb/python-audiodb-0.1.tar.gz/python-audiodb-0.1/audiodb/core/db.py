"""Db module provides an high level database access to log files and
events. This module is a paranoid logger in order to log file moving,
tag modification, file renaming in a transparency manner.

WARNING: To use it, you must initialize Db class !

The main table of the db is the table file. A file element is the path
of an audio file and some informations such as type, modification
date, duration and audio fingerprint. The File class permits to ask
(through Get static method) the db if a file is already known. If the
file is already known, the Get method returns the id of the database
entry. If the path file is not known, an entry is created. For more
information, see File.Get method information.

To create an new event, create a class that inherited FileEvent or Event.

All method attributes 'path' must implement getPath() method. Path class is a string wrapper.
All method name ended by Song use zicApt in dbquery

"""


#import common
import file

from sqlalchemy import  create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime , desc
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.sql.expression import func
from sqlalchemy.pool import StaticPool
from datetime import datetime

import logging
logging.basicConfig(filename='example.log',level=logging.DEBUG)
logger=logging
#logger.setLevel(logging.DEBUG)

version=1.5
fingerprint_length=6000


class Path(unicode):
    """ A default Path class implementation. Use it to add a string
    path to the database. """
    def getPath(self): return self


class Db(object):
    """This class configures sqlalchemy database engine.
    It is used by all events to access the database.
    Method Configure MUST be called during initialisation."""
    Base = declarative_base()

    @staticmethod
    def Configure(engine):
        """ Called to initialize database module """
        Db.engine=engine
        Db.session = sessionmaker(bind=Db.engine)()
        Db.Base.metadata.create_all(Db.engine)
        logger.info("Database loaded")

    @staticmethod
    def ConfigureMySQL(database,user,password):
        engine=create_engine("mysql://%s:%s@localhost/%s" % (user,password,database),pool_recycle=3600)
        Db.Configure(engine)

    @staticmethod
    def ConfigureSqlite(dbfile):
        engine=create_engine('sqlite:///%s'%dbfile,assert_unicode=(True))
#        engine.text_factory = str
        Db.Configure(engine)

    @staticmethod
    def ConfigureUrl(url):
        engine=create_engine(url,connect_args={'check_same_thread':False})#,poolclass=StaticPool) #, encoding='utf8')
#        engine.text_factory = str
#        engine.raw_connection().connection.text_factory = str
        Db.Configure(engine)
        

# Use to manage file error ... shity -> TODO.
class FileError(Exception):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return repr("FileError on '%s'" % self.path)


class Song(Db.Base):
    """ Song Table """
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    who = Column(String(64))
    hostname = Column(String(64))
    version = Column(String(64))
    fingerprint = Column(String(fingerprint_length))
    fingerprint_version = Column(String(64))
    duration = Column(Integer)

    def __init__(self,fingerprint,duration,frontend='default'):
        self.date = datetime.now()
        self.who = frontend
        self.version = version
        self.fingerprint = fingerprint
        self.fingerprint_version = "TODO;"
        self.duration = duration


class File(Db.Base):
    """ File Table """
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    who = Column(String(64))
    hostname = Column(String(64))
    version = Column(String(64))
    format = Column(String(16))
    path = Column(String(1024))
    lastModDate = Column(DateTime)
    duration = Column(Integer)
    song_id = Column(Integer, ForeignKey('song.id'))

    song = relationship("Song", backref=backref('files', order_by=desc(date)))

    def getPath(self):
        return self.path

    @staticmethod
    def Add(path,frontend='default'):
        """Get a file from the db or create an entry in the db and return it.
        Path should be a str or implement getPath method.
        An entry is added if:
        
        * the path is not found
        * the modification date in db is older than modification date of the file

        """
        if isinstance(path,basestring):path=Path(path) # Hack !
        ret=Db.session.query(File).filter(File.path==path.getPath()).order_by(desc(File.date)).limit(1).first()
        if ret != None:
            mdfile = file.modification_date(path.getPath())
            mddb = ret.lastModDate
            if mdfile > mddb:
                print "File '%s' has been modified" % path.getPath()
                print "A new entry is created"
            else :
                return ret
        f = file.format(path.getPath())
        fingerprint = file.fingerprint(path.getPath())
        dur = file.duration(path.getPath())
        if dur == None :
            raise Exception()
        fdb=File(path,f,dur,frontend=frontend)
        song=Db.session.query(Song).filter(Song.fingerprint==fingerprint).limit(1).first()
        if song == None:
            song=Song(fingerprint,dur)
        fdb.song=song
        Db.session.add(fdb)
        Db.session.commit()
        return fdb


    @staticmethod
    def Get(path,frontend="pimp"):
        """Get a file from the db or create an entry in the db and return it.
        Path should be a str or implement getPath method.
        An entry is added if:
        
        * the path is not found
        * the modification date in db is older than modification date of the file

        """
        if isinstance(path,basestring):path=Path(path) # Hack !
        ret=Db.session.query(File).filter(File.path==path.getPath()).order_by(desc(File.date)).limit(1).first()
        if ret == None:
            return File.Add(path)
        return ret

    @staticmethod
    def Find(path,limit=None):
        """ Find all files matching path pattern, and sort them by
        date. arg:'limit' is not implemented. Path should be a str or
        implement getPath method."""
        if isinstance(path,basestring):path=Path(path)
        ret=Db.session.query(File).filter(File.path.like('%'+path.getPath()+'%')).order_by(desc(File.date)).all()
        return ret

    def update(self):
        Db.session.add(self)
        Db.session.commit()

    @staticmethod
    def All():
        """ Return all file row """
        return Db.session.query(File).all()

    @staticmethod
    def Lasts(number=None):
        """ Return 'number' lasts events or 100 lasts events if number is None """ 
        return Db.session.query(File).order_by(desc(File.date)).limit(number or 100).all()

    def __init__(self,path,format,duration,frontend):
        self.date = datetime.now()
        self.who = frontend
        self.hostname = "Unused"
        self.version = version
        self.format = format
        self.path = path.getPath()
        self.lastModDate = file.modification_date(path.getPath())
        self.duration = duration
        
        
    def __repr__(self):
        return "File %s, %s ,%s, %s , %s , %s" % (self.id, self.date, self.who, self.format, self.path, self.song)


    






