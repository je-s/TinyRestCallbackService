import sys
from flask import Flask, request

if len( sys.argv ) < 2:
    sys.exit( "Port number is missing. Exiting." )

service = Flask( __name__ )

@service.route( "/", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
def endpoint():
    print( request.data )
    return request.data

service.run( "0.0.0.0", sys.argv[1] )