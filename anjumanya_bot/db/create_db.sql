CREATE TABLE IF NOT EXISTS users(
   user_id INT PRIMARY KEY,
   username TEXT,
   name TEXT
   );

CREATE TABLE IF NOT EXISTS exercises(
   id INT PRIMARY KEY,
   name TEXT
   );

CREATE TABLE IF NOT EXISTS data_training(
   id INT PRIMARY KEY,
   user_id INT,
   exercise_id INT,
   sets FLOAT,
   repetition FLOAT,
   date_insert DATETIME,
   FOREIGN KEY (user_id)
      REFERENCES users (user_id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION,
   FOREIGN KEY (exercise_id)
      REFERENCES exercises (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
   );

INSERT INTO exercises(name) VALUES
("анжуманя"),
("подтягивания"),
("планочка"),
("пресс качат"),
("бегит")
;
COMMIT;