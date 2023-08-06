#!/usr/bin/env python

"""To load templates."""

from argparse import ArgumentParser, REMAINDER
from distutils.dir_util import copy_tree
from flask.ext.script import prompt_bool
from imp import load_source
from os import mkdir
from os.path import abspath, dirname, join, sep
from sys import argv, path

from project import current_project

parser = ArgumentParser('flasker')

parser.add_argument(
  '-f',
  '--file',
  default='project.py',
  dest='file',
  help='filepath to module where the project lies [project.py]'
)

parser.add_argument(
  'command',
  nargs=REMAINDER,
  help="""
    available options: new, server*, shell*, worker*, flower*
    (* commands only available with a valid project file).
    type `flasker command -h` for detailed help on each command
  """
)

def main():
  args = parser.parse_args()
  if not args.command:
    parser.print_help()
  elif args.command == ['new']:
    if prompt_bool('Start a new project'):
      src = join(dirname(__file__), 'examples')
      # copy project files
      copy_tree(join(src, '1'), '.')
      # copy html files
      copy_tree(join(src, 'templates'), join('app', 'templates'))
      # create default directories
      mkdir(join('app', 'static'))
      for folder in ['celery', 'db', 'logs']:
        mkdir(folder)
  else:
    try:
      path.append(abspath('.')) # necessary for reloader to work
      load_source('project', args.file)
    except (IOError, ImportError) as e:
      print '%s (%s)' % (e, args.file)
    else:
      # hackish to work with flask-script manager and the server reloader...
      while len(argv) > 1: argv.pop()
      argv.extend(args.command)
      __import__('flasker.manager')

if __name__ == '__main__':
  main()
