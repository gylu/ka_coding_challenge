.header on
.mode column
.timer on

#to create a database
#$ sqlite3 ka_challenge.db

DROP TABLE USERS;
DELETE FROM USERS;
CREATE TABLE USERS(
   user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   name TEXT,
   version REAL
);


--allowing user_role also a primary key allows for user to be in a class as both teacher and student
DROP TABLE ENROLLMENTS;
Delete FROM ENROLLMENTS;
CREATE TABLE ENROLLMENTS(
   course_id INTEGER NOT NULL,
   user_id INTEGER NOT NULL,
   user_role TEXT NOT NULL,
   PRIMARY KEY(course_id, user_id)
);







#################################
## Random notes and scratch paper queries below
#################################
--


#################################
## Should try to optimize this query
#################################

statement='update users set version='+infection_version+' where user_id in (select user_id from ENROLLMENTS where course_id in (select course_id from ENROLLMENTS where user_id='+user_id_to_infect+'))'



# O(N) for inner most loop to find the courses with the right user_id, becauser user_id is not indexed
# This user could be in every possible course, so up to N (or N/2) number of the entries in Enrollments will be returned
# This second loop O(NlogN), in addiiton to the first loop's O(N). Because for each of the N potential course_ids, you check search through enrollments for the matching course_id and get the user_id. 
#The search i LogN because course_id is indexed.
# This "where user_id in" the outside is also O(Log N) each (to find the right user_id and udpate that user), and there could be N user IDs
# If the two subqueries are run for each row in the outter most "where user_id in", then that becomes O(N^3)


#total:
#O(NlogN + NlogN + LogN)
Update users set version = 5
where user_id in #For each result again, update that entry. so O(N Log N again)
	(Select user_id
	from enrollments
	where course_id in #O(N Log N). For each result, search for the course_id, which is log N each. so total here is O(N log N). Might return N results.
		(select course_id  
		from enrollments
		where use_Id=target)) #O(Log N), because indexed by user_id. Might return N results


'select u1.user_id from '
'ENROLLMENTS e1 '
'join users u1 ' 
'on u1.user_id=e1.user_id '  #O(e log u) from inner join. Going through u rows of enrollment, searching for the equal user_id (log u). If not indexed, then O(e*u). say it returns E results.
'where u1.version<>'+infection_version+' '
'and e1.course_id in ' #O(E log E). E results, each one looking up logE to find the course_id
	'(select e2.course_id from '
	    'ENROLLMENTS e2 where e2.user_id='+user_id_to_infect_in_loop+')' #O(log N). Most select statements are LogN. Result might be N of these



#returns 1468
select u1.user_id from
	ENROLLMENTS e1
	join users u1
	on u1.user_id=e1.user_id
	where u1.version <> 1.5 
	and e1.course_id in 
	(select e2.course_id from 
		ENROLLMENTS e2 where e2.user_id=639612);

-----
update users set version=1.4
where user_id in
(select u1.user_id from
	ENROLLMENTS e1
	join users u1
	on u1.user_id=e1.user_id
	where u1.version <> 1.5 
	and e1.course_id in 
	(select e2.course_id from 
		ENROLLMENTS e2 where e2.user_id=639612));


--
Update users set version=1.4
where user_id in 
(select user_id from
	ENROLLMENTS where 
course_id in (select course_id 
	from ENROLLMENTS where user_id=639612))

------
#returns 1468 
select count(*)
from enrollments e1
join users on users.user_id=e1.user_id
join enrollments e2 on e1.course_id=e2.course_id
where e2.user_id=639612;

----
#returns 1221
select count(*)
from users
where user_id in 
(select user_id from
	ENROLLMENTS where 
course_id in (select course_id 
	from ENROLLMENTS where user_id=639612));

-----

#returns 1221
select count(distinct(user_id)) from
	ENROLLMENTS where 
course_id in (select course_id 
	from ENROLLMENTS where user_id=639612);



INSERT INTO USERS (NAME,VERSION) VALUES ( 'Paul', 1.0);
INSERT INTO USERS (NAME,VERSION) VALUES ( 'George', 1.0);
INSERT INTO USERS (NAME,VERSION) VALUES ( 'Dave', 1.1);



--Decided to not go with this option because it would require more duplicate data
--For example, adding a new teacher to a course would require a new row for each student in the course
--The course_id attribute is necessary in order to allow remove ambiguity and cycles in relationships such as A coaches B (course1), B coaches (course2)
DROP TABLE RELATIONSHIPS;
CREATE TABLE RELATIONSHIPS(
   relationship_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   coach_user_id INTEGER,
   student_user_id INTEGER,
   course_id INTEGER
);


