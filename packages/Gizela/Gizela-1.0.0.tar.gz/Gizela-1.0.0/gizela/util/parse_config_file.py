# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

def parse_config_file(name):
    """
    parses configuration file
    every value try to convert to float

    name: string or tuple of stirngs: name(s) of configuration file
    return: dict: dictionary of configuration file sections
    """

    import ConfigParser, os, sys
    configParser = ConfigParser.SafeConfigParser()
    configParser.optionxform = str # to make options case sensitive

    readed = configParser.read(name)
    print >>sys.stderr, "Fonfiguration file(s) readed: %s" % ", ".join(readed)
    
    config = {}

    for sec in configParser.sections():
        config[sec] = {}
        for p,v in configParser.items(sec):
            try:
                v=float(v)
            except:
                pass
            config[sec][p] = v

    return config
