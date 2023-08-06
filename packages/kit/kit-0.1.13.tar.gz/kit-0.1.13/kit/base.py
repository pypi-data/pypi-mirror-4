  #!/usr/bin/env python

"""Core module.

This module defines the :class:`kit.Kit` class which contains all the logic
between the Flask and Celery applications and the SQLAlchemy sessions.

For convenience, both these variables are also available directly in the
``kit`` namespace.

"""

from logging import getLogger, NullHandler, StreamHandler, DEBUG
from os import getenv
from os.path import abspath, basename, dirname, join
from sys import path as sys_path
from traceback import format_exc
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

  :param path: path to the configuration file.
  :type path: str
  
  """

  #: Default configuration
  default_conf = {
    'flask':                    {},
    'celery':                   {},
    'engine':                   {},
    'session':                  {},
    'modules':                  [],
    'root':                     '.',
    'debug':                    False,
  }

  __stack = []

  def __init__(self, path=None, load_modules=False):

    if not path:
      try:
        self.__dict__ = self.__stack[-1].__dict__
      except IndexError:
        raise KitImportError('Kit instantiated without a ``path`` argument '
                             'but outside of imports.')

    else:
      self.path = abspath(path)

      self._flask = None
      self._celery = None
      self._session = None

      with open(path) as f:
        self.conf = load(f)

      for k, v in self.default_conf.items():
        self.conf.setdefault(k, v)

      self.logger = getLogger(__name__)
      self.logger.handlers = []
      if self.conf['debug']:
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(StreamHandler())
      else:
        self.logger.addHandler(NullHandler())

    if load_modules:
      with self:
        for module_name in self.conf['modules']:
          self.logger.debug('Importing %s...' % (module_name, ))
          __import__(module_name)

  def __enter__(self):
    self.__stack.append(self)
    sys_path.insert(0, abspath(join(dirname(self.path), self.conf['root'])))

  def __exit__(self, exc_type, exc_value, traceback):
    self.__stack.pop()
    sys_path.remove(abspath(join(dirname(self.path), self.conf['root'])))

  def __repr__(self):
    return '<Kit %r>' % (self.path, )

  @property
  def flask(self):
    """Flask application.

    Lazily initialized.

    """
    if self._flask is None:

      from flask import Flask
      from flask.signals import request_tearing_down

      folder = abspath(join(
        self.conf['root'],
        self.conf['flask'].get('app_folder', '.'),
      ))

      flask_app = Flask(
        basename(folder),
        static_folder=join(
          folder,
          self.conf['flask'].get('static_folder', 'static')
        ),
        template_folder=join(
          folder,
          self.conf['flask'].get('template_folder', 'templates')
        ),
        instance_path=folder,
        instance_relative_config=True,
      )

      flask_app.config.update(
        {k.upper(): v for k, v in self.conf['flask'].get('conf', {}).items()}
      )

      flask_app._kit = proxy(self)
      request_tearing_down.connect(_remove_session, flask_app)

      self._flask = flask_app
      self.logger.debug('Flask app loaded')

    return self._flask

  @property
  def celery(self):
    """Celery application.

    Lazily initialized.

    """
    if self._celery is None:

      from celery import Celery
      from celery.signals import task_postrun
      from celery.task import periodic_task

      celery_app = Celery()

      celery_app.conf.update(
        {k.upper(): v for k, v in self.conf['celery'].get('conf', {}).items()}
      )

      celery_app.periodic_task = periodic_task

      celery_app._kit = proxy(self)
      task_postrun.connect(_remove_session)

      self._celery = celery_app
      self.logger.debug('Celery app loaded')

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
        self.conf['engine'].get('url', 'sqlite://'),
        **{k: v for k, v in self.conf['engine'].items() if not k == 'url'}
      )
      session = scoped_session(
        sessionmaker(bind=engine, **self.conf['session'])
      )

      self._session = session
      self.logger.debug('Session loaded')

    return self._session

  def _remove_session(self, flask=False, celery=False):
    """Remove database connections."""
    if self._session is not None:
      try:
        flask = flask and self.conf['flask'].get('autocommit', False)
        celery = celery and self.conf['celery'].get('autocommit', False)
        if flask or celery:
          self.session.commit()
      except InvalidRequestError as e:
        self.session.rollback()
        self.logger.error('Error while committing session: %s' % (e, ))
        if self.conf['debug']:
          raise e
      finally:
        self.session.remove()


def _remove_session(sender, *args, **kwargs):
  """Globally namespaced function for signals to work."""
  if hasattr(sender, 'app'):
    # sender is a celery task
    sender.app._kit._remove_session(celery=True)
  else:
    # sender is a flask application
    sender._kit._remove_session(flask=True)


