# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

import matplotlib
import sys

class BackendSingleton(object):
    """
    singleton class for setting a backend of
    matplotlib package
    """

    __instance = None

    def __new__(cls, backend="GTKAgg"):

        if BackendSingleton.__instance is None:
            BackendSingleton.__instance = object.__new__(cls)
            matplotlib.use(backend)
            BackendSingleton.__instance.backend = backend

            print >>sys.stderr, "Backend set: %s" % backend

        return BackendSingleton.__instance

    def __str__(self):
        return self.__instance.backend
