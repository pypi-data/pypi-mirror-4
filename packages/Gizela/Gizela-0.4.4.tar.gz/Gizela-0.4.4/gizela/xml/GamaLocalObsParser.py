# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
#$Id: GamaLocalObsParser.py 103 2010-11-29 00:06:19Z tomaskubin $


from gizela.util.Error           import Error

# parser
import xml.parsers.expat

# points
from gizela.data.PointLocalGama  import PointLocalGama
from gizela.data.PointCartCovMat import PointCartCovMat
#from gizela.data.PointListCovMat import PointListCovMat
#from gizela.data.PointList       import PointList
#from gizela.data.CovMat          import CovMat
from gizela.data.GamaCoordStatus import GamaCoordStatus
from gizela.data.GamaCoordStatus import gama_coord_status_attr_fix
from gizela.data.GamaCoordStatus import gama_coord_status_attr_adj

# measurements
from gizela.data.ObsCluster      import ObsCluster
from gizela.data.ObsClusterHeightDiff import ObsClusterHeightDiff
from gizela.data.ObsDirection     import ObsDirection
from gizela.data.ObsDistance      import ObsDistance
from gizela.data.ObsSDistance     import ObsSDistance
from gizela.data.ObsZAngle        import ObsZAngle
from gizela.data.ObsHeightDiff    import ObsHeightDiff
from gizela.data.ObsClusterVector import ObsClusterVector
from gizela.data.ObsVector        import ObsVector
from gizela.data.ObsClusterCoor   import ObsClusterCoor 

# covariance matrix
from gizela.data.CovMat import CovMat

# units
from gizela.util.Unit import Unit


class GamaLocalObsParserError(Error): pass


class GamaLocalObsParser(object):
    """
        Expat parser for <gama-local> document - measurements
        Units required: meter, gon (degrees are not allowed)
        Warning: covariance matrix for observations with unit gon is not
                 correctly readed. Only unit meter is readed correctly.
        """

    __slots__ = ["data", "_parser", "_characterData", "_tagName",
                 "_tagLast", "_tagLLast", "_coor", "_cluster",
                 "_pointListAdj", "_pointListFix", "_clusterList",
                 "_description", "_root"]

    def __init__(self, data):
        '''
        data : instance for data storage
        '''

        # data
        self.data=data
        
        # create expat parser
        self._parser = xml.parsers.expat.ParserCreate()
        
        # handles
        self._parser.StartElementHandler = self._handle_start_element
        self._parser.EndElementHandler = self._handle_end_element
        self._parser.CharacterDataHandler = self._handle_char_data
        # internal data
        self._root=False # is root element ok?
        self._characterData=""
        self._tagName=""
        self._tagLast=""
        self._tagLLast=""
        self._coor=False # indicates tag <coordinates>
        self._cluster=None # actual cluster
        
        # setting of lists in data instance
        self._pointListAdj = self.data.pointListAdj
        self._pointListFix = self.data.pointListFix
        self._clusterList = self.data.obsClusterList

    def parse_file(self, file):
        '''parses file - file object'''
        self._parser.ParseFile(file)
    
    def parse_string(self, str):
        '''parses string'''
        self._parser.Parse(str)

    def _handle_start_element(self, name, attrs):
        '''start element handler for method all'''

        if not self._root:
            if name == "gama-local":
                self._root = True
            else:
                raise GamaLocalObsParserError, "<gama-local> root element not found"

        self._tagLLast=self._tagLast
        self._tagLast=self._tagName
        self._tagName=name

        if name=="network" or\
           name=="parameters" or\
           name=="points-observations":
            
            # save attributes
            if attrs:
                for aname, val in attrs.items():
                    #import sys 
                    #print >>sys.stderr, "Parameter: %s" % aname

                    #parameters
                    if aname=="update-constrained-coordinates":
                        self.data.param[aname] = val

                    elif aname=="epoch":
                        self.data.param[aname] = float(val)

                    elif aname=="tol-abs":
                        self.data.param[aname] = float(val) / Unit.tolabs 

                    # standard deviation
                    elif aname=="direction-stdev" or\
                         aname=="angle-stdev" or\
                         aname=="zenith-angle-stdev":
                        self.data.param[aname] = \
                                float(val) / Unit.angleStdev

                    elif aname=="distance-stdev":
                        val = [float(v) / Unit.distStdev \
                               for v in val.split()]
                        self.data.param[aname] = val

                    elif aname=="sigma-apr":
                        self.data.stdev["apriori"] = float(val)
                        #self.data.stdev.apriori = float(val)

                    elif aname=="sigma-act":
                        self.data.stdev["used"] = val.strip()
                        #if val.strip() == "apriori":
                        #    self.data.stdev.set_use_apriori()
                        #elif val.strip() == "aposteriori":
                        #    self.data.stdev.set_use_aposteriori()
                        #else:
                        #    raise GamaLocalObsParserError, \
                        #        "unknown sigma-act tag: %s" %val

                    elif aname=="conf-pr":
                        self.data.stdev["probability"] = float(val)
                        #self.data.stdev.set_conf_prob(float(val))

                    elif aname=="axes-xy":
                        self.data.param[aname] = val
                        #self.data.coordSystemLocal.axesOri = val

                    elif aname=="angles":
                        self.data.param[aname] = val
                        #self.data.coordSystemLocal.bearingOri = val

                    else:
                        import sys
                        sys.stderr.write("unhandled parameter %s = \"%s\"\n" %\
                                         (aname, val))

        # points and coordinates
        elif name=="point":
            
            x, y, z, adj, fix = None, None, None, None, None

            if "x" in attrs: x = float(attrs["x"])
            if "y" in attrs: y = float(attrs["y"])
            if "z" in attrs: z = float(attrs["z"])

            if self._coor: # inside tag <coordinates>
                point = PointCartCovMat(id = attrs['id'], x=x, y=y,\
                    z=z)
                self._cluster.append_obs(point)

            else:
                point = PointLocalGama(id = attrs['id'], x=x, y=y, z=z)
                if "adj" in attrs:
                    point.status = gama_coord_status_attr_adj(attrs["adj"])
                    self._pointListAdj.add_point(point)
                elif "fix" in attrs:
                    point.status = gama_coord_status_attr_fix(attrs["fix"])
                    self._pointListFix.add_point(point)

        # cluster obs and observations
        elif name=="obs":
            
            if "from" in attrs: fromid = attrs["from"]
            else: fromid=None
            
            if "from_dh" in attrs: fromdh = float(attrs["from_dh"])
            else: fromdh=None

            if "orientation" in attrs: 
                import sys
                print >>sys.stderr, 'warning: attribute "orientation" not accepted'
            self._cluster = ObsCluster(fromid=fromid, fromdh=fromdh)
            self._clusterList.append_cluster(self._cluster)

        elif name=="direction":
            
            if "stdev" in attrs: 
                stdev = float(attrs["stdev"] ) / Unit.angleStdev
            else: 
                stdev=None
            
            if "from_dh" in attrs: fromdh = float(attrs["from_dh"])
            else: fromdh=None

            if "to_dh" in attrs: todh = float(attrs["to_dh"])
            else: todh=None
            
            val = float(attrs["val"]) / Unit.angleVal

            direction = ObsDirection(toid=attrs["to"], val=val,\
                    stdev=stdev, fromdh=fromdh, todh=todh)
            self._cluster.append_obs(direction)
        
        elif name=="distance":
            
            if "from" in attrs: fromid = attrs["from"]
            else: fromid=None

            if "stdev" in attrs: 
                stdev = float(attrs["stdev"]) / Unit.distStdev
            else: 
                stdev=None
            
            if "from_dh" in attrs: fromdh = float(attrs["from_dh"])
            else: fromdh=None

            if "to_dh" in attrs: todh = float(attrs["to_dh"])
            else: todh=None
            
            distance = ObsDistance(toid=attrs["to"], val=float(attrs["val"]),\
                    fromid=fromid, stdev=stdev, fromdh=fromdh, todh=todh)
            
            self._cluster.append_obs(distance)
        
        elif name=="s-distance":
            
            if "from" in attrs: fromid = attrs["from"]
            else: fromid=None

            if "stdev" in attrs: 
                stdev = float(attrs["stdev"]) / Unit.distStdev
            else: 
                stdev=None
            
            if "from_dh" in attrs: fromdh = float(attrs["from_dh"])
            else: fromdh=None

            if "to_dh" in attrs: todh = float(attrs["to_dh"])
            else: todh=None
            
            sdistance = ObsSDistance(toid=attrs["to"], val=float(attrs["val"]),\
                    fromid=fromid, stdev=stdev, fromdh=fromdh, todh=todh)
            
            self._cluster.append_obs(sdistance)
        
        elif name=="z-angle":
            
            if "from" in attrs: fromid = attrs["from"]
            else: fromid=None

            if "stdev" in attrs:
                stdev = float(attrs["stdev"] ) / Unit.angleStdev
            else: 
                stdev=None
            
            if "from_dh" in attrs: fromdh = float(attrs["from_dh"])
            else: fromdh=None

            if "to_dh" in attrs: todh = float(attrs["to_dh"])
            else: todh=None

            val = float(attrs["val"]) / Unit.angleVal
            
            zangle = ObsZAngle(toid=attrs["to"], val=val,\
                    fromid=fromid, stdev=stdev, fromdh=fromdh, todh=todh)
            
            self._cluster.append_obs(zangle)

        # cluster height-differences and observations
        elif name=="height-differences":
            
            self._cluster = ObsClusterHeightDiff()
            self._clusterList.append_cluster(self._cluster)

        elif name=="dh":
            
            if "stdev" in attrs: 
                stdev = float(attrs["stdev"]) / Unit.distStdev
            else: 
                stdev=None
            
            if "dist" in attrs: 
                dist = float(attrs["dist"]) / Unit.dhdist
            else: 
                dist=None
            
            dh = ObsHeightDiff(fromid=attrs["from"], toid=attrs["to"], 
                    val=float(attrs["val"]), stdev=stdev, dist=dist)
            self._cluster.append_obs(dh)
        
        # cluster vector and observations
        elif name=="vectors":

            self._cluster = ObsClusterVector()
            #self.data["clusterList"].append_cluster(cluster)
            self._clusterList.append_cluster(self._cluster)

        elif name=="vec":

            if "from_dh" in attrs: fromdh = float(attrs["from_dh"])
            else: fromdh=None

            if "to_dh" in attrs: todh = float(attrs["to_dh"])
            else: todh=None
            
            vec = ObsVector(fromid=attrs["from"], toid=attrs["to"],
                    dx=float(attrs["dx"]), dy=float(attrs["dy"]),
                    dz=float(attrs["dz"]))
                    #fromdh=fromdh, todh=todh)
            self._cluster.append_obs(vec)
        
        # cluster coordinates - observations <point /> are handled in "point"
        elif name=="coordinates":
            
            self._coor = True
            self._cluster = ObsClusterCoor()
            self._clusterList.append_cluster(self._cluster)

        # covariance matrix inside cluster
        elif name=="cov-mat":

            self._cluster.covmat = CovMat(dim=int(attrs["dim"]),
                    band=int(attrs["band"]))

        # tags with nothing to do
        elif name=="gama-local" or \
                name=="description":
            pass
        else:
            import sys
            sys.stderr.write("unhandled start tag %s\n" % name)


    def _handle_end_element(self, name):
        '''end element handler for method all'''

        # description
        if name=="description":
            self.data.description = self._characterData.strip()
            #import sys
            #print >>sys.stderr, "Decsr.", self.data.description

        # covariance matrix
        elif name=="cov-mat": 
            for val in self._characterData.split():
                self._cluster.covmat.append_value(\
                                float(val) / Unit.distStdev**2)
        
        # end section of coordinates
        elif name=="coordinates": 
            self._coor = False 
        
        # tags with nothig to do
        elif name=="point" or\
                name=="vectors" or\
                name=="vec" or\
                name=="gama-local" or\
                name=="network" or\
                name=="points-observations" or\
                name=="parameters" or\
                name=="direction" or\
                name=="distance" or\
                name=="s-distance" or\
                name=="z-angle" or\
                name=="obs" or\
                name=="dh" or\
                name=="height-differences":
            pass
        else:
            import sys
            sys.stderr.write("unhandled end tag \"%s\"\n" % name)

        self._characterData=""
    
    def _handle_char_data(self, data):
        '''character data handler for method all and info'''
        self._characterData+=data
    


if __name__=="__main__":

        print "see gizela/data/GamaLocalDataObs.py"
