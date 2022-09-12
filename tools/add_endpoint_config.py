import sys
sys.path.insert( 0, '.' )

from utils import Database
import sys
import sqlite3

if len( sys.argv ) < 2:
    sys.exit( "Database-Name is missing. Exiting." )

endpointConfig = \
{
    "endpoint" : "",
    "method" : "GET",
    "log" : True,
    "message" : "",
    "redirectUrl" : "",
    "redirectWait" : 0,
    "webhookUrl" : "",
    "webhookMethod" : "POST",
    "webhookBody" : ""
}

print( "Enter Endpoint Configuration:" )
endpointConfig["endpoint"] = str( input( "\tEndpoint Path: " ) )
endpointConfig["method"] = str( input( "\tMethod (GET, POST, PUT, DELETE, PATCH, CUSTOM, TEST): " ) )
endpointConfig["log"] = True if input( "\tLog? (y/n): " ) == "y" else False
endpointConfig["message"] = str( input( "\tMessage: " ) )
endpointConfig["redirectUrl"] = str( input( "\tRedirect URL: " ) )
endpointConfig["redirectWait"] = int( input( "\tRedirect Wait (in ms): " ) )
endpointConfig["webhookUrl"] = str( input( "\tWebhook URL: " ) )
endpointConfig["webhookMethod"] = str( input( "\tWebhook Method (GET, POST, PUT, DELETE, PATCH, CUSTOM, TEST): " ) )
endpointConfig["webhookBody"] = str( input( "\tWebhook Body: " ) )

if len( sys.argv ) < 3:
    database = Database( sys.argv[1] )
else:
    database = Database( sys.argv[1], sys.argv[2] )

database.createEndpointConfig( endpointConfig )