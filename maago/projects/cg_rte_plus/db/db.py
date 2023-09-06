import duckdb
import glob


class CGRTEPlusSingletonDuckDB:
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
        # os.listdir('maago/database')
        sql_files = glob.glob("maago/projects/cg_rte_plus/db/migrations/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def cleanup():
        instance = CGRTEPlusSingletonDuckDB.get_instance()
        sql_files = glob.glob("maago/projects/cg_rte_plus/db/cleanup/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, "r") as file:
                sql = file.read()
                instance.execute(sql)
