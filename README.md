# Khan Academy Coding Challenge
https://www.google.com/url?hl=en&q=https://docs.google.com/a/khanacademy.org/document/d/1NiKv-MjULOFyyc8f5w8R_EqvuPJ10wJVJgZhtTK9VKc/edit%23heading%3Dh.24vvz52659j3&source=gmail&ust=1478512420209000&usg=AFQjCNGx71bFvo6iXMb-B2c51_OlH4mJLw

# How to run
First navigate to khan_coding_challenge/webserver, then run in the console:
$ python3 run.py

Then open up a web browser and navigate to: http://0.0.0.0:1024/

The entire logic is in the file: khan_coding_challenge/webserver/app/views.py


# Requirements (as imposed by challenge):
1. Model the user 
	- Have version attribute
	- capture the coaching relationship
	- A coach can coach any number of users
2. Create an infection algorithm that:
 1. total_infection:
	- Starting from any given user, the entire connected component of the coaching graph containing that user should become infected.
 	- Infections are transitive
 	- Infections are transferred by both the “coaches” and “is coached by” relations
 2. perform_infection


# Solution:
Treat problem as a sql problem:
* A user will be a row in a database
* Total_infection would then be an update sql call
* perform_infection would also be a sql call
Pros:
Easier to perform total_infection (just update all users)
Cons:
Harder to perform perform_infection (might require some complicated joins)


# Web framework to use:
Flask (I have some familiarty with flask, where as Django would be too heavyweight, Webapp2 is not as popular)


# Database considerations:
* I am going to use SQLITE. Most linux machines come pre-installed with sqllite. SQLite's main drawback is that it can't do concurrent writes and only runs on one machine, but that is acceptable for this project.
* For a more capable database in the future, maybe MySQL or Postgres: http://stackoverflow.com/questions/4813890/sqlite-or-mysql-how-to-decide
* Postgres is more SQL standard adhereing than MySQL, more capable that sqlite.
* SQL databases are easier/smaller memory requirements than Neo4j or Casandra.

Schema:
Two tables: USERS and ENROLLMENTS

CREATE TABLE USERS(
   user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   name TEXT,
   version REAL #version of the site that the user see
);

CREATE TABLE ENROLLMENTS(
   course_id INTEGER NOT NULL,
   user_id INTEGER NOT NULL,
   user_role TEXT NOT NULL, #can be TEACHER or STUDENT
   PRIMARY KEY(course_id, user_id)
);

Instead of having a table for relations, for example (user1, user2), the ENROLLMENTS table stores the relationship information via who's in a course

See khan_coding_challenge/webserver/app/views.py for how the database is populated, queried, and updated

Tutorials followed:
http://opentechschool.github.io/python-flask/extras/databases.html


==============================

Another way of approaching this problem (the path not taken):

Using python classes and objects, where each user is an object. 
Relationships with other users will be modeled as as list or dictionary
E.g.
user1:
user1.coaches = [user2, user3, user4, ....]

Then spreading an infection will involve doing a recursive call such as:
def total_infection(newVersion, targetUser):
	targetUser.version=newVersion
	for user in targetUser.coaches + targetUser.coachedby: #or alternatively, use an efficient graph algorithm
		if not <something that detects cycle looping>:
			total_infection(user,newVersion)

Spreading a limited infection will involve doing a recursive call such as:
def perform_infection(newVersion, targetUser, infection_type):
	targetUser.version=newVersion
	if infection_type=="class_only":
		for user in targetUser.coaches + targetUser.coachedby:
				perform_infection(user,newVersion)
	elif infection_type=="something_else"...

Drawbacks to this approach:
* Python lists/dictionaries can't be larger than memory size
* Not a "permenant" solution (not stored to database)
* Longer runtime to perform total_infection
* Might be difficult to implement graphs in python: e.g. https://www.python.org/doc/essays/graphs/

Pros:
* Perhaps shorter runtime to perform perform_infection

BUT, I think for this coding challenege, using an actual database is a more realistic approach.







# thoughts_issues_to_address_after_submission.txt

Testing:
-Unit testing on the python functions (using pythons unit testing framework)
-Integrated testing on the front end (using Selenium or something)



# Runtime:
infection_type=='ALL_RELATIONS_RECUR'


# Optimizations and updates that could have been made:
Could have done a recursive query instead of the wierd thing I did that mixed python and sql

# Questions that may come up
What are some other SQL queries that I can run?


How do you check if two users are in the same course?


# Background on SQLITE indicies and run times
## SQLITE indexes:
https://www.tutorialspoint.com/sqlite/sqlite_indexes.htm

## Run time of SQLITE Queries:
https://www.sqlite.org/queryplanner.html
SQLITE full table Scan = O(N)
Lookup by RowID = O(logN)
SELECT price FROM fruitsforsale WHERE rowid=4;

After creating an Index, SQL lite will do 2 binary searches.
First one on the indexed column, eg to get username to rowID,
then a second search to find that rowID

## Primary key vs index:
-need to have one primary key (primary key = for uniqueness)
-can have many indexes (index= for uniqueness and for performance)
http://stackoverflow.com/questions/2878272/when-i-should-use-primary-key-or-index


## Some Big O runtimes:
http://stackoverflow.com/questions/1347552/what-is-the-big-o-for-sql-select
Merge join vs hash join:
http://stackoverflow.com/questions/2065754/is-there-any-general-rule-on-sql-query-complexity-vs-performance

