""" To get information about system files """
from os.path import isfile,getmtime
import time
import datetime

import logging
import subprocess

class MediaInfoError (Exception):pass
class SoxError (Exception):pass
class IsNotFile (Exception):pass
class FormatNotSupported (Exception):pass

MediaInfoType={"MPEG Audio":"mp3",
               "Vorbis":"ogg",
               "FLAC":"flac"}


def __get_status_output(cmd, input=None, cwd=None, env=None):
    pipe = subprocess.Popen(cmd, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output, errout) = pipe.communicate(input=input)
    assert not errout
    status = pipe.returncode
    return (status, output)

def format(path):
    """Return the format (mp3, flac,...) of a file. If format is not supported, raise FormatNotSupported."""

    if not isfile(path) : 
        raise IsNotFile(path)
    t=__get_status_output('mediainfo --Inform="General;%%Format%%" "%s"' % path)
    if t[0] != 0:raise MediaInfoError(path)
    ret=t[1].rstrip()
    try:
        return MediaInfoType[ret]
    except KeyError:raise FormatNotSupported(path)

def duration(path):
    """Get the duration of a file (in seconds)."""
    t=__get_status_output('mediainfo --Inform="Audio;%%Duration%%" "%s"' % path)
    if t[0] != 0:raise MediaInfoError
    ret=t[1].rstrip()
    if ret=="":raise Exception(t) #return None
    return int(ret)/1000

def modification_date(path):
    if not isfile(path) : 
        logging.warning("Is not a file : %s " % path)
        return None
    return datetime.datetime.utcfromtimestamp(getmtime(path))



import sys
import gobject
gobject.threads_init()

# Shity kack to avoid gst parsing arguments ...
tmpArgv=sys.argv ; sys.argv=[]
import pygst
pygst.require("0.10")
import gst
import gst ; sys.argv=tmpArgv

def chromaprint(path):
    bin = gst.parse_launch("filesrc name=source ! decodebin ! audioconvert ! chromaprint name=chromaprint0 duration=60 ! fakesink sync=0 silent=TRUE")
    source = bin.get_by_name("source")
    source.set_property("location", path)

    mainloop = gobject.MainLoop()

    bus = bin.get_bus()
    bus.add_signal_watch()
    bus.connect('message::eos', lambda a,b : mainloop.quit())

    bin.set_state(gst.STATE_PLAYING)
    mainloop.run()

    format = gst.Format(gst.FORMAT_TIME)
    length = bin.query_duration(format)[0] / gst.SECOND
    bin.set_state(gst.STATE_NULL)

    chromaprint = bin.get_by_name("chromaprint0")
    fingerprint = chromaprint.get_property("fingerprint")
    return (length,fingerprint)


def fingerprint(path):
    format(path)
    return chromaprint(path)[1]

import urllib, urllib2
from xml.etree import ElementTree
def chromaprintInfo(path):
    cp=chromaprint(path)
    print "Looking up fingerprint"

    data = {}
    data['client'] = 'IUThVP5T'
    data['meta'] = '2'
    data['length'] = str(cp[0])
    data['fingerprint'] = cp[1]
    resp = urllib2.urlopen('http://api.acoustid.org/lookup', urllib.urlencode(data))
    tree = ElementTree.parse(resp)
    results = tree.findall('results/result')
    if results:
        print 'Found %s matching song(s):' % (len(results),)
        for result in results:
            print
            print 'Score:', result.find('score').text
            print 'ID:', result.find('id').text
            for track in result.findall('tracks/track'):
                print 'http://musicbrainz.org/track/%s.html' % track.find('id').text
    else:
        print 'No matching songs found'


def fingerprint_md5(path):
    f=format(path)
    if f == None : return None
    p1 = Popen(['sox -t %s "%s" -t wav -' % (f,path)], stdout=PIPE,stderr=PIPE,shell=True)
    p2 = Popen(["dd bs=1 count=%dkB |md5sum"% 500], stdin=p1.stdout , stdout=PIPE,stderr=PIPE, shell=True)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()
    p1.wait()
    retcode=p1.returncode
#    p2.terminate() #useless ?
#    p1.terminate() #useless ?
    if retcode != 0 :
        logging.warning("Sox return a bad return code on file '%s'" % path)
        raise SoxError
        return None
    md5=output[0].split(" ")[0]
    logging.debug("format='%s' ; md5='%s' ; filepath='%s'" % (f,md5,path))
    return (md5)









