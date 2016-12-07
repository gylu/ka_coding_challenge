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
import pdb
import math
DATABASE = '../ka_challenge.db' #assuming we are running from khan_coding_challenge/webserver/run.py, and ka_challenge.db is at khan_coding_challenge/ka_challenge.db



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
    Helper function response to an AJAX call to query the data and return to front end
    """
    total_num_users = g.db.execute("SELECT count(*) FROM USERS;").fetchall() #Expected runtime O(N) or O(1)
    num_of_distinct_versions = g.db.execute("SELECT count(distinct(version)) FROM users").fetchall()[0][0] # O(N)
    list_of_versions = [version_item[0] for version_item in g.db.execute("SELECT distinct(version) FROM users").fetchall()] #because the query returns with: [(1.1,), (1,)]. O(N)
    random_users = g.db.execute("SELECT * FROM USERS ORDER BY RANDOM() LIMIT 5;").fetchall() # O(1), gets 5 random users
    all_users = g.db.execute("SELECT user_id, version FROM USERS;").fetchall() #O(1) runtime?
    nodes=[{'id': item[0], 'group':item[1]} for item in all_users]
    all_relationships = g.db.execute("SELECT * FROM RELATIONSHIPS;").fetchall()
    links=[{"source":item[0], "target":item[1],"value":1} for item in all_relationships]
    users_per_version=[]
    for version in list_of_versions: #O(N*N) total depending on how many versions there are
        users_per_version.append(g.db.execute("SELECT count(*) FROM users where version="+str(version)).fetchall()[0][0]) #this is O(N) because I don't have index.
    versions_info={"nodes":nodes,"links":links,"total_num_users":total_num_users,"num_of_distinct_versions":num_of_distinct_versions, "list_of_versions":list_of_versions, "users_per_version":users_per_version, "random_users":random_users}
    return versions_info



@app.route('/_delete_all_entries_from_db')
def delete_all_entries_from_db():
    """
    Called via AJAX from the client side    
    Deletes all entries from all tables. Does not delete the tables
    """
    cur = g.db.cursor()
    statement = 'Delete FROM RELATIONSHIPS;'
    cur.execute(statement)
    statement = 'Delete FROM USERS;'
    cur.execute(statement)
    g.db.commit()
    cur.close()
    return jsonify(count_infection_versions())


@app.route('/_perform_infection')
def perform_infection():
    """
    Called via AJAX from the client side
    Performs a "limited infection"
    Input: AJAX input 
    infection_type can be one of two options:
    SAME_COURSES_ONLY: only infects everyone that is in the same course as the user.
    ALL_RELATIONS_RECUR: infects every course mate of the user (i.e. everyone that is in the same course as the user), and then does the same thing for each course mate, until they all have been infected
    # 1. query to get all class mates of target user, for every class the target user is in
    # 2. infect all of these classmates
    # 3. repeat step 1 for each of these classmates
    """        
    infection_version=request.args.get('infection_version', 0, type=str)
    user_id_to_infect=request.args.get('user_id_to_infect', 0, type=str)
    infection_type=request.args.get('infection_type', 0, type=str)
    print("infection_version:", infection_version)
    print("user_id_to_infect:", user_id_to_infect)
    print("infection_type:", infection_type)
    #
    if infection_type=='LIMITED': #this loop is most likely O(N^2), or O(NlogN) to go through an indexed version of this
        #get all classes that this user is in
        subquery=( 
            'select student_id as user_id from '
                'RELATIONSHIPS '
                'where teacher_id=' +user_id_to_infect+ ' '
                'or teacher_id in '
                '(select teacher_id from '
                    'RELATIONSHIPS where student_id='+user_id_to_infect+') '
            'UNION '
            'select teacher_id as user_id from '
                'RELATIONSHIPS where student_id='+user_id_to_infect+' '
        )
        print("subquery: ",subquery)
        statement=(
            'update users set version='+infection_version+' '
                'where user_id='+user_id_to_infect+' '
                'or user_id in '
                 +'('+subquery+');'
        )             
        execute_statement(statement)
    # this gets all the users in the same courses as user_id_to_infect and infect them, then repeat for those users
    elif infection_type=='TOTAL':
        users_to_infect=set()
        users_to_infect.add(user_id_to_infect)
        while users_to_infect: #This whole loop is O(N^2 log N)
            user_id_to_infect_in_loop=str(users_to_infect.pop())
            print("user_id_to_infect_in_loop: ", user_id_to_infect_in_loop)
            subquery=( 
                'select u1.user_id from '
                    '(select r1.student_id as user_id from '
                        'RELATIONSHIPS r1 '
                        'where r1.teacher_id=' +user_id_to_infect_in_loop+ ' '
                        'or r1.teacher_id in '
                        '(select teacher_id from '
                            'RELATIONSHIPS where student_id='+user_id_to_infect_in_loop+') '
                    'UNION '
                    'select teacher_id as user_id from '
                        'RELATIONSHIPS where student_id='+user_id_to_infect_in_loop+') as q1 '
                'join users u1 '
                    'on u1.user_id=q1.user_id '
                    'where u1.version<>'+infection_version+' '
            )
            print("subquery: ",subquery)
            # 1. query to get all classmates
            more_users=g.db.execute(subquery+';').fetchall()
            print("more_users: ", more_users)
            # pdb.set_trace()
            for new_user_to_add in more_users:
                # 3. repeating step 1 for each of these classmates
                users_to_infect.add(new_user_to_add[0]) #new_user_to_add is of the form (user_id,)  - has a comma at the end for some reason
            statement=(
                'update users set version='+infection_version+' '
                'where user_id in '
                 +'('+subquery+');'
            )
            print("statement: ", statement)
            # 2. infect all of these classmates
            execute_statement(statement)
    return jsonify(count_infection_versions())




@app.route('/_populate_database')
def populate_database():
    """
    Called via AJAX from the client side
    Populates database by adding more users according to the numbers requested
    1. create the total number of users, insert into USERS table
    2. Designate some users as teachers (randomly, without replacement from list)
    3. Generate the desired number of teacher-to-student relationships, insert into RELATIONSHIPS table
       Resample and assign again if there are more teacher-to-student relationships than there are (num_users_to_create minus num_teachers)
    """
    print("request.args: ", request.args)
    #parse variables from the ajax request
    num_users_to_create=request.args.get('num_users_to_create', 0, type=int)
    num_teachers=request.args.get('num_teachers', 0, type=int)
    version_number=request.args.get('version_number', 0, type=str)
    num_teacher_student_relationships_to_make=int(request.args.get('num_teacher_student_relationships_to_make', 0, type=int))
    count=0
    cur = g.db.cursor()
    new_users=set()
    #1. create users
    while count < num_users_to_create:
        userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
        statement = make_insert_statement("USERS", ['name','version'], [userName,version_number])
        count+=1
        cur.execute(statement, [userName,version_number]) #the execute statement needs to have the values there
        last_row=cur.lastrowid
        new_users.add(last_row)
    g.db.commit()
    cur.close()

    #2. Designate some users as teachers
    teachers=random.sample(new_users,num_teachers)
    students_to_add=new_users.copy()
    students_to_add.difference_update(teachers) #remove the teachers that were just sampled out
    #Condition for handling if there are less teacher-to-student relationships to be created than there are number of users
    if num_teacher_student_relationships_to_make <= num_users_to_create-num_teachers:
        students_to_add=set(random.sample(students_to_add,num_teacher_student_relationships_to_make))
    num_students_to_add=len(students_to_add)

    #3. Generate the desired number of teacher-to-student relationships, insert into RELATIONSHIPS table (each user that is not a teacher gets assigned to a teacher) for the first pass    
    cur = g.db.cursor()
    pdb.set_trace()
    while num_teacher_student_relationships_to_make>0:
        for i,teacher in enumerate(teachers):
            if i+1==len(teachers):             
                students=students_to_add #If there is only 1 teacher left, randomly assign the remaining students
            else:
                avg_num_students_per_teacher=num_students_to_add//num_teachers
                random_num_students_to_assign=random.randint(math.ceil(avg_num_students_per_teacher-0.2*avg_num_students_per_teacher),math.ceil(avg_num_students_per_teacher+0.2*avg_num_students_per_teacher))
                students=random.sample(students_to_add,random_num_students_to_assign)
                students_to_add.difference_update(students)
            for student in students:
                try:
                    statement=make_insert_statement("RELATIONSHIPS", ['teacher_id','student_id'],[teacher,student])
                    cur.execute(statement, [teacher,student]) #the execute statement needs to have the values there
                except:
                    print("tried to insert a duplicate, ignored")
        #Resample and perform more teacher-to-stduent assignments if there are more teacher-to-student relationships than there are (num_users_to_create minus num_teachers)
        num_teacher_student_relationships_to_make-=num_students_to_add
        if num_teacher_student_relationships_to_make>num_users_to_create-num_teachers:
            num_students_to_add=num_users_to_create-num_teachers
        else:
            num_students_to_add=num_teacher_student_relationships_to_make
        students_to_add=set(random.sample(new_users, num_students_to_add))
        g.db.commit()
    cur.close()
    return jsonify(count_infection_versions())


def execute_statement(statement):
    """
    Helper function to execute sql statements
    """
    cur = g.db.cursor()
    cur.execute(statement)
    g.db.commit()
    last_row_id = cur.lastrowid
    cur.close()
    return last_row_id


def make_insert_statement(table, fields=(), values=()):
    """
    Helper function to generate and format sql statements
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
