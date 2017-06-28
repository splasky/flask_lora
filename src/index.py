#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-06-28 10:18:06

from flask import Flask
from flask import (Flask, request, session, g, redirect, url_for, abort,
                   render_template, flash)
import logging
import os
import sqlite3
import sys
from package.abp_decrypt import decodePHYpayload
app = Flask(__name__)


SQLITE_DB_PATH = 'main_db.db'
SQLITE_DB_SCHEMA = 'create_db.sql'


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
        filename, lineno, exc_type, exc_obj))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/draw', methods=['POST'])
def draw():

    device_id = request.form.get('device_id', None)
    abp_key = request.form.get('abp_key', None)
    payload = request.form.get('payload', None)

    # error handling
    if device_id is None or (abp_key is None and payload is None):
        err_msg = "<p>No members in group '%s'</p>" % group_name
        return err_msg, 404

    logging.debug("device_id:{},payload:{},key:{}".format(
        device_id, payload, abp_key))

    try:
        decrypt = decodePHYpayload(payload.encode('utf-8'), abp_key)
        data = decrypt.getdata()
        insert_into_database(device_id, data, abp_key)
        cursor = db_execute("Select dev.device_id, dev.abp_key, data.payload, data.time from Devices dev, "
                            "Device_Data data where dev.device_id=data.device_id"
                            ";").fetchall()

        return render_template('history.html', devices=cursor)
    except:
        PrintException()


def db_execute(command):
    try:
        db = get_db()
        cursor = db.execute(command)
        return cursor
    except:
        db.rollback()
        PrintException()
        print('query string:{}'.format(command))


def insert_into_database(device_id: str, data: str, key: str)->None:
    db = get_db()

    if not check_device_id_exists(device_id):
        if key is not None:
            db.execute("Insert into Devices(device_id, abp_key) Values(?, ?)", (
                device_id, key))
            db.commit()

    if data is not None:
        db.execute(
            "Insert into Device_Data(device_id, payload) Values(?, ?)", (device_id, data))
        db.commit()


def check_device_id_exists(device_id: str)->bool:
    query = "select device_id from Devices where device_id='{}';".format(
        device_id)
    try:
        cursor = db_execute(query)
        if cursor.fetchone() is None:
            return False
    except:
        logging.debug("query failed! query:{}".format(query))
        PrintException()
    return True


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with app.open_resource(SQLITE_DB_SCHEMA, mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # To allow aptana to receive errors, set use_debugger=False
    if app.debug:
        use_debugger = True
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
        app.run(use_debugger=use_debugger, debug=app.debug,
                use_reloader=use_debugger, host='0.0.0.0')
    except:
        PrintException()
