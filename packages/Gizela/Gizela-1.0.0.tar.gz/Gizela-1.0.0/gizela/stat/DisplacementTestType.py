# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: DisplacementTestType.py 69 2010-08-24 23:46:33Z tomaskubin $


from gizela.util.Error import Error


class DisplacementTestTypeError(Error): pass


class DisplacementTestType(object):
    "enumeration: types of tests of displacements"

    __slots__ = ["none", "x", "y", "z", "xy", "xyz", "all"]

    none = None
    x    = 1
    y    = 2
    z    = 3
    xy   = 4
    xyz  = 5
    #all  = [x, y, z, xy, xyz]

    @classmethod
    def get_string(cls, ind):
        "returns string representation of test"

        string = {cls.none   : None,
                  cls.x      : 'x',
                  cls.y      : 'y',
                  cls.z      : 'z',
                  cls.xy     : 'xy',
                  cls.xyz    : 'xyz'}
    
        if ind==None:
            return None

        #if type(ind)==int:
        try:
            return string[ind]
        except KeyError:
            raise DisplacementTestTypeError('Unknown index')
    #elif type(ind)==list or type(ind)==tuple:
    #    try:
    #        return [ string[i] for i in ind ]
    #    except KeyError:
    #        raise DisplacementTestTypeError('Unknown index')
    #else:
    #    raise DisplacementTestTypeError('Unknown type of input argument')

    @classmethod
    def get_dim(cls, ind):
        "returns dimension of test"

        dim = { cls.none:   None,
                cls.x:      1,
                cls.y:      1,
                cls.z:      1,
                cls.xy:     2,
                cls.xyz:    3}
    
        if ind == None:
            return None

        #if type(ind)==int:
        try:
            return dim[ind]
        except KeyError:
            raise DisplacementTestTypeError('Unknown index')
   # elif type(ind)==list or type(ind)==tuple:
   #     try:
   #         return [ dim[i] for i in ind ]
   #     except KeyError:
   #         raise DisplacementTestTypeError('Unknown index')
   # else:
   #     raise DisplacementTestTypeError('Unknown type of input argument')

if __name__ == "__main__":

    t = DisplacementTestType.xy
    print t
    print DisplacementTestType.get_string(t)
    print DisplacementTestType.get_dim(t)
    
    #none
    print "Type: None"
    print DisplacementTestType.none
    print DisplacementTestType.get_string(DisplacementTestType.none)
    print DisplacementTestType.get_dim(DisplacementTestType.none)
