# -*- coding: UTF-8 -*-
from sys import argv
import os
import locale
import argparse

from rtorrentnotify import Event, Events, IrkerEvent


def parse(argv, encoding='utf-8'):
    def noner(v):
        if v and v.lower() != 'none':
            return v

    def unicd(v):
        return unicode(v, encoding)

    class JoinValues(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, u' '.join(values))

    parser = argparse.ArgumentParser(description='Register an event.')
    parser.add_argument('name', type=unicd,
                        help='Event name')
    parser.add_argument('desc', type=unicd, nargs='+', action=JoinValues,
                        help='Event description')
    parser.add_argument('-d', '--db', type=noner,
                        default=os.path.expanduser('~/rtorrent-notify.db'),
                        help='Database location')
    parser.add_argument('-r', '--rss', type=noner,
                        default=os.path.expanduser('~/rtorrent-notify.xml'),
                        help='RSS location')
    parser.add_argument('-i', '--irk', action='append', default=[],
                        help='Irker target')
    parser.add_argument('-n', '--irknick', action='append', default=[],
                        help='Irker target (nick)')
    return parser.parse_args(argv[1:])


def main():
    args = parse(argv, locale.getpreferredencoding())
    event = Event(args.name, args.desc)

    if args.db:
        with open(args.db, 'a+b') as db:
            events = Events(db)
            events.load()
            events.append(event)
            events.save()
    else:
        events = Events(None)
        events.append(event)

    if args.rss:
        feed = events.build_rss()
        with open(args.rss, 'w') as f:
            feed.write_xml(f, "utf-8")

    if args.irk or args.irknick:
        event = event.to_class(IrkerEvent)
        event.send(args.irk + ['%s,isnick' % t for t in args.irknick])
