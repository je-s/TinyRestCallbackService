from ..utils import Database
import sys
import sqlite3

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
endpointConfig["endpoint"] = str( input( "    Endpoint Path: " ) )
endpointConfig["method"] = str( input( "    Method (GET, POST, PUT, DELETE, PATCH, CUSTOM, TEST): " ) )
endpointConfig["log"] = True if input( "    Log? (y/n): " ) == "y" else False
endpointConfig["message"] = str( input( "    Message: " ) )
endpointConfig["redirectUrl"] = str( input( "    Redirect URL: " ) )
endpointConfig["redirectWait"] = int( input( "    Redirect Wait: " ) )
endpointConfig["webhookUrl"] = str( input( "    Webhook URL: " ) )
endpointConfig["webhookMethod"] = str( input( "    Webhook Method (GET, POST, PUT, DELETE, PATCH, CUSTOM, TEST): " ) )
endpointConfig["webhookBody"] = str( input( "    Webhook Body: " ) )

database = Database( sys.argv[2] )
database.createEndpointConfig( endpointConfig )
