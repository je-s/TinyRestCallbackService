import sys

def printUsage():
    print( "Usage: " )
    print( "\t- \"service <configPath>\" for starting the main service" )
    print( "\t- \"dbhelper <databasePath>\" for starting the database helper" )
    print( "\t- \"webhook-testservice\" for starting the webhook testservice" )

if __name__ == '__main__':
    if sys.argv.__len__() < 2:
        print( "No arguments given." )
        printUsage()
        sys.exit()

    if sys.argv[1] == "service":
        import src.tinyhttpcallbackservice
    elif sys.argv[1] == "dbhelper":
        import src.tools.database_helper
    elif sys.argv[1] == "webhook-testservice":
        import src.tools.webhook_testservice
    else:
        printUsage()