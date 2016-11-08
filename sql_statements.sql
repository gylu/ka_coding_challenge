.header on
.mode column
.timer on

DROP TABLE USERS;
CREATE TABLE USERS(
   user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   name TEXT,
   version REAL,
);



DROP TABLE ENROLLMENTS;
CREATE TABLE ENROLLMENTS(
   course_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   user_id INTEGER PRIMARY KEY,
   user_role TEXT
);




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


INSERT INTO USERS (NAME,VERSION) VALUES ( 'Paul', 1.0);
INSERT INTO USERS (NAME,VERSION) VALUES ( 'George', 1.0);
INSERT INTO USERS (NAME,VERSION) VALUES ( 'Dave', 1.1);