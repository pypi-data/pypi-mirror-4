# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: GamaLocalDataObs.py 103 2010-11-29 00:06:19Z tomaskubin $

"""
Class Module GamaLocalDataObs, main class for handling GaMa Local obsevation
"""

from gizela.data.GamaLocalData import GamaLocalData
from gizela.xml.GamaLocalObsParser import GamaLocalObsParser
from gizela.data.point_text_table import gama_coor_table
from gizela.corr.ObsCorrSphere import ObsCorrSphere
from gizela.util.Unit import Unit
from gizela.util.Error import Error
from gizela.data.GamaCoordStatus import GamaCoordStatus


class GamaLocalDataObsError(Error): pass


class GamaLocalDataObs(GamaLocalData):
    """
    Main class for gama-local input data
    geodetic network observation
    """
    
    def __init__(self):
        super(GamaLocalDataObs, self).__init__()
        self.pointListAdj.textTable = gama_coor_table()
        
    
    def parse_file(self, file):
        """
        Reads and parses Gama-local XML file with observation
        @param file: Gama-local XML file handler
        @type file: file object
        """
        parser = GamaLocalObsParser(self)
        parser.parse_file(file)
        
    



if __name__ == "__main__":

    try:
        file = open("../../example/xml1/example-all_obs.gkfc")
    except Exception, e:
        print e
        import sys
        sys.exit()

    adj = GamaLocalDataObs()
    adj.parse_file(file)
    print adj

    print adj.make_gama_xml()

    # corrections
    from math import pi
    adj.set_local_system(ellipsoidCode="wgs84", 
                         lat=50.09115331111*pi/180, 
                         lon=14.401833202777*pi/180, 
                         height=302.495,
                         axesOri="ne")
    try:
        adj.compute_corr()
    except Exception, e:
        print "Computation of correction failed"
        print e

    adj.description += " - korekce"
    
    print adj.make_gama_xml(corrected=True)
    
    # transformation of gps vectors
    adj.tran_vec_local_ne()
    print adj.make_gama_xml()

    # graph
    try:
        from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
    except:
        print "import gizela.pyplot.FigureLayoutBase failed"
    else:
        fig = FigureLayoutBase()
        adj.plot_point(fig)
        fig.set_free_space()
        fig.show_()
