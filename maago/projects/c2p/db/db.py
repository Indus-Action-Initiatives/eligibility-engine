import datetime
import duckdb
import glob

from utils.exception_handler import ErrorCatcher
from utils.logger import logger


class C2PSingletonDuckDB(metaclass=ErrorCatcher):
    __instance = None

    @staticmethod
    def get_instance():
        if C2PSingletonDuckDB.__instance == None:
            C2PSingletonDuckDB()
        return C2PSingletonDuckDB.__instance

    def __init__(self):
        if C2PSingletonDuckDB.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            C2PSingletonDuckDB.__instance = duckdb.connect(
                database=":memory:", read_only=False
            )
            C2PSingletonDuckDB._migrate()

    @staticmethod
    def _migrate():
        instance = C2PSingletonDuckDB.get_instance()
        # os.listdir('database')
        sql_files = glob.glob("projects/c2p/db/migrations/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def cleanup():
        instance = C2PSingletonDuckDB.get_instance()
        sql_files = glob.glob("projects/c2p/db/cleanup/*.sql")

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
        logger.info('\n{}: C2P DB reset\n\n'.format(ct))