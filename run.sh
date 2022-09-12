#!/bin/sh

printUsage()
{
    echo "Usage: "
    echo -e "\t- \"service <configPath>\" for starting the main service"
    echo -e "\t- \"dbhelper <databasePath> [<schemaFile>]\" for starting the database helper"
    echo -e "\t- \"webhook-testservice\" for starting the webhook testservice"
}

if [ "$#" -lt 1 ]; then
    echo "No arguments given."
    printUsage
    exit 1
fi

if [ "$1" = "service" ]; then
    python3 tinyhttpcallbackservice.py $2
elif [ "$1" = "db-helper" ]; then
    python3 tools/database_helper.py $2 $3
elif [ "$1" = "webhook-testservice" ]; then
    python3 tools/webhook_testservice.py
else
    printUsage
fi