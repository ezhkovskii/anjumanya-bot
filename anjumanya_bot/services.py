from datetime import datetime as dt
from datetime import timedelta as td
from collections import namedtuple

from aiogram.types.input_file import InputFile

from database import Database

from tabulate import tabulate

class User:

    db = Database()

    def __init__(self, user_id, username, name):
        self.user_id = int(user_id)
        self.username = username
        self.name = name

    def registration(self):
        """
        Регистрация пользователя
        проверяем на наличие в бд
        если его нет, то добавляем в бд юзера
        """
        if not self._check_user_in_db():
            self._add_user_to_db()

    def _check_user_in_db(self):
        q = f"""SELECT 1 FROM 'users' WHERE user_id = {self.user_id}"""
        if self.db.sql_query_execute(q):
            return True
        else:
            return False

    def _add_user_to_db(self):
        q = f"""
                INSERT INTO 'users' (user_id, username, name) 
                VALUES 
                ({self.user_id}, "{self.username}", "{self.name}")
            """
        self.db.sql_query_execute(q)


class Exercise:

    Exercise = namedtuple('Exercise', 'name type')
    EXERCISES = [
        Exercise("анжуманя", "set"),
        Exercise("турничек", "set"),
        Exercise("планочка", "time"),
        Exercise("пресс качат", "set"),
        Exercise("приседания", "set"),
        Exercise("бассик", "time"),
        Exercise("спортзал", "time"),
    ]

    @classmethod
    def get_exercises_all(cls):
        return cls.EXERCISES

    @classmethod
    def get_exercise(cls, name):
        for ex in cls.EXERCISES:
            if ex.name == name:
                return ex




class TrainingData:

    OUTPUT_FILENAME = "data.txt"

    db = Database()

    data_for_database = {}

    TIME_INTERVALS = [
        "сегодня",
        "неделя",
        "месяц",
        "год",
    ]

    TYPE_DATA_OUTPUT = ('file', 'text')

    @classmethod
    def get_data_for_time_interval(cls, user_id, interval):
        query = """
                SELECT 
                    exercise,
                    type_ex,
                    sum(sets),
                    sum(repetition),
                    sum(duration_training),
                    date_insert
                FROM
                    data_training
        """
        params = None

        if interval == cls.TIME_INTERVALS[0]: # за "сегодня"
            date_today = dt.today().strftime('%Y-%m-%d')
            query += "WHERE date_insert = ? and user_id = ?"
            params = (date_today, user_id)

        elif interval == cls.TIME_INTERVALS[1]: # за "неделя"
            ...

        elif interval == cls.TIME_INTERVALS[2]: # за "месяц"
            ...

        elif interval == cls.TIME_INTERVALS[3]: # за "год"
            ...

        query += "\nGROUP by exercise, type_ex, date_insert\nORDER BY date_insert"
        data = cls.db.sql_query_execute(query, params)
        print(data)

        if data:
            table = cls._transform_data(data)
        else:
            return None, None

        table_for_output = cls._pretty_table(table)

        if len(data) > 10:
            # формируем файл с таблицей
            with open(cls.OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                f.write(table_for_output)

            file = InputFile(cls.OUTPUT_FILENAME)
            return file, cls.TYPE_DATA_OUTPUT[0]

        else:
            # формируем текст с таблицей
            msg = "<pre>" + table_for_output + "</pre>"
            return msg, cls.TYPE_DATA_OUTPUT[1]


    @classmethod
    def _transform_data(cls, data):
        # преобразуем данные из бд в нормальный вид

        table_set = []
        table_dur = []

        for row in data:
            if row[1] == 'set':
                table_set.append( (row[5], row[0], int(row[2]) * int(row[3])) )
            elif row[1] == 'time':
                table_dur.append( (row[5], row[0], cls._second_to_minutes(row[4])) )

        return table_set + table_dur

    @classmethod
    def _second_to_minutes(cls, seconds):
        minutes_seconds = str(seconds // 60)
        minutes_seconds += "."
        minutes_seconds += str(seconds % 60)
        return minutes_seconds

    @classmethod
    def _pretty_table(cls, table):
        return tabulate(table, headers=("дата", "упражнение", "результат"), stralign='center', tablefmt="grid")

    @classmethod
    def get_time_intervals_all(cls):
        return cls.TIME_INTERVALS

    @classmethod
    def time_interval_exist(cls, name_interval):
        if name_interval in cls.TIME_INTERVALS:
            return True
        else:
            return False

    @classmethod
    def add_training_data(cls, user_id, exercise, sets=None, repetition=None, duration_training=None):
        date_insert = dt.today().strftime('%Y-%m-%d')
        ex = Exercise.get_exercise(exercise)  # ex[0] упражнение, ex[1] тип упражнения

        if (sets == None and repetition == None and duration_training == None) or ex is None:
            # todo: описать ошибки
            return False

        data_to_insert = (user_id, ex.name, ex.type, sets, repetition, duration_training, date_insert)
        q = f"""
                    INSERT INTO 'data_training' (user_id, exercise, type_ex, sets, repetition, duration_training, date_insert) 
                    VALUES 
                    (?, ?, ?, ?, ?, ?, ?)
                """
        cls.db.sql_query_execute(q, data_to_insert)
        return True

    @staticmethod
    def _pars_duration_training(duration_training: str):
        try:
            data = list(map(int, duration_training.split('.')))
        except Exception as e:
            print(e)
            return None
        if len(data) == 1:
            if data[0] < 0:
                return None
            return td(minutes=data[0]).seconds
        elif len(data) == 2:
            if data[0] < 0 or data[1] < 0:
                return None
            return td(minutes=data[0], seconds=data[1]).seconds

    @classmethod
    def data_is_valid(cls, data):
        error = ""

        exercise = Exercise.get_exercise(data.get("exercise", None))
        if exercise is None:
            error += "нормально выбери упражнение\n"

        sets = data.get("sets", None)
        repetition = data.get("rep", None)
        if sets is not None and repetition is not None:
            try:
                sets = int(data.get("sets", None))
                repetition = int(data.get("rep", None))
            except Exception as e:
                print(e)
                error += "нормально пиши циферки\n"

        if sets < 0 or repetition < 0:
            error += "нормально пиши циферки\n"

        duration_training = data.get("duration_training", None)
        duration_training_in_seconds = None
        if duration_training is not None:
            duration_training_in_seconds = cls._pars_duration_training(duration_training)
            if duration_training_in_seconds is None:
                error += "нормально пиши циферки\n"

        if sets is None and repetition is None and duration_training is None:
            error += "чето не то"

        if error == "":
            cls.data_for_database["exercise"] = exercise.name
            cls.data_for_database["sets"] = sets
            cls.data_for_database["repetition"] = repetition
            cls.data_for_database["duration_training"] = duration_training_in_seconds

        return error