import toml
import os
import sys

# Loads a config in TOML format and returns its' contents as a dict
def loadConfig( configPath ):
    config = {}

    try:
        config = toml.load( configPath, _dict = dict )

        print( "Config successfully loaded from \"" + os.path.abspath( configPath ) + "\"." )

        return config
    except FileNotFoundError:
        sys.exit( "Could not find config file \"" + os.path.abspath( configPath ) + "\". Exiting." )