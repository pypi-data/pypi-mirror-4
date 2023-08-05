# vim: set fileencoding=utf-8 sw=4 ts=4 et :

# bedup - Btrfs deduplication
# Copyright (C) 2012 Gabriel de Perthuis <g2p.code+bedup@gmail.com>
#
# This file is part of bedup.
#
# bedup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# bedup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bedup.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import collections
import os
import sqlalchemy
import sys
import xdg.BaseDirectory  # pyxdg, apt:python-xdg

from contextlib import closing
from sqlalchemy.orm import sessionmaker

from .btrfs import find_new, get_root_generation
from .dedup import dedup_same, FilesInUseError
from .ioprio import set_idle_priority
from .model import META
from .syncfs import syncfs
from .termupdates import TermTemplate
from .tracking import (
    show_vols, get_vol, track_updated_files, dedup_tracked, forget_vol)


APP_NAME = 'bedup'


def cmd_dedup_files(args):
    try:
        return dedup_same(args.source, args.dests, args.defragment)
    except FilesInUseError as exn:
        exn.describe(sys.stderr)
        return 1


def cmd_find_new(args):
    volume_fd = os.open(args.volume, os.O_DIRECTORY)
    if args.zero_terminated:
        sep = '\0'
    else:
        sep = '\n'
    # May raise FindError, let Python print it
    find_new(volume_fd, args.generation, sys.stdout, terse=args.terse, sep=sep)


def cmd_show_vols(args):
    sess = get_session(args)
    show_vols(sess)


def sql_setup(dbapi_con, con_record):
    cur = dbapi_con.cursor()
    # Uncripple the SQL implementation
    cur.execute('PRAGMA foreign_keys = ON')
    cur.execute('PRAGMA foreign_keys')
    val = cur.fetchone()
    assert val == (1,), val

    # So that writers do not block readers
    # https://www.sqlite.org/wal.html
    cur.execute('PRAGMA journal_mode = WAL')
    cur.execute('PRAGMA journal_mode')
    val = cur.fetchone()
    assert val == ('wal',), val


def get_session(args):
    if args.db_path is None:
        data_dir = xdg.BaseDirectory.save_data_path(APP_NAME)
        args.db_path = os.path.join(data_dir, 'db.sqlite')
    url = sqlalchemy.engine.url.URL('sqlite', database=args.db_path)
    engine = sqlalchemy.engine.create_engine(url, echo=args.verbose_sql)
    sqlalchemy.event.listen(engine, 'connect', sql_setup)
    Session = sessionmaker(bind=engine)
    sess = Session()
    META.create_all(engine)
    return sess


def vol_cmd(args):
    with closing(TermTemplate()) as tt:
        # Adds about 1s to cold startup
        sess = get_session(args)
        volumes = set(
            get_vol(sess, volpath, args.size_cutoff) for volpath in args.volume)
        vols_by_fs = collections.defaultdict(list)

        if args.command == 'forget-vol':
            for vol in volumes:
                forget_vol(sess, vol)

        if args.command in ('scan-vol', 'dedup-vol'):
            set_idle_priority()
            for vol in volumes:
                if args.flush:
                    tt.format('{elapsed} Flushing %r' % vol.desc)
                    syncfs(vol.fd)
                    tt.format(None)
                # May raise IOError
                track_updated_files(sess, vol, tt)
                vols_by_fs[vol.fs].append(vol)

        if args.command == 'dedup-vol':
            for volset in vols_by_fs.itervalues():
                dedup_tracked(sess, volset, tt)


def cmd_generation(args):
    volume_fd = os.open(args.volume, os.O_DIRECTORY)
    if args.flush:
        syncfs(volume_fd)
    generation = get_root_generation(volume_fd)
    print('%d' % generation)


def sql_flags(parser):
    parser.add_argument(
        '--db-path', dest='db_path',
        help='Override the location of the sqlite database')
    parser.add_argument(
        '--verbose-sql', action='store_true', dest='verbose_sql',
        help='print SQL statements being executed')


def vol_flags(parser):
    parser.add_argument('volume', nargs='+', help='btrfs volumes')
    sql_flags(parser)
    parser.add_argument(
        '--size-cutoff', type=int, dest='size_cutoff',
        help='Change the minimum size (in bytes) of tracked files '
        'for the listed volumes. '
        'Lowering the cutoff will trigger a partial rescan of older files.')


def scan_flags(parser):
    vol_flags(parser)
    parser.add_argument(
        '--flush', action='store_true', dest='flush',
        help='Flush outstanding data using syncfs before scanning volumes')


def main(argv):
    parser = argparse.ArgumentParser(prog='python -m bedup')
    commands = parser.add_subparsers(dest='command')

    sp_scan_vol = commands.add_parser('scan-vol', description="""
Scans listed volumes to keep track of potentially duplicated files.""")
    sp_scan_vol.set_defaults(action=vol_cmd)
    scan_flags(sp_scan_vol)

    sp_dedup_vol = commands.add_parser('dedup-vol', description="""
Runs scan-vol, then deduplicates identical files.""")
    sp_dedup_vol.set_defaults(action=vol_cmd)
    scan_flags(sp_dedup_vol)

    sp_forget_vol = commands.add_parser('forget-vol', description="""
Forget tracking data for the listed volumes. Mostly useful for testing.""")
    sp_forget_vol.set_defaults(action=vol_cmd)
    vol_flags(sp_forget_vol)

    sp_show_vols = commands.add_parser('show-vols', description="""
Shows known volumes.""")
    sp_show_vols.set_defaults(action=cmd_show_vols)
    sql_flags(sp_show_vols)

    sp_dedup_files = commands.add_parser(
        'dedup-files', description="""
Freezes files, checks them for being identical,
and projects the extents of the first file onto the other files.

The effects are visible with filefrag -v (apt:e2fsprogs),
which displays the extent map of files.
        """.strip())
    sp_dedup_files.set_defaults(action=cmd_dedup_files)
    sp_dedup_files.add_argument('source', metavar='SRC', help='source file')
    sp_dedup_files.add_argument(
        'dests', metavar='DEST', nargs='+', help='dest files')
    sp_dedup_files.add_argument(
        '--defragment', action='store_true',
        help='defragment the source file first')

    sp_generation = commands.add_parser(
        'generation', description="""
Show the btrfs generation of VOLUME""")
    sp_generation.set_defaults(action=cmd_generation)
    sp_generation.add_argument('volume', help='btrfs volume')
    sp_generation.add_argument(
        '--flush', action='store_true', dest='flush',
        help='Flush outstanding data using syncfs before lookup')

    sp_find_new = commands.add_parser(
        'find-new', description="""
lists changes to volume since generation

This is a reimplementation of btrfs find-new,
modified to include directories as well.""")
    sp_find_new.set_defaults(action=cmd_find_new)
    sp_find_new.add_argument(
        '-0|--zero-terminated', dest='zero_terminated', action='store_true',
        help='use a NUL character as the line separator')
    sp_find_new.add_argument(
        '--terse', dest='terse', action='store_true', help='print names only')
    sp_find_new.add_argument('volume', help='volume to search')
    sp_find_new.add_argument(
        'generation', type=int, nargs='?', default=0,
        help='only show items modified at generation or a newer transaction')

    args = parser.parse_args(argv[1:])
    return args.action(args)


def script_main():
    # site.py takes about 1s before main gets called
    sys.exit(main(sys.argv))


if __name__ == '__main__':
    script_main()

