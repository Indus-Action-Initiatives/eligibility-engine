import mysql.connector
from utils.exception_handler import ErrorCatcher
from utils.random import generate_token


class SingletonMySQLDB(metaclass=ErrorCatcher):
    __instance = None

    @staticmethod
    def get_instance():
        if SingletonMySQLDB.__instance == None:
            SingletonMySQLDB()
        return SingletonMySQLDB.__instance

    def __init__(self) -> None:
        if SingletonMySQLDB.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SingletonMySQLDB.__instance = mysql.connector.connect(
                host="localhost",
                database="ee",
                user="ee",
                password="ee"
            )

    @staticmethod
    def fetch_auth_key(tenant: str):
        where_clause = "WHERE tenant_id = " + len(tenant) > 0 if tenant else ""
        select_clause = "SELECT auth_key from auth_key " + where_clause

        db = SingletonMySQLDB.get_instance()
        cursor = db.cursor()
        cursor.execute(select_clause)
        # Handle Error
        result = cursor.fetchall()
        auth_keys_tuple = list(zip(*result))[0]
        return list(auth_keys_tuple)
    
    @staticmethod
    def confirm_auth_table():
        db = SingletonMySQLDB.get_instance()
        create_clause = "CREATE TABLE IF NOT EXISTS auth_key (id VARCHAR(20) NOT NULL, tenant_id VARCHAR(20) NOT NULL, auth_key VARCHAR(20) NOT NULL, PRIMARY KEY (id), UNIQUE(tenant_id), UNIQUE(auth_key))"
        cursor = db.cursor()
        cursor.execute(create_clause)
        db.commit()
    
    @staticmethod
    def add_key(tenant_id, auth_key):
        db = SingletonMySQLDB.get_instance()
        SingletonMySQLDB.confirm_auth_table()
        key_id = "K~{}".format(generate_token())
        insert_clause = "INSERT INTO auth_key VALUES ('{}', '{}', '{}')".format(key_id, tenant_id, auth_key)
        cursor = db.cursor()
        cursor.execute(insert_clause)
        db.commit()
        return cursor.rowcount
