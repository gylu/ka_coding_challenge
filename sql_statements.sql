.header on
.mode column
.timer on

CREATE TABLE USERS(
   user_id INT PRIMARY KEY NOT NULL AUTOINCREMENT,
   name TEXT,
   version INT,
   region TEXT,
);


CREATE TABLE CLASSES(
   class_id INT PRIMARY KEY NOT NULL AUTOINCREMENT,
   class_name TEXT,
   user_id INT,
   user_role TEXT,
);

CREATE TABLE COACHES(
   relationship_id INT PRIMARY KEY NOT NULL AUTOINCREMENT,
   coach_user_id TEXT,
   student_user_id INT,
);


INSERT INTO USERS (NAME,VERSION) VALUES ( 'Paul', 1.0);