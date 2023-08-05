# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

"""
module with functions for 
gama-data-obs.py and gama-data-adj.py scripts
"""

import sys

def read_configuration_file(configFile, localSystem2D, localSystem3D):
    """
    reads configuration file

    returns: configuration dictionary
             localSystem
    """

    configDict = []
    localSystem = None

    if configFile is not None:
        from gizela.util.parse_config_file import parse_config_file
        try:
            configDict = parse_config_file(configFile)
        except Exception, e:
            print >>sys.stderr, \
                "Parsing of configuration file '%s' failed." % configFile
            print >>sys.stderr, e
            sys.exit(1)
    
        if localSystem2D:
            if "localSystem2D" not in configDict:
                print >>sys.stderr, \
                    "No localSystem2D section in config file %s" % configFile
                sys.exit(1)
            else:
                from gizela.util.CoordSystemLocal2D import CoordSystemLocal2D
                localSystem = CoordSystemLocal2D()
                localSystem.parse_config_dict(configDict)
    
        if localSystem3D:
            if "localSystem3D" not in configDict:
                print >>sys.stderr, \
                    "No localSystem3D section in config file %s" % configFile
                sys.exit(1)
            else:
                from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
                localSystem = CoordSystemLocal3D()
                localSystem.parse_config_dict(configDict)

    return configDict, localSystem
