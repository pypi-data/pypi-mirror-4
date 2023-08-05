# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Michal Seidl <michal.seidl@fsv.cvut.cz>
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsCorrSphere.py 122 2011-03-01 10:28:01Z michal $
from gizela.data import ObsClusterList

"""
Class Module ObsCorrSphere

Basic concept of correction
- correction on the sphere
- radius of sphere is computed for central point on reference ellipsoid
- in correction formulas measured values are substituted with values computed
  from given coordinates in local system.
  This is not the case of direction correction which firstly try to get measured
  zenith angle and if no success the coordinates in local system are used.
- correction respects axis and bearing orientation

Basic concepts of computed observation
- computation on sphere and its radius is same as for correction
- used formulas are exact and based on vector algebra
- computed values respect axis and bearing orientation
"""

import math
import numpy as np

from gizela.util.Error import Error
from gizela.data.ObsZAngle import ObsZAngle

class ObsCorrSphereError(Error):
    """
    Exception for class ObsCorrSphere
    """
    pass

class ObsCorrSphere(object):
    """
    Class of observation correction from sphere to local cartesian system.
    Class is used through visitors of observation object.
    """

    debug = True # print detail information to stderr

    def __init__(self, ellipsoid, centralPointGeo, centralPointLoc, axesOri, bearingOri, pointList, obsClusterList):
        """
        
        @param ellipsoid: Type of ellipsoid used to compute local reference sphere
        @type ellipsoid: object Ellipsoid
        @param centralPointGeo: Central point of local system expressed in Geo coordinates
        @type centralPointGeo: object PointGeodetic
        @param centralPointLoc: Central point of local system expressed in Local cartesian coordinates
        @type centralPointLoc: object PointCart
        @param axesOri: Axes orientation from class AxesOrientation.
        @type axesOri: string
        @param bearingOri: Bearing orientation from class AxesOrientation.
        @type bearingOri: string
        @param pointList: List of points on local cartesian coordinates
        @type pointList: object PointList
        @param obsClusterList: Container of all measured values
        @type obsClusterList: object ObsClusterList        
        """

        self._ellipsoid = ellipsoid
        self._centralPointLoc = centralPointLoc
        self._centralPointGeo  = centralPointGeo
        self._axesOri = axesOri
        self._bearingOri = bearingOri
        self._pointList = pointList
        self._obsClusterList = obsClusterList
        
        self._R = self._ellipsoid.get_R(self._centralPointGeo.lat) + self._centralPointGeo.height - self._centralPointLoc.z

    def correct_direction(self, obs):
        """
        Computes and sets correction of direction in I{obs.corr}
        @param obs: Observation of direction
        @type obs: object ObsDirection
        @return: Correction
        @rtype: float
        """     
        
        # coordinates
        try:
            pointFrom = self._pointList.get_point(obs.fromid)
        except Error, e:
            raise ObsCorrSphereError, "Point id='%s' unknown" % pointFrom.id
        try:
            pointTo   = self._pointList.get_point(obs.toid)
        except Error, e:
            raise ObsCorrSphereError, "Point id='%s' unknown" % pointFrom.id

        # check coordinates x, y for None
        self._check_coord_xy(pointFrom)
        self._check_coord_xy(pointTo)

        if ObsCorrSphere.debug:
            import sys
            print >>sys.stderr, "Direction: from %s" % pointFrom.make_gama_xml()
            print >>sys.stderr, "           to   %s" % pointTo.make_gama_xml()
            #print >>sys.stderr, "Point from:\n", pointFrom
            #print >>sys.stderr, "Point to:\n", pointTo
        
        #Checks the values if None replace with 0
        fromdh = self._check_obs(obs,'fromdh')
        todh = self._check_obs(obs,'todh')

        # no correction at central point
        if pointFrom.id == self._centralPointLoc.id :
            corr = 0
            gamma = 0
            sigma = 0
            sigma0 = 0
        else :
            gamma = self._gamma_ij(self._centralPointLoc, pointFrom)
            sigma = self._bearing_lh_ij(pointFrom, pointTo)
            sigma0 = self._bearing_lh_ij(self._centralPointLoc,pointFrom)
            dist2D = ((pointTo.x-pointFrom.x)**2+(pointTo.y-pointFrom.y)**2)**0.5
            
            
            #Creates generator for measured zenith angles at given
            generatorObsZAngle = self._obsClusterList.iter_obs_from_to(ObsZAngle, obs.fromid, obs.toid, obs.fromdh, obs.todh)
            
            zAngle = None
            
            for zAngleObs in generatorObsZAngle:
                if zAngle == None:
                    zAngle = []
                zAngle.append(zAngleObs.val)
            
            #Computes correction with respect if zenith angle is known or not
            if zAngle == None:
                if pointTo.z is None:
                    toZ = self._centralPointLoc.z
                else:
                    toZ = pointTo.z

                if pointFrom.z is None:
                    fromZ = self._centralPointLoc.z
                else:
                    fromZ = pointFrom.z

                deltaZ = toZ+todh-(fromZ+fromdh)

                if deltaZ == 0:
                    corr = 0
                else:
                    corr = -1/(dist2D/deltaZ)*math.sin(sigma-sigma0)*gamma
            else:
                zAngle = np.average(zAngle)
                if zAngle == 0:
                    corr = 0
                else:
                    corr = -(1/math.tan(zAngle))*math.sin(sigma-sigma0)*gamma
            
            #Sets the correct sign by quadrant
            if self._bearingOri == 'right-handed':
                corr = -corr

        # Test print
        if ObsCorrSphere.debug:
            print >>sys.stderr, "  Angle gamma:", gamma*200/math.pi       
            print >>sys.stderr, "  Grid azimuth from i to j:", sigma*200/math.pi
            print >>sys.stderr, "  Grid azimuth from ref. point to i:", sigma0*200/math.pi
            print >>sys.stderr, "  Grid distance from i to j:", dist2D
            #print>>sys.stderr,  "Grid deltaZ from i to j:\n", deltaZ
            print >>sys.stderr, "  Correction: ", corr*200/math.pi

        return corr

    def correct_z_angle(self, obs):
        """
        Computes and sets correction of zenith angle in I{obs.corr}
        @param obs: Observation of zenith angle
        @type obs: object ObsZAngle
        @return: Correction
        @rtype: float
        """
        
        # coordinates
        pointFrom = self._pointList.get_point(obs.fromid)
        pointTo   = self._pointList.get_point(obs.toid)

        if ObsCorrSphere.debug:
            import sys
            print >>sys.stderr, "ZAngle: from %s" % pointFrom.make_gama_xml()
            print >>sys.stderr, "        to   %s" % pointTo.make_gama_xml()
        
        # check coordinates x, y for None
        self._check_coord_xy(pointFrom)
        self._check_coord_xy(pointTo)

        # No correction at central point
        if pointFrom.id == self._centralPointLoc.id :
            corr = 0
            gamma = 0
            sigma = 0
            sigma0 = 0
        else :
            gamma = self._gamma_ij(self._centralPointLoc, pointFrom)
            sigma = self._bearing_lh_ij(pointFrom, pointTo)
            sigma0 = self._bearing_lh_ij(self._centralPointLoc,pointFrom)
            corr = gamma*math.cos(sigma-sigma0)

        # Test print
        if ObsCorrSphere.debug:
            print >>sys.stderr, "  Angle gamma:", gamma*200/math.pi
            print >>sys.stderr, "  Grid azimuth from i to j:", sigma*200/math.pi
            print >>sys.stderr, "  Grid azimuth from ref. point to i:", sigma0*200/math.pi
            print >>sys.stderr, "  Correction: ", corr*200/math.pi

        return corr

    def correct_height_diff(self, obs):
        """
        Computes and sets correction of leveled height differences in I{obs.corr}
        @param obs: Observation of hight difference
        @type obs: object ObsHeightDiff
        @return: Correction
        @rtype: float
        """

        # coordinates
        pointFrom = self._pointList.get_point(obs.fromid)
        pointTo   = self._pointList.get_point(obs.toid)

        if ObsCorrSphere.debug:
            import sys
            print >>sys.stderr, "HDiff: from %s" % pointFrom.make_gama_xml()
            print >>sys.stderr, "       to   %s" % pointTo.make_gama_xml()
        
        # check coordinates x, y for None
        self._check_coord_xy(pointFrom)
        self._check_coord_xy(pointTo)

        qFrom = self._curvature_height_diff(pointFrom)
        qTo = self._curvature_height_diff(pointTo)
        
        corr = qTo-qFrom

        # Test print        
        if ObsCorrSphere.debug:
            print >>sys.stderr, "  Correction at pointFrom:", qFrom
            print >>sys.stderr, "  Correction at pointTo:", qTo
            print >>sys.stderr, "  Correction: ", corr
            #s1 = math.sqrt((pointFrom.x - self._centralPointLoc.x)**2 + (pointFrom.y - self._centralPointLoc.y)**2)
            #s2 = math.sqrt((self._centralPointLoc.x - pointTo.x)**2 + (self._centralPointLoc.y - pointTo.y)**2)
            #print >>sys.stderr, "  dist.: ", s1, s2
            #print >>sys.stderr, "  Corr s^2/2R: ", s1**2/2/6380000.0, s2**2/2/6380000.0
        
        return corr
    
    def compute_direction(self,obs):
        """
        Computes direction (in Geo system) from coordinates
        @param obs: Observation
        @type obs: object ObsDirection
        @return: Direction
        @rtype: float        
        """

        #Checks the values if None replace with 0
        fromdh = self._check_obs(obs,'fromdh')
        todh = self._check_obs(obs,'todh')

        # coordinates
        pointFrom = self._pointList.get_point(obs.fromid)
        pointTo   = self._pointList.get_point(obs.toid)
        
        #Start of constructing Numpy variables
        pointI = np.array([pointFrom.x, pointFrom.y, pointFrom.z+fromdh])
        pointJ = np.array([pointTo.x, pointTo.y, pointTo.z+todh])
        
        R = self._ellipsoid.get_R(self._centralPointGeo.lat)
        pointR = np.array([self._centralPointLoc.x, self._centralPointLoc.y, self._centralPointLoc.z])
        
        vectorR = np.array([self._centralPointLoc.x, self._centralPointLoc.y, self._centralPointLoc.z+R])
        ez = np.array([0,0,1])
        #End of constructing Numpy variables
        
        n = vectorR+(pointI-pointR)
        n = n/np.linalg.norm(n)
        
        vectorRI = pointI-pointR
        vectorRI = vectorRI/np.linalg.norm(vectorRI)

        vectorIJ = pointJ-pointI
        vectorIJ = vectorIJ/np.linalg.norm(vectorIJ)
        
        # Plane of sight in local system
        nLocalRI = np.cross(ez,vectorRI)
        nLocalRI = nLocalRI/np.linalg.norm(nLocalRI)        
        
        #Plane of sight in geodetic system
        nGeoIJ = np.cross(n,vectorIJ)
        nGeoIJ = nGeoIJ/np.linalg.norm(nGeoIJ)

        #dirGeoIJ = acos(dot(nGeoX,nGeoIJ)/(norm(nGeoX)*norm(nGeoIJ)))
        cVectorGeo = np.cross(nLocalRI,nGeoIJ)
        dirGeoIJ = math.atan2(np.linalg.norm(np.cross(nLocalRI,nGeoIJ)),np.dot(nLocalRI,nGeoIJ))
        if (cVectorGeo[2] < 0):
            dirGeoIJ = 2*math.pi-dirGeoIJ        
            
        # Test print        
#        print "Computed geodetic direction"
#        print "Point from:\n", pointFrom
#        print "Point to:\n", pointTo
#        print "vectorR:\n", vectorR
#        print "n:\n", n
#        print "vectorIJ:\n", vectorIJ
#        print "nLocalRI:\n", nLocalRI
#        print "nGeoIJ:\n", nGeoIJ
#        print "cVectorGeo:\n", cVectorGeo
#        print "Direction: ", dirGeoIJ*200/math.pi

        if (self._axesOri == 'en' or self._axesOri == 'nw' or self._axesOri == 'ws' or self._axesOri == 'se' ):
            if self._bearingOri == 'right-handed':
                dirGeoIJ = 2*math.pi-dirGeoIJ
        else:
            if self._bearingOri == 'left-handed':
                dirGeoIJ = 2*math.pi-dirGeoIJ
                
        return dirGeoIJ

    def compute_distance(self,obs):
        return 0

    def compute_height_diff(self,obs):
        return 0

    def compute_s_distance(self,obs):
        """
        Computes slope distance (in Geo system) from coordinates
        @param obs: Observation
        @type obs: object ObsDirection
        @return: Slope distance
        @rtype: float        
        """
        
        #Checks the values if None replace with 0
        fromdh = self._check_obs(obs,'fromdh')
        todh = self._check_obs(obs,'todh')

        # coordinates
        pointFrom = self._pointList.get_point(obs.fromid)
        pointTo   = self._pointList.get_point(obs.toid)
        
        s_distance = ((pointTo.x-pointFrom.x)**2+(pointTo.y-pointFrom.y)**2+(pointTo.z+todh-pointTo.z-fromdh)**2)**0.5
        return s_distance        
    
    def compute_vector(self,obs):
        return 0
    
    def compute_z_angle(self,obs):
        return 0
    
    def _check_obs(self,obs,what):
        """
        Checks "from" and "to" dh.
        @param obs: Observation
        @type obs: object One of observation objects
        @param what: What to check
        @type what: string
        """
        
        #Checks the fromdh and todh values
        if (what == 'fromdh'):
            if obs.fromdh == None:
                check = 0
            else:
                check = obs.fromdh
                
        if (what == 'todh'):                        
            if obs.todh == None:
                check = 0
            else:
                check = obs.todh
        
        return check


    def _check_coord_xy(self, point):
        if point.x is None:
            raise ObsCorrSphereError, "Point id='%s': no x coordinate"\
                                        % point.id
        if point.y is None:
            raise ObsCorrSphereError, "Point id='%s': no y coordinate"\
                                        % point.id

        
#    def _gamma_ij(self,pointFrom,pointTo):
#        """
#        Computes central angle between two points measured at center of reference sphere
#        @param pointFrom: Point of observation
#        @type pointFrom: object PointCart
#        @param pointTo: Target point
#        @type pointTo: object PointCart
#        @return: Central angle between two points
#        @rtype: float
#        """        
#        
#        # Radius of reference sphere
#        R = self._ellipsoid.get_R(self._centralPointGeo.lat)
#        
#        dist2D12 = ((pointFrom.x-self._centralPointLoc.x)**2+(pointFrom.y-self._centralPointLoc.y)**2)**0.5
#        gamma12 = math.atan(dist2D12/(R+pointFrom.z))
#        q12 = (R+self._centralPointLoc.z)*(1/math.cos(gamma12)-1)
#        H2 = self._centralPointLoc.z+(pointFrom.z-self._centralPointLoc.z)/math.cos(gamma12)+q12
#        
#        dist2D13 = ((pointTo.x-self._centralPointLoc.x)**2+(pointTo.y-self._centralPointLoc.y)**2)**0.5
#        gamma13 = math.atan(dist2D13/(R+pointTo.z))
#        q13 = (R+self._centralPointLoc.z)*(1/math.cos(gamma13)-1)
#        H3 = self._centralPointLoc.z+(pointTo.z-self._centralPointLoc.z)/math.cos(gamma13)+q13        
#        
#        dist3D23 = ((pointTo.x-pointFrom.x)**2+(pointTo.y-pointFrom.y)**2+(pointTo.z-pointFrom.z)**2)**0.5
#        gamma23 = math.acos(((R+H2)**2+(R+H3)**2-dist3D23**2)/(2*(R+H2)*(R+H3)))
#        
#        return gamma23
    
    def _gamma_ij(self, pointFrom, pointTo):
        """
        Computes central angle between two points measured at center of reference sphere
        @param pointFrom: Point of observation
        @type pointFrom: object PointCart
        @param pointTo: Target point
        @type pointTo: object PointCart
        @return: Central angle between two points
        @rtype: float
        """        

        fromZ = pointFrom.z
        toZ = pointTo.z

        if not pointFrom.is_set_z():
            fromZ = self._centralPointLoc.z

        if not pointTo.is_set_z():
            toZ = self._centralPointLoc.z

        #if pointFrom.z is None and pointTo.z is None:
        #    fromZ = self._centralPointLoc.z
        #    toZ = self._centralPointLoc.z
        #elif pointTo.z is None:
        #    fromZ = pointFrom.z
        #    toZ = pointFrom.z
        #elif pointFrom.z is None:
        #    fromZ = pointTo.z
        #    toZ = pointTo.z
        #else:
        #    fromZ = pointFrom.z
        #    toZ = pointTo.z
                
        dist2D12 = ((pointFrom.x-self._centralPointLoc.x)**2+(pointFrom.y-self._centralPointLoc.y)**2)**0.5
        gamma12 = math.atan(dist2D12/(self._R+fromZ))
        q12 = self._R/math.cos(gamma12)-self._R
        
        #Height above reference sphere
        h2 = fromZ/math.cos(gamma12)+q12
        
        dist2D13 = ((pointTo.x-self._centralPointLoc.x)**2+(pointTo.y-self._centralPointLoc.y)**2)**0.5
        gamma13 = math.atan(dist2D13/(self._R+toZ))
        q13 = self._R/math.cos(gamma13)-self._R
        
        h3 = toZ/math.cos(gamma13)+q13        
        
        dist3D23 = ((pointTo.x-pointFrom.x)**2+(pointTo.y-pointFrom.y)**2+(toZ-fromZ)**2)**0.5
        arg = ((self._R+h2)**2+(self._R+h3)**2-dist3D23**2)/(2*(self._R+h2)*(self._R+h3))
        if arg >= 1.0:
            import sys
            print >>sys.stderr, "warning: cos(gamma23) > 1.0:", arg-1.0
            return 0.0

        gamma23 = math.acos(((self._R+h2)**2+(self._R+h3)**2-dist3D23**2)/(2*(self._R+h2)*(self._R+h3)))
        
        return gamma23    
    
    def _bearing_lh_ij (self, pointFrom, pointTo):
        """
        Computes azimuth measured from axis I{X} in left-handed (anticlockwise)S direction
        @param pointFrom: Point of observation
        @type pointFrom: object PointCart
        @param pointTo: Target point
        @type pointTo: object PointCart
        @return: Azimuth angle
        @rtype: float
        """
        
        if (self._axesOri == 'en' or self._axesOri == 'nw' or self._axesOri == 'ws' or self._axesOri == 'se' ):
            sigma = math.atan2((pointTo.y - pointFrom.y), (pointTo.x - pointFrom.x))
        else :
            sigma = math.atan2(-(pointTo.y - pointFrom.y), (pointTo.x - pointFrom.x))
        if sigma < 0 : sigma += 2*math.pi
        return sigma
    
#    def _curvature_height_diff (self, point):
#        """
#        Computes differences between height and I{Z} coordinates caused by curvature
#        @param point: Point
#        @type point: object PointCart
#        @return: Height difference M{q = H - Z}
#        @rtype: float
#        """
#        R = self._ellipsoid.get_R(self._centralPointGeo.lat)
#        dist2D12 = ((point.x-self._centralPointLoc.x)**2+(point.y-self._centralPointLoc.y)**2)**0.5
#        gamma12 = math.atan(dist2D12/(R+point.z))
#        q12 = (R+self._centralPointLoc.z)*(1/math.cos(gamma12)-1)
#        q122 = (point.z-self._centralPointLoc.z)-(point.z-self._centralPointLoc.z)/math.cos(gamma12)
#        
#        print "Point_p", point
#        print "gamma12_p\n", gamma12
#        print "q12_p\n", q12
#        print "q122_p\n", q122, "\n"
#        
#        return (q12-q122)
    
    def _curvature_height_diff (self, point):
        """
        Computes differences between height above reference sphere I{H} and I{Z} coordinates
        in local system caused by sphere curvature
        @param point: Point
        @type point: object PointCart
        @return: Height difference M{corr = Z - H}
        @rtype: float
        """

        gamma12 = self._gamma_ij(self._centralPointLoc, point)
        q1 = self._R/math.cos(gamma12)-self._R
        q2 = point.z/math.cos(gamma12)-point.z
        
#        print "Point", point
#        print "gamma12:\n", gamma12
#        print "Curvature q1:\n", q1
#        print "Correction to Z q2:\n", q2, "\n"
        
        return (-q1-q2)
    
    def _z_angle_ij (self, pointFrom, pointTo, obs):
        """
        Cumputes Zenith angle meassured from axis {Z} in local system
        @param pointFrom: Point of observation
        @type pointFrom: object PointCart
        @param pointTo: Target point
        @type pointTo: object PointCart
        @return: Zenith angle
        @rtype: float
        """
        
        #Checks the values if None replace with 0
        fromdh = self._check_obs(obs,'fromdh')
        todh = self._check_obs(obs,'todh')
            
        dist2D = ((pointTo.x-pointFrom.x)**2+(pointTo.y-pointFrom.y)**2)**0.5
        deltaZ = pointTo.z+todh-(pointFrom.z+fromdh)
        
        if deltaZ == 0 :
            z_angle = math.pi/2
        else :
            z_angle = math.atan(dist2D/deltaZ)
        return z_angle
        
if __name__ == "__main__":
    """
    Main module doc
    """
    print "This is ObsCorrSphere class instance"
    
#    corr = ObsCorrSphere(ellipsoid, centralPointGeo, centralPointLoc, pointList)


    print "Making correction"
    from gizela.util.Ellipsoid     import Ellipsoid
    from gizela.data.PointGeodetic import PointGeodetic
    from gizela.data.PointCart     import PointCart
    from gizela.data.PointList     import PointList

    centralPointLoc = PointCart("99", 0, 0, 0)
    
    pointList = PointList(textTable=centralPointLoc.textTable)
    pointList.add_point(centralPointLoc)
    pointList.add_point(PointCart("999", 1000, 000, 0))
    pointList.add_point(PointCart("1", 2000, 0, 0))
    pointList.add_point(PointCart("2", 2000, 1000, 0))
    pointList.add_point(PointCart("3", 1000, 1000, 0))
    pointList.add_point(PointCart("4", 0, 1000, 0))
    pointList.add_point(PointCart("5", 0, 0, 0))
    pointList.add_point(PointCart("6", 0, -1000, 0))
    pointList.add_point(PointCart("7", 1000, -1000, 0))
    pointList.add_point(PointCart("8", 2000, -1000, 0))
    
    pointList.add_point(PointCart("11", 2000, 0, 1000))
    pointList.add_point(PointCart("12", 2000, 1000, 1000))
    pointList.add_point(PointCart("13", 1000, 1000, 1000))
    pointList.add_point(PointCart("14", 0, 1000, 1000))
    pointList.add_point(PointCart("15", 0, 0, 1000))
    pointList.add_point(PointCart("16", 0, -1000, 1000))
    pointList.add_point(PointCart("17", 1000, -1000, 1000))
    pointList.add_point(PointCart("18", 2000, -1000, 1000))
    
    pointList.add_point(PointCart("21", 2000, 0, -1000))
    pointList.add_point(PointCart("22", 2000, 1000, -1000))
    pointList.add_point(PointCart("23", 1000, 1000, -1000))
    pointList.add_point(PointCart("24", 0, 1000, -1000))
    pointList.add_point(PointCart("25", 0, 0, -1000))
    pointList.add_point(PointCart("26", 0, -1000, -1000))
    pointList.add_point(PointCart("27", 1000, -1000, -1000))
    pointList.add_point(PointCart("28", 2000, -1000, -1000))    
        
    pointList.add_point(PointCart("91", 2000, -1000, 1000))
    print "Point List table:"
    print pointList
    
    roDeg = 180/math.pi
    roGon = 200/math.pi
    centralPointGeo = PointGeodetic(99,50/roDeg,14/roDeg,0)

    from gizela.data.ObsClusterList import ObsClusterList    
    from gizela.data.ObsCluster  import ObsCluster    
    from gizela.data.ObsDistance  import ObsDistance
    from gizela.data.ObsDirection import ObsDirection
    from gizela.data.ObsZAngle    import ObsZAngle
    from gizela.data.ObsSDistance import ObsSDistance
    from gizela.data.ObsHeightDiff import ObsHeightDiff

#    dist  = ObsDistance("2", 100.00)
#    dir   = ObsDirection("2", 0)
#    zen   = ObsZAngle("3", math.pi/2)
#    sdist = ObsSDistance("2", 100.00)
#    heightdiff = ObsHeightDiff("1","2",100.00)
    obsClusterList = ObsClusterList()

    obsCluster = ObsCluster("999")
#    obsCluster.append_obs(ObsDistance("91", 100))

#    obsCluster.append_obs(ObsDirection("1", 0))
#    obsCluster.append_obs(ObsDirection("2", 0))
#    obsCluster.append_obs(ObsDirection("3", 0))
#    obsCluster.append_obs(ObsDirection("4", 0))
#    obsCluster.append_obs(ObsDirection("5", 0))
#    obsCluster.append_obs(ObsDirection("6", 0))
#    obsCluster.append_obs(ObsDirection("7", 0))
#    obsCluster.append_obs(ObsDirection("8", 0))
    
#    obsCluster.append_obs(ObsZAngle("999", math.pi/2))    
    
#    obsCluster.append_obs(ObsZAngle("1", -1*math.pi/4))
#    obsCluster.append_obs(ObsZAngle("2", 1*math.pi/4))
#    obsCluster.append_obs(ObsZAngle("3", 0))
#    obsCluster.append_obs(ObsZAngle("14", 0))
#    obsCluster.append_obs(ObsZAngle("15", 0))
#    obsCluster.append_obs(ObsZAngle("16", 0))
#    obsCluster.append_obs(ObsZAngle("17", 0))
#    obsCluster.append_obs(ObsZAngle("18", 0))
    
#    obsCluster.append_obs(ObsSDistance("91", 100))    
    
    obsCluster.append_obs(ObsHeightDiff("999","11", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","12", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","13", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","14", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","15", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","16", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","17", 0, 1))
    obsCluster.append_obs(ObsHeightDiff("999","18", 0, 1))

    obsClusterList.append_cluster(obsCluster)

    #    corr = ObsCorrSphere(ellipsoid, centralPointGeo, centralPointLoc, pointList)    
    corr = ObsCorrSphere(Ellipsoid(), centralPointGeo, centralPointLoc, 'sw', 'left-handed', pointList, obsClusterList)

    obsClusterList.compute_corr(corr)
    #obsCluster.compute_obs(corr)

    
    print "Observation Cluster List table before correction"
    print obsClusterList
#    print "Observation Cluster GaMa XML before correction"
    print obsClusterList.make_gama_xml()
#    
#
    print "Observation Cluster List table after correction"
    print obsClusterList
#    print "Observation Cluster GaMa XML after correction"
    print obsClusterList.make_gama_xml(corrected=True)    
    
#    print    "Example code see in file gizela.data.ObsCluster \
#    or gizela.data.ObsClusterHeightDiff"
