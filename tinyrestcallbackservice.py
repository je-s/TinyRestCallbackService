from utils import loadConfig, Database, PLACEHOLDER
import sys
import os
import signal
from flask import Flask, request, render_template
from markupsafe import escape
import time
import json
import requests
import string
import threading
from gevent.pywsgi import WSGIServer

# Constants
MAIN_HTML_FILE = "main.html"

# Variables
CONFIG = {}
service = Flask( __name__ )
database = None
server = None

# Load config
if len( sys.argv ) < 2:
    sys.exit( "Config path as parameter is missing. Exiting." )

CONFIG = loadConfig( str( sys.argv[1] ) )

# Define our signal handler for gracefully ending the script
def signalHandler( signal, frame ):
    print( "\nStopping all services..." )
    server.stop()

# Init SIGINT-Signal to gracefully quit the Script
def initInterruptSignal():
    signal.signal( signal.SIGINT, signalHandler )

    print( "Press Ctrl+C to exit." )

def callWebhook( target, method, body, requestInfo ):
    try:
        target = complementString( target, requestInfo )
        print( "--> Calling webhook URL \"" + target + "\"" )

        if body:
            body = complementString( body, requestInfo )

        response = requests.request( method, target, data = body )

        print( "--> Response code: " + str( response.status_code ) )
    except Exception as e:
        print( "--> Error while calling webhook URL \"" + target + "\": " + str( e ) )

# Replace all placeholders (defined in PLACEHOLDERS) in the string with the actual values from requestInfo
def complementString( string, requestInfo ):
    requestInfo["timestamp"] = str( requestInfo["timestamp"] )

    # Names of dict-entries in PLACEHOLDER and requestInfo must be in sync, or otherwise the items can not be matched.
    for entry in PLACEHOLDER:
        string = string.replace( PLACEHOLDER[entry], requestInfo[entry] )

    return string

# Endpoint processor
@service.route( CONFIG["PATH_PREFIX"] + "/<path:endpoint>", methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] )
def endpoint( endpoint ):
    requestInfo = \
    {
        "endpoint" : str( escape( endpoint ) ),
        "method" : str( request.method ),
        "host" : str( request.host ),
        "requestUrl" : str( request.url ),
        "remoteIp" : str( request.remote_addr ),
        "userAgent" : str( request.user_agent ),
        "timestamp" : int( time.time() )
    }

    print( "-> Endpoint \"" + requestInfo["endpoint"] + "\" called with method \"" + requestInfo["method"] + "\" from " + requestInfo["remoteIp"] )
    endpointConfig = database.getEndpointConfig( requestInfo["endpoint"], requestInfo["method"] )

    if endpointConfig is None:
        return CONFIG["DEFAULT_MESSAGE"]

    endpointConfig["message"] = complementString( endpointConfig["message"], requestInfo )
    endpointConfig["redirectUrl"] = complementString( endpointConfig["redirectUrl"], requestInfo )

    if endpointConfig["log"]:
        database.logRequest( requestInfo )

    if endpointConfig["webhookUrl"]:
        webhookThread = threading.Thread(target = callWebhook, args = ( endpointConfig["webhookUrl"], endpointConfig["webhookMethod"], endpointConfig["webhookBody"], requestInfo ) )
        webhookThread.start()

    return render_template( MAIN_HTML_FILE, message = endpointConfig["message"], redirectUrl = endpointConfig["redirectUrl"], redirectWait = endpointConfig["redirectWait"] )

print( "Starting service." )
initInterruptSignal()
database = Database( CONFIG["DATABASE"], CONFIG["SCHEMA"] )
server = WSGIServer( ( CONFIG["HOST"], CONFIG["PORT"] ), service )
server.serve_forever()
