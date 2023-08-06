=========
Renuntius
=========

``renuntius`` is a RESTful webservice for sending messages.

Installation
============

This application was tested, using the following versions:

  * python==2.7
  * flask==0.9
  * flask-restless==0.9.3
  * flask-sqlalchemy==0.16


Installation with pip
---------------------

Using ``pip`` is probably the easiest way to install ``renuntius``::

    pip install renuntius

Local application
-----------------

In order to run the application, write the following python-code (e.g.:
``start_renuntius.py``)::

    from renuntius.messaging import flask, db, app, Message

    db.create_all()

    manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    manager.create_api(Message, methods=['GET', 'POST'])

    app.run(host=localhost, port=5001)

**Note**: Within the application folder you need a ``config.py``, like::

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/renuntius.sqlite'
    SQLALCHEMY_ECHO = True

    # E-Mail-Server
    SMTP_SERVER = 'MAILSERVER.DOMAIN.ORG'
    SMTP_SERVER_PORT = 25

    # Messages
    SERVICE_PREAMBLE = u"This message was automatically generated."
    FROM_DEFAULT = u'"IT-Renuntius" <renuntius@DOMAIN.ORG>'

Please adjust this ``config.py`` to your own settings.

Finally::

    python start_renuntius.py


Special use case: PostgreSQL
----------------------------

In order to be able to use a postgresql server, you need to install
``psycopg2``. To install ``psycopg2`` within a virtualenv under linux, do the
following::

  sudo aptitude install libpq-dev python-dev
  pip install psycopg2

Example ``config.py`` for postgresql (you probably want to specify the
``SCHEMA``!)::

    # Database
    SQLALCHEMY_DATABASE_URI = 'postgresql://_ren_admin@ama-prod/mucam'
    SCHEMA = 'renuntius'
    SQLALCHEMY_ECHO = False

    # E-Mail-Server
    SMTP_SERVER = 'MAILSERVER.DOMAIN.ORG'
    SMTP_SERVER_PORT = 25

    # Messages
    SERVICE_PREAMBLE = u"This message was automatically generated."
    FROM_DEFAULT = u'"IT-Renuntius" <renuntius@DOMAIN.ORG>'

Quickstart
==========

Sending an E-Mail via ``renuntius``::

    POST http://localhost:5001/api/messages/

    {"header_from":     "other_service@domain.org",
     "header_to":       "admins@domain.org",
     "header_subject":  "Sent by Renuntius",
     "content":         "Everything works fine!",
     "service":         "other_service"
    }

**Note**: For firefox use ``RESTClient`` add-on to easily ``POST``.

Getting a list of all messages::

    GET http://localhost:5001/api/messages/

(Try `<http://localhost:5001/api/messages/>`_ within your default browser)

Querying for specific messages::

    GET http://localhost:5001/api/messages/?q={"filters":[{"name": "header_from", "op": "==", "val":"other_service@domain.org"}]}

For a detailed specification of how to use filters, please look at
`flask-restless <https://flask-restless.readthedocs.org/en/latest/searchformat.html>`_


Copyright License
=================

For information, see the files LICENSE.txt in this directory.
