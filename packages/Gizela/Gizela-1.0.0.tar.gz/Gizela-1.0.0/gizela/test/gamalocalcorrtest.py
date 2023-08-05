# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Michal Seidl <michal.seidl@fsv.cvut.cz>
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: Ellipsoid.py 67 2010-08-03 16:10:35Z michal $

"""
Module of Gama-local Correction Tests
"""

from gizela.data.GamaLocalDataObs import GamaLocalDataObs


if __name__ == "__main__":
    """
    Main module doc
    """
    
    dataObs = GamaLocalDataObs()
    #file = open("../../example/xml-corr/xml-corr.xml")
    file = open("../../example/xml-corr/xml-corr2.xml")
    dataObs.parse_file(file)
#    print dataObs

    from gizela.data.Network import Network
    from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
    net = Network(coordSystemLocal=CoordSystemLocal3D(), data=dataObs)

    #import sys
    #print >>sys.stderr, net.make_gama_xml()

    net.compute_corr()

    try:
        file = open("../../example/xml-corr/xml-corr2.corrected.xml","wt")
    except Exception, e:
        import sys
        print >>sys.stderr, "Unable to open file"
        print >>sys.stderr, e
        sys.exit(1)

    print >>file, net.make_gama_xml(corrected=True)
