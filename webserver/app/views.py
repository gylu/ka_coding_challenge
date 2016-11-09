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

@app.route('/_view_database')
def view_database():
    return jsonify(count_infection_versions())


@app.route('/')
def home():
    title = "KA Coding Challenge"
    return render_template('home.html', title=title)


@app.route('/_delete_all_entries_from_db')
def delete_all_entries_from_db():
    cur = g.db.cursor()
    statement = 'Delete FROM ENROLLMENTS;'
    cur.execute(statement)
    statement = 'Delete FROM USERS;'
    cur.execute(statement)
    g.db.commit()
    cur.close()
    return jsonify(count_infection_versions())


@app.route('/_total_infection')
def total_infection():
    infection_version=request.args.get('infection_version', 0, type=str)
    print("infection_version", infection_version)
    if not isinstance(infection_version, str):
        print("performing total_infection")
        infection_version=1.1
    cur = g.db.cursor()
    query = 'update users set version='+str(infection_version)
    cur.execute(query)
    g.db.commit()
    cur.close()
    return jsonify(count_infection_versions())


@app.route('/_limited_infection')
def limited_infection():
    print("here in limited infection")
    infection_version=request.args.get('infection_version', 0, type=str)
    user_id_to_infect=request.args.get('user_id_to_infect', 0, type=str)
    limited_infection_type=request.args.get('limited_infection_type', 0, type=str)
    print("request.args",request.args)
    print("infection_version", infection_version)
    print("user_id_to_infect", user_id_to_infect)
    print("limited_infection_type", limited_infection_type)
    # cur = g.db.cursor()
    # query = 'update users set version='+str(infection_version)
    # cur.execute(query)
    # g.db.commit()
    # cur.close()
    return jsonify(count_infection_versions())


def count_infection_versions():
    total_num_users = g.db.execute("SELECT count(*) FROM USERS;").fetchall()
    num_of_distinct_versions = g.db.execute("SELECT count(distinct(version)) FROM users").fetchall()[0][0]
    list_of_versions = [version_item[0] for version_item in g.db.execute("SELECT distinct(version) FROM users").fetchall()] #because for some reason, the query returns with: [(1.1,), (1,)]
    random_users = g.db.execute("SELECT * FROM USERS ORDER BY RANDOM() LIMIT 5;").fetchall()
    users_per_version=[]
    for version in list_of_versions:
        users_per_version.append(g.db.execute("SELECT count(*) FROM users where version="+str(version)).fetchall()[0][0])
    versions_info={"total_num_users":total_num_users,"num_of_distinct_versions":num_of_distinct_versions, "list_of_versions":list_of_versions, "users_per_version":users_per_version, "random_users":random_users}
    print("versions_info:",versions_info)
    return versions_info

# @app.route('/_populate_database_old')
# def populate_database():
#     num_entries=request.args.get('num_entries', 0, type=int)
#     print("num_entries", num_entries)
#     if num_entries==0 or not isinstance(num_entries, int):
#         print("here")
#         num_entries=100
#     fast_db_populate(num_entries)
#     return jsonify(count_infection_versions())




# def fast_db_populate_old(num_entries):
#     count=0
#     cur = g.db.cursor()
#     while count < num_entries:
#         userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
#         # insert_result = insert("USERS", ['name','version'], [userName,1.0])
#         query = make_insert_statement("USERS", ['name','version'], [userName,1.0])
#         count+=1
#         cur.execute(query, [userName,1.0])
#         id = cur.lastrowid
#         print("id:", id)
#     g.db.commit()
#     id = cur.lastrowid
#     cur.close()


@app.route('/_populate_database')
def populate_database():
    num_entries=request.args.get('num_entries', 0, type=int)
    print("num_entries", num_entries)
    if num_entries==0 or not isinstance(num_entries, int):
        print("here")
        num_entries=100
    fast_db_populate(num_entries)
    return jsonify(count_infection_versions())



def fast_db_populate(num_entries):
    count=0
    cur = g.db.cursor()
    max_num_courses_user_can_be_in=4
    total_num_courses=20
    list_possible_courses=[num for num in range(1,total_num_courses)]
    role=''
    students_per_teachers=20

    while count < num_entries:
        userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
        statement = make_insert_statement("USERS", ['name','version'], [userName,1.0])
        #print("statement",statement)
        count+=1
        cur.execute(statement, [userName,1.0]) #the execute statement needs to have the values there
        user_id_just_created = cur.lastrowid
        #randomly determine how many courses user will be in
        number_of_courses_user_enrolled_in = random.choice(range(1,max_num_courses_user_can_be_in+1))
        courses_user_enrolled_in = random.sample(list_possible_courses,number_of_courses_user_enrolled_in) #samples without replacement
        #for each course, randomly determine user's role. 1 of 20 becomes teacher
        for course_id in courses_user_enrolled_in:
            if random.randrange(students_per_teachers) == 1:
                role='TEACHER'
            else:
                role='STUDENT'
            values=[course_id,user_id_just_created,role]
            statement = make_insert_statement("ENROLLMENTS", ['course_id','user_id', 'user_role'], values)
            cur.execute(statement,values)
        print("user_id_just_created:", user_id_just_created)
    g.db.commit()
    cur.close()




def make_insert_statement(table, fields=(), values=()):
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




@app.route('/about')
def about():
    title="VSS"
    return render_template('about.html', title=title)
