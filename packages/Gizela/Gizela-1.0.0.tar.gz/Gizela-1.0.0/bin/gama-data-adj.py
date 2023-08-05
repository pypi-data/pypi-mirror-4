#!/usr/bin/python

'''
Script: work with gama-local adjustment
'''

import sys
import datetime
import gizela

# Gizela signature
dateTime = datetime.datetime.now()
gizelaSignature = "\n".join(["",
                             ">-- Gizela project ver. %s -->" % gizela.__version__,
                             ">-- Created: %i.%i.%i  %2i:%2i:%2i -->" % (
                                 dateTime.day, 
                                 dateTime.month,
                                 dateTime.year,
                                 dateTime.hour, 
                                 dateTime.minute, 
                                 dateTime.second)])

# nacteni vstupnich parametru
from optparse import OptionParser
usage = "usage: %prog [opt] file1 file2 ..."
version = "%prog $Revision: 119 $"
parser = OptionParser(usage=usage, version=version)

#testing
parser.add_option("", "--test-xy", action="store_true", default=False,
                  dest="testXY", help="test xy displacements with 2D test")

parser.add_option("", "--test-z", action="store_true", default=False,
                  dest="testZ", help="test z displacements with 1D test")

parser.add_option("", "--conf-prob", action="store", default=0.95, type="float",
                  dest="confProb", help="Set confidence probability for testing")


# plotting
parser.add_option("", "--plot-xy", action="store_true", dest="plot_xy", 
                  default=False,
                  help="draw 2D graph of xy coordinates") 

parser.add_option("", "--plot-z", action="store_true", dest="plot_z", default=False,
                  help="draw 1D graph of z coordinates") 

parser.add_option("", "--config-fig", action="store", type="string",
                  dest="configFig", help="use configutation file for pyplot graph")

parser.add_option("", "--title", action="store", type="string", default="",
                  dest="title", help="title of figure")

parser.add_option("", "--subtitle", action="store", type="string", default="",
                  dest="subtitle", help="subtitle of figure")

parser.add_option("", "--fig-scale", action="store", type="string",
                  dest="figScale", 
                  help="figure scale factor eg. 1e-3 or 1:1000")

parser.add_option("", "--displ-scale-xy", action="store", type="string", 
                  default="1", dest="displScale2D",
                  help="relative scale of displ. of xy points - defult 1:1")

parser.add_option("", "--displ-scale-z", action="store", type="string",
                  default="1", dest="displScale1D", 
                  help="absolute scale of displ. of z coordinate - defult 1:1")

parser.add_option("", "--show-figure", action="store_true", dest="showFigure", 
                  default=False,
                  help="Draw figure on the screen.")
        

# save plots
parser.add_option("", "--save-xy", action="store", type="string",
                  dest="saveXY", help="store figure XY to file fileName")

parser.add_option("", "--save-z", action="store", type="string",
                  dest="saveZ", help="store figure Z to file fileName")

parser.add_option("", "--dpi", action="store", type="float",
                  dest="dpi", default=300, help="dip of image to save")

# select points
parser.add_option("", "--no-fix", action="store_true", default=False,
                  dest="noFix", help="plot fixed points?")

parser.add_option("", "--test-id", action="store", type="string", default=None,
                  dest="testId", help="test and plot just points with given id")

#parser.add_option("", "--idFix", action="store", type="string", default=None,
#                  dest="idFix", help="plot just points with given id")


# standard deviation
parser.add_option("", "--use-apriori", action="store_true", default=True,
                  dest="useApriori", help="Use apriori standart deviation")

parser.add_option("", "--use-aposteriori", action="store_false", default=True,
                  dest="useApriori", help="Use aposteriori standart deviation")


# text outputs
parser.add_option("", "--print-displacements", action="store", 
                  dest="printDisplFile", help="print displacements to file")

parser.add_option("", "--print-coordinates", action="store", 
                  dest="printCoordFile", help="prints coordinates to file")

parser.add_option("", "--print-test", action="store", 
                  dest="printTestFile", help="prints test results to file")


# setting of 2D or 3D local system
parser.add_option("", "--config", action="store", type="string", 
                  dest="configFile", default=None,
                  help="Set a name of configuration file")

parser.add_option("", "--local-system-2d", action="store_true", default=False,
                  dest="localSystem2D", 
                  help="set 2D local system from configuration file")

parser.add_option("", "--local-system-3d", action="store_true", default=False,
                  dest="localSystem3D", 
                  help="set 3D local system from configuration file")

# joined adjustment
parser.add_option("", "--joined", action="store", type="string", 
                  dest="joined", default=None,
                  help="Set parameters for separating joined adjustment of epochs. --joined=restring,epochIndex,pointIndex")

# transfomations of points
parser.add_option("", "--tran-point-2d", action="store", type="string", 
                  dest="tranPoint2D", default=None,
                  help="Transform points with transformation a,b,c,d,e,f: xx=ax + by + e; yy=cx + dy + f.")



(opt, args) = parser.parse_args(); 



if len(args) is 0:
    sys.exit("No file set")

# is coordinate system set?
if not opt.localSystem2D and not opt.localSystem3D:
    print >>sys.stderr, "No coordinate system set."
    sys.exit(1)

# join
if opt.joined is not None:
    print >>sys.stderr, "Joined adjustment set."

    if len(args) != 1:
        print >>sys.stderr, "One file required for joined adjustment."
        sys.exit(1)

    opt.joined = opt.joined.split(",")
    if len(opt.joined) != 3:
        print >>sys.stderr, "Three parameters separated by commas requred."
        print >>sys.stderr, "Option: %s" % opt.joined
        sys.exit(1)

    try:
        epochIndex = int(opt.joined[1])
        pointIndex = int(opt.joined[2])
    except Exception, e:
        print >>sys.stderr, "Unable to set indexes for joined adjustment."
        print >>sys.stderr, e
        sys.exit(1)

# compute scale
def compute_scale(sc):
    if sc is not None:
        s = sc.split(":")
        if len(s) == 2:
            return float(s[0]) / float(s[1])
        else:
            return float(sc)

# open file for protocol
numProt = 0
for fn in opt.printCoordFile, opt.printDisplFile, opt.printTestFile:
    if fn is not None:
        try:
            filePrint = open(fn, "wt")
            numProt += 1
            print >>sys.stderr, "Protocol file opened: %s" % fn
        except:
            print >>sys.stderr, "Can not open file %s" % fn
            sys.exit(1)

if numProt > 1:
    print >>sys.stderr, "Just one type of protocol for single run supported"
    sys.exit(1)

# text table to use
textTable=None
if opt.printDisplFile:
    from gizela.stat.displ_test_text_table import point_displ_text_table
    textTable = point_displ_text_table()
elif opt.printCoordFile:
    from gizela.data.point_text_table import gama_coor_stdev_table
    textTable = gama_coor_stdev_table()
elif opt.printTestFile:
    from gizela.stat.displ_test_text_table import displ_test_text_table
    textTable = displ_test_text_table()

#print textTable
#print opt.test

# scale factors
if opt.figScale is not None:
    opt.figScale = compute_scale(opt.figScale)
    print >>sys.stderr, "Figure scale set: %s" % opt.figScale
if opt.displScale2D is not None:
    opt.displScale2D = compute_scale(opt.displScale2D)
    print >>sys.stderr, "XY Displacement scale set: %s" % opt.displScale2D
if opt.displScale1D is not None:
    opt.displScale1D = compute_scale(opt.displScale1D)
    print >>sys.stderr, "Z Displacement scale set: %s" % opt.displScale1D

#for sc in (opt.figScale, opt.displScale2D,
#           opt.displScale1D):
#    print sc

# ids of points
if opt.testId is not None:
    opt.testId = [i.strip() for i in opt.testId.split(",")]

if opt.noFix:
    opt.idFix = []
else:
    opt.idFix = None


# read configuration file
from gizela.util.gama_data_fun import read_configuration_file

configDict, localSystem = read_configuration_file(opt.configFile,
                                                  opt.localSystem2D,
                                                  opt.localSystem3D)


# epoch list - the main object
from gizela.data.NetworkAdjList import NetworkAdjList
epochList = NetworkAdjList(coordSystemLocal=localSystem,
                           stdevUseApriori=opt.useApriori,
                           confProb=opt.confProb,
                           textTable=textTable,
                           testId=opt.testId)

# confProb works only in class NetworkAdjList !!!

from gizela.data.Network import Network


if not localSystem.is_consistent():
    print >>sys.stderr, "Local coordinate system is not consistent"
    print >>sys.stderr, localSystem
    sys.exit(1)

# set local system from configuration file
if opt.configFile is not None:
    if opt.localSystem2D:
        epochList.coordSystemLocal = localSystem
        print >>sys.stderr, "Local 2D system '%s' set." % localSystem.name
    if opt.localSystem3D:
        epochList.coordSystemLocal = localSystem
        print >>sys.stderr, "Local 3D system '%s' set." % localSystem.name

# 2d transformation
if opt.tranPoint2D:
    trnKey = opt.tranPoint2D.split(",")
    if len(trnKey) != 6:
        print trnKey
        sys.exit("Six transformation parameters required.")

    from gizela.tran.Tran2D import Tran2D
    tran = Tran2D()
    tran.set_trn_key(trnKey)

# open files, read data and add them into epochList
from gizela.data.GamaLocalDataAdj import GamaLocalDataAdj
for name in args:
    try:
        file = open(name)
    except IOError, e:
        print >>sys.stderr, "Cannot open file '%s'" % name
        print e
        sys.exit(1)

    data = GamaLocalDataAdj()

    try:
        data.parse_file(file)
    except Exception, e:
        print >>sys.stderr, "Cannot parse file '%s'" % name
        print e
        sys.exit(1)

    net = Network(coordSystemLocal=localSystem, data=data)

    if opt.tranPoint2D is not None:
        #print net.pointListAdj
        #print net.pointListAdjCovMat
        #print net.pointListAdjCovMat.covmat
        net.tran_point(tran)
        #print net.pointListAdj
        #print net.pointListAdjCovMat
        #print net.pointListAdjCovMat.covmat

    if opt.joined is None:
        epochList.append(net)

    else:
        epochList.append_joined(net, 
                                reString=opt.joined[0], 
                                epochIndex=epochIndex,
                                pointIndex=pointIndex)

print >>sys.stderr, "File(s) readed:", " ".join(args)
if opt.tranPoint2D:
    print >>sys.stderr, "Points transformed."


# compute test
if opt.testXY:
    from gizela.stat.DisplacementTestType import DisplacementTestType
    epochList.compute_displacement_test(testType=DisplacementTestType.xy)
    print >>sys.stderr, "Test of xy displacements computed."

# print text outputs
if opt.printDisplFile or opt.printCoordFile or opt.printTestFile:
    print >>sys.stderr, epochList
    print >>filePrint, epochList
    print >>filePrint, epochList.get_epoch_table()
    print >>filePrint, gizelaSignature
    print >>sys.stderr, "Results wrote to text file:", filePrint.name


# create figure
#
# plot position and displacements of xy points with error ellipses
if opt.plot_xy:
    if opt.testXY:
        from gizela.pyplot.FigureLayoutEpochList2DTest import FigureLayoutEpochList2DTest
        figXY = FigureLayoutEpochList2DTest(figScale=opt.figScale,
                                            displScale=opt.displScale2D,
                                            title=opt.title,
                                            subtitle=opt.subtitle,
                                            #confProb=opt.confProb, this does not work
                                            configFileName=opt.configFig)

    else:
        from gizela.pyplot.FigureLayoutEpochList2D import FigureLayoutEpochList2D
        figXY = FigureLayoutEpochList2D(figScale=opt.figScale,
                                        displScale=opt.displScale2D,
                                        title=opt.title,
                                        subtitle=opt.subtitle,
                                        #confProb=3.93469340287366e-01, this does not work
                                        configFileName=opt.configFig)

    
    # plot points
    epochList.plot_xy(figXY, 
                      idAdj=opt.testId,
                      idFix=opt.idFix,
                      plotTest=opt.testXY)

# plot z coordinates and displacements of points with error interval
if opt.plot_z:
    figZList = [] # list of figures with graph of z coordinate

    zTestId = opt.testId
    if opt.testId is None:
        zTestId = [id for id in epochList.epochPointList.iter_id()]

    if opt.testZ:
        from gizela.pyplot.FigureLayoutEpochList1DTest import FigureLayoutEpochList1DTest
        for id in zTestId:
            subtitle = opt.subtitle + " - bod %s" %id
            figZ = FigureLayoutEpochList1DTest(displScale=opt.displScale1D,
                                               title=opt.title,
                                               subtitle=subtitle,
                                               #confProb=opt.confProb, this does not work
                                               configFileName=opt.configFig)
            # plot points
            epochList.plot_z(figZ, id=id)
            figZList.append(figZ)
        
    else:
        from gizela.pyplot.FigureLayoutEpochList1D import FigureLayoutEpochList1D
        for id in zTestId:
            subtitle = opt.subtitle + " - bod %s" %id
            figZ = FigureLayoutEpochList1D(displScale=opt.displScale1D,
                                           title=opt.title,
                                           subtitle=subtitle,
                                           #confProb=opt.confProb, this does not work
                                           configFileName=opt.configFig)
            # plot points
            epochList.plot_z(figZ, id=id)
            figZList.append(figZ)

# show figure
if opt.plot_xy:
    figXY.show_(mainloop=opt.showFigure)
if opt.plot_z:
    figZ.show_(mainloop=opt.showFigure)

# save figure
if opt.saveXY is not None and opt.plot_xy:
    figXY.save_as(opt.saveXY)
if opt.saveZ is not None and opt.plot_z:
    saveZ = opt.saveZ.split(".")

    if len(saveZ) == 1:
        print >>sys.stderr, "No extension found: %s" % saveZ
        sys.exit(1)

    for fig, id in zip(figZList, zTestId):
        fig.save_as(".".join(saveZ[:-1]) + "_%s" % id + "." + saveZ[-1])
