import audiodb.model.player as player

import audiodb.core.db as db

import audiodb.model.event as event
#import argparse
import os
import datetime

class Timeline(db.Db.Base):
    __tablename__ = 'timeline'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer)
    starttime = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    song = db.relationship("Song") #, backref=db.backref('files', order_by=db.desc(date)))


    def __init__(self,date,starttime,duration,song_id): 
        self.date = date
        self.starttime = starttime
        self.duration = duration
        self.song_id = song_id

        db.Db.session.add(fdb)
        db.Db.session.commit()


def parse_args(args):
    compute(args)

def parser(subparsers):
    parser = subparsers.add_parser('timeline', help='timeline commands') #,parents=[parser_selector])
    parser.add_argument('-d','--db',type=str,required=True,help="Sqlite database file")
#    parser.add_argument('-u','--url',type=str,required=True,help="SqlAlchemy database url (ex:'sqlite:///database-file', mysql://user:pwd@localhost/database)")
    parser.set_defaults(func=parse_args)


def compute(args):
    db.Db.ConfigureSqlite(os.path.abspath(args.db))
    for p in player.Play.All():
        s_dur=p.file.duration
        td=datetime.timedelta(seconds=p.file.duration)
        event_start=p.date
        print event_start,s_dur,event_start+td
        for e in player.Pause.ByDate(event_start,event_start+td):
            print "\tpause",e.date,e.file.path
        for e in player.Play.ByDate(event_start,event_start+td):
            print "\tplay",e.date,e.file.path
        for e in player.Stop.ByDate(event_start,event_start+td):
            print "\tstop",e.date,e.file.path
