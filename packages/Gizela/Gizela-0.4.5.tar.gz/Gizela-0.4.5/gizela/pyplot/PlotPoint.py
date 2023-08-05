# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PlotPoint.py 119 2011-01-11 23:44:34Z tomaskubin $

from gizela.util.Error import Error

class PlotPointError(Error): pass


class PlotPoint(object):
    '''class for plotting of geodetic points with error ellipse
    '''
    
    @classmethod
    def plot_point_xy(cls, figure, x, y, style):
        "plots point - position with marker"

        if figure.is_swap_xy():
            y, x = x, y
        
        line, = figure.gca().plot([x], [y])
        
        figure.set_style(style, line)


    @classmethod
    def plot_point_dot(cls, figure, point, style):
        cls.plot_point_xy(figure, point.x, point.y, style)
    
    @classmethod
    def plot_point_x(cls, figure, point, x, style):
        cls.plot_point_xy(figure, x, point.x, style)
    
    @classmethod
    def plot_point_y(cls, figure, point, x, style):
        cls.plot_point_xy(figure, x, point.y, style)
    
    @classmethod
    def plot_point_z(cls, figure, point, x, style):
        cls.plot_point_xy(figure, x, point.z, style)
    

    @classmethod
    def plot_label_xy(cls, figure, id, x, y, style):
        "plot point id"
        
        if figure.is_swap_xy():
            y, x = x, y

        text = figure.gca().text(x, y, id,
                                transform=figure.get_label_tran())
        
        figure.set_style(style, text)

    
    @classmethod
    def plot_point_label(cls, figure, point, style):
        cls.plot_label_xy(figure, point.id, point.x, point.y, style)

    
    @classmethod
    def plot_error_ellipse_xy(cls, figure, x, y, abom, style): 
        """
        plots standard error ellipse
        x, y : position of center of ellipse
        abom : a, b, om parameters of ellipse

        method do not handle axes orientation (self.figure.axesXY)
        """

        from matplotlib.patches import Ellipse
        from math import pi

        a, b, om = abom

        #print "swapXY:", figure.is_swap_xy()
        if figure.is_swap_xy():
            y, x = x, y
            om = pi/2 - om
            #om = om - pi/2

        ell = Ellipse((x, y), 2*a, 2*b, om*180.0/pi) #?
                      #transform=self.axes.transData + self.ellTrans)

        figure.set_style(style, ell)
        
        ell.set_clip_box(figure.gca().bbox) # cut edges outside axes box?
        figure.gca().add_artist(ell)


    @classmethod
    def plot_point_error_ellipse(cls, figure, point, ellScale, style):
        abom = point.errEll
        abom[0] *= ellScale
        abom[1] *= ellScale

        import sys
        print >>sys.stderr, point.id, ":s_x s_y:", point.stdevx, point.stdevy
        print >>sys.stderr, point.id, ":xi,yi,zi:", point.xi, point.yi, point.zi
        print >>sys.stderr, point.id, ":covmat:", point.covmat
        print >>sys.stderr, point.id, ":covmat:", point.covmat.data
        print >>sys.stderr, point.id, ":ell:", point.errEll
        print >>sys.stderr, point.id, ":scale:", ellScale
        print >>sys.stderr, point.id, ":ell_scaled:", abom

        cls.plot_error_ellipse_xy(figure, point.x, point.y, abom, style)

    @classmethod
    def _compute_segments(cls, x, y):
        "returns segments of line divided by Nones"
        
        # find line segments for Nones
        xx, yy = [], [] # lines without None(s)
        xn, yn = [], [] # line with None(s)
        xl, yl = None, None # last not None coordinate
        new = True # new segment of line?
        for xi, yi in zip(x, y):
            if xi == None or yi == None:
                new = True
            else:
                if new:
                    # start new line
                    xx.append([xi])
                    yy.append([yi])
                    if xl != None: 
                        # add line for Nones
                        xn.append([xl, xi])
                        yn.append([yl, yi])
                else:
                    # add next point to line
                    xx[-1].append(xi)
                    yy[-1].append(yi)
                
                new = False        
                xl, yl = xi, yi # save xi as last not None values

        return xx, xn, yy, yn

    @classmethod
    def plot_vector_xy(cls, figure, x, y, style, styleNone):
        """
        plot vector
        just line with specific style

        style: style for line
        styleNone: style for connections with None values

        x, y: lists of coordinates
        """
    
        if figure.is_swap_xy():
            x, y = y, x

        #from matplotlib.patches import FancyArrowPatch, ArrowStyle

        #arr = Arrow(x, y, dx, dy)
        #figure.axes.add_artist(arr)
        
        xx, xn, yy, yn = cls._compute_segments(x, y)
        #yy, yn = cls._compute_segments(y)


        # draw lines
        for x, y in zip(xx, yy):
            line, = figure.gca().plot(x, y)
            figure.set_style(style, line)
        
        # draw lines for Nones
        for x, y in zip(xn, yn):
            line, = figure.gca().plot(x, y)
            figure.set_style(styleNone, line)


    @classmethod
    def plot_vector(cls, figure, pointList, style, styleNone):
        
        x = []; y = []
        for p in pointList:
            x.append(p.x)
            y.append(p.y)
        cls.plot_vector_xy(figure, x, y, style, styleNone)
    
        
    @classmethod
    def plot_y_stdev(cls, figure, x, y, stdev, style):
        "plots 1sigma interval for standard deviation along y axis"

        #print "stdev_all:", stdev
        #print "errScale:", figure.errScale
        #print "confScale:", figure.stdev.get_conf_scale_1d()

        # line
        line, = figure.gca().plot([x, x], 
                                  [y - stdev, y + stdev])
        line.set_solid_capstyle("butt")
        figure.set_style(style, line)


        

if __name__ == "__main__": 
    
    from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
    fig = FigureLayoutBase()

    from gizela.data.PointCartCovMat import PointCartCovMat
    p = PointCartCovMat(id="A", x=0, y=0)
    p.var = (9, 4)

    print p.errEll

    style = {}
    PlotPoint.plot_point_xy(fig, p.x, p.y, style)
    PlotPoint.plot_label_xy(fig, p.id, p.x, p.y, style)
    PlotPoint.plot_error_ellipse_xy(fig, p.x, p.y, p.errEll, style)
    PlotPoint.plot_vector_xy(fig, [p.x, p.x + 3, p.x + 1.0], 
                          [p.y, p.y - 2, p.y - 1.5], style, style)

    fig.gca().axis([-4,4,-4,4])
    fig.set_aspect_equal()
    #fig.show_()
    ori = ("en", "wn", "ne", "nw", "es", "ws", "se", "sw")
    for o in ori:
        fig = FigureLayoutBase(axesOri=o)
        from math import pi
        fig.config["errorEllipseStyle"]["alpha"] = 0.2
        PlotPoint.plot_error_ellipse_xy(fig, x=0.5, y=0.2, 
                                        abom=(0.3,0.1,20*pi/200),
                                        style="errorEllipseStyle") 
        fig.config["errorEllipseStyle"]["alpha"] = 1
        PlotPoint.plot_error_ellipse_xy(fig, x=0.5, y=0.2, 
                                        abom=(0.3,0.1,0),
                                        style="errorEllipseStyle") 
        print fig.get_axes_ori()
        print fig.is_swap_xy()
    fig.show_()
