#!/bin/bash

printUsage()
{
    echo "Usage: "
    echo -e "\t- \"service <configPath>\" for starting the main service"
    echo -e "\t- \"add-endpoint <databasePath> [<schemaFile>]\" for adding an ednpoint config"
    echo -e "\t- \"webhook-testservice <port>\" for starting the webhook testservice"
}

if [ "$#" -lt 1 ]; then
    echo "No arguments given."
    printUsage
    exit 1
fi

if [ "$1" = "service" ]; then
    python3 tinyrestcallbackservice.py $2
elif [ "$1" = "add-endpoint" ]; then
    python3 tools/add_endpoint_config.py $2 $3
elif [ "$1" = "webhook-testservice" ]; then
    python3 tools/webhook_testservice.py $2
else
    printUsage
fi