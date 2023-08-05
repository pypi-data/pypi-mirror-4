# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsCluster.py 114 2010-12-14 02:30:56Z tomaskubin $


from gizela.data.ObsBase import ObsBase
from gizela.data.ObsClusterBase import ObsClusterBase
from obs_table import obs_cluster_table


class ObsCluster(ObsClusterBase):
    """iterable class for cluster of observations
    """

    def __init__(self, fromid=None, fromdh = None, textTable=None):
        """cluster of observations:
            fromid  id of station
            fromdh    height of instrument in meters
        """
        if textTable == None:
            textTable = obs_cluster_table()

        super(ObsCluster, self).__init__(fromid=fromid, fromdh=fromdh,
                                         textTable=textTable)

    def make_gama_xml(self, corrected=False):
        if len(self) == 0:
            return ""

        str1 = ["<obs"]
        if self.fromid != None: str1.append('from="%s"' % self.fromid)
        if self.fromdh != None: str1.append('from_dh="%.5f"' % self.fromdh)
        str1.append(">")
        str = [" ".join(str1)]
        str.extend(["\t" + obs.make_gama_xml(corrected) for obs in self])
        if self.is_cov_mat():
            str.append(self.make_gama_xml_covmat())
        str.append("</obs>")

        return "\n".join(str)


    def sdist_to_dist(self, holdObs=True):
        """
        transform observations to xy dimension
        without covariance matrix
        s-distance -> distance
    
        s-distance is deleted
        """

        from gizela.data.ObsZAngle import ObsZAngle
        from gizela.data.ObsSDistance import ObsSDistance

        newCl = ObsCluster(fromid=self.fromid, fromdh=self.fromdh,
                           textTable=self.textTable)

        l = []

        for obs in self:
            if isinstance(obs, ObsSDistance):
                zangle = [o for o in self.iter_obs_from_to(ObsZAngle,
                                                           obs.fromid,
                                                           obs.toid,
                                                           obs.fromdh,
                                                           obs.todh)]
                if len(zangle) >= 1:
                    dist = obs.get_distance(zangle[0])
                    self.append_obs(dist)
            #elif isinstance(obs, ObsZAngle):
                #pass
            else:
                l.append(obs)


        # new initialization of self
        self.__init__(fromid=self.fromid, fromdh=self.fromdh,
                      textTable=self.textTable)
        for obs in l:
            self.append_obs(obs)


    def dist_scale(self, coordSystem):
        """
        scales horizontal distances
        """
        from gizela.data.ObsDistance import ObsDistance

        for dist in self.iter_obs(ObsDistance):
            dist.scale(coordSystem.distScale)




if __name__ == "__main__":

    from gizela.data.ObsDistance  import ObsDistance
    from gizela.data.ObsDirection import ObsDirection
    from gizela.data.ObsZAngle    import ObsZAngle
    from gizela.data.ObsSDistance import ObsSDistance

    dist  = ObsDistance("AB", 100.01)
    dir   = ObsDirection("AB", 100.01)
    zen   = ObsZAngle("AB", 100.01)
    sdist = ObsSDistance("AB", 100.01)

    cl = ObsCluster("CD")
    cl.append_obs(dist)
    cl.append_obs(dir)
    cl.append_obs(zen)
    cl.append_obs(sdist)

    print cl
    print cl.make_gama_xml()

    # covariance matrix
    from gizela.data.CovMat import CovMat
    cl.covmat = CovMat(4,0)
    cl.covmat.var = (0.01, 0.02, 0.03, 0.04)

    # iterator
    print "\n".join(["from=%s to=%s" % (obs.fromid, obs.toid) for obs in cl])

    # type of observations
    for obs in cl:
        if isinstance(obs, ObsDirection):
            print obs, "is a direction"
        if isinstance(obs, ObsDistance):
            print obs, "is a horizontal distance"
        if isinstance(obs, ObsZAngle):
            print obs, "is zenit angle"
        if isinstance(obs, ObsSDistance):
            print obs, "is slope distance"
    
    print "Making correction"
    from gizela.corr.ObsCorrSphere import ObsCorrSphere
    from gizela.util.Ellipsoid     import Ellipsoid
    from gizela.data.PointGeodetic import PointGeodetic
    from gizela.data.PointCart     import PointCart
    from gizela.data.PointList     import PointList
    from gizela.data.ObsClusterList import ObsClusterList

    pA = PointCart("AB", x=0, y=0, z=0)
    pl = PointList(textTable=pA.textTable)
    pl.add_point(pA)
    pl.add_point(PointCart("CD", x=1, y=1, z=1))
    print pl
    ocl = ObsClusterList()
    ocl.append_cluster(cl)

    corr = ObsCorrSphere(ellipsoid=Ellipsoid(), 
            centralPointGeo=PointGeodetic(id="c", lat=0, lon=0, height=0),
            centralPointLoc=PointCart(id="c", x=0, y=0, z=0),
            axesOri="ne",
            bearingOri="righ-handed",
            pointList=pl,
            obsClusterList=ocl)
    cl.compute_corr(corr)
    print cl
    print cl.make_gama_xml(corrected=True)

    print "Delete zenith angles"
    cl.delete_observation(ObsZAngle)
    print cl.make_gama_xml(corrected=True)
