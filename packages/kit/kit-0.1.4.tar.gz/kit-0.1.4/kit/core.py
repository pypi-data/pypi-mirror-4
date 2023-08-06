  #!/usr/bin/env python

"""Core module.

This module defines the :class:`kit.Kit` class which contains all the logic
between the Flask and Celery applications and the SQLAlchemy sessions.

For convenience, both these variables are also available directly in the
``kit`` namespace.

"""

from logging import getLogger, NullHandler, StreamHandler, DEBUG
from os.path import abspath, basename, dirname, isabs, join
from sys import path
from weakref import proxy

try:
  from yaml import load
  from sqlalchemy.exc import InvalidRequestError
  from celery import current_app
except ImportError:
  pass


class KitImportError(Exception):

  """Generic error raised when something goes wrong during import."""

  pass


class Kit(object):

  """Kit class.

  :param conf_path: path to the configuration file.
  :type conf_path: str
  
  """

  #: Current kit
  current = None

  #: Default configuration
  default_conf = {
    'database_url':             'sqlite://',
    'flask':                    {},
    'celery':                   {},
    'engine':                   {},
    'session':                  {},
    'modules':                  [],           # 
    'root_folder':              '.',          # 
    'commit_on_teardown':       False,        #
    'debug':                    False,
    'flask_app_folder':         '.',
    'flask_static_folder':      'static',
    'flask_template_folder':    'templates',
  }

  __registry = {}

  def __init__(self, conf_path=None, set_as_current=True, load_modules=False):
    if conf_path is None:

      if self.current:
        self.__dict__ = self.current.__dict__
      else:
        raise KitImportError('No current configuration found. '
                             'Calling `Kit()` without the '
                             '`conf_path` argument only works when the '
                             'current kit has already been set.')
    else:

      if not isabs(conf_path):
        raise KitImportError('Configuration path must be absolute. Relative '
                             'path %r not supported.' % (conf_path, ))

      __registry = self.__registry

      if conf_path in __registry:
        self.__dict__ = __registry[conf_path].__dict__

      else:
        with open(conf_path) as f:
          self.conf = load(f)

        self.conf_path = conf_path
        for k, v in self.default_conf.items():
          self.conf.setdefault(k, v)

        def _callback(*args):
          del __registry[conf_path]

        __registry[conf_path] = proxy(self, _callback)

        self._flask = None
        self._celery = None
        self._session = None

        self.logger = getLogger(__name__)
        self.logger.handlers = []
        if self.conf['debug']:
          self.logger.setLevel(DEBUG)
          self.logger.addHandler(StreamHandler())
        else:
          self.logger.addHandler(NullHandler())

        if load_modules:

          # appending to python path
          self.conf['root_folder'] = abspath(join(
            dirname(self.conf_path),
            self.conf['root_folder']
          ))
          if not self.conf['root_folder'] in path:
            path.append(self.conf['root_folder'])

          # load all kit modules
          for module_name in self.conf['modules']:
            self.logger.debug('importing %s...' % (module_name, ))
            try:
              __import__(module_name)
            except ImportError:
              raise KitImportError('Unable to load module %s. Check that '
                                       'it is on your python path. Use the '
                                       '`root_folder` option to add your '
                                       'kit\'s root folder to your python '
                                       'path.' % (module_name, ))

      if set_as_current:
        self.__class__.current = self

  def __repr__(self):
    return '<Kit %r>' % (self.conf_path, )

  @property
  def flask(self):
    """Flask application.

    Lazily initialized.

    """
    if self._flask is None:

      from flask import Flask

      folder = abspath(join(
        self.conf['root_folder'],
        self.conf['flask_app_folder'],
      ))

      flask_app = Flask(
        basename(folder),
        static_folder=join(folder, self.conf['flask_static_folder']),
        template_folder=join(folder, self.conf['flask_template_folder']),
        instance_path=folder,
        instance_relative_config=True,
      )

      flask_app.config.update(
        {k.upper(): v for k, v in self.conf['flask'].items()}
      )

      self._flask = flask_app
      self._handle_session(for_flask=True)
      self.logger.debug('flask app loaded')

    return self._flask

  @property
  def celery(self):
    """Celery application.

    Lazily initialized.

    """
    if self._celery is None:

      from celery import Celery
      from celery.task import periodic_task

      celery_app = Celery()

      celery_app.conf.update(
        {k.upper(): v for k, v in self.conf['celery'].items()}
      )

      # proxy for easy access
      celery_app.periodic_task = periodic_task

      self._celery = celery_app
      self._handle_session(for_celery=True)
      self.logger.debug('celery app loaded')

    return self._celery

  @property
  def session(self):
    """SQLAlchemy scoped sessionmaker.

    Lazily initialized.

    """
    if self._session is None:

      from sqlalchemy import create_engine  
      from sqlalchemy.orm import scoped_session, sessionmaker

      engine = create_engine(
        self.conf['database_url'], **self.conf['engine']
      )

      session = scoped_session(
        sessionmaker(bind=engine, **self.conf['session'])
      )

      self._session = session
      self._handle_session(for_flask=True, for_celery=True)
      self.logger.debug('session loaded')

    return self._session

  def _handle_session(self, for_flask=False, for_celery=False):
    """Properly handle session removal after requests and tasks."""

    if self._session:

      if self._celery and for_celery:
        self._celery._kit = proxy(self)

        from celery.signals import task_postrun, worker_init

        @worker_init.connect
        def _worker_init_handler(*args, **kwargs):
          task_postrun.connect(_remove_session)

      if self._flask and for_flask:
        self._flask._kit = proxy(self)

        from flask.signals import request_tearing_down

        request_tearing_down.connect(_remove_session, self._flask)

  def _remove_session(self):
    """Remove database connections."""
    try:
      if self.conf['commit_on_teardown']:
        self.session.commit()
    except InvalidRequestError as e:
      self.session.rollback()
      self.logger.error('error while committing session: %s' % (e, ))
      if self.conf['debug']:
        raise e
    finally:
      self.session.remove()


def _remove_session(sender, *args, **kwargs):
  """Globally namespaced function for signals to work."""
  if not isinstance(sender, str):
    # sender is a flask application
    sender._kit._remove_session()
  else:
    # sender is a celery task
    current_app._kit._remove_session()


