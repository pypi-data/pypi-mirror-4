#!/usr/bin/env python

"""Flasker command line tool.

There are currently 5 commands available via the flasker command tool, all
detailed below.

All commands, aside from ``new``, accept an optional argument ``-c, --conf``
to indicate the path of the configuration file to use. If none is specified
flasker will search in the current directory for possible matches. If a single
file ``.cfg`` file is found it will use it.

"""

from argparse import ArgumentParser, REMAINDER
from code import interact
from distutils.dir_util import copy_tree
from functools import wraps
from os import listdir, mkdir
from os.path import abspath, dirname, exists, join, splitext
from re import findall
from shutil import copy

from flasker import current_project
from flasker.project import Project, ProjectImportError


def _project_context(handler):
  """Create the project context.

  Some (most) subparser handlers require the project to be created before
  returning, this decorator handles this.

  """
  @wraps(handler)
  def wrapper(*args, **kwargs):
    parsed_args = args[0]
    try:
      conf_file = parsed_args.conf
      if not conf_file:
        conf_files = [fn for fn in listdir('.') if splitext(fn)[1] == '.cfg']
        if len(conf_files) == 0:
          print (
            'No configuration file found in current directory. '
            'Please enter a path to one with the -c option.'
          )
          return
        elif len(conf_files) > 1:
          print (
            'Several configuration files found in current directory: %s. '
            'Please disambiguate with the -c option.'
          ) % ', '.join(conf_files)
          return
        else:
          conf_file = conf_files[0]
      pj = Project(conf_file, make=False)
    except ProjectImportError as e:
      print e
      return
    else:
      pj._make()
      handler(*args, **kwargs)
  return wrapper


# Parsers

# Main parser

parser = ArgumentParser('flasker')

parser.add_argument('-c', '--conf',
  dest='conf',
  default='',
  help='path to configuration file'
)
subparsers = parser.add_subparsers(
  title='available commands',
  dest='command',
)

# New

new_parser = subparsers.add_parser('new', help='start new project')

new_parser.add_argument('-a', '--app',
  action='store_false',
  help='don\'t include basic bootstrap app template'
)
new_parser.add_argument('-n', '--name',
  default='default',
  help='name of the new config file [%(default)s]'
)
new_parser.add_argument('config',
  choices=[
    splitext(name)[0]
    for name in listdir(join(dirname(__file__), 'data', 'configs'))
  ],
  help='the type of config to create'
)

def new_handler(parsed_args):
  """Create a new project::

    flasker new ...

  The following options are available:

  * ``-a, --app`` to toggle the creation of a bootstrap starter app
  * ``-n, --name`` to set the name of the configuration file to be created
    (defaults to ``default``)

  """
  src = dirname(__file__)
  conf_name = '%s.cfg' % parsed_args.name
  if exists(conf_name):
    print (
      'There already exists a configuration file with this name. '
      'Please enter a different name with the -n option.'
    )
  else:
    copy(join(src, 'data', 'configs', '%s.cfg' % parsed_args.config), conf_name)
    print 'Project configuration file created!'
  if parsed_args.app:
    if exists('app'):
      print (
        'There already seems to be an app folder here. '
        'App creation skipped.'
      )
    else:
      mkdir('app')
      copy_tree(join(src, 'data', 'app'), 'app')
      print 'Bootstrap app folder created!'

new_parser.set_defaults(handler=new_handler)

# Server

server_parser = subparsers.add_parser('server', help='start server')

server_parser.add_argument('-r', '--restrict',
  action='store_true',
  help='disallow remote server connections'
)
server_parser.add_argument('-p', '--port',
  default=5000,
  type=int,
  help='listen on port [%(default)s]'
)
server_parser.add_argument('-d', '--debug',
  action='store_true',
  help='run in debug mode (autoreload and debugging)'
)

@_project_context
def server_handler(parsed_args):
  """Start a Werkzeug server for the Flask application::
  
    flasker server ...

  The following options are available:

  * ``-r, --restrict`` to disallow remove server connections.
  * ``-p, --port`` to set the port on which to run the server (default to 
    ``5000``).
  * ``-d, --debug`` to run in debug mode (enables autoreloading and in-browser
    debugging).
  
  """
  pj = current_project
  host = '127.0.0.1' if parsed_args.restrict else '0.0.0.0'
  pj.flask.run(host=host, port=parsed_args.port, debug=parsed_args.debug)

server_parser.set_defaults(handler=server_handler)

# Shell

shell_parser = subparsers.add_parser('shell', help='start shell')

@_project_context
def shell_handler(parsed_args):
  """Start a shell in the context of the project::

    flasker shell ...

  The following global variables will be available:

  * ``pj``, an alias for the ``current_project``

  Flasker will use IPython if it is available.
  
  """
  pj = current_project
  context = {
    'pj': pj,
  }
  try:
    import IPython
  except ImportError:
    interact(local=context)
  else:
    sh = IPython.frontend.terminal.embed.InteractiveShellEmbed()
    sh(local_ns=context)

shell_parser.set_defaults(handler=shell_handler)

# Worker

worker_parser = subparsers.add_parser('worker', help='start worker')

worker_parser.add_argument('-o', '--only-direct',
  action='store_true',
  help='only listen to direct queue'
)
worker_parser.add_argument('-v', '--verbose-help',
  action='store_true',
  help='show full help from celery worker'
)
worker_parser.add_argument('-r', '--raw',
  nargs=REMAINDER,
  help='raw options to pass through',
)

@_project_context
def worker_handler(parsed_args):
  """Starts a celery worker::

    flasker worker ...

  The following options are available:

  * ``-o, --only-direct`` to have the worker only listen to its direct queue
    (this option requires the CELERY_WORKER_DIRECT to be set to ``True``).
  * ``-v, --verbose-help`` to show the worker help.
  * ``-r, --raw`` to pass arguments to the worker (any arguments after this
    option will be passed through).

  If no hostname is provided, one will be generated automatically using the
  project domain and subdomain and current worker count. For example, the first
  two workers started for project ``my_project`` and configuration ``default``
  will have respective hostnames:

  * w1.default.my_project
  * w2.default.my_project

  """
  pj = current_project
  pj_worker_names = [d.keys()[0] for d in pj.celery.control.ping()]
  worker_pattern = r'w(\d+)\.%s.%s' % (pj.subdomain, pj.domain)
  worker_numbers = [
    findall(worker_pattern, worker_name) or ['0']
    for worker_name in pj_worker_names
  ]
  wkn = min(
    set(range(1, len(worker_numbers) + 2)) -
    set([int(n[0]) for n in worker_numbers] or [len(worker_numbers) + 2]) 
  )
  if parsed_args.verbose_help:
    pj.celery.worker_main(['worker', '-h'])
  else:
    hostname = 'w%s.%s.%s' % (wkn, pj.subdomain, pj.domain)
    options = ['worker', '--hostname=%s' % hostname]
    if parsed_args.only_direct:
      options.append('--queues=%s.dq' % hostname)
    if parsed_args.raw:
      options.extend(parsed_args.raw)
    pj.celery.worker_main(options)

worker_parser.set_defaults(handler=worker_handler)

# Flower

flower_parser = subparsers.add_parser('flower', help='start flower')

flower_parser.add_argument('-p', '--port',
  default=5555,
  type=int,
  help='listen on port [%(default)s]'
)
flower_parser.add_argument('-v', '--verbose-help',
  action='store_true',
  help='show full help from celery flower'
)
flower_parser.add_argument('-r', '--raw',
  help='raw options to pass through',
  nargs=REMAINDER
)

@_project_context
def flower_handler(parsed_args):
  """Start flower worker manager::
    
    flasker flower ...

  The following arguments are available:

  * ``-p, --port`` to set the port to run flower on (defaults to ``5555``).
  * ``-v, --verbose-help`` to show the flower help.
  * ``-r, --raw`` to pass arguments to flower (any arguments after this option
    will be passed through).
  
  """
  pj = current_project
  if parsed_args.verbose_help:
    pj.celery.start(['celery', 'flower', '--help'])
  else:
    options = ['celery', 'flower', '--port=%s' % parsed_args.port]
    if parsed_args.raw:
      options.extend(parsed_args.raw)
    pj.celery.start(options)

flower_parser.set_defaults(handler=flower_handler)

# END of parsers

def main():
  parsed_args = parser.parse_args()
  parsed_args.handler(parsed_args)

if __name__ == '__main__':
  main()
