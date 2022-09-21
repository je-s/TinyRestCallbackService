import sys
from flask import Flask, request

if len( sys.argv ) < 2:
    sys.exit( "Port number is missing. Exiting." )

service = Flask( __name__ )

@service.route( "/", methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] )
def index():
    print( "Endpoint: /" )
    print( "Request data: " + str( request.data ) )

    return request.data

@service.route( "/<path:endpoint>", methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] )
def endpoint( endpoint ):
    print( "Endpoint: " + endpoint )
    print( "Request data: " + str( request.data ) )

    return request.data

service.run( "0.0.0.0", sys.argv[1] )