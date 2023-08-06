#!/usr/bin/env python

"""The engine behind it all."""

from __future__ import absolute_import

from celery.signals import task_postrun
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import InvalidRequestError

from ..project import current_project
from ..util import Model, _QueryProperty

class Db(object):

  """Session handling.

  Usage inside the app::

    db.session.add(something)
    db.session.commit()

  Session creation and destruction is handled out of the box.

  Or (but not recommended)::

    with db() as session:
      # do stuff

  """

  def __init__(self, db_url):
    self.url = db_url

  def __enter__(self):
    return self.session()

  def __exit__(self, type, value, traceback):
    self.dismantle()

  def create_connection(self, app=None, celery=None):
    """Initialize database connection."""
    engine = create_engine(self.url, pool_recycle=3600)
    Model.metadata.create_all(engine, checkfirst=True)
    self.session = scoped_session(sessionmaker(bind=engine))
    Model.query = _QueryProperty(self)
    if app:
      @app.teardown_request
      def teardown_request_handler(exception=None):
        self.dismantle()
    if celery:
      @task_postrun.connect
      def task_postrun_handler(*args, **kwargs):
        self.dismantle()

  def dismantle(self, **kwrds):
    """Remove database connection.

    Has to be called after app request/job terminates or connections
    will leak.

    """
    try:
      self.session.commit()
    except InvalidRequestError as e:
      self.session.rollback()
      self.session.expunge_all()
      # logger.error('Database error: %s' % e)
    finally:
      self.session.remove()

current_project.db = Db(current_project.config['PROJECT']['DB_URL'])

