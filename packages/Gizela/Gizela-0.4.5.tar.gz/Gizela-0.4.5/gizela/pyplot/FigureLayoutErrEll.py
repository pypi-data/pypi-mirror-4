# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
from gizela.pyplot.PlotPoint import PlotPoint
import math

class FigureLayoutErrEll(FigureLayoutBase):
    """
    layout with error ellipses
    designed for GamaLocalData instance
    """

    def __init__(self, 
                 axesOri="en",
                 figScale=None,
                 errScale=1,
                 stdev=None,
                 configFileName=None):
        """
        figScale: scale of data in axes
        errScale: relative scale of error ellipses
        stdev: StandardDeviation instance
        configFileName ... name of configuration file
        """

        super(FigureLayoutErrEll, self).__init__(axesOri=axesOri,
                                                 figScale=figScale,
                                                 configFileName=configFileName)

        self.errScale = errScale

        if stdev is None:
            from gizela.data.StandardDeviation import StandardDeviation
            self.stdev = StandardDeviation()
        else:
            self.stdev = stdev

        # error ellipse scale circle
        #if "errorEllipseScaleCircle" in self.config and figScale is not None:
        #    from matplotlib.patches import Circle
        #    if self.config["errorEllipseScaleCircle"]["visible"] == "on":
        #        # plot scale bar
        #        radius_norm = self.config["errorEllipseScaleCircle"]["radius"]/100
        #        offset_norm = self.config["errorEllipseScaleCircle"]["offset"]/100
        #        radius_real = radius_norm * self.figWidth / figScale
        #        print "Radius norm:", radius_norm
        #        print "Radius real:", radius_real
        #            #: radius in milimeters in real
        #        exp = round(math.log10(radius_real))
        #        print "exp", exp
        #        radius = round(radius_real, int(-exp))
        #        print "Radius:", radius
        #        radius_norm = radius * figScale / self.figWidth
        #        xy = [1 - offset_norm, 1 - offset_norm]
        #        facecolor="white"
        #        trnax = self.gca().transAxes
        #        for i in xrange(4):
        #            self.gca().add_patch(Circle(xy=xy,
        #                                        radius=radius_norm,
        #                                        transform=trnax,
        #                                        facecolor=facecolor))


    def update_(self, gamaLocalData):
        "update figure settings according to data"
        self.set_axes(gamaLocalData.get_axes_ori())
        self.stdev = gamaLocalData.stdev
        if self.figScale is not None:
            self.set_scale_ratio(self.figScale)


    def set_axes_ori(self, axesOri):
        self.set_axes(axesOri)

    
    def plot_point_error_ellipse(self, point):
        #import sys
        #print >>sys.stderr, "errScale: %s" % self.errScale
        #print >>sys.stderr, "stdev: %s" % self.stdev
        #print >>sys.stderr, "conf_scale_2d(): %s" %\
        #                        self.stdev.get_conf_scale_2d()
        PlotPoint.plot_point_error_ellipse(self, point,
                       self.errScale*self.stdev.get_conf_scale_2d(),
                       style="errorEllipseStyle")

    def plot_point_x_stdev(self, point, x):
        PlotPoint.plot_y_stdev(self, x, point.x, 
               self.errScale*self.stdev.get_conf_scale_1d()*point.stdevx,
               style="stdevStyle")

    def plot_point_y_stdev(self, point, x):
        PlotPoint.plot_y_stdev(self, x, point.y,
               self.errScale*self.stdev.get_conf_scale_1d()*point.stdevy,
               style="stdevStyle")

    def plot_point_z_stdev(self, point, x):
        PlotPoint.plot_y_stdev(self, x, point.z,
               self.errScale*self.stdev.get_conf_scale_1d()*point.stdevz,
               style="stdevStyle")
    
    def plot_point_error_z(self, point):
        PlotPoint.plot_y_stdev(self, point.x, point.y,
               self.errScale*self.stdev.get_conf_scale_1d()*point.stdevz,
               style="errorZStyle")
             
if __name__ == "__main__":

    try:
        file = open("../../example/xml-epoch/epoch.adj.xml")
    except Exception, e:
        print e
        print "try to run make in ../../example/xml-epoch/ directory"
        import sys
        sys.exit()
        
    from gizela.data.GamaLocalDataAdj import GamaLocalDataAdj

    adj = GamaLocalDataAdj()
    adj.parse_file(file)
    print adj
    print adj.pointListAdjCovMat.covmat.make_gama_xml()
    print adj.stdev

    from gizela.data.Network import Network
    from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
    c3d = CoordSystemLocal3D()
    net = Network(c3d, adj, useApriori=True)
    fig = FigureLayoutErrEll(figScale=0.0001, errScale=2e3)
    net.plot_point(fig)
    fig.show_()

    # graph
    # test orientation of axes
    for ori in ("ne", "en", "se", "es", "sw", "ws", "nw", "wn"):
        fig = FigureLayoutErrEll(errScale=2e3)
        from matplotlib import pyplot as pl
        pl.figtext(0.5, 0.5, ori, fontsize=20)
        net.set_axes_ori(ori)
        net.plot_point(fig)

    #fig.set_scale_ratio(1.0/4000)
    #print fig.get_scale_ratio_string_min()

    #fig.save_as("errell.png")
    fig.show_()
