# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.Error import Error


class AxesOrientationError(Error): pass


class AxesOrientation(object):
    "orientation of axes xy"

    # names of orientation of axes
    __axesName = ["ne", "sw", "wn", "es", "nw", "se", "en", "ws"]
    __axesIndex = {"ne": 0,
                  "sw": 1,
                  "wn": 2,
                  "es": 3,
                  "nw": 4,
                  "se": 5,
                  "en": 6,
                  "ws": 7}

    # names of orientation of axes
    __axesOriName = ["right-handed", "left-handed"]

    # orientation of axes
    __axesOri = [0, 0, 0, 0, 1, 1, 1, 1]

    # names of bearing orientation
    __bearingOriName = ["right-handed", "left-handed"]
    __bearingOriIndex = {"right-handed": 0, "left-handed": 1}

    def __init__(self, axesOri, bearingOri):
        """
        axesOri: string: ne, en, sw, ws, nw, wn, es, se
        bearingOri: string: right-handed/left-handed
        """

        self.axesOri = axesOri
        self.bearingOri =bearingOri


    def _get_axes_ori(self): return self.__axesName[self._axesOri]
    def _set_axes_ori(self, ori):
        try:
            self._axesOri = self.__axesIndex[ori]
        except KeyError:
            raise AxesOrientationError, "Unknown axes orientation %s" % ori

    axesOri = property(_get_axes_ori, _set_axes_ori)

    def _get_bearing_ori(self): return self.__bearingOriName[self._bearingOri]
    def _set_bearing_ori(self, bearing):
        try:
            self._bearingOri = self.__bearingOriIndex[bearing]
        except KeyError:
            raise AxesOrientationError, "Unknown bearing orientation %s" %\
                bearing

    bearingOri = property(_get_bearing_ori, _set_bearing_ori)

    #def is_right_handed(self):
    #    return self.axesOri[1] is "right-handed"
    #
    #def is_left_handed(self):
    #    return self.axesOri[1] is "left-handed"

    def is_consistent(self):
        return self.__axesOri[self._axesOri] == self._bearingOri

    def __str__(self):
        str = ["Axes: %s" % self.axesOri,
               "Axes orientation: %s" %\
                   self.__axesOriName[self.__axesOri[self._axesOri]],
               "Bearing orientation: %s" % self.bearingOri]
        
        return "\n".join(str)


if __name__ == "__main__":
    ax = AxesOrientation("ne","left-handed")
    print ax
    print "Is", ax.is_consistent() and "consistent" or "inconsistent"

    ax.bearingOri = "right-handed"
    print ax.bearingOri
    print "Is", ax.is_consistent() and "consistent" or "inconsistent"

    ax.axesOri = "en"
    print ax.axesOri
    print "Is", ax.is_consistent() and "consistent" or "inconsistent"
    #ax.axesOri = "ee"
