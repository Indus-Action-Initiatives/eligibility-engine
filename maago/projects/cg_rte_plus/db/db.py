import datetime
import duckdb
import glob

from utils.exception_handler import ErrorCatcher


class CGRTEPlusSingletonDuckDB(metaclass=ErrorCatcher):
    __instance = None

    @staticmethod
    def get_instance():
        if CGRTEPlusSingletonDuckDB.__instance == None:
            CGRTEPlusSingletonDuckDB()
        return CGRTEPlusSingletonDuckDB.__instance

    def __init__(self):
        if CGRTEPlusSingletonDuckDB.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CGRTEPlusSingletonDuckDB.__instance = duckdb.connect(
                database=":memory:", read_only=False
            )
            CGRTEPlusSingletonDuckDB._migrate()

    @staticmethod
    def _migrate():
        instance = CGRTEPlusSingletonDuckDB.get_instance()
        # os.listdir('database')
        sql_files = glob.glob("projects/cg_rte_plus/db/migrations/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def cleanup():
        instance = CGRTEPlusSingletonDuckDB.get_instance()
        sql_files = glob.glob("projects/cg_rte_plus/db/cleanup/*.sql")

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
        print('\n{}: CGRTE DB reset\n\n'.format(ct))