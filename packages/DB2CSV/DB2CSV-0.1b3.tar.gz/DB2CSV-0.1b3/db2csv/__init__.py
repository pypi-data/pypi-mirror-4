# Copyright (C) 2012 the DB2CSV authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .utf8csv import UnicodeWriter
import argparse
import csv
import datetime
import os
import os.path
import shutil
import tempfile
import urlparse
import zipfile


class Database(object):

    def __init__(self, db_uri, dst_dir, as_zip=True, verbose=False):
        self.db_uri = db_uri
        self.dst_dir = dst_dir
        self.as_zip = as_zip
        self.verbose = verbose
        self.engine = create_engine(db_uri, echo=verbose)
        self.Base = declarative_base()
        self.Base.metadata.bind = self.engine
        self.Base.metadata.reflect(self.engine, views=True)

    def archive(self, includes=None, excludes=None, chunk_size=None):

        if not os.path.exists(self.dst_dir):
            os.makedirs(self.dst_dir)

        if self.as_zip:
            dst = tempfile.mkdtemp()

        else:
            dst = self.dst_dir

        files =[]
        for name, table in self.Base.metadata.tables.items():
            if name in excludes or (includes and name not in includes):
                continue

            dst_file = os.path.join(dst, name) + '.{}.csv'
            files.extend(self.write_table_to_csv(table, dst_file, chunk_size))

        if self.as_zip:
            uri = urlparse.urlparse(self.db_uri).path.split('?')[0]
            now = datetime.datetime.now()
            format = '%Y-%m-%d_%H:%M:%S.%f'
            file_name = '{}_{}'.format(os.path.basename(uri),
                                                         now.strftime(format))
            dst_file = os.path.join(self.dst_dir, file_name + '.zip')
            with zipfile.ZipFile(dst_file, 'w') as myzip:
                for file_ in files:
                    myzip.write(file_, arcname=os.path.basename(file_))

            shutil.rmtree(dst)

    def write_table_to_csv(self, table, dst_file, chunk_size=None):

        cols = [col.name for col in table.columns]
        rows = [row for row in self.engine.execute(table.select())]
        files = []
        if not chunk_size:
            chunks = [rows]
        else:
            chunks = self.chunk_values(rows, chunk_size)

        for i, chunk in enumerate(chunks):
            file_ = dst_file.format(i)
            files.append(file_)
            with open(file_, 'wb') as csvfile:
                writer = UnicodeWriter(csvfile, quoting=csv.QUOTE_ALL)
                writer.writerow(cols)
                writer.writerows(chunk)

        return files

    def chunk_values(self, values, size):
        for i in xrange(0, len(values), size):
            yield values[i:i+size]


class Parser(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Export database tables as CSV files and archive them.')
        parser.add_argument('--uri',
                            dest='db_uri',
                            metavar='DATABASE_URI',
                            required=True,
                            help='The SQLAlchemy database URI: http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html?highlight=engine#database-urls')
        parser.add_argument('-d',
                            dest='dst_dir',
                            metavar='DESTINATION_DIR',
                            default='.',
                            help='The destination path of archived files. (Default: .)')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--include',
                           dest='includes',
                           default=[],
                           nargs='*',
                           help='The list of tables that must be included, other tables will be skipped.')
        group.add_argument('--exclude',
                           dest='excludes',
                           nargs='*',
                           default=[],
                           help='The list of tables that must be excluded from being archived.')
        parser.add_argument('--chunk-size',
                            dest='chunk_size',
                            type=int,
                            default=0,
                            help='Split exported rows into multiple files of $CHUNK_SIZE lines.')
        parser.add_argument('-z',
                            dest='zip',
                            default=False,
                            action='store_true',
                            help='Archive files as zip.')
        parser.add_argument('-v',
                            dest='verbose',
                            action='store_true',
                            help='Verbose mode.')
        self.parser = parser
        self.args = parser.parse_args()

    @property
    def db_uri(self):
        return self.args.db_uri

    @property
    def dst_dir(self):
        return self.args.dst_dir

    @property
    def zip(self):
        return self.args.zip

    @property
    def verbose(self):
        return self.args.verbose

    @property
    def includes(self):
        return self.args.includes

    @property
    def excludes(self):
        return self.args.excludes

    @property
    def chunk_size(self):
        return self.args.chunk_size
