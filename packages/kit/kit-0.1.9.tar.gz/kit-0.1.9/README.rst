Kit
===

A configurable, lightweight framework that integrates Flask_, SQLAlchemy_, and
Celery_.

Why use Kit?
  
- 3 great tools, 1 YAML_ configuration file

    Versioning and keeping track of your different configuration options
    becomes almost fun!

- With the ``kit`` command line tool, switching configurations is easy as pie

    ``kit server -c dev.yaml`` vs.  ``kit server -c prod.yaml``

- Kit sets up the Flask, Celery and SQLAlchemy applications smartly

    It only creates those you need and makes sure database connections are
    correctly handled under the hood.

Kit is under development. Check out the ``examples/`` folder to see how Kit
can simplify your prototyping needs!


Installation
------------

.. code:: bash

   $ pip install kit


Quickstart
----------

There are two ways to use Kit: without and with the ``load_modules`` option.

- In the first case (default behavior), you instantiate each kit once with the
  configuration filepath:

  .. code:: python

    from kit import Kit

    kit = Kit('/path/to/conf.yaml')

  The configured kit components are available directly on ``kit``:

  * ``kit.flask``, the Flask application object
  * ``kit.celery``, the Celery application object
  * ``kit.session``, the SQLAlchemy scoped session maker
  
  Cf. Example_ for a sample application using this approach.
     

- In the second case, you use the ``modules`` option in the configuration
  file to specify which modules belong to your kit:

  .. code:: yaml

    modules: ['app.models', 'app.tasks']
    ...

  Inside all these modules, any instantiation of ``Kit`` will return a copy
  of the configured kit (you don't need to pass the configuration filepath or).
  A very simple pattern is to add the following line to each module as needed:

  .. code:: python

    from kit import Kit

    kit = Kit()

    # Do stuff with ``kit.flask``, ``kit.celery``, etc.

  To start your project, you can either use the ``kit`` command line tool or
  instantiate ``Kit`` as follows:

  .. code:: python

    kit = Kit('/path/to/conf.yaml', load_modules=True)

  Cf. ``examples/twitter_poller`` for a sample application built using this
  method.


Example
-------

In this section we walk through the implementation a very simple page view
tracker: Each time a page in our application will be visited, we would like to
store the visit in a local SQLite database. And since this is for testing
purposes, let's imagine we are also interested in seeing what queries are
issued by the database engine. This can be done with the following minimalistic
configuration file:

.. code:: yaml

   database_url: sqlite:///db.sqlite
   flask:
     debug: yes
     testing: yes
   engine:
     echo: yes

Note that the ``flask`` and ``engine`` options are used to configure the Flask
application and SQLAlchemy engine respectively (cf. Configuration_ for a full
list of available options). 

Our application will consist of a single Flask view and a model corresponding
to page visits:

.. code:: python

  #!/usr/bin/env python

  """Page view tracker."""

  from datetime import datetime
  from kit import Kit
  from os.path import abspath
  from sqlalchemy import Column, DateTime, Integer
  from sqlalchemy.ext.declarative import declarative_base

  # Our tookit!
  # ===========
  #
  # The kit instance exposes the configured Flask application, Celery
  # application and SQLAlchemy session maker through its attributes
  # `flask`, `celery`, `session` (only `flask` and `session` are used here).

  kit = Kit(abspath('conf.yaml'))

  # SQLAlchemy
  # ==========
  # 
  # First, we use SQLAlchemy declarative to create the table where we will
  # keep track of the visits. This is very similar to what you can find in
  # the tutorial (http://docs.sqlalchemy.org/en/rel_0_8/orm/tutorial.html).

  Base = declarative_base()

  class Visit(Base):

    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)

  Base.metadata.create_all(kit.session.get_bind())
  # Note the use of ``kit.session`` to get access to the configured engine

  # Flask
  # =====
  #
  # We are now ready to create our Flask view!
  # For more information on creating views and routing, refer to the excellent
  # Flask online documentation (http://flask.pocoo.org/docs/tutorial/).

  @kit.flask.route('/')
  def index():
    """This view returns the number of times it has been visited.

    Note that since the option `commit_on_teardown` is set to ``True`` in our
    configuration file, we don't need to commit our changes manually, it is
    done automatically after the request ends.
    
    """
    visit = Visit()                           # we create a new visit
    kit.session.add(visit)                    # we add it to our session
    count = kit.session.query(Visit).count()  # the total number of visits
    return 'This page has been visited %s times now!' % (count, )


  if __name__ == '__main__':
    kit.flask.run()     # this starts a development server for our Flask app

To run this application, save both files as ``conf.yaml`` and ``app.py`` and
run ``python app.py``. The code for this example is available in the
``examples/`` folder, along with another more detailed example which implements
an automatic  Twitter API poller using Celery.


Configuration
-------------

The following options are special in a kit configuration file:

* ``database_url``: url to the database used.
* ``flask``: any valid flask configuration option.
* ``celery``: any valid celery configuration option.
* ``engine``: any valid engine configuration option.
* ``session``: any valid session maker configuration option.
* ``commit_on_teardown``: if ``True``, the session will be committed after
  each request or task executed in a worker, otherwise the session is simply
  removed (default behavior).
* ``modules``: the list of modules that belong to this kit. This is used by
  the command line tool to know which modules to import.
* ``root_folder``: the kit's root folder, the modules defines in ``modules``
  should be importable from this folder (defaults to the configuration file's
  directory).
* ``flask_app_folder``: the root folder of the Flask application, relative to
  ``root_folder`` (defaults to the same directory).
* ``flask_static_folder``: the Flask application's static folder, relative to
  ``flask_app_folder`` (defaults to ``static/``).
* ``flask_template_folder``: the Flask application's template folder, relative
  ``flask_app_folder`` (defaults to ``templates/``).

You can of course include other options in this file, these will be
available on the ``conf`` kit attribute.


Command line tool
-----------------

Kit includes a command line tool from where you can:

- Launch the Flask built in Werkzeug_ server: ``kit server -p 5050 -d`` will
  start a server on port 5050 in debug mode.
- Start Celery workers: ``kit worker`` will start a worker listening for tasks
  sent from your application.
- Run the Flower_ monitoring tool: ``kit flower -p 8000``
- Run a shell in your project's context: ``kit shell``

Help is available for each command by typing ``kit <command> -h``.


Extensions
----------

Kit also comes with extensions for commonly needed functionalities:

- Expanded SQLAlchemy models and queries
- ReSTful API


.. _Bootstrap: http://twitter.github.com/bootstrap/index.html
.. _Flask: http://flask.pocoo.org/docs/api/
.. _Flask-Script: http://flask-script.readthedocs.org/en/latest/
.. _Flask-Login: http://packages.python.org/Flask-Login/
.. _Flask-Restless: https://flask-restless.readthedocs.org/en/latest/
.. _Jinja: http://jinja.pocoo.org/docs/
.. _Celery: http://docs.celeryproject.org/en/latest/index.html
.. _Flower: https://github.com/mher/flower
.. _Datatables: http://datatables.net/examples/
.. _SQLAlchemy: http://docs.sqlalchemy.org/en/rel_0_7/orm/tutorial.html
.. _MySQL: http://dev.mysql.com/doc/
.. _Google OAuth 2: https://developers.google.com/accounts/docs/OAuth2
.. _Google API console: https://code.google.com/apis/console
.. _jQuery: http://jquery.com/
.. _jQuery UI: http://jqueryui.com/
.. _Backbone-Relational: https://github.com/PaulUithol/Backbone-relational
.. _FlaskRESTful: http://flask-restful.readthedocs.org/en/latest/index.html
.. _GitHub pages: http://mtth.github.com/kit
.. _GitHub: http://github.com/mtth/kit
.. _IPython: http://ipython.org/
.. _Werkzeug: http://werkzeug.pocoo.org/
.. _Requests: http://docs.python-requests.org/en/latest/
.. _examples/view_tracker: https://github.com/mtth/kit/tree/master/examples/view_tracker
.. _YAML: http://www.yaml.org/

