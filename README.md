# Khan Academy Coding Challenge
https://www.google.com/url?hl=en&q=https://docs.google.com/a/khanacademy.org/document/d/1NiKv-MjULOFyyc8f5w8R_EqvuPJ10wJVJgZhtTK9VKc/edit%23heading%3Dh.24vvz52659j3&source=gmail&ust=1478512420209000&usg=AFQjCNGx71bFvo6iXMb-B2c51_OlH4mJLw


# Requirements (as imposed by challenge):

1. Model the user 
	-Have version attribute
	-capture the coaching relationship
	-A coach can coach any number of users
2. Create an infection algorithm that:
 1. total_infection:
	-Starting from any given user, the entire connected component of the coaching graph containing that user should become infected.
 	-infections are transitive
 	-infections are transferred by both the “coaches” and “is coached by” relations
 2. limited_infection



 # Initial Thoughts:

	User attributes:
		version: version number that this user is using
		region: an id corresponding to location
		classes involved in, and role for that class (coach or student)
		coaches: all the users that this user coaches
		coachedby: all the users that coach this user
		friends:
	Infection methods:
		total_infection
			Input: newVersionNumber, userID, or classId
		limited_infection
			Input: newVersionNumber, userID, infection options (how limited)

Solution:
Treat problem as a sequel problem:
A user would be a row in a database
Total_infection would then be an update call
Limited_infection would also be a sequel call

Pros:
Easier to perform total_infection (just update all users)

Cons:
Harder to perform limited_infection (might require some complicated joins)

Webframework to use:
Flask (I've used flask before, where as Django was too heavyweight, Webapp2 is not as popular)

Database:
Postgres
http://stackoverflow.com/questions/4813890/sqlite-or-mysql-how-to-decide
(More SQL standard adhereing than MySQL, more capable that sqlite (even though most linux machines come pre-installed with sqllite). Easier/smaller memory requirements than Neo4j or Casandra.)
SQLite's main drawback is that it can't concurrent writes.

Approximate hours spent:
Planning, design decisions on webframework and DB to use: 3hrs

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
def limited_infection(newVersion, targetUser, infection_type):
	targetUser.version=newVersion
	if infection_type=="class_only":
		for user in targetUser.coaches + targetUser.coachedby:
				limited_infection(user,newVersion)
	elif infection_type=="something_else"...

Drawbacks to this approach:
Cons:
Python lists/dictionaries can't be larger than memory size
Not a permenant solution (not stored to database)
Longer runtime to perform total_infection
Might be difficult to implement graphs in python: e.g. https://www.python.org/doc/essays/graphs/

Pros:
Shorter runtime to perform limited_infection


BUT, I think for this coding challenege, using an actual database is a more realistic approach.
