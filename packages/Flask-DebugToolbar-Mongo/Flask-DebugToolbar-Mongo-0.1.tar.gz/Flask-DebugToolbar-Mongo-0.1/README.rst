==================================
Flask Debug Toolbar MongoDB Panel
==================================

:Info: An extension panel for Matt Good's `Flask-DebugToolbar`_ that adds
       MongoDB debugging information
:Author: Bruno Carlin (http://github.com/bcarlin, http://twitter.com/brunocarlin)

.. Flask-DebugToolbar:: http://flask-debugtoolbar.rtfd.org/

History
=======

This is a port of the MongoDB addon to the Django Debug Toolbar written
by Harry Marr (http://github.com/hmarr, http://twitter.com/harrymarr).

There existed another port (https://github.com/cenkalti/flask-debug-toolbar-mongo)
that was neither up-to-date nor operational (there are still imports
from django).

Here is a clean port that I intend to maintain current with Harry Marr's
original work, and occasionnally augment with new features if needed.

All the thanks go to Harry!

.. warning::
   This package is still at an early stage. While it works, it is not
   yet complete and its reports are not exhaustives.

   If you want to help improve it, you are the most welcome to do so.
   Just fork the repository on
   `Github <https://github.com/bcarlin/flask-debugtoolbar-mongo>`__ and
   send your pull requests !

Setup
=====

First, you need to get the package. Install it with pip:

::

    pip install flask-debugtoolbar-mongo

Somewhere after you've set ``app.debug = True`` and before ``app.run``, you need
to specify the ``flask_debugtoolbar`` panels that you want to use and include
``'flask_debugtoolbar_mongo.panels.MongoDebugPanel'`` in that list.

For example, here's a small flask app with the panel installed and with line
profiling enabled for the `hello_world`::

    from flask import Flask
    app = Flask(__name__)

    import flask_debugtoolbar

    @app.route('/')
    def hello_world():
        return 'Hello World')

    if __name__ == '__main__':
        app.debug = True

        # Specify the debug panels you want
        app.config['DEBUG_TB_PANELS'] = [
            'flask_debugtoolbar.panels.versions.VersionDebugPanel',
            'flask_debugtoolbar.panels.timer.TimerDebugPanel',
            'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
            'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
            'flask_debugtoolbar.panels.template.TemplateDebugPanel',
            'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
            'flask_debugtoolbar.panels.logger.LoggingPanel',
            'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
            # Add the MongoDB panel
            'flask_debugtoolbar_mongo.panel.MongoDebugPanel',
        ]
        toolbar = flask_debugtoolbar.DebugToolbarExtension(app)

        app.run()


``Flask-debugtoolbar-mongo`` accepts the following configration options::

  app.config['DEBUG_TB_MONGO'] = {
    'SHOW_STACKTRACES' = True
    'HIDE_FLASK_FROM_STACKTRACES' = True
  }

``SHOW_STACKTRACES``
   Obtaining stack traces can slow down queries significantly. You can
   turn them off by setting this option to ``False``.
``HIDE_FLASK_FROM_STACKTRACES``
   Hides Flask calls from the stacktrace.
