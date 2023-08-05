#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from StringIO import StringIO

from rtorrentnotify import Event, Events


def test_db():
    maxitems = 20
    db = StringIO()
    events = Events(db, maxitems)
    events.load()
    for n in range(1, 42):
        events.append(Event('LOL', 'cat %s' % n))
    e = Event('B', 'b')
    events.append(e)
    events.save()

    events = Events(db)
    events.load()
    assert events._events[0].datetime.ctime() == e.datetime.ctime()
    assert len(unicode(events).splitlines()) == maxitems


def test_add():
    events = Events(None)
    events.append(Event('LOL', 'cat'))
    events.append(Event('LOL', 'cat'))
    out = unicode(events)
    assert len(out.splitlines()) == 2


def test_rss():
    events = Events(None)
    events.append(Event('a', 'b'))
    events.append(Event('c', u'héhéhé'))

    feed = events.build_rss()
    out = StringIO()
    feed.write_xml(out, "utf-8")
    out = out.getvalue()
    assert 'guid' in out
