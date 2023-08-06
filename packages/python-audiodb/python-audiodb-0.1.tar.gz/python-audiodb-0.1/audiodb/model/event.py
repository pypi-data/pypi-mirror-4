import logging

from audiodb.core.db import *

class Event(object):
    """Event is the base class of the event logger engine. It contains the
    base field for all event and the static method Add used to add an
    event to db."""
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    frontend = Column(String(64))
    backend = Column(String(64))
    hostname = Column(String(64))
    version = Column(String(64))

    @classmethod
    def Add(cls,*params,**kwds):
        """Create an cls object and add it to the db. If an error
        occurs, it return None"""
#        try:
        a=cls(*params,**kwds)
        # except FileError as e: 
        #     logging.info(e)
        #     return None
        # except TypeError as e: 
        #     logging.error("%s : %s " % (cls.__name__,e))
        #     return None
        Db.session.add(a)
        Db.session.commit()
        logging.info("%s" % a)
        return a
        
    def __init__(self,frontend="pimp"):
        self.date = datetime.now()
        self.frontend = frontend
        self.backend = "unspecified"
        self.hostname = "unspecified"
        self.version = "Version TODO"
        
    def __repr__(self):
        return "%s id:%s" % (self.__class__.__name__,self.id)

    @classmethod
    def Lasts(cls,number=None,til=None):
        """ Return 'number' lasts events or 100 lasts events if number is None """ 
        return Db.session.query(cls).order_by(desc(cls.date)).limit(number or 100).all()

    @classmethod
    def All(cls):
        return Db.session.query(cls).all()

    @classmethod
    def ByDate(cls,date_min,date_max):
        return Db.session.query(cls).filter((cls.date > date_min) & (cls.date < date_max)).all()




class FileEvent(Event):
    """ A fileEvent is an event on a file.  
    """
#    zicApt = Column(String(32))
    # For sqlalchemy
    @declared_attr
    def fileId(cls):
        return Column(Integer, ForeignKey('file.id'))
    # For sqlalchemy
    @declared_attr
    def file(cls):
        return relationship(File,primaryjoin="%s.fileId == File.id" % cls.__name__) #,order_by=desc(File.date))
        # return relationship(File,primaryjoin="%s.zicApt == File.zicApt" % cls.__name__,
        #                     order_by=desc(File.date),
        #                     foreign_keys=File.zicApt,
        #                     uselist=False,lazy='immediate')


    @declared_attr
    def song_id(cls):
        return Column(Integer, ForeignKey('song.id'))
    # For sqlalchemy
    @declared_attr
    def song(cls):
        return relationship(Song) #,primaryjoin="%s.song_id == Song.id" % cls.__name__) #,order_by=desc(File.date))


    @classmethod
    def FindByPath(cls,path):
        """ Find all cls events for the path.  Path can be a partial string path.
        See method:'FindBySong' for more information about path"""
        if type(path) is str:path=Path(path)
        return Db.session.query(cls).join(File).filter(File.path.like('%'+path+'%')).all() 

    @classmethod
    def FindBySong(cls,path):
        """ High level search function. Find all cls events for the
        zicApt associated to the path. Path can be a partial string
        path.  If many entry of file matched to pattern exist, it
        return all events associated to its zicApt. The last filepath
        of this zicApt is returned. Respond is a list sorted by
        filepath. Even if a file has been moved, it returns all
        records.  Path should be a string or implement Path class."""
        if type(path) is str:path=Path(path)
        return Db.session.query(cls).join((File, cls.zicApt==File.zicApt)).filter(File.path.like('%'+path+'%')).all() 


    def __init__(self,path,**kwds):
        Event.__init__(self,**kwds)
        self.file=File.Get(path)
        if self.file == None :
            raise FileError(path)
        self.fileId = self.file.id
        self.song_id = self.file.song_id

    def __repr__(self):
        return "%s , fileid:%s , file:%s" % (Event.__repr__(self),self.fileId, self.file.path)

    def getPath(self):
        return self.file
