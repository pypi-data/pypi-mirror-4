Kit
===

A configurable, lightweight framework that integrates Flask_, SQLAlchemy_, and
Celery_.

  * Kit integrates 3 great tools into a single YAML configuration file

    .. code:: yaml

      database_url: 'mysql://...'
      flask:
        debug: yes
        testing: yes
      celery:
        broker_url: 'redis://'
      engine:
        pool_recycle: 3600

  * Kit comes with a command line tool to manage your application so witching
    configurations is easy: ``kit server -c dev.yaml`` vs.  ``kit server -c
    prod.yaml``.

  * Kit sets up Flask, Celery and SQLAlchemy smartly. It only creates those you
    need for your application and makes sure database connections are correctly
    handled under the hood.

Check out the ``examples/`` folder for a couple sample applications.

*Kit is under development.*


Installation
------------

.. code:: bash

   $ pip install kit


Quickstart
----------

There are two ways you can use Kit.

Basic usage
***********

.. code:: python

  from kit import Kit

  kit = Kit('/path/to/conf.yaml')

  flask_app = kit.flask     # the configured Flask application
  celery_app = kit.celery   # the configured Celery application
  session = kit.session     # the configured SQLAlchemy scoped session maker

  @flask_app.route('/')
  def index():
    return 'Hello world!'

  if __name__ == '__main__':
    flask_app.run()

In this snippet we only used ``kit.flask``, the application in 
``examples/view_tracker`` shows an example of using ``kit.session`` as well.


Next steps
**********

To use the ``kit`` command line tool, we need to tell it which modules belong
to our project. This is done via the ``modules`` option in the configuration
file:

.. code:: yaml

  database_url: 'sqlite:///...'
  modules: ['app.models', 'app.tasks']
  ...

Inside all these modules, any instantiation of ``Kit`` will return a copy
of the configured kit (you don't need to pass the configuration filepath).
You can then use the command line tool to manage your project (more help is
available for each command by typing ``kit <command> -h``):

- Launch the Flask built in Werkzeug_ server: ``kit server -p 5050 -d`` will
  start a server on port 5050 in debug mode.
- Start Celery workers: ``kit worker`` will start a worker listening for tasks
  sent from your application.
- Run the Flower_ monitoring tool: ``kit flower -p 8000``
- Run a shell in your project's context: ``kit shell``

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
.. _Pandas: http://pandas.pydata.org/
