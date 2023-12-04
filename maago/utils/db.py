import mysql.connector
from mysql.connector import Error
from utils.logger import logger

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
            logger.info("connected to the mysql db")
    except Error as e:
        logger.error("error: ", e)
        return None
    return dbConnection
