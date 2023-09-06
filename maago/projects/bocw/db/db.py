import duckdb
import glob


class BoCWSingletonDuckDB:
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
        # os.listdir('maago/database')
        sql_files = glob.glob("maago/projects/bocw/db/migrations/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def cleanup():
        instance = BoCWSingletonDuckDB.get_instance()
        sql_files = glob.glob("maago/projects/bocw/db/cleanup/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)
