import toml
import os
import sys

def loadConfig( configPath ):
    config = {}

    try:
        config = toml.load( configPath, _dict = dict )

        print( "Config successfuly loaded from '" + os.path.abspath( configPath ) + "'." )

        return config
    except FileNotFoundError:
        sys.exit( "Could not find config file '" + os.path.abspath( configPath ) + "'. Exiting." )