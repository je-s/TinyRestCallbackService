import sys
import os
import toml
import signal
from flask import Flask, request
from markupsafe import escape

# Constants

# Variables
CONFIG = {}

# Load config
def loadConfig( configPath ):
    try:
        global CONFIG
        CONFIG = toml.load( configPath, _dict = dict )
        print( "Config successfuly loaded from '" + os.path.abspath( configPath ) + "'." )
    except FileNotFoundError:
        sys.exit( "Could not find config file '" + os.path.abspath( configPath ) + "'. Exiting." )

loadConfig( str( sys.argv[1] ) )

# ## Define our signal handler for gracefully ending the script
# def signalHandler( signal, frame ):
#     print( "Stopping all services..." )

# # Init SIGINT-Signal to gracefully quit the Script
# def initInterruptSignal():
#     signal.signal( signal.SIGINT, signalHandler )
#     print( "Press Ctrl+C to exit." )

service = Flask (__name__ )

@service.route( CONFIG["PATH_PREFIX"] + "/<path:endpoint>", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
def endpoint( endpoint ):
    endpoint = escape( endpoint )
    method = request.method
    host = request.host
    requestUrl = request.url
    remoteIp = request.remote_addr
    userAgent = request.user_agent

    return "msg"

@service.route( CONFIG["PATH_PREFIX"] + "/<path:endpoint>/debug", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
def debugEndpoint( endpoint ):
    endpoint = escape( endpoint )
    method = request.method
    host = request.host
    requestUrl = request.url
    remoteIp = request.remote_addr
    userAgent = request.user_agent

    return f"""
                Endpoint: { endpoint }
                <br>Method: { method }
                <br>Host: { host }
                <br>Request URL: { requestUrl }
                <br>Remote IP: { remoteIp }
                <br>User Agent: { userAgent }"""

if __name__=='__main__':
    # initInterruptSignal()
    service.run( CONFIG["HOST"], CONFIG["PORT"] )