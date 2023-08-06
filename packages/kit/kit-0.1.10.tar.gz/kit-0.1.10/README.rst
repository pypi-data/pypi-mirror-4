Kit
===

A configurable, lightweight framework that integrates Flask_, SQLAlchemy_, and
Celery_.

Why use Kit?
  
- It integrates 3 great tools into 1 YAML_ configuration file

  .. code:: yaml

    database_url: 'mysql://...'
    flask:
      debug: yes
      testing: yes
    celery:
      broker_url: 'redis://'
    engine:
      pool_recycle: 3600

  Versioning and keeping track of your different configuration options
  becomes almost fun!

- It sets up your Flask, Celery and SQLAlchemy applications smartly

  Kit only creates those you need for your application and makes sure database
  connections are correctly handled under the hood.

- It comes with a command line tool to manage your application

  .. code:: bash

    $ kit -h

    Usage: kit [-h] [-c CONF] {shell,worker,flower,server} ...

    optional arguments:
      -h, --help            show this help message and exit
      -c CONF, --conf CONF  path to configuration file

    available commands:
      {shell,worker,flower,server}
        server              start server
        shell               start shell
        worker              start worker
        flower              start flower

  Switching configurations is easy as pie: ``kit server -c dev.yaml`` vs.
  ``kit server -c prod.yaml``

Kit is under development. Check out the ``examples/`` folder to see how Kit
can simplify your prototyping needs!


Installation
------------

.. code:: bash

   $ pip install kit


Quickstart
----------

There are two ways you can use Kit.

Basic usage
***********

Here, you instantiate each kit once with the configuration filepath:

.. code:: python

  from kit import Kit

  kit = Kit('/path/to/conf.yaml')

The configured kit components are available directly on ``kit``:

* ``kit.flask``, the Flask application object
* ``kit.celery``, the Celery application object
* ``kit.session``, the SQLAlchemy scoped session maker

This works great for simple applications which don't use Celery or require
using the shell for debugging. Cf. ``examples/view_tracker`` for a sample
application using this approach.
     

Advanced
********

To use the ``kit`` command line tool, we need to tell it which modules belong
to our project. This is done via the ``modules`` option in the configuration
file:

.. code:: yaml

  database_url: 'sqlite:///...'
  modules: ['app.models', 'app.tasks']
  ...

Inside all these modules, any instantiation of ``Kit`` will return a copy
of the configured kit (you don't need to pass the configuration filepath or).
A very simple pattern is to add the following line to each module as needed:

.. code:: python

  from kit import Kit

  kit = Kit()

  # Do stuff with ``kit.flask``, ``kit.celery``, etc.

You can then use the command line tool to manage your project:

- Launch the Flask built in Werkzeug_ server: ``kit server -p 5050 -d`` will
  start a server on port 5050 in debug mode.
- Start Celery workers: ``kit worker`` will start a worker listening for tasks
  sent from your application.
- Run the Flower_ monitoring tool: ``kit flower -p 8000``
- Run a shell in your project's context: ``kit shell``

Help is available for each command by typing ``kit <command> -h``.

Alternatively, to load you project outside of the command line tool, you can
pass ``load_modules=True`` when instantiating the ``Kit``:
``kit = Kit('/path/to/conf.yaml', load_modules=True)``.  You can then use its
components as you like (for example to run the application on a different
server or load data in an IPython notebook).

Cf. ``examples/twitter_poller`` for a sample application built using this
method.


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

