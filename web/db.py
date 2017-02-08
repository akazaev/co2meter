# coding: utf-8

from sqlite3 import dbapi2 as sqlite3

from flask import g

import settings


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


def get_uart_data(from_date=None, limit=None):
    db = get_db()
    limit = limit or 360
    cur = db.execute(
        'select time, ppm, temp from co2meter order by time desc limit {0}'
        ''.format(limit))
    entries = cur.fetchall()
    rows = [list(row) for row in entries]
    rows.reverse()
    data = {
        "rows": rows
    }

    return data


def get_pwm_data(from_date=None, limit=None):
    db = get_db()
    limit = limit or 3600
    cur = db.execute('select time, ppm, 0 from co2meter_pwm '
                     'order by time desc limit {0}'.format(limit))
    entries = cur.fetchall()
    rows = [list(row) for row in entries]
    rows.reverse()
    data = {
        "rows": rows
    }

    return data


def reset_data():
    db = get_db()
    db.execute('delete from co2meter')
    db.execute('delete from co2meter_pwm')
    db.commit()
