from flask import Flask, request

service = Flask( __name__ )

@service.route( "/", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
def endpoint():
    print( request.data )
    return request.data

service.run( "0.0.0.0", 5001 )