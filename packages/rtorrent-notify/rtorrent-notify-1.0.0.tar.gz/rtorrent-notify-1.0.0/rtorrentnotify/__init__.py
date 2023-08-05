# -*- coding: UTF-8 -*-
from datetime import datetime
import PyRSS2Gen as rss2
import socket
import getpass
import hashlib
import json

USER = getpass.getuser()
HOST = socket.gethostname()


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return dict(e=obj.name, n=obj.desc, d=obj.datetime)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        return json.JSONEncoder.default(self, obj)


class Decoder(json.JSONDecoder):
    def __init__(self, encoding):
        json.JSONDecoder.__init__(self, encoding, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        return Event(d['e'],
                     d['n'],
                     datetime.strptime(d['d'], '%Y-%m-%dT%H:%M:%S'))


class Event(object):
    def __init__(self, name, desc, dt=None):
        self.name = name
        self.desc = desc
        self.datetime = dt or datetime.utcnow()

    def get_title(self):
        return u"%s :: %s" % (self.name, self.desc)

    def __unicode__(self):
        return u"%s - %s" % (self.get_title(), self.datetime.strftime('%Y-%m-%d %H:%M'))

    def to_class(self, cls):
        return cls(self.name, self.desc, self.datetime)


class RssEvent(Event):
    def get_guid(self):
        return rss2.Guid("%s@%s:%s_%s" % (USER,
                         HOST,
                         self.name,
                         hashlib.md5(self.desc.encode('utf-8') + str(self.datetime)).hexdigest()),
                         False
                         )

    def build_rss(self):
        item = rss2.RSSItem(
            title=self.get_title(),
            guid=self.get_guid(),
            pubDate=self.datetime,
        )
        return item


class IrkerEvent(Event):
    def send(self, target):
        message = self.get_title()
        data = {'to': target, 'privmsg': message}
        s = socket.create_connection(('localhost', 6659))
        s.sendall(json.dumps(data))


class Events(object):
    def __init__(self, db, maxitems=20):
        self._events = []
        self.db = db
        self.maxitems = maxitems

    def save(self):
        events = self._events[:self.maxitems]
        self.db.truncate(0)
        json.dump(events, self.db, cls=Encoder)

    def load(self):
        try:
            self.db.seek(0)
            self._events = json.load(self.db, cls=Decoder)
        except ValueError:
            # first run
            self._events = []

    def append(self, event):
        self._events.insert(0, event)

    def build_rss(self):
        def to_rss(event):
            if not isinstance(event, RssEvent):
                event = event.to_class(RssEvent)
            return event
        feed = rss2.RSS2(
            title="rtorrent events for %s@%s" % (getpass.getuser(), socket.gethostname()),
            link="https://git.p.engu.in/laurentb/rtorrent-notify/",
            description="rtorrent events",
            lastBuildDate=datetime.utcnow(),
            items=(to_rss(event).build_rss() for event in self._events)
        )
        return feed

    def __unicode__(self):
        return u"\n".join(u"[%d] %s" % (i, event) for i, event in enumerate(self._events))
