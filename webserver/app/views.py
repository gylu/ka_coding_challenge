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
    total_num_users = g.db.execute("SELECT count(*) FROM USERS;").fetchall() #added comment: O(N) or O(1)
    num_of_distinct_versions = g.db.execute("SELECT count(distinct(version)) FROM users").fetchall()[0][0] #added comment: O(N)
    list_of_versions = [version_item[0] for version_item in g.db.execute("SELECT distinct(version) FROM users").fetchall()] #because the query returns with: [(1.1,), (1,)]. #added comment: O(N)
    random_users = g.db.execute("SELECT * FROM USERS ORDER BY RANDOM() LIMIT 5;").fetchall() ##added comment: O(1)
    all_users = g.db.execute("SELECT user_id, version FROM USERS;").fetchall() #O(1) runtime?
    nodes=[{'id': item[0], 'group':item[1]} for item in all_users]
    all_relationships = g.db.execute("SELECT * FROM RELATIONSHIPS;").fetchall()
    links=[{"source":item[0], "target":item[1],"value":1} for item in all_relationships]


    users_per_version=[]
    for version in list_of_versions: #added comment: O(N*N) total depending on how many versions there are
        users_per_version.append(g.db.execute("SELECT count(*) FROM users where version="+str(version)).fetchall()[0][0]) #this is O(N) because I don't have index.
    versions_info={"nodes":nodes,"links":links,"total_num_users":total_num_users,"num_of_distinct_versions":num_of_distinct_versions, "list_of_versions":list_of_versions, "users_per_version":users_per_version, "random_users":random_users}
    #print("versions_info:",versions_info)
    return versions_info



@app.route('/_delete_all_entries_from_db')
def delete_all_entries_from_db():
    """
    Called via AJAX from the client side    
    Deletes all entries from all tables
    Does not delete the tables
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
    print("Running limited infection")
    infection_version=request.args.get('infection_version', 0, type=str)
    user_id_to_infect=request.args.get('user_id_to_infect', 0, type=str)
    infection_type=request.args.get('infection_type', 0, type=str)
    print("infection_version:", infection_version)
    print("user_id_to_infect:", user_id_to_infect)
    print("infection_type:", infection_type)
    #ALL_RELATIONS_RECUR, ALL_RELATIONS, SAME_COURSE_ONLY
    if infection_type=='LIMITED': #this loop is most likely O(N^2), or O(NlogN) to go through an indexed version of this
        statement='update users set version='+infection_version+' where user_id in (select user_id from ENROLLMENTS where course_id in (select course_id from ENROLLMENTS where user_id='+user_id_to_infect+'))'
        execute_statement(statement)
    #this gets all the users in the same courses as user_id_to_infect and infect them, then repeat for those users
    elif infection_type=='TOTAL':
        users_to_infect=set()
        users_to_infect.add(user_id_to_infect)
        while users_to_infect: #This whole loop is O(N^2 log N)
            user_id_to_infect_in_loop=str(users_to_infect.pop())
            print("user_id_to_infect_in_loop: ", user_id_to_infect_in_loop)
            print("infection_version: ", infection_version)
            query=( #this query is O(NlogN). This query gets all the users that have the same course as the target user
                'select u1.user_id from '
                'ENROLLMENTS e1 '
                'join users u1 '
                'on u1.user_id=e1.user_id '
                'where u1.version<>'+infection_version+' ' #this prevents looping
                'and e1.course_id in '
                '(select e2.course_id from '
                    'ENROLLMENTS e2 where e2.user_id='+user_id_to_infect_in_loop+')'
            )
            print("query: ",query)
            # 1. query to get all classmates
            more_users=g.db.execute(query).fetchall()
            print("more_users: ", more_users)
            for new_user_to_add in more_users:
                # 3. repeating step 1 for each of these classmates
                users_to_infect.add(new_user_to_add[0]) #new_user_to_add is of the form (user_id,name,version,)  - has a comma at the end for some reason

            statement=(
                'update users set version='+infection_version+' '
                'where user_id in '
                 +'('+query+');'
            )
            print("statement: ", statement)
            # 2. infect all of these classmates
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
    1. create the total number of uesers, insert into USERS table
    2. select the teachers (randomly, without replacement from list)
    3. for each teacher, assign users as students in the enrollments
    """
    print("request.args: ", request.args)
    #parse variables from the ajax request
    num_users_to_create=request.args.get('num_users_to_create', 0, type=int)
    num_teachers=request.args.get('num_teachers', 0, type=int)
    version_number=request.args.get('version_number', 0, type=str)
    num_users_with_teachers=request.args.get('num_users_with_teachers', 0, type=int)
    num_users_with_teachers=int(num_users_with_teachers)
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

    #2. Designate users as teachers
    teachers=random.sample(new_users,num_teachers)
    students_to_add=new_users.copy()
    students_to_add.difference_update(teachers) #remove the teachers that were just sampled out

    #3. Assign students with users uniquely (each user that is not a teacher gets assigned to a teacher) for the first pass
    #4. Then, resample and assign again if more than one teacher if this was specified        
    cur = g.db.cursor()
    while num_users_with_teachers>0:
        for i,teacher in enumerate(teachers):
            #randomly assign some students
            if i+1==len(teachers):
                students=students_to_add #add all remaining number of students
            else:
                if num_users_with_teachers > len(students_to_add):
                    avg_num_students_per_teacher=len(students_to_add)//len(teachers)
                else:
                    avg_num_students_per_teacher=num_users_with_teachers//len(teachers)
                random_num_students_to_assign=random.randint(math.ceil(avg_num_students_per_teacher-0.3*avg_num_students_per_teacher),math.ceil(avg_num_students_per_teacher+0.3*avg_num_students_per_teacher))
                students=random.sample(students_to_add,random_num_students_to_assign)
                students_to_add.difference_update(students)
            for student in students:
                try:
                    statement=make_insert_statement("RELATIONSHIPS", ['teacher_id','student_id'],[teacher,student])
                    cur.execute(statement, [teacher,student]) #the execute statement needs to have the values there
                except:
                    print("tried to insert a duplicate, ignored")
        if num_users_with_teachers>num_users_to_create-num_teachers:
            num_students_to_add=num_users_to_create-num_teachers
        else:
            num_students_to_add=num_users_with_teachers   
        num_users_with_teachers-=num_students_to_add
        students_to_add=set(random.sample(new_users, num_users_with_teachers))
        g.db.commit()
    cur.close()
    return jsonify(count_infection_versions())



    # num_users_to_create=request.args.get('num_users_to_create', 0, type=int)
    # max_num_courses_user_can_be_in=request.args.get('max_num_courses_user_can_be_in', 0, type=int)
    # total_num_courses=request.args.get('total_num_courses', 0, type=int)
    # students_per_teacher=request.args.get('students_per_teacher', 0, type=int)
    # version_number=request.args.get('version_number', 0, type=str)
    #course_ids will be incremental, starting from 1
    #old stuff, now commented out

    # list_possible_courses=[num for num in range(1,total_num_courses+1)]
    # count=0
    # cur = g.db.cursor()
    # while count < num_users_to_create:
    #     userName=random.choice(string.ascii_letters[26::])+random.choice(['a','e','i','o','u','y'])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(['a','e','i','o','u','y'])
    #     statement = make_insert_statement("USERS", ['name','version'], [userName,version_number])
    #     count+=1
    #     cur.execute(statement, [userName,version_number]) #the execute statement needs to have the values there
    #     user_id_just_created = cur.lastrowid
    #     #randomly determine how many courses this user will be in, from 1 to the max_num_courses_user_can_be_in
    #     number_of_courses_user_enrolled_in = random.choice(range(1,max_num_courses_user_can_be_in+1))
    #     courses_user_enrolled_in = random.sample(list_possible_courses,number_of_courses_user_enrolled_in) #samples without replacement
    #     #for each course, randomly determine user's role. 1 of 20 becomes teacher
    #     for course_id in courses_user_enrolled_in:
    #         if random.randrange(students_per_teacher) == 1:
    #             role='TEACHER'
    #         else:
    #             role='STUDENT'
    #         values=[course_id,user_id_just_created,role]
    #         statement = make_insert_statement("ENROLLMENTS", ['course_id','user_id', 'user_role'], values)
    #         cur.execute(statement,values)
    # g.db.commit()
    # cur.close()
    # return jsonify(count_infection_versions())


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
