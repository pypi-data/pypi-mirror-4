# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: GamaLocalDataAdj.py 103 2010-11-29 00:06:19Z tomaskubin $

"""
Class Module GamaLocalDataAdj, main class for handling GaMa Local adjustment result
"""

from gizela.data.GamaLocalData import GamaLocalData
from gizela.xml.GamaLocalAdjParser import GamaLocalAdjParser


class GamaLocalDataAdj(GamaLocalData):
    """
    Main class for handling and manipulating Gama-local geodetic network adjustemnt
    (gama-local-adjustment v 0.5)
    """
    
    def __init__(self): 
                super(GamaLocalDataAdj, self).__init__()
        
    def parse_file(self, file):
        """
        Reads and parses Gama-local XML file with adjustment results
        @param file: Gama-local XML file handler
        @type file: File handler
        """
        parser = GamaLocalAdjParser(self)
        parser.parse_file(file)


if __name__ == "__main__":

    try:
        file = open("../../example/xml-epoch/epoch0.adj.xml")
    except Exception, e:
        print e
        print "try to run make in ../../example/xml-epoch/ directory"
        import sys
        sys.exit()
        
    adj = GamaLocalDataAdj()
    adj.parse_file(file)
    print adj
    print adj.pointListAdjCovMat.covmat.make_gama_xml()

    # graph
    try:
        from gizela.pyplot.FigureLayoutErrEll import FigureLayoutErrEll
    except:
        print "import of gizela.pyplot.FigureLayoutBase failed"
    else:
        fig = FigureLayoutErrEll(errScale=2e3)
        adj.plot_point(fig)
        fig.show_()
