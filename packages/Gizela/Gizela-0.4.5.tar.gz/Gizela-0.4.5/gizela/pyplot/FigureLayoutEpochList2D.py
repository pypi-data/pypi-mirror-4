# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.FigureLayoutErrEll import FigureLayoutErrEll
from gizela.pyplot.PlotPoint import PlotPoint
from gizela.util.Error import Error

#import matplotlib

class FigureLayoutEpochList2DError(Error): pass


class FigureLayoutEpochList2D(FigureLayoutErrEll):
    """
    class with layout for EpochList
    sets title, subtitle, comment, legend

          b o r d e r
      +-------------------------+-------+
      |         title           | comm  |
      |         subtitle        | ent   |
      +-------------------------+-------+
    b |                    | t  |  l    | b
    o |                    | i  |  e    | o
    r |         A X E S    | c  |  g    | r
    d |                    | k  |  e    | d
    e | -------------------+ S  |  n    | e
    r |       tickSpace      p. |  d    | r
      +-------------------------+-------+
         b o r d e r

    """

        
    def __init__(self, 
                 figScale=None,
                 displScale=1.0,
                 title="",
                 subtitle="",
                 confProb=0.95,
                 configFileName=None):
        """
        data: EpochList instance
        figScale: scale ratio of axes for data
        displScale: relative scale ratio for displacements
        title: figure title
        subtitle: figure subtitle
        confProb: confidence probability
        configFileName: file name of configuration file
        """
        
        super(FigureLayoutEpochList2D,
              self).__init__(figScale=figScale, 
                             errScale=displScale,
                             configFileName=configFileName)

        self.legendWidth = self.config["legend"]["width"]
        self.titleHeight = self.config["title"]["height"]
        
        # position of title in relative figure coordinates 0-1
        self.posTitle = [self.border/self.figWidth, 
                         1 - (self.border + self.titleHeight)/self.figHeight,
                         1 - (2*self.border + self.legendWidth)/self.figWidth,
                         self.titleHeight/self.figHeight]
        
        # position of axes in 0-1
        self.posAxes = [self.border/self.figWidth,
                        self.border/self.figHeight,
                        1 - (2*self.border + self.legendWidth + 
                             self.tickSpaceY)/self.figWidth,
                        1 - (2*self.border + self.titleHeight + 
                             self.tickSpaceX)/self.figHeight
                       ]
        
        # position of legend
        self.posLegend = [1 - (self.border + self.legendWidth)/self.figWidth,
                          self.border/self.figHeight,
                          self.legendWidth/self.figWidth,
                          1 - (2*self.border + self.titleHeight)/self.figHeight
                         ]

        # position of comment rectangle
        self.posComment = [1 - (self.border + self.legendWidth)/self.figWidth,
                           1 - (self.border + self.titleHeight)/self.figHeight,
                           self.legendWidth/self.figWidth,
                           self.titleHeight/self.figHeight]

        # set size of axes
        self._set_axes_position()

        # epochs
        #self.numEpoch = None # the number of epoch
        self.epochIndex = None # index of actual epoch

        # styles
        self.pointDotStyleList = [] # list of styles of point dots
        self.pointFixDotStyleList = [] # fixed points
        self.pointConDotStyleList = [] # constrained points
        self.pointAdjDotStyleList = [] # adjusted points


        # set title and comment
        self.titleText = None
        self.subtitleText = None
        self.commentText = None
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.set_comment()

        # set color map
        self.cmap = self.config["colorMap"]["name"]

    
    def _get_legend_label_date(self, epochList):
        return [dt.date().__str__() for dt in epochList.dateTimeList]
    
    def _get_legend_label_labels(self, epochList):
        return self.config["legend"]["labels"].split()


    def set_legend(self, epochList):
        "sets legend of figure for all epochs"

        # make labels
        fun = getattr(self, "_get_legend_label_" +\
                      self.config["legend"]["label"])
        label = fun(epochList)

        # make artists
        from matplotlib.patches import Circle
        artist = [Circle((0,0), fc=c) for c in self.epochColor]
        
        #import sys
        #print >>sys.stderr, "len(epochColor)", len(self.epochColor)
        #print >>sys.stderr, "len(label)", len(label)

        self.legend = self.gca().legend(artist, label, 
                                        loc=2,
                                        borderaxespad=0)

        # bounding box to location 2 - upper left
        bbox = [self.posLegend[0],
                self.posLegend[1] + self.posLegend[3]
               ]
        self.legend.set_bbox_to_anchor(bbox=bbox,
                                       transform=self.figure.transFigure)

        self.legend.set_title(self.config["legend"]["title"])

        # set fontSize of label text
        text = self.legend.get_texts()
        fontSize = self.config["legend"]["fontSize"]
        for t in text:
            t.set_fontsize(fontSize)
        
        title = self.legend.get_title()
        titleFontSize = self.config["legend"]["titleFontSize"]
        title.set_fontsize(titleFontSize)

    
    #def set_legend_color(self, color, label):
    #    "sets legend by color and label"

    #    from matplotlib.patches import Circle
    #    
    #    artist = [Circle((0,0), fc=c) for c in color]
    #    self.set_legend(artist, label)

    
    def set_title(self, title):
        "sets title of figure"

        # delete existing text
        if self.titleText is not None:
            self.titleText.set_text("")

        # set text
        fontSize = self.config["title"]["fontSize"]
        x = self.posTitle[0] + self.posTitle[2]/2
        y = self.posTitle[1] + self.posTitle[3]/2
        
        import matplotlib.pyplot as pyplot
        self.titleText = pyplot.figtext(x, y, title, fontsize=fontSize,
                                        verticalalignment="center",
                                        horizontalalignment="center")
        

    def set_subtitle(self, subtitle):
        "sets subtitle of figure"

        # adjust title vertical alignment
        if self.titleText is not None:
            self.titleText.set_verticalalignment("bottom")

        if self.subtitleText is not None:
            self.subtitleText.set_text("")

        # set subtitle
        fontSize = self.config["subTitle"]["fontSize"]
        x = self.posTitle[0] + self.posTitle[2]/2
        y = self.posTitle[1] + self.posTitle[3]/2
        import matplotlib.pyplot as pyplot
        self.subtitleText = pyplot.figtext(x, y, subtitle, 
                                           fontsize=fontSize,
                                           verticalalignment="top",
                                           horizontalalignment="center")
        

    def set_comment(self, cls=None):
        """
        sets comment string
        according to config settings

        cls: instance with some methods append_comment_*
        """
        
        # erase existing comment
        if self.commentText is not None:
            self.commentText.set_text("")

        comment = [c.strip() for c in 
                   self.config["comment"]["content"].split(",")]
        
        for cm in comment:
            fun = getattr(self, "append_comment_" + cm, lambda x: None)
            try:
                #print "Comment function:", fun
                if cls is None:
                    fun()
                else:
                    fun(cls)
            except Exception, e:
                pass
                #import sys
                #print >>sys.stderr, "Function:", fun
                #print >>sys.stderr, e
    
    
    def append_comment_line(self, line):
        """
        adds line to comment text
        """
        
        if self.commentText is None: # create comment Text instance
            fontSize = self.config["comment"]["fontSize"]
            x = self.posComment[0]# + self.posComment[2]/2
            y = self.posComment[1] + self.posComment[3]/2
            import matplotlib.pyplot as pyplot
            self.commentText = pyplot.figtext(x, y, line,
                                              fontsize=fontSize,
                                              verticalalignment="center",
                                              horizontalalignment="left",
                                              multialignment="left")
            return

        text = self.commentText.get_text()
        self.commentText.set_text("\n".join([text, line]))


    def append_comment_figScale(self, unusedParameter):
        label = self.config["figScale"]["label"]
        self.append_comment_line(label + ": " +\
                                 self.get_scale_ratio_string_min())
    

    def append_comment_displScale(self, unusedParameter):
        label = self.config["displScale"]["label"]
        self.append_comment_line(label + ": " + \
         self.get_scale_ratio_string(self.errScale*min(self.get_scale_ratio())))

    def append_comment_coordSystem(self, epochList):
        label = self.config["coordSystem"]["label"]
        self.append_comment_line(label + ": " + epochList.coordSystemLocal.name)
    

    def append_comment_ellipsoid(self, epochList):
        label = self.config["ellipsoid"]["label"]
        self.append_comment_line(label + ": " +
                                   epochList.coordSystemLocal.ellipsoid.get_code())

    def append_comment_stdevUse(self, epochList):
        label = self.config["stdevUse"]["label"]
        self.append_comment_line(label + ": " + epochList.get_stdev_use())

    def append_comment_axesOri(self, epochList):
        label = self.config["axesOri"]["label"]
        self.append_comment_line(label + ": " + epochList.coordSystemLocal.axesOri)
    
   
    def append_comment_confProb(self, epochList):
        label = self.config["confProb"]["label"]
        #print epochList.get_conf_prob()
        self.append_comment_line(label + ": %.2f" % epochList.get_conf_prob())



    def update_(self, epochList):
        "update figure settings and axes x and y"
        
        self.set_axes(epochList.coordSystemLocal.axesOri)

        self.set_color_style(epochList)

        #import sys
        #print >>sys.stderr, "axesOri: ", epochList.coordSystemLocal.axesOri
        #print >>sys.stderr, "Figure scale: %s" % self.figScale
        #print >>sys.stderr, "Displ. scale: %s" % self.errScale

        if self.figScale is not None:
            self.set_scale_ratio(self.figScale)
        self.set_comment(epochList)
        self.set_legend(epochList)

        
    def plot_vector_xy(self, point):
        PlotPoint.plot_vector(self, point,
                              self.config["displacementStyle"],
                              self.config["displacementNoneStyle"])

    def plot_vector_z(self, dateTimeList, z):
        PlotPoint.plot_vector_xy(self, 
                                 dateTimeList,
                                 z,
                                  self.config["displacementStyle"],
                                  self.config["displacementNoneStyle"])

    def plot_vector_z0(self, dateTimeList, z):
        "plot zero line"
        PlotPoint.plot_vector_xy(self, 
                                 dateTimeList,
                                 z,
                                 self.config["zeroLineStyle"],
                                 self.config["zeroLineStyle"])

    def set_color_style(self, epochList): 
        "sets colors and styles according to number of epoch"

        #self.numEpoch = epochList.numEpoch
        self.reset_epoch_counter()
        
        # set styles
        self.pointDotStyleList = []
        self.pointFixDotStyleList = []
        self.pointConDotStyleList = []
        self.pointAdjDotStyleList = []
        
        # get colors from colormap
        from gizela.pyplot.ColorMap import ColorMap

        cm = ColorMap(self.cmap, 0, epochList.numEpoch)
        self.epochColor = [cm.get_color(i) for i in xrange(epochList.numEpoch)]
        
        for c in self.epochColor:
            for st, li in zip(["pointDotStyle",
                               "pointFixDotStyle",
                               "pointConDotStyle",
                               "pointAdjDotStyle"],
                              [self.pointDotStyleList,
                               self.pointFixDotStyleList,
                               self.pointConDotStyleList,
                               self.pointAdjDotStyleList]):
                import copy
                style = copy.copy(self.config[st])
                style["markerfacecolor"] = c
                li.append(style)

    def reset_epoch_counter(self): self.epochIndex = 0
    
    def set_stdev(self, epochList):
        "sets stdev from epochList for confidence regions"
        self.stdev = epochList.stdevList[self.epochIndex]
        #import sys
        #print >>sys.stderr, "Epoch index: %i" % self.epochIndex
        #print >>sys.stderr, self.stdev

    def next_point_dot_style(self): 
        self.epochIndex += 1
        
    def get_point_dot_style(self): 
        return self.pointDotStyleList[self.epochIndex]

    def get_point_fix_dot_style(self):
        return self.pointFixDotStyleList[self.epochIndex]

    def get_point_con_dot_style(self):
        return self.pointConDotStyleList[self.epochIndex]

    def get_point_adj_dot_style(self):
        return self.pointAdjDotStyleList[self.epochIndex]

    def plot_point_dot(self, point):
        PlotPoint.plot_point_dot(self, point, style=self.get_point_dot_style())
    
    def plot_point_fix_dot(self, point):
        PlotPoint.plot_point_dot(self, point, 
                                 style=self.get_point_fix_dot_style())
    
    def plot_point_con_dot(self, point):
        PlotPoint.plot_point_dot(self, point, 
                                 style=self.get_point_con_dot_style())
    
    def plot_point_adj_dot(self, point):
        PlotPoint.plot_point_dot(self, point, 
                                 style=self.get_point_adj_dot_style())
    
    def plot_point_fix_x(self, point, x):
        PlotPoint.plot_point_x(self, point, x,
                               style=self.get_point_fix_dot_style())
    
    def plot_point_fix_y(self, point, x):
        PlotPoint.plot_point_y(self, point, x,
                               style=self.get_point_fix_dot_style())
    
    def plot_point_fix_z(self, point, x):
        PlotPoint.plot_point_z(self, point, x,
                               style=self.get_point_fix_dot_style())

    def plot_point_con_x(self, point, x):
        PlotPoint.plot_point_x(self, point, x,
                               style=self.get_point_con_dot_style())
    
    def plot_point_con_y(self, point, x):
        PlotPoint.plot_point_y(self, point, x,
                               style=self.get_point_con_dot_style())
    
    def plot_point_con_z(self, point, x):
        PlotPoint.plot_point_z(self, point, x,
                               style=self.get_point_con_dot_style())

    def plot_point_adj_x(self, point, x):
        PlotPoint.plot_point_x(self, point, x,
                               style=self.get_point_adj_dot_style())
    
    def plot_point_adj_y(self, point, x):
        PlotPoint.plot_point_y(self, point, x,
                               style=self.get_point_adj_dot_style())
    
    def plot_point_adj_z(self, point, x):
        PlotPoint.plot_point_z(self, point, x,
                               style=self.get_point_adj_dot_style())
    
    
    

        

if __name__ == "__main__":
    
    print "run gizela/stat/EpochList.py"
