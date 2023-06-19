import mysql.connector
from mysql.connector import Error


def GetDBConnection():
    # TODO: Make singleton?
    dbConnection = mysql.connector.connect(
        host='localhost',
        user='maago',
        passwd='maagoindus',
        db='ee'
    )
    try:
        if dbConnection.is_connected():
            print("connected to the mysql db")
    except Error as e:
        print("error: ", e)
        return None
    return dbConnection
