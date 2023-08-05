#!/usr/bin/python

'''
Script: handles gama-local files with observations

    --config: configuration file with section localSystem to set local
              geodetic coordinate system
    --correct: corrects observations to E3 local geodetic system
    --join: join several files with observations
    --tran-vec-3d: transform vectors to local E3 coordinate system
    --proj-vec-2d: transform vectors to local E2 coordinate system with
                   projection
    --compare-vec: compare vectors --NOT IMPLEMENTED--
    --vec-covmat-scale: scale factor for covariance matrix of vector
                        cm = cm * factor**2
    --xml=file.gkf: write xml with observations to file.gkf
    --fileFixXYZ=file.txt: reads coordinates XYZ from file 
                           and set stutus fix_xyz
        alternaives --fileConXYZ, --fileFixXY, --fileConXY
    --con=id1,id2,... : sets points id1, id2,... status constrained
        alternatives --fix 
    --proj-point-2d
    

'''

# $Id: gama-data-obs.py 120 2011-01-13 22:55:31Z tomaskubin $

import sys
import datetime
from gizela.data.GamaCoordStatus import GamaCoordStatus

# Gizela signature
revStr = "$Revision: 120 $"
revStr = revStr.split()
revision = revStr[1]
dateTime = datetime.datetime.now()
gizelaSignature = "\n".join(["",
                             ">-- Gizela rev%s -->" % revision,
                             ">-- Created: %i.%i.%i  %i:%i:%i -->" % (
                                 dateTime.day, 
                                 dateTime.month,
                                 dateTime.year,
                                 dateTime.hour, 
                                 dateTime.minute, 
                                 dateTime.second)])

# nacteni vstupnich parametru
from optparse import OptionParser

usage = "usage: %prog [options] file1 file2 ..."
version = "%prog $Revision: 120 $"

parser = OptionParser(usage=usage, version=version)

parser.add_option("", "--config", action="store", type="string", 
                  dest="configFile", 
                  help="Set a name of configuration file")

parser.add_option("", "--xml", action="store", type="string", 
                  dest="xmlFile", 
                  help="Write xml with observations to file.")

parser.add_option("", "--correct", action="store_true", default=False,
                  dest="correct", 
                  help="Correct observations for adjustment in E3 local geodetic system")

#parser.add_option("", "--join", action="store_true", default=False, 
#                  dest="join", 
#                  help="Join several files with observations")

# transformation and projection of vectors and points
parser.add_option("", "--tran-vec-3d", action="store_true", default=False, 
                  dest="tranVec3D", 
                  help="Transform vectors to local E3 system")

parser.add_option("", "--proj-vec-2d", action="store_true", default=False, 
                  dest="projVec2D", 
                  help="Projects vectors to xy with proj")

parser.add_option("", "--proj-point-2d", action="store_true", default=False,
                  dest="projPoint2D", 
                  help="Transform points with proj to xy")

# scale covariance matrix of vectors
parser.add_option("", "--scale-vec-cov-mat", action="store", 
                  dest="scaleVecCovMat", 
                  help="Scale covariance matrix with factor**2")

# compare vectors
#parser.add_option("", "--compare-vec", action="store_true", default=False,
#                  dest="compareVec", 
#                  help="Transform vectors to local system")

# coordinates
#parser.add_option("", "--fileFixXYZ", action="store", type="string", 
#                  dest="fileFixXYZ", 
#                  help="reads coordinates xyz from file and sets them fix")
#
#parser.add_option("", "--fileConXYZ", action="store", type="string", 
#                  dest="fileConXYZ", 
#                  help="reads coordinates xyz from file and sets them con")
#
#
#parser.add_option("", "--fileFixXY", action="store", type="string", 
#                  dest="fileFixXY", 
#                  help="reads coordinates xy from file and sets them fix")
#
#parser.add_option("", "--fileConXY", action="store", type="string", 
#                  dest="fileConXY", 
#                  help="reads coordinates xy from file and sets them con")
#
parser.add_option("", "--file-coord", action="store", type="string", 
                  dest="fileCoord", 
                  help="reads coordinates and status from file")

parser.add_option("", "--point-delete-all", action="store_true", default=False,
                  dest="pointDel", 
                  help="delete all tags <point />")

parser.add_option("", "--coord-from-adjustment", action="store", 
                  dest="coordFromAdjustment", 
              help="Add coordinates from adjustment. Delete old coordinates.")



# points status
#parser.add_option("", "--fix-xyz", action="store", type="string", 
#                  dest="fixXYZ", 
#                  help="sets points status fix_xyz")
#
#parser.add_option("", "--fix-xy", action="store", type="string", 
#                  dest="fixXY", 
#                  help="sets points status fix_xy")
#
#parser.add_option("", "--con-xyz", action="store", type="string", 
#                  dest="conXYZ", 
#                  help="sets points status con_xyz")
#
#parser.add_option("", "--con-xy", action="store", type="string", 
#                  dest="conXY", 
#                  help="sets points status con_xy")
#
#parser.add_option("", "--adj-xyz", action="store", type="string", 
#                  dest="adjXYZ", 
#                  help="sets points status adj_xyz")
#
#parser.add_option("", "--adj-xy", action="store", type="string", 
#                  dest="adjXY", 
#                  help="sets points status adj_xy")

# reduction of distances
parser.add_option("", "--sdist-to-dist", action="store_true", default=False,
                  dest="sdistToDist", 
                  help="reduce slope distances to horizontal distance")

parser.add_option("", "--dist-scale", action="store_true", default=False,
                  dest="distScale", 
                  help="scale horizontal distance with factor from config file")

# setting of 2D or 3D local system
parser.add_option("", "--local-system-2d", action="store_true", default=False,
                  dest="localSystem2D", 
                  help="set 2D local system from configuration file")

parser.add_option("", "--local-system-3d", action="store_true", default=False,
                  dest="localSystem3D", 
                  help="set 3D local system from configuration file")

# changing of point ids
parser.add_option("", "--change-id-prefix", action="store",
                  dest="changeIdPrefix", 
                  help="changes ids of points for each epoch with prefix")

parser.add_option("", "--hold-id", action="store", type="string",
                  dest="holdId", 
                  help="ids which do not change with option --change-ids")

# use apriori/aposteriori standard deviation
parser.add_option("", "--use-apriori", action="store_true", default=False,
                  dest="useApriori", 
                  help="Use apriori standard deviation. Rewrites config file settings")

parser.add_option("", "--use-aposteriori", action="store_true", default=False,
                  dest="useAposteriori", 
                  help="Use aposteriori standard deviation. Rewrites config file settings")

# delete observations
parser.add_option("", "--delete-zenith-angle", action="store_true", 
                  default=False,
                  dest="deteleZenithAngle", 
                  help="Delete all zenith angles")

# average of measurements
parser.add_option("", "--average-distance", action="store_true", 
                  default=False,
                  dest="averageDistance", 
                  help="Compute average of counter and repeated distance")
parser.add_option("", "--average-direction", action="store_true", 
                  default=False,
                  dest="averageDirection", 
                  help="Compute average of repeatd distance")

# set date of epochs
parser.add_option("", "--epoch-date", action="store", 
                  dest="epochDate", 
                  help="set dates of epochs in format y1.m1.d1,y2.m2.d2,...")



(opt, arg) = parser.parse_args();

#if len(arg) is 0:
#    sys.exit("No file set")

#if opt.compareVec and len(arg) != 2:
#    sys.exit("Two files required for comparison of vectors.")


# read configuration file
from gizela.util.gama_data_fun import read_configuration_file

configDict, localSystem = read_configuration_file(opt.configFile,
                                                  opt.localSystem2D,
                                                  opt.localSystem3D)

# coordinate system
from gizela.util.CoordSystemLocal2D import CoordSystemLocal2D
from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D

if localSystem is not None:
    if not localSystem.is_consistent():
        print >>sys.stderr, "Local coordinate system is not consistent"
        print >>sys.stderr, localSystem
        sys.exit(1)

    if isinstance(localSystem, CoordSystemLocal2D):
        print >>sys.stderr, "Local 2D system '%s' set." % localSystem.name
    elif isinstance(localSystem, CoordSystemLocal3D):
        print >>sys.stderr, "Local 3D system '%s' set." % localSystem.name
else:
    localSystem = CoordSystemLocal3D()

# read coordinates with point status from file
#
# possible formats of line
# point_id                             point_status
# point_id  coord_x  coord_y           point_status
# point_id  coord_x  coord_y  coord_z  point_status
# point_id                    coord_z  point_status
#
# point_status: adj_xy adj_xyz adj_z adj_XY adj_XYZ adj_Z adj_xyZ adj_XYz
#               fix_xy fix_xyz fix_z

pList = None
if opt.fileCoord is not None:

    from gizela.data.GamaCoordStatus import GamaCoordStatus
    from gizela.data.GamaCoordStatus import GamaCoordStatusError,\
                                            gama_coord_status_string,\
                                            gama_coord_status_dim,\
                                            gama_coord_status_attr
    from gizela.data.PointLocalGama import PointLocalGama
    from gizela.data.PointList import PointList

    pList = PointList()

    try:
        file = open(opt.fileCoord);
    except IOError:
        sys.exit("Cannot open file \"%s\"" % opt.fileCoord)

    line = file.readline()
    line_num = 1
    pointsId = []
    while line:
        line = line.strip()
        if len(line) == 0:
            line = file.readline()
            line_num+=1
            continue
        if line[0] == "#":
            line = file.readline()
            line_num+=1
            continue

        group = line.split()

        if len(group) == 1:
            print >>sys.stderr, "Wrong line %i: %s" %(line_num, line)
            line = file.readline()
            line_num+=1
            continue

        #print >>sys.stderr, group
        id = group.pop(0)
        coord = []

        for str in group:
            try:
                coord.append(float(str))
            except:
                break

        rest = group[len(coord):]
        #print >>sys.stderr, rest

        if len(rest) == 0:
            print >>sys.stderr, "Wrong line %i: %s" %(line_num, line)
            line = file.readline()
            line_num+=1
            continue

        statusStr = rest[0]

        if len(rest) > 1:
            if rest[1][0] != "#":
                print >>sys.stderr, "Wrong line %i: %s" %(line_num, line)
                print >>sys.stderr, rest
                line = file.readline()
                line_num+=1
                continue

        try:
            status = gama_coord_status_attr(statusStr)
        except GamaCoordStatusError, e:
            print >>sys.stderr, e
            print >>sys.stderr, "Wrong line %i: %s" %(line_num, line)
            line = file.readline()
            line_num+=1
            continue

        if len(coord) == 0:
            point = PointLocalGama(id=id, status=status)
        else:
            if gama_coord_status_dim(status) != len(coord):
                print >>sys.stderr, "The number of coordinates (%i) do not agree with status '%s'" % (len(coord), gama_coord_status_string(status))
                line = file.readline()
                line_num+=1
                continue
            if len(coord) == 1:
                point = PointLocalGama(id=id, z=coord[0], status=status)
            elif len(coord) == 2:
                point = PointLocalGama(id=id, x=coord[0], y=coord[1],
                                       status=status)
            elif len(coord) == 3:
                point = PointLocalGama(id=id, x=coord[0], y=coord[1],
                                       z=coord[2], status=status) 

        pList.add_point(point)
        pointsId.append("%s(%s)" % (id,
                                    gama_coord_status_string(status)))

        line = file.readline()
        line_num+=1
    print >>sys.stderr, "Point(s) read: " + " ".join(pointsId)
        


# read observation files
from gizela.data.GamaLocalDataObs import GamaLocalDataObs
from gizela.data.NetworkObsList import NetworkObsList
from gizela.data.Network import Network

obsList = NetworkObsList(coordSystemLocal=localSystem)
#fileNameList = []

for fn in arg:
    try:
        print >>sys.stderr, "Reading gama-local observations: ", fn
        file = open(fn)
    except Exception, e:
        print >>sys.stderr, e
        sys.exit("Cannot open file '%s'" % fn)
        
    try:
        #print fn
        obs = GamaLocalDataObs()
        obs.parse_file(file)
        #fileNameList.append(fn)
        net = Network(coordSystemLocal=localSystem, data=obs)
        #print >>sys.stderr, net.make_gama_xml()
        net.set_file_name(fn)
        obsList.append(net)
    except Exception, e:
        print >>sys.stderr, e
        sys.exit("Cannot parse file '%s'" % fn)

        #try:
        #    #print "*", fn
        #    adj = GamaLocalDataAdj()
        #    file.seek(0)
        #    adj.parse_file(file)
        #    #print adj
        #    if obsList.numEpoch > 0:
        #        obsList[-1].add_adj(adj)
        #        print >>sys.stderr, \
        #                "Adjustment '%s' added to observation '%s'." %\
        #                (fn, obsFileName[-1])
        #        #print >>sys.stderr, obsList[-1].pointListFix
        #        #print >>sys.stderr, obsList[-1].pointListAdj
        #    else:
        #        sys.exit("The first file must contain observations")
        ##except: pass
        #except Exception, ee:
        #    print >>sys.stderr, "Obs parser:", e
        #    print >>sys.stderr, "Adj parser:", ee
        #    sys.exit("Cannot parse file '%s'" % fn)

#if len(fileNameList) > 0:
#    print >>sys.stderr, "Gama data readed: " + ", ".join(fileNameList)

#print obsList[-1]


# ** CHANGE ** ids in observations and points and point readed from file
if opt.changeIdPrefix:

    hold = []
    if opt.holdId:
        hold = opt.holdId.split(",")

    obsList.set_prefix(opt.changeIdPrefix)
    obsList.change_id(holdId=hold)

   # for i, obs in zip(xrange(len(obsList)), obsList):
   #     if opt.pointDel:
   #         obs.delete_all_points()
   #     if pList is not None:
   #         import copy
   #         for point in pList:
   #             obs.add_point(copy.deepcopy(point))
   #     idDict = {}
   #     for id in obs.iter_point_id():
   #         if id not in hold:
   #             idDict[id] = "_epoch_%i__" % i + id
   #     obs.change_id(idDict)
   #     #print >>sys.stderr, obs.make_gama_xml()

   # pList = None # pList allready inserted
   # opt.pointDel = False # points allready deleted

# delete all points
if opt.pointDel:
    for obs in obsList:
        obs.delete_all_points()
    print >>sys.stderr, "All points deleted."

# join observation files
if len(obsList) > 1:
    obsList.join()
    print >>sys.stderr, "Observation files joined."

elif len(obsList) == 1: pass
else:
    # empty NetworkList
    obsList = NetworkObsList(coordSystemLocal=localSystem)
    obsList.append(Network(coordSystemLocal=localSystem, data=None))

obsJoined = obsList[0]

# set date of epoch
if opt.epochDate:
    obsJoined.set_date_time_string(opt.epochDate.replace(",", " "))
    print >>sys.stderr, "Date and time of epochs set: %s" % opt.epochDate

# read adjustment and insert points
if opt.coordFromAdjustment is not None:
    fn = opt.coordFromAdjustment
    try:
        print >>sys.stderr, "Reading gama-local adjustment: ", fn
        file = open(fn)
    except Exception, e:
        print >>sys.stderr, e
        sys.exit("Cannot open file '%s'" % fn)

    from gizela.data.GamaLocalDataAdj import GamaLocalDataAdj
    try:
        adj = GamaLocalDataAdj()
        adj.parse_file(file)
    except Exception, e:
        print >>sys.stderr, e
        sys.exit("Cannot parse file '%s'" % fn)
    else:
        net = Network(localSystem, adj)
        # replace pointListAdj with adjusted points
        obsJoined.replace_point_with_adjusted(net)
        # add fixed points
        for point in net.pointListAdj:
            obsJoined.add_point(point)


# write point readed from file
if pList is not None:
    #print >>sys.stderr, pList
    for point in pList:
        obsJoined.pointListAdj.update_point(point)


# write command line options to <description>
if not obsJoined.configParser.has_section('script'):
    obsJoined.configParser.add_section('script')

obsJoined.configParser.set('script', 'name', 'gama-data-obs.py')
obsJoined.configParser.set('script', 'options', " ".join([i for i in sys.argv[1:]]))

# set local system from configuration file
#if opt.configFile is not None:
#    if opt.localSystem2D:
#        obsJoined.coordSystemLocal = localSystem
#        print >>sys.stderr, "Local 2D system '%s' set." % localSystem.name
#    if opt.localSystem3D:
#        obsJoined.coordSystemLocal = localSystem
#        print >>sys.stderr, "Local 3D system '%s' set." % localSystem.name


# set standard deviation of measurements and use of stdev
if "stdev" in configDict:
    #obsJoined.parse_stdev_dict(configDict["stdev"])
    from gizela.util.Unit import Unit
    stdevDict = configDict["stdev"]

    if "direction" in stdevDict:
        obsJoined.obsStdev["direction"] =\
            float(stdevDict["direction"]) / Unit.angleVal 
        print >>sys.stderr, "Direction standard deviation set %s (gon)"%\
                stdevDict["direction"]

    if "distance" in stdevDict:
        if type(stdevDict["distance"]) is float:
            obsJoined.obsStdev["distance"] = [stdevDict["distance"]]
        else:
            obsJoined.obsStdev["distance"] =\
                    [float(i) for i in stdevDict["distance"].split()]
        print >>sys.stderr, "Distance standard deviation set %s (meters)"%\
                stdevDict["distance"]

    if "zAngle" in stdevDict:
        obsJoined.obsStdev["zenith-angle"] = \
                float(stdevDict["zAngle"]) / Unit.angleVal
        print >>sys.stderr, "Zenith angle standard deviation set %s (gon)"%\
                stdevDict["zAngle"]

    if "use" in stdevDict:
        obsJoined.set_stdev_use(stdevDict["use"])
        print >>sys.stderr, "Use standard deviation: %s" % stdevDict["use"]

    #import sys
    #print >>sys.stderr, self.param
    #print >>sys.stderr,"Standard deviations set (angles gon, distances meters)."
    #print >>sys.stderr, "\n".join(["  %s: %s" %(k,v)\
    #                   for k,v in (configDict["stdev"].items())])

# set use of apriori/aposteriori stdev
if opt.useApriori:
    obsJoined.set_use_apriori(True)
    print >>sys.stderr, "set: use apriori standard deviation"
if opt.useAposteriori:
    obsJoined.set_use_apriori(False)
    print >>sys.stderr, "set: use aposteriori standard deviation"

# scale vectors covmat
if opt.scaleVecCovMat is not None:
    obsJoined.scale_vec_cov_mat(float(opt.scaleVecCovMat))
    print >>sys.stderr, \
    "Covariance matrix of vector scaled with factor %s**2." % opt.scaleVecCovMat


# compare observations
#if opt.compareVec:
#    if opt.tranVec3D:
#        if opt.configFile is None:
#            sys.exit("Local coordinate system not set.")
#
#    for obs in obsList:
#        if opt.tranVec3D:
#            obs.tran_vec_local_ne()
#
#    print >>sys.stderr, "Vectors transformed."
#
#    from gizela.stat.CompareObs import CompareObs
#    
#    cmp = CompareObs(obsList[0], obsList[1])
#    cmp.compare_vector(mean=True)
#
#    # print results
#    print cmp.str_summary()
#    print cmp.str_compared()
#    print cmp.str_uncompared()
#    print cmp.str_mean()
#    sys.exit(0)


# transform vectors to E3 and E2
if opt.tranVec3D:
    if not opt.localSystem3D:
        sys.exit("No 3D local coordinate system set")

    obsJoined.tran_vec_3d()
    print >>sys.stderr, "Vectors transformed to 3D local system."

if opt.projVec2D:
    if not opt.localSystem2D:
        sys.exit("No 2D local coordinate system set")

    #print >>sys.stderr, "ClusterList"
    #print >>sys.stderr, obsJoined.obsClusterList
    #print >>sys.stderr, obsJoined.pointListFix
    #print >>sys.stderr, obsJoined.pointListAdj

    obsJoined.tran_vec_2d()
    print >>sys.stderr, "Vectors projected to 2D local system."

    #if obsJoined.coordSystemLocal.axesOri != "ne":
    #    print >>sys.stderr, "Warning: transformation of vectors to local system with north-east orientation of axes. But in local system is set '%s' orientation" % obsJoined.coordSystemLocal.axesOri


# transform points to xy with proj
if opt.projPoint2D:
    if opt.configFile is None:
        sys.exit("Local coordinate system not set. Cannot project points.")

    obsJoined.proj_point_xy()
    print >>sys.stderr, "Points projected."

# slope distances to horizontal distances
if opt.sdistToDist:
    obsJoined.sdist_to_dist()
    print >>sys.stderr, "Slope distances transformed to horizontal."

# distance scale
if opt.distScale:
    obsJoined.dist_scale()
    print >>sys.stderr, "Horizontal distances scaled with factor %.10f." %\
                                        obsJoined.coordSystemLocal.distScale

# compute average
if opt.averageDirection:
    obsJoined.average_direction()
if opt.averageDistance:
    obsJoined.average_distance(counter=True)

# correct
corrected = False
if opt.correct:

    # compute correction
    #try:
    print >>sys.stderr, obsJoined.pointListAdj
    obsJoined.compute_corr()
    #except Exception, e:
    #    print >>sys.stderr, "Computation of correction failed."
    #    print >>sys.stderr, e
    #    sys.exit(1)

    print >>sys.stderr, "Corrections of observations computed."
    corrected = True

# delete zenith angles
if opt.deteleZenithAngle:
    from gizela.data.ObsZAngle import ObsZAngle
    obsJoined.delete_observation_class(ObsZAngle)
    print >>sys.stderr, "Zenith angles deleted."


# print xml with observations
if opt.xmlFile and obsJoined:
    # write to file
    try:
        file = open(opt.xmlFile, "wt")
        print >>file, obsJoined.make_gama_xml(corrected=corrected)
        print >>sys.stderr, "Observation file write to file '%s'." %\
                opt.xmlFile
    except IOError, e:
        print >>sys.stderr, "Cannot open file '%s'." % opt.xmlFile
        print >>sys.stderr, e
        sys.exit(1)

else:
    # write to stdout
    print obsJoined.make_gama_xml(corrected=corrected)
    print >>sys.stderr, "Observation file wrote to standard output."

