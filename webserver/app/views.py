import os
import sys
import pdb
import time
import json

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, g
from app import app
import random
import string

DATABASE = '../ka_challenge.db' #assuming we are running from coding_challenge/webserver/run.py, and ka_challenge.db is at coding_challenge/users.db


@app.route('/_populate_database')
def populate_database():
    num_entries=request.args.get('num_entries', 0, type=int)
    print("num_entries", num_entries)
    if num_entries==0 or not isinstance(num_entries, int):
        print("here")
        num_entries=100
    count=0
    cur = g.db.cursor()
    while count < num_entries:
        userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
        # insert_result = insert("USERS", ['name','version'], [userName,1.0])
        query = getquery("USERS", ['name','version'], [userName,1.0])
        count+=1
        cur.execute(query, [userName,1.0])
    g.db.commit()
    id = cur.lastrowid
    cur.close()
    users = g.db.execute("SELECT * FROM USERS LIMIT 10;").fetchall()
    count = g.db.execute("SELECT count(*) FROM USERS WHERE version=1.0;").fetchall()        
    response_data=jsonify(users=users,counts=count)
    return response_data


def fast_db_populate(num_entries):
    count=0
    cur = g.db.cursor()
    while count < num_entries:
        userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
        # insert_result = insert("USERS", ['name','version'], [userName,1.0])
        query = getquery("USERS", ['name','version'], [userName,1.0])
        count+=1
        cur.execute(query, [userName,1.0])
    g.db.commit()
    id = cur.lastrowid
    cur.close()
    return True

def getquery(table, fields=(), values=()):
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    return query


def insert(table, fields=(), values=()):
    # g.db is the database connection
    cur = g.db.cursor()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    g.db.commit()
    id = cur.lastrowid
    cur.close()
    return id




@app.route('/_view_database')
def view_database():
    print("g.db", g.db)
    users = g.db.execute("SELECT * FROM USERS LIMIT 10;").fetchall()
    count = g.db.execute("SELECT count(*) FROM USERS WHERE version=1.0;").fetchall()
    response_data=jsonify(users=users,counts=count)
    return response_data


@app.before_request
def before_request():
    print("before_request ran")
    g.db = sqlite3.connect(DATABASE)
    print("g.db", g.db)

@app.teardown_request
def teardown_request(exception):
    print("teardown_request ran")
    if hasattr(g, 'db'):
        g.db.close()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@app.route('/')
def home():
    title = "KA Coding Challenge"
    return render_template('home.html', title=title)


@app.route('/about')
def about():
    title="VSS"
    return render_template('about.html', title=title)
