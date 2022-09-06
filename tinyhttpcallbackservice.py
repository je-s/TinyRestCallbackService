from sql_statements import STATEMENT
from placeholders import PLACEHOLDER
import sys
import os
import toml
import signal
from flask import Flask, request, render_template
from markupsafe import escape
import sqlite3
import time
import json
import requests
import string

# Constants
MAIN_HTML_FILE = "main.html"

# Variables
CONFIG = {}
service = Flask( __name__ )

# Load config
def loadConfig( configPath ):
    try:
        global CONFIG
        CONFIG = toml.load( configPath, _dict = dict )

        print( "Config successfuly loaded from '" + os.path.abspath( configPath ) + "'." )
    except FileNotFoundError:
        sys.exit( "Could not find config file '" + os.path.abspath( configPath ) + "'. Exiting." )

loadConfig( str( sys.argv[1] ) )

# Define our signal handler for gracefully ending the script
def signalHandler( signal, frame ):
    print( "Stopping all services..." )
    #service.terminate()
    #service.join()

# Init SIGINT-Signal to gracefully quit the Script
def initInterruptSignal():
    signal.signal( signal.SIGINT, signalHandler )

    print( "Press Ctrl+C to exit." )

def initDatabase():
    databaseConnection = sqlite3.connect( CONFIG["DATABASE"] )

    cursor = databaseConnection.cursor()

    try:
        cursor.execute( STATEMENT["GET_ALL_ENDPOINTS"] )
    except sqlite3.OperationalError:
        print( "Database with name \"" + CONFIG["DATABASE"] + "\" not initialised. Creating tables." )

        cursor.execute( STATEMENT["CREATE_ENDPOINT_CONFIG"] )
        cursor.execute( STATEMENT["CREATE_LOG"] )

        databaseConnection.commit()

    databaseConnection.close()

def getEndpointConfig( endpoint, method ):
    databaseConnection = sqlite3.connect( CONFIG["DATABASE"] )

    cursor = databaseConnection.cursor()
    cursor.execute( STATEMENT["GET_ENDPOINT"], ( endpoint, method, ) )
    result = cursor.fetchone()

    databaseConnection.close()

    endpointConfig = None

    if result is not None:
        endpointConfig = {
            "log" : result[2],
            "message" : result[3],
            "redirectUrl": result[4],
            "redirectWait": result[5],
            "webhook" : result[6],
            "webhookMethod" : result[7],
            "webhookBody" : result[8]
        }

    return endpointConfig

def logRequest( requestInfo ):
    databaseConnection = sqlite3.connect( CONFIG["DATABASE"] )

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
    requestInfo = {
        "endpoint" : str( escape( endpoint ) ),
        "method" : str( request.method ),
        "host" : str( request.host ),
        "requestUrl" : str( request.url ),
        "remoteIp" : str( request.remote_addr ),
        "userAgent" : str( request.user_agent ),
        "timestamp" : int( time.time() )
    }

    print( "-> Endpoint \"" + requestInfo["endpoint"] + "\" called with method \"" + requestInfo["method"] + "\" from " + requestInfo["remoteIp"] )
    endpointConfig = getEndpointConfig( requestInfo["endpoint"], requestInfo["method"] )

    if endpointConfig is None:
        return CONFIG["DEFAULT_MESSAGE"]

    if endpointConfig["log"]:
        logRequest( requestInfo )

    if endpointConfig["webhook"]:
        print( "--> Calling webhook \"" + endpointConfig["webhook"] + "\"" )
        webhookBody = ""

        if endpointConfig["webhookBody"]:
            webhookBody = complementWebhookBody( endpointConfig["webhookBody"], requestInfo )

        response = callWebHook( endpointConfig["webhook"], endpointConfig["webhookMethod"], webhookBody )

        print( "--> Response code: " + str( response.status_code ) )

    return render_template( MAIN_HTML_FILE, message = endpointConfig["message"], redirectUrl = endpointConfig["redirectUrl"], redirectWait = endpointConfig["redirectWait"] )

if __name__=='__main__':
    #initInterruptSignal()
    initDatabase()
    service.run( CONFIG["HOST"], CONFIG["PORT"] )