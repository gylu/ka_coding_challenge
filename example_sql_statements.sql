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


