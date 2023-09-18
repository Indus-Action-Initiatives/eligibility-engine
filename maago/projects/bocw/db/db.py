import datetime
import duckdb
import glob

from utils.exception_handler import ErrorCatcher


class BoCWSingletonDuckDB(metaclass=ErrorCatcher):
    __instance = None

    @staticmethod
    def get_instance():
        if BoCWSingletonDuckDB.__instance == None:
            BoCWSingletonDuckDB()
        return BoCWSingletonDuckDB.__instance

    def __init__(self):
        if BoCWSingletonDuckDB.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BoCWSingletonDuckDB.__instance = duckdb.connect(
                database=":memory:", read_only=False
            )
            BoCWSingletonDuckDB._migrate()

    @staticmethod
    def _migrate():
        instance = BoCWSingletonDuckDB.get_instance()
        # os.listdir('database')
        sql_files = glob.glob("projects/bocw/db/migrations/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def cleanup():
        instance = BoCWSingletonDuckDB.get_instance()
        sql_files = glob.glob("projects/bocw/db/cleanup/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def reset():
        __class__.cleanup()
        __class__._migrate()
        ct = datetime.datetime.now()
        print('\n{}: BOCW DB reset\n\n'.format(ct))
