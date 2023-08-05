# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: FigureLayoutBase.py 117 2011-01-05 23:28:15Z tomaskubin $


import matplotlib
import gizela
from gizela.util.Error import Error
from gizela.pyplot.PlotPoint import PlotPoint
from gizela.pyplot.BackendSingleton import BackendSingleton
#import math


class FigureLayoutBaseError(Error): pass


class FigureLayoutBase(object):
    '''
    object with matplotlib Figure instance
    base class for other Layouts

    just figure with one axes rectangle
    work with: axes orientation
               axes scale
               save figure as image
               plot points xy and x, y, or z coordinate separately
               plot standard deviation along vertical axis
               plot error ellipses
    '''
    
    # matplotlib backend
    #backend = None # backend - just the first instance can set backend


    #@classmethod
    #def set_backend(cls, backend):
    #    if cls.backend == None:
    #        try:
    #            matplotlib.use(backend)
    #            cls.backend = backend
    #        except:
    #            raise FigureLayoutBaseError, "Backend set error"
    #    else:
    #        if backend != cls.backend:
    #            raise FigureLayoutBaseError, "Different backend can not set"

    
    def __init__(self, 
                 axesOri="en",
                 figScale=None,
                 configFileName=None):
        """
        axesOri: orientation of axes ne, en, sw, ws, ...
        figScale: scale of data in axes
        configFileName ... name of configuration file
        """

        # sets self.config dictionary
        self.parse_config_file(name=configFileName)
        
        # first of all set backend
        # call the BackendSingleton class
        if "backend" in self.config and "name" in self.config["backend"]:
            self.backend = BackendSingleton(self.config["backend"]["name"])
        else:
            self.backend = BackendSingleton("GTK") # implicit backend
        
        # set figure
        import matplotlib.pyplot
        self.figure = matplotlib.pyplot.figure() #figure instance
        
        # set size of figure
        if "figure" in self.config and "size" in self.config["figure"]:
            self.figSize = [float(s) 
                      for s in self.config["figure"]["size"].split(",")]
        else:
            # default value A4
            self.figSize = [297, 210]
        # figure size in milimeters
        self.figWidth = self.figSize[0]
        self.figHeight = self.figSize[1]
        sizei = [i / 25.4 for i in self.figSize]
        self.figure.set_size_inches(sizei, forward=True)
            # forward figure size to window size 
            # works just for GTK* and WX* backends

        # compute sizes
        if "figure" in self.config and "border" in self.config["figure"]:
            self.border = self.config["figure"]["border"]
        else: self.border = 5 # implicit value
        if "axes" in self.config and "tickLabelSpace" in self.config["axes"]:
            tickSpace = [float(i) 
                     for i in self.config["axes"]["tickLabelSpace"].split(",")]
        else: tickSpace = [7.0, 10.0] # implicit value
        self.tickSpaceX = tickSpace[0]
        self.tickSpaceY = tickSpace[1]
        
        # position of axes in 0-1
        self.posAxes = [self.border/self.figWidth,
                        self.border/self.figHeight,
                        1 - (2*self.border + self.tickSpaceY)/self.figWidth,
                        1 - (2*self.border + self.tickSpaceX)/self.figHeight
                       ]

        # offset for posAxes
        self.posTickSpace = [self.tickSpaceY/self.figWidth,
                             self.tickSpaceX/self.figHeight,
                             0, 0]
        
        # set axes
        self.figure.add_axes(self.posAxes)
        self.set_axes(axesOri)

        # set adjustable and autoscale
        self.gca().set_adjustable("datalim")
        #self.gca().set_autoscale_on(False)

        # set tick formatter
        import matplotlib.ticker as ticker
        formatter = ticker.ScalarFormatter(useOffset=False)
        formatter.set_powerlimits((-4,10))
        self.gca().xaxis.set_major_formatter(formatter)
        self.gca().yaxis.set_major_formatter(formatter)

        # scale
        self.figScale = None
        if figScale is not None:
            self.set_scale_ratio(figScale)
            self.figScale = figScale
        
        # sets logo
        self.logo = self.figure.text(1 - self.border/2/self.figWidth,
                                     self.border/2/self.figHeight,
                                     ">--Gizela-%s-->" % gizela.__version__,
                                     fontsize=6,
                                     verticalalignment="center",
                                     horizontalalignment="right")
                                     #transform=self.figure.tranFigure)

        # set scale bar
        #if "scaleBar" in self.config and figScale is not None:
        #    from matplotlib.patches import Rectangle
        #    if self.config["scaleBar"]["visible"] == "on":
        #        # plot scale bar
        #        width = self.config["scaleBar"]["width"]/100
        #        height = self.config["scaleBar"]["height"]/100
        #        offset = self.config["scaleBar"]["offset"]/100
        #        width_m = width * self.figWidth / figScale
        #            #: width of bar in meters in real
        #        exp = 10**math.round(math.log10(width_m))
        #        widthi_m = width_m/4.0
        #        xy = [1 - width - offset, offset]
        #        widthi = width/4
        #        facecolor="white"
        #        trnax = self.gca().transAxes
        #        for i in xrange(4):
        #            self.gca().add_patch(Rectangle(xy=xy,
        #                                           width=widthi,
        #                                           height=height,
        #                                           transform=trnax,
        #                                           facecolor=facecolor))
        #            xy[0] += widthi
        #            if facecolor is "white":
        #                facecolor="black"
        #            else:
        #                facecolor="white"

    

    def update_(self, axesOri=None, figScale=None):
        "updates properties of figure"
        if axesOri is not None:
            self.set_axes(axesOri=axesOri)
        if figScale is not None:
            self.set_scale_ratio(figScale)

    def set_axes(self, axesOri="en", xLabel="X", yLabel="Y"):
        """
        axesXY: orientation of axes: ne, nw, se, sw
                                     en, wn, es, ws
        sets direction and position of ticks and its properties
        sets _swapXY for drawing
        sets position of axes object and posAxes attribute
        """
        #import sys
        #print >>sys.stderr, "set_axes", axesOri
        
        ax = self.gca()
        self._axesOri = axesOri

        if axesOri == "ne" or axesOri == "en":
            self.posTickSpace[0] = self.tickSpaceY/self.figWidth
            self.posTickSpace[1] = self.tickSpaceX/self.figHeight

        elif axesOri == "sw" or axesOri == "ws":
        
            # direction of axes
            if not ax.xaxis_inverted():
                ax.invert_xaxis()
            if not ax.yaxis_inverted():
                ax.invert_yaxis()
            
            # ticks position
            for tick in ax.xaxis.get_major_ticks():
                    tick.label1On = False
                    tick.label2On = True
            
            for tick in ax.yaxis.get_major_ticks():
                    tick.label1On = False
                    tick.label2On = True

            # position of axes
            self.posTickSpace[0] = 0
            self.posTickSpace[1] = 0

        elif axesOri == "es" or axesOri == "se":
            # direction of axes
            if not ax.yaxis_inverted():
                ax.invert_yaxis()
            
            # ticks position
            for tick in ax.xaxis.get_major_ticks():
                    tick.label1On = False
                    tick.label2On = True

            # position of axes
            self.posTickSpace[0] = self.tickSpaceY/self.figWidth
            self.posTickSpace[1] = 0
        
        elif axesOri == "wn" or axesOri == "nw":
            # direction of axes
            if not ax.xaxis_inverted():
                ax.invert_xaxis()
            
            # ticks position
            for tick in ax.yaxis.get_major_ticks():
                    tick.label1On = False
                    tick.label2On = True

            # position of axes
            self.posTickSpace[0] = 0
            self.posTickSpace[1] = self.tickSpaceX/self.figHeight
        
        else:
            raise FigureLayoutBaseError, "Unknown axes orientation %s" % axesOri

        # set axes position
        self._set_axes_position()

        # set ticks label properties
        for l in ax.xaxis.get_ticklabels():
            if "axes" in self.config and "tickFontSize" in self.config["axes"]:
                l.set_fontsize(self.config["axes"]["tickFontSize"])
            else:
                l.set_fontsize(6)

        for l in ax.yaxis.get_ticklabels():
            if "axes" in self.config and "tickFontSize" in self.config["axes"]:
                l.set_fontsize(self.config["axes"]["tickFontSize"])
            else:
                l.set_fontsize(6)

        # set swapXY
        if axesOri == "ne" or axesOri == "nw" \
           or axesOri == "se" or axesOri == "sw":
            self._swapXY = True
        else:
            self._swapXY = False
    
        #sets label of x-axis
        
        if axesOri=="en" or axesOri=="wn" or axesOri=="es" or axesOri=="ws":
            ax.xaxis.set_label_text(xLabel)
            if axesOri=="es" or axesOri=="ws":
                ax.xaxis.set_label_position("top")
            else:
                ax.xaxis.set_label_position("bottom")
        else:
            ax.yaxis.set_label_text(xLabel)
            if axesOri=="se" or axesOri=="ne":
                ax.yaxis.set_label_position("left")
            else:
                ax.yaxis.set_label_position("right")
    
    
        #sets label of y axis
        
        if axesOri=="ne" or axesOri=="nw" or axesOri=="se" or axesOri=="sw":
        
            ax.xaxis.set_label_text(yLabel)
            if axesOri=="se" or axesOri=="sw":
                ax.xaxis.set_label_position("top")
            else:
                ax.xaxis.set_label_position("bottom")
        
        else:
            ax.yaxis.set_label_text(yLabel)
            if axesOri=="es" or axesOri=="en":
                ax.yaxis.set_label_position("left")
            else:
                ax.yaxis.set_label_position("right")


    def _set_axes_position(self):
        self.gca().set_position([i+j for i, j in zip(self.posAxes,
                                                     self.posTickSpace)])

    def get_axes_ori(self): return self._axesOri
    
    def gca(self):
        "returns current axes"
        return self.figure.gca()
   

    def plot_xy(self, x, y):
        "plots data to axes with respect to axes orientation"

        if type(x) != list and type(x) != tuple:
            x = [x]
        
        if type(y) != list and type(y) != tuple:
            y = [y]

        if self._swapXY:
            return self.gca().plot(y, x)
        else:
            return self.gca().plot(x, y)
        

    def set_aspect_equal(self):
        "sets equal aspect ratio for axes"
        self.gca().set_aspect("equal")

    
    def is_swap_xy(self):
        return self._swapXY

    
    def get_scale_ratio(self):
        """
        returns scale ratio for x and y axis
        supposed that data are in meters
        """
        
        xmin, xmax = self.gca().get_xbound()
        ymin, ymax = self.gca().get_ybound()

        return (self.posAxes[2]*self.figWidth/1000)/(xmax -  xmin),\
               (self.posAxes[3]*self.figHeight/1000)/(ymax -  ymin)

    def get_scale_ratio_x(self):
        return self.get_scale_ratio()[0]
    
    def get_scale_ratio_y(self):
        return self.get_scale_ratio()[1]

    def set_scale_ratio(self, ratio):
        "set scale ration of both x and y axes"

        self.set_scale_ratio_x(ratio)
        self.set_scale_ratio_y(ratio)


    def set_scale_ratio_x(self, ratio):
        """
        sets scale ratio of x axis
        manipulating xlim properties of axes object
        """

        dx_ = self.posAxes[2]*self.figWidth/1000/ratio
       
        xmin, xmax = self.gca().get_xbound()
        
        dx = xmax - xmin

        ddx = dx_ - dx

        xmin, xmax = xmin - ddx/2, xmax + ddx/2

        self.gca().set_xbound(xmin, xmax)


    def set_scale_ratio_y(self, ratio):
        """
        sets scale ratio of y axis
        manipulating ylim properties of axes object
        """
        
        dy_ = self.posAxes[3]*self.figHeight/1000/ratio

        ymin, ymax = self.gca().get_ybound()
        
        dy = ymax - ymin

        ddy = dy_ - dy

        ymin, ymax = ymin - ddy/2, ymax + ddy/2

        self.gca().set_ybound(ymin, ymax)


    @staticmethod
    def get_scale_ratio_string(ratio):

        if ratio > 1.0:
            if round(ratio) - ratio > 1e-5:
                return "%.5f : 1" % ratio
            else:
                return "%.0f : 1" % ratio
        else:
            ratio = 1.0/ratio
            if round(ratio) - ratio > 1e-5:
                return "1 : %.5f" % ratio
            else:
                return "1 : %.0f" % ratio


    def get_scale_ratio_string_min(self):
        "returns string with min scale ratio"
        
        return self.get_scale_ratio_string(min(self.get_scale_ratio()))
        

    def get_scale_ratio_string_y(self):
        "returns scale ratio of y axis - vertical axis"
        
        return self.get_scale_ratio_string(self.get_scale_ratio()[1])


    def show_(self, mainloop=True):
        """
        show figure
        """
        if self.figScale is not None:
            self.set_scale_ratio(self.figScale)
        
        import matplotlib.pyplot
        
        matplotlib.pyplot.show(mainloop)


    def set_free_space(self, border=10, equal=False):
        """
        border: white space around drawing in percents
        equal: equal border for x and y direction?
        """
        
        xmin, xmax = self.gca().get_xlim()
        ymin, ymax = self.gca().get_ylim()
        dx = xmax - xmin
        dy = ymax - ymin
        dxp = dx * border/100
        dyp = dy * border/100
        if equal:
            dxyp = (dxp + dyp)/2 # mean value
            dxp = dxyp
            dyp = dxyp
        self.gca().set_xlim((xmin - dxp, xmax + dxp))
        self.gca().set_ylim((ymin - dyp, ymax + dyp))
        

    def save_as(self, fileName="figure"):
        "saves figure as image"
        
        if self.figScale is not None:
            self.set_scale_ratio(self.figScale)
        
        dpi = self.config["figure"]["dpi"]
        
        # set image size
        sizem = self.config["figure"]["size"]
        sizei = [float(i) / 25.4 for i in sizem.split(",")]
        self.figure.set_size_inches(sizei)
        
        import sys
        print >>sys.stderr, "Figure name:", fileName,\
        "size (mm):", sizem, "DPI:", dpi
        
        #self.figure.set_dpi(dpi)
        self.figure.savefig(fileName, dpi=dpi)
    
    
    def parse_config_file(self, name):
        "parser for configuration file"

        import ConfigParser, os, sys
        configParser = ConfigParser.SafeConfigParser()
        configParser.optionxform = str # to make options case sensitive
 
        defaults = os.path.sep.join(["gizela", "pyplot", "default.cfg"])
        path = [p + os.path.sep + defaults for p in sys.path]
        
        if name is not None:
            path.extend([p + os.path.sep + name for p in sys.path])
            path.append(name)

        readed = configParser.read(path)
                     #os.path.expanduser("~/" + name),
                     #"./" + name])
        print >>sys.stderr, \
                "Figure configuration file(s) readed: %s" % ", ".join(readed)
        
        self.config = {}

        for sec in configParser.sections():
            self.config[sec] = {}
            for p,v in configParser.items(sec):
                try:
                    v=float(v)
                except:
                    pass
                self.config[sec][p] = v


    def get_config_section(self, section):
        "returns configuration section items in dictionary"

        return self.config[section]


    def set_style(self, style, artist):
        """
        sets properties of artist according to
        configuration file. 
        styleType: the name of section in config file or
                   dictionary with properties
        artist: instance of graphic object (line, text, ...)
        """

        if type(style) is str:
            style = self.get_config_section(style)

        for p, v in style.items():
            fun = getattr(artist, "set_" + p)
            fun(v)

    def get_style_dict(self, style):
        "returns style dictionary of properties"
        return self.get_config_section(style)


    def get_label_tran(self):
        "return transformation for text labels"
        
        from matplotlib.transforms import offset_copy
    
        offset = self.get_config_section("pointLabelOffset")

        return offset_copy(self.gca().transData, self.figure, 
                           offset["x"], offset["y"], 
                           units="points")
    

    def plot_point_dot(self, point):
        PlotPoint.plot_point_dot(self, point, style="pointDotStyle")
    
    def plot_point_fix_dot(self, point):
        PlotPoint.plot_point_dot(self, point, style="pointFixDotStyle")
    
    def plot_point_con_dot(self, point):
        PlotPoint.plot_point_dot(self, point, style="pointConDotStyle")
    
    def plot_point_adj_dot(self, point):
        PlotPoint.plot_point_dot(self, point, style="pointAdjDotStyle")
    
    def plot_point_label(self, point):
        PlotPoint.plot_point_label(self, point, style="pointLabelStyle")
    
    def plot_point_fix_label(self, point):
        PlotPoint.plot_point_label(self, point, style="pointFixLabelStyle")
    
    def plot_point_con_label(self, point):
        PlotPoint.plot_point_label(self, point, style="pointConLabelStyle")
    
    def plot_point_adj_label(self, point):
        PlotPoint.plot_point_label(self, point, style="pointAdjLabelStyle")
    
    def plot_point_x(self, point, x):
        PlotPoint.plot_point_x(self, point, x, style="pointDotStyle")
    
    def plot_point_y(self, point, x):
        PlotPoint.plot_point_y(self, point, x, style="pointDotStyle")
    
    def plot_point_z(self, point, x):
        PlotPoint.plot_point_z(self, point, x, style="pointDotStyle")
    
    #def plot_point_error_ellipse(self, point): pass
    #def plot_point_x_stdev(self, point, x): pass
    #def plot_point_y_stdev(self, point, x): pass
    #def plot_point_z_stdev(self, point, x): pass
    #def plot_point_error_z(self, point): pass

    def plot_scale_bar(self):pass


if __name__ == "__main__":
    
    fig = FigureLayoutBase(figScale=1e-5)

    fig.set_axes("sw")
    
    fig.plot_xy([1e3, 1.001e3, 1.001e3, 1e3, 1e3],
                [0.5e3, 0.5e3, 0.501e3, 0.501e3, 0.5e3])

    scalex, scaley = fig.get_scale_ratio()
    print 1/scalex, 1/scaley
    
    fig.set_aspect_equal()
    print 1/scalex, 1/scaley

    fig.show_()
    #fig.save_as()
