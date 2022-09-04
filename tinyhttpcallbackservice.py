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

STATEMENT = {
    "CREATE_ENDPOINT_CONFIG" : "CREATE TABLE ENDPOINT_CONFIG( ENDPOINT TEXT, METHOD TEXT, LOG BOOLEAN, MESSAGE TEXT, REDIRECT_URL TEXT, REDIRECT_WAIT INTEGER, WEBHOOK TEXT, WEBHOOK_METHOD TEXT, WEBHOOK_BODY TEXT, PRIMARY KEY ( ENDPOINT, METHOD ) )",
    "CREATE_LOG" : "CREATE TABLE LOG( ENDPOINT TEXT, METHOD TEXT, TIMESTAMP DATETIME, HOST TEXT, REMOTE_IP TEXT, USER_AGENT TEXT )",
    "GET_ALL_ENDPOINTS" : "SELECT * FROM ENDPOINT_CONFIG",
    "GET_ENDPOINT" : "SELECT * FROM ENDPOINT_CONFIG WHERE ENDPOINT = ? AND METHOD = ?",
    "INSERT_LOG_ENTRY" : "INSERT INTO LOG ( ENDPOINT, METHOD, TIMESTAMP, HOST, REMOTE_IP, USER_AGENT ) VALUES ( :endpoint, :method, :timestamp, :host, :remoteIp, :userAgent )"
}

PLACEHOLDER = {
    "endpoint" : "<<endpoint>>",
    "method" : "<<method>>",
    "host" : "<<host>>",
    "requestUrl" : "<<requestUrl>>",
    "remoteIp" : "<<remoteIp>>",
    "userAgent" : "<<userAgent>>",
    "timestamp" : "<<timestamp>>"
}

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

service = Flask( __name__ )

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

def logCall( requestInfo ):
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

def complementWebhookBody( body, requestInfo ):
    requestInfo["timestamp"] = str( requestInfo["timestamp"] )

    # Names of dict-entries in PLACEHOLDER and requestInfo must be in sync, or otherwise the items can not be matched.
    for entry in PLACEHOLDER:
        body = body.replace( PLACEHOLDER[entry], requestInfo[entry] )

    return body

@service.route( CONFIG["PATH_PREFIX"] + "/<path:endpoint>", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
def endpoint( endpoint ):
    requestInfo = {
        "endpoint" : escape( endpoint ),
        "method" : request.method,
        "host" : request.host,
        "requestUrl" : request.url,
        "remoteIp" : request.remote_addr,
        "userAgent" : str( request.user_agent ),
        "timestamp" : int( time.time() )
    }

    endpointConfig = getEndpointConfig( requestInfo["endpoint"], requestInfo["method"] )

    if endpointConfig is None:
        return CONFIG["DEFAULT_MESSAGE"]

    if endpointConfig["log"]:
        logCall( requestInfo )

    if endpointConfig["webhook"]:
        body = ""

        if endpointConfig["webhookBody"]:
            body = complementWebhookBody( endpointConfig["webhookBody"], requestInfo )

        response = callWebHook( endpointConfig["webhook"], endpointConfig["webhookMethod"], body )

    return render_template( MAIN_HTML_FILE, message = endpointConfig["message"], redirectUrl = endpointConfig["redirectUrl"], redirectWait = endpointConfig["redirectWait"] )

if __name__=='__main__':
    #initInterruptSignal()
    initDatabase()
    service.run( CONFIG["HOST"], CONFIG["PORT"] )