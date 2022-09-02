import sys
import os
import toml
import signal
from flask import Flask, request
from markupsafe import escape
import sqlite3
import time
import json
import requests

# Constants
STATEMENT = {
    "CREATE_ENDPOINT_CONFIG" : "CREATE TABLE ENDPOINT_CONFIG( ENDPOINT TEXT, METHOD TEXT, LOG BOOLEAN, MESSAGE TEXT, REDIRECT_URL TEXT, WEBHOOK TEXT, WEBHOOK_METHOD TEXT, WEBHOOK_PARAMS TEXT, PRIMARY KEY ( ENDPOINT, METHOD ) )",
    "CREATE_LOG" : "CREATE TABLE LOG( ENDPOINT TEXT, METHOD TEXT, TIME DATETIME, HOST TEXT, REMOTE_IP TEXT, USER_AGENT TEXT )",
    "GET_ALL_ENDPOINTS" : "SELECT * FROM ENDPOINT_CONFIG",
    "GET_ENDPOINT" : "SELECT * FROM ENDPOINT_CONFIG WHERE ENDPOINT = ? AND METHOD = ?",
    "INSERT_LOG_ENTRY" : "INSERT INTO LOG ( ENDPOINT, METHOD, TIME, HOST, REMOTE_IP, USER_AGENT ) VALUES ( :endpoint, :method, :time, :host, :remoteIp, :userAgent )"
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

    return result

def logCall( endpoint, method, time, host, remoteIp, userAgent ):
    databaseConnection = sqlite3.connect( CONFIG["DATABASE"] )
    cursor = databaseConnection.cursor()
    cursor.execute(
        STATEMENT["INSERT_LOG_ENTRY"],
        {
            "endpoint" : endpoint,
            "method" : method,
            "time" : time,
            "host" : host,
            "remoteIp" : remoteIp,
            "userAgent" : userAgent
        }
    )
    databaseConnection.commit()
    databaseConnection.close()

def callWebHook( target, method, params ):
    print(params)
    requests.request( method, target, json = params )

@service.route( CONFIG["PATH_PREFIX"] + "/<path:endpoint>", methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'CUSTOM', 'TEST'] )
def endpoint( endpoint ):
    endpoint = escape( endpoint )
    method = request.method
    host = request.host
    requestUrl = request.url
    remoteIp = request.remote_addr
    userAgent = request.user_agent

    result = getEndpointConfig( endpoint, method )
    print(result)

    if result is None:
        return CONFIG["DEFAULT_MESSAGE"]

    endpointConfig = {
        "log" : result[2],
        "message" : result[3],
        "redirectUrl": result[4],
        "webhook" : result[5],
        "webhookMethod" : result[6],
        "webhookParams" : result[7]
    }

    if endpointConfig["log"]:
        logCall( endpoint, method, int( time.time() ), host, remoteIp, str( userAgent ) )

    if endpointConfig["webhook"]:
        params = ""

        if endpointConfig["passParams"]:
            params = json.dumps(
                {
                    "endpoint" : endpoint,
                    "method" : method,
                    "host" : host,
                    "requestUrl" : requestUrl,
                    "remoteIp" : remoteIp,
                    "userAgent" : str( userAgent )
                }
            )

        callWebHook( endpointConfig["webhook"], endpointConfig["webhookMethod"], params )

    return endpointConfig["message"]

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
    #initInterruptSignal()
    initDatabase()
    service.run( CONFIG["HOST"], CONFIG["PORT"] )