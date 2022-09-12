from . import STATEMENT
import sys
import sqlite3

class Database:
    def __init__ ( self, database, schema ):
        self.database = database

        self.schema = schema or './schema.sql'

        databaseConnection = sqlite3.connect( self.database )

        cursor = databaseConnection.cursor()

        try:
            cursor.execute( STATEMENT["GET_ALL_ENDPOINTS"] )
        except sqlite3.OperationalError:
            print( "Database with name \"" + self.database + "\" not initialised. Creating database." )

            try:
                with open( schema, "r" ) as file:
                    cursor.executescript( file.read() )
            except FileNotFoundError:
                sys.exit( "Couldn't create Database, schema file \"" + schema + "\" not found. Exiting." )

            databaseConnection.commit()

        databaseConnection.close()

    def createEndpointConfig( self, endpointConfig ):
        databaseConnection = sqlite3.connect( self.database )

        cursor = databaseConnection.cursor()
        cursor.execute(
            STATEMENT["INSERT_ENDPOINT_CONFIG"],
            {
                "endpoint" : endpointConfig["endpoint"],
                "method" : endpointConfig["method"],
                "log" : endpointConfig["log"],
                "message" : endpointConfig["message"],
                "redirectUrl" : endpointConfig["redirectUrl"],
                "redirectWait" : endpointConfig["redirectWait"],
                "webhookUrl" : endpointConfig["webhookUrl"],
                "webhookMethod" : endpointConfig["webhookMethod"],
                "webhookBody" : endpointConfig["webhookBody"]
            }
        )

        databaseConnection.commit()
        databaseConnection.close()

    def getEndpointConfig( self, endpoint, method ):
        databaseConnection = sqlite3.connect( self.database )

        cursor = databaseConnection.cursor()
        cursor.execute( STATEMENT["GET_ENDPOINT"], ( endpoint, method, ) )
        result = cursor.fetchone()

        databaseConnection.close()

        endpointConfig = None

        if result is not None:
            endpointConfig = \
            {
                "log" : result[2],
                "message" : result[3],
                "redirectUrl": result[4],
                "redirectWait": result[5],
                "webhookUrl" : result[6],
                "webhookMethod" : result[7],
                "webhookBody" : result[8]
            }

        return endpointConfig

    def logRequest( self, requestInfo ):
        databaseConnection = sqlite3.connect( self.database )

        cursor = databaseConnection.cursor()
        cursor.execute(
            STATEMENT["INSERT_LOG_ENTRY"],
            {
                "endpoint" : requestInfo["endpoint"],
                "method" : requestInfo["method"],
                "timestamp" : requestInfo["timestamp"],
                "host" : requestInfo["host"],
                "remoteIp" : requestInfo["remoteIp"],
                "userAgent" : requestInfo["userAgent"]
            }
        )

        databaseConnection.commit()
        databaseConnection.close()