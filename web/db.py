# coding: utf-8

from sqlite3 import dbapi2 as sqlite3

from flask import g

from web import settings


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(settings.DB)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#
# @app.teardown_appcontext
# def close_db(error):
#     """Closes the database again at the end of the request."""
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()


def get_data(from_date=None):
    db = get_db()
    cur = db.execute(
        'select time, ppm from co2meter order by time desc limit 50')
    entries = cur.fetchall()
    
    data = {
        "rows": [list(row) for row in entries]
    }

    return data
