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

# Constants
MAIN_HTML_FILE = "main.html"

# Variables
CONFIG = {}
service = Flask( __name__ )
database = None

# Load config
if sys.argv.__len__() < 2:
    sys.exit( "Config path as parameter is missing. Exiting." )

CONFIG = loadConfig( str( sys.argv[1] ) )

# Define our signal handler for gracefully ending the script
def signalHandler( signal, frame ):
    print( "Stopping all services..." )
    #service.terminate()
    #service.join()

# Init SIGINT-Signal to gracefully quit the Script
def initInterruptSignal():
    signal.signal( signal.SIGINT, signalHandler )

    print( "Press Ctrl+C to exit." )

def callWebHook( target, method, body ):
    return requests.request( method, target, data = body )

def complementWebhookBody( webhookBody, requestInfo ):
    requestInfo["timestamp"] = str( requestInfo["timestamp"] )

    # Names of dict-entries in PLACEHOLDER and requestInfo must be in sync, or otherwise the items can not be matched.
    for entry in PLACEHOLDER:
        webhookBody = webhookBody.replace( PLACEHOLDER[entry], requestInfo[entry] )

    return webhookBody

@service.route( CONFIG["PATH_PREFIX"] + "/<path:endpoint>", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
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

    if endpointConfig["log"]:
        database.logRequest( requestInfo )

    if endpointConfig["webhookUrl"]:
        print( "--> Calling webhook URL \"" + endpointConfig["webhookUrl"] + "\"" )
        webhookBody = ""

        if endpointConfig["webhookBody"]:
            webhookBody = complementWebhookBody( endpointConfig["webhookBody"], requestInfo )

        response = callWebHook( endpointConfig["webhookUrl"], endpointConfig["webhookMethod"], webhookBody )

        print( "--> Response code: " + str( response.status_code ) )

    return render_template( MAIN_HTML_FILE, message = endpointConfig["message"], redirectUrl = endpointConfig["redirectUrl"], redirectWait = endpointConfig["redirectWait"] )

print( "Starting service." )
#initInterruptSignal()
database = Database( CONFIG["DATABASE"])
service.run( CONFIG["HOST"], CONFIG["PORT"] )