#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Fri Apr 20 12:04:44 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Commands the AT&T database can respond to.
"""

import os
import sys
from bob.db.driver import Interface as BaseInterface

def dumplist(args):
  """Dumps lists of files based on your criteria."""

  from .__init__ import Database
  db = Database()

  r = db.objects(
      groups=args.group,
      purposes=args.purpose,
      model_ids=args.client
  )

  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  for f in r:
    output.write('%s\n' % f.make_path(directory=args.directory, extension=args.extension))

  return 0


def checkfiles(args):
  """Checks the existence of the files based on your criteria."""

  from .__init__ import Database
  db = Database()

  r = db.objects()

  # go through all files, check if they are available
  good = {}
  bad = {}
  for f in r:
    if os.path.exists(f.make_path(directory=args.directory, extension=args.extension)): good[f.id] = f.make_path(directory=args.directory, extension=args.extension)
    else: bad[f.id] = f.make_path(directory=args.directory, extension=args.extension)

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  if bad:
    for f in bad:
      output.write('Cannot find file "%s"\n' % (f,))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(r), args.directory))

  return 0


def reverse(args):
  """Returns a list of file database identifiers given the path stems"""

  from .query import Database
  db = Database()

  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  r = db.reverse(args.path)
  for f in r: output.write('%s\n' % f.id)

  if not r: return 1

  return 0


def path(args):
  """Returns a list of fully formed paths or stems given some file id"""

  from .query import Database
  db = Database()

  output = sys.stdout
  if args.selftest:
    from bob.db.utils import null
    output = null()

  r = db.paths(args.id, prefix=args.directory, suffix=args.extension)
  for path in r: output.write('%s\n' % path)

  if not r: return 1

  return 0



class Interface(BaseInterface):

  def name(self):
    return 'atnt'

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('xbob.db.%s' % self.name())[0].version

  def files(self):
    return ()

  def type(self):
    return 'python_integrated'

  def add_commands(self, parser):

    from . import __doc__ as docs

    subparsers = self.setup_parser(parser,
        "AT&T/ORL Face database", docs)

    from . import Database
    from .models import Client
    import argparse

    db = Database()

    # add the dumplist command
    dump_parser = subparsers.add_parser('dumplist', help="Dumps list of files based on your criteria")
    dump_parser.add_argument('-d', '--directory', default='', help="if given, this path will be prepended to every entry returned.")
    dump_parser.add_argument('-e', '--extension', default='', help="if given, this extension will be appended to every entry returned.")
    dump_parser.add_argument('-C', '--client', type=int, help="if given, limits the dump to a particular client.", choices=Client.m_valid_client_ids)
    dump_parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular group.", choices=db.m_groups)
    dump_parser.add_argument('-p', '--purpose', help="if given, this value will limit the output files to those belonging to a particular purpose.", choices=db.m_purposes)
    dump_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    dump_parser.set_defaults(func=dumplist) #action

    # add the checkfiles command
    check_parser = subparsers.add_parser('checkfiles', help="Check if the files exist, based on your criteria")
    check_parser.add_argument('-d', '--directory', required=True, help="the path to the AT&T images.")
    check_parser.add_argument('-e', '--extension', default=".pgm", help="the extension of the AT&T images default: '.pgm'.")
    check_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    check_parser.set_defaults(func=checkfiles) #action

    # adds the "reverse" command
    parser = subparsers.add_parser('reverse', help=reverse.__doc__)
    parser.add_argument('path', nargs='+', help="one or more path stems to look up. If you provide more than one, files which cannot be reversed will be omitted from the output.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=reverse) #action

    # adds the "path" command
    parser = subparsers.add_parser('path', help=path.__doc__)
    parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    parser.add_argument('id', type=int, nargs='+', help="one or more file ids to look up. If you provide more than one, files which cannot be found will be omitted from the output. If you provide a single id to lookup, an error message will be printed if the id does not exist in the database. The exit status will be non-zero in such case.")
    parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    parser.set_defaults(func=path) #action

