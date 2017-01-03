# Khan Academy Coding Challenge

<kbd>
![Alt text](screenshot.png?raw=true "Pipeline")
</kbd>
# How to run
1. Clone or download all contents of this repo, including the .db file
2. Navigate to ```khan_coding_challenge/webserver ```
3. Then run in the console: ``` $ python3 run.py ```
4. Then open up a web browser and navigate to: http://0.0.0.0:1024/

The entire logic is in the file: ```khan_coding_challenge/webserver/app/views.py```


# Requirements as imposed by challenge
1. Model the user 
	- Have version attribute
	- Capture the coaching relationship
	- A coach can coach any number of users
2. Create an infection algorithm that has:
 1. Total_infection:
	- Starting from any given user, the entire connected component of the coaching graph containing that user should become infected.
 	- Infections are transitive
 	- Infections are transferred by both the “coaches” and “is coached by” relations
 2. Limited infection
 	- Performs a limited version of total infection (up to me to decide how to implement)
 3. Optional
 	- Create GUI to help visualization

Original description of problem
https://www.google.com/url?hl=en&q=https://docs.google.com/a/khanacademy.org/document/d/1NiKv-MjULOFyyc8f5w8R_EqvuPJ10wJVJgZhtTK9VKc/edit%23heading%3Dh.24vvz52659j3&source=gmail&ust=1478512420209000&usg=AFQjCNGx71bFvo6iXMb-B2c51_OlH4mJLw

# Solution
Treat problem as a sql problem, therefore each user will be a row in a database

# Web framework used
Flask - I already have some familiarty with flask, where as Django would be too heavyweight, and Webapp2 does not have a large user base

# Database Design
Schema:
Two tables: USERS and RELATIONSHIPS, with the following schemas:

```
CREATE TABLE USERS(
   user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   name TEXT,
   version REAL #version of the site that the user see
);

CREATE TABLE RELATIONSHIPS(
   teacher_id INTEGER NOT NULL,
   student_id INTEGER NOT NULL,
   PRIMARY KEY(teacher_id, student_id)
);
```

# Database considerations
* I chose to use SQLITE. Most linux machines come pre-installed with sqllite. SQLite's main drawback is that it can't do concurrent writes and only runs on one machine, but that is acceptable for this project.
* For a more capable database in the future, maybe MySQL or Postgres: http://stackoverflow.com/questions/4813890/sqlite-or-mysql-how-to-decide
* Postgres is more SQL standard adhereing than MySQL, more capable that sqlite.
* SQL databases are easier/smaller memory requirements than Neo4j or Casandra.

See ```khan_coding_challenge/webserver/app/views.py``` for how the database is populated, queried, and updated



# Other Thoughts and Issues Considered

## Another way of approaching this problem (the path not taken) 

Another approach would have been to use python classes and objects, where each user is an object. 
Relationships with other users will be modeled as as list or dictionary

For example:
```
class User:
    def __init__(self, name, version, list_of_student_ids, list_of_coach_ids):
        self.name=name 						#e.g. 'john'
        self.version=version 				#e.g. 1.1
        self.coaches=list_of_student_ids  	#e.g. [124, 353, 235]
        self.coached_by=list_of_coach_ids 	#e.g. [124, 353, 235]
```

Then spreading an infection will involve doing a recursive call such as:
```
def total_infection(newVersion, targetUser):
	targetUser.version=newVersion
	for user in targetUser.coaches + targetUser.coachedby: #or alternatively, use an efficient graph algorithm
		if not <something that detects cycle looping>:
			total_infection(user,newVersion)
```

Spreading a limited infection will involve doing a recursive call such as:
```
def perform_infection(newVersion, targetUser, infection_type):
	targetUser.version=newVersion
	if infection_type=="class_only":
		for user in targetUser.coaches + targetUser.coachedby:
				perform_infection(user,newVersion)
	elif infection_type=="something_else"...
```

Drawbacks to this approach:
* Python lists/dictionaries can't be larger than memory size
* Not a "permenant" solution (not stored to database)
* Longer runtime to perform total_infection
* Might be difficult to implement graphs in python: e.g. https://www.python.org/doc/essays/graphs/

Pros:
* Perhaps shorter runtime to perform perform_infection

For this coding challenege, using an actual database seemed to be a more realistic approach, therefore this alternative approach of using code was not implemented



## Testing
I did not get a chance to implment unit testing or integrated testing. Instead, I developed a web UI that was used for visual inspection, which could be thought of as a form of beta testing.

## Areas that could use more consideration
I could have done a recursive query instead of the wierd thing I did that mixed python and sql

What are some other SQL queries that I can run?

How do you check if two users are in the same course?




# Notes on SQLITE indexes and run times
## SQLITE indexes:
https://www.tutorialspoint.com/sqlite/sqlite_indexes.htm

## Run time of SQLITE Queries
https://www.sqlite.org/queryplanner.html
SQLITE full table Scan = O(N)
Lookup by RowID = O(logN)
SELECT price FROM fruitsforsale WHERE rowid=4;

After creating an Index, SQL lite will do 2 binary searches.
First one on the indexed column, eg to get username to rowID,
then a second search to find that rowID

## Primary key vs index
- Need to have one primary key (primary key = for uniqueness)
- Can have many indexes (index= for uniqueness and for performance)
http://stackoverflow.com/questions/2878272/when-i-should-use-primary-key-or-index


## Some Big O runtimes
http://stackoverflow.com/questions/1347552/what-is-the-big-o-for-sql-select
Merge join vs hash join:
http://stackoverflow.com/questions/2065754/is-there-any-general-rule-on-sql-query-complexity-vs-performance

## Tutorials followed:
http://opentechschool.github.io/python-flask/extras/databases.html


# Hindsight and feedback from a good friend about areas I need improvement and perhaps why my implementation ultimately did not get me an interview

## Didn't use a DAO or ORM
This caused my code to not be object oriented at all. Object oriented-ness would have provided more encapsulation and future-proof-ness. E.g. the ability to add more methods and properties to classes.
DAOs or ORMs allow you to access your database rows in terms of objects and not just sql statements acting on database rows. I had my front end directly access my sql database. DAOs and ORMs also provide the flexiblity in allowing you to store some of the data in the RAM layer, and potentially do something with it (e.g. something like memcache)
Using DAOs and ORMs provide flexiblity, e.g. it'll allow you to swap out the database, and you won't have to re-write everything.

The fix would have been for my views.py to accessed objects (e.g. user objects, relationship objects), where each object is a row in a database, with there being an object class and methods.

## Lack of code structuring
I didn't use classes or functions or structures. This again makes the code difficult to read, understand, and update

(For future reading: http://docs.python-guide.org/en/latest/writing/structure/)

## Didn't show how I'd programatically implement business knowledge
My garble of sql with python code due directly manipulating the database means business logic and UI code were all jumbled together, which led to difficulty in understanding


## How to get better at the above:
### Read a lot of other people's code
### Work for a company, and that'll force you to read a lot of other people's code