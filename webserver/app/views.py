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



@app.route('/')
def home():
    title = "KA Coding Challenge"
    return render_template('home.html', title=title)


@app.route('/_view_database')
def view_database():
    """
    Response to an AJAX call to perform some queries
    """
    return jsonify(count_infection_versions())


def count_infection_versions():
    """
    Helper function response to an AJAX call to perform some queries
    """
    total_num_users = g.db.execute("SELECT count(*) FROM USERS;").fetchall()
    num_of_distinct_versions = g.db.execute("SELECT count(distinct(version)) FROM users").fetchall()[0][0]
    list_of_versions = [version_item[0] for version_item in g.db.execute("SELECT distinct(version) FROM users").fetchall()] #because the query returns with: [(1.1,), (1,)]
    random_users = g.db.execute("SELECT * FROM USERS ORDER BY RANDOM() LIMIT 5;").fetchall()
    users_per_version=[]
    for version in list_of_versions:
        users_per_version.append(g.db.execute("SELECT count(*) FROM users where version="+str(version)).fetchall()[0][0])
    versions_info={"total_num_users":total_num_users,"num_of_distinct_versions":num_of_distinct_versions, "list_of_versions":list_of_versions, "users_per_version":users_per_version, "random_users":random_users}
    print("versions_info:",versions_info)
    return versions_info



@app.route('/_delete_all_entries_from_db')
def delete_all_entries_from_db():
    """
    Called via AJAX from the client side    
    Deletes all entries from all tables
    Does not delete the tables
    """
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
    """
    Called via AJAX from the client side
    Performs a "total infection", by simple updating all rows in USERS table with new version
    """    
    infection_version=request.args.get('infection_version', 0, type=str)
    print("Performing total infection. Infection_version", infection_version)
    query = 'update users set version='+str(infection_version)
    execute_statement(query)
    return jsonify(count_infection_versions())


@app.route('/_limited_infection')
def limited_infection():
    """
    Called via AJAX from the client side
    Performs a "limited infection"
    Input: AJAX input 
    limited_infection_type can be one of two options:
    SAME_COURSES_ONLY: only infects everyone that is in the same course as the user.
    ALL_RELATIONS_RECUR: infects every course mate of the user (i.e. everyone that is in the same course as the user), and then does the same thing for each course mate, until they all have been infected
    """        
    print("Running limited infection")
    infection_version=request.args.get('infection_version', 0, type=str)
    user_id_to_infect=request.args.get('user_id_to_infect', 0, type=str)
    limited_infection_type=request.args.get('limited_infection_type', 0, type=str)
    print("infection_version:", infection_version)
    print("user_id_to_infect:", user_id_to_infect)
    print("limited_infection_type:", limited_infection_type)
    #ALL_RELATIONS_RECUR, ALL_RELATIONS, SAME_COURSE_ONLY
    if limited_infection_type=='SAME_COURSES_ONLY':
        statement='update users set version='+infection_version+' where user_id in (select user_id from ENROLLMENTS where course_id in (select course_id from ENROLLMENTS where user_id='+user_id_to_infect+'))'
        execute_statement(statement)
    #this gets all the users in the same courses as user_id_to_infect and infect them, then repeat for those users
    elif limited_infection_type=='ALL_RELATIONS_RECUR':
        users_to_infect=set()
        users_to_infect.add(user_id_to_infect)
        while users_to_infect: 
            user_id_to_infect_in_loop=str(users_to_infect.pop())
            print("user_id_to_infect_in_loop: ", user_id_to_infect_in_loop)
            print("infection_version: ", infection_version)
            query=(
                'select u1.user_id from '
                'ENROLLMENTS e1 '
                'join users u1 '
                'on u1.user_id=e1.user_id '
                'where u1.version<>'+infection_version+' '
                'and e1.course_id in '
                '(select e2.course_id from '
                    'ENROLLMENTS e2 where e2.user_id='+user_id_to_infect_in_loop+')'
            )
            print("query: ",query)
            more_users=g.db.execute(query).fetchall()
            print("more_users: ", more_users)
            for new_user_to_add in more_users:
                users_to_infect.add(new_user_to_add[0])
            statement=(
                'update users set version='+infection_version+' '
                'where user_id in '
                 +'('+query+');'
            )
            print("statement: ", statement)
            execute_statement(statement)
    return jsonify(count_infection_versions())


def execute_statement(statement):
    cur = g.db.cursor()
    cur.execute(statement)
    g.db.commit()
    last_row_id = cur.lastrowid
    cur.close()
    return last_row_id



@app.route('/_populate_database')
def populate_database():
    """
    Called via AJAX from the client side
    Populates database by adding more users according to the numbers requested
    """
    print("request.args: ", request.args)
    #parse variables from the ajax request
    num_users_to_create=request.args.get('num_users_to_create', 0, type=int)
    max_num_courses_user_can_be_in=request.args.get('max_num_courses_user_can_be_in', 0, type=int)
    total_num_courses=request.args.get('total_num_courses', 0, type=int)
    students_per_teacher=request.args.get('students_per_teacher', 0, type=int)
    version_number=request.args.get('version_number', 0, type=str)
    #course_ids will be incremental, starting from 1
    list_possible_courses=[num for num in range(1,total_num_courses+1)]
    count=0
    cur = g.db.cursor()
    while count < num_users_to_create:
        userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
        statement = make_insert_statement("USERS", ['name','version'], [userName,version_number])
        count+=1
        cur.execute(statement, [userName,version_number]) #the execute statement needs to have the values there
        user_id_just_created = cur.lastrowid
        #randomly determine how many courses this user will be in, from 1 to the max_num_courses_user_can_be_in
        number_of_courses_user_enrolled_in = random.choice(range(1,max_num_courses_user_can_be_in+1))
        courses_user_enrolled_in = random.sample(list_possible_courses,number_of_courses_user_enrolled_in) #samples without replacement
        #for each course, randomly determine user's role. 1 of 20 becomes teacher
        for course_id in courses_user_enrolled_in:
            if random.randrange(students_per_teacher) == 1:
                role='TEACHER'
            else:
                role='STUDENT'
            values=[course_id,user_id_just_created,role]
            statement = make_insert_statement("ENROLLMENTS", ['course_id','user_id', 'user_role'], values)
            cur.execute(statement,values)
    g.db.commit()
    cur.close()
    return jsonify(count_infection_versions())


def make_insert_statement(table, fields=(), values=()):
    """
    Generates SQL statements
    """
    statement = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    return statement


@app.before_request
def before_request():
    print("before_request ran")
    g.db = sqlite3.connect(DATABASE)

@app.teardown_request
def teardown_request(exception):
    print("teardown_request ran")
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/about')
def about():
    title="KA Coding Challenge"
    return render_template('about.html', title=title)
