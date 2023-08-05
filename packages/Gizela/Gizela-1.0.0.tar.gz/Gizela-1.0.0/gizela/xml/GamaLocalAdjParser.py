# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
#$Id: GamaLocalAdjParser.py 103 2010-11-29 00:06:19Z tomaskubin $

import xml.parsers.expat
from gizela.util.Error           import Error
from gizela.data.PointLocalGama  import PointLocalGama
from gizela.data.GamaCoordStatus import GamaCoordStatus
from gizela.util.Unit import Unit
from gizela.data.GamaCoordStatus import gama_coord_status_attr_adj,\
                                        gama_coord_status_attr_fix

class GamaLocalAdjParserError(Error): pass

class GamaLocalAdjParserInfoError(Error):
    'Exception for parsing break - used with type = info'
    pass

class GamaLocalAdjParser(object):
    """
    Expat parser for <gama-local-adjustment version="0.5"> document
    Tags <coordinates-summary>
         <approximate>
         <orientation-shifts>
         <original-index>
         <observations> are not readed yet
    Covariance matrix are sliced to cut off part with orientations shifts
    In tag <description> used ConfigParser to read date of epoch
    """

    def __init__(self, data, type="all"):
        '''
        data : GamaLocalDataAdj instance for data storage
        type : what type of data to read
               info - just information about adjustment 
                      (not covariance matrix and points)
               all  - everything
        '''

        # data
        self.data=data
        
        # create expat parser
        self._parser = xml.parsers.expat.ParserCreate()
        
        if type=="info":
            # handles
            self._parser.StartElementHandler = self._handle_start_element_info
            self._parser.EndElementHandler = self._handle_end_element_info
            self._parser.CharacterDataHandler = self._handle_char_data_all
            # internal data
            self._characterData=""
            self._tagName=""
            self._tagLast=""
            self._tagLLast=""

        elif type=="all":
            # handles
            self._parser.StartElementHandler = self._handle_start_element_all
            self._parser.EndElementHandler = self._handle_end_element_all
            self._parser.CharacterDataHandler = self._handle_char_data_all
            # internal data
            self._root = False # is root element present?
            self._characterData=""
            self._tagName=""
            self._tagLast=""
            self._tagLLast=""
            self._coordX=None
            self._coordY=None
            self._coordZ=None
            self._coordType=""
            #self._coordNum=0
            self._covmatrow=0 # actual row in covariance matrix
            #self._flt=[]
            #self._orientationApprox=0
            #self._orientationAdj=0
        else:
            raise GamaLocalAdjParserError("Unknown type of parser")
    
    def parse_file(self, file):
        '''parses file - file object'''
        self._parser.ParseFile(file)
    
    def parse_string(self, str):
        '''parses string'''
        self._parser.Parse(str)

    def _handle_start_element_all(self, name, attrs):
        '''start element handler for method all'''

        if not self._root:
            if name == "gama-local-adjustment":
                self._root = True
            else:
                raise GamaLocalAdjParserError, "<gama-local-adjustment> root element not found"

        self._tagLLast=self._tagLast
        self._tagLast=self._tagName
        self._tagName=name

        # save attributes
        if attrs:
            for aname, val in attrs.items():
                # parameters
                if aname=="epoch":
                    self.data.param[aname] = val
                elif aname=="axes-xy":
                    self.data.param[aname] = val
                    #self.data.coordSystemLocal.axesOri = val
                elif aname=="angles":
                    self.data.param[aname] = val
                    #self.data.coordSystemLocal.bearingOri = val
                elif aname=="gama-local-version" or\
                     aname=="gama-local-algorithm" or\
                     aname=="gama-local-compiler":
                    self.data.gamaLocal[aname] = val
                elif aname=="version":
                    self.data.gamaLocal["gama-local-adjustment-version"] = val

    def _handle_end_element_all(self, name):
        '''end element handler for method all'''

        if name=="description":
            self.data.description=self._characterData.strip()
            
        elif name=="id":
            self._id=self._characterData.strip()

        elif name=="x":
            self._coordX=float(self._characterData)
            self._coordType += name
            #if self._tagLLast == "fixed":
            #    self._coordType |= GamaCoordStatus.fix_x
            #else: # "adjusted"
            #    self._coordType |= GamaCoordStatus.adj_x

        elif name=="X":
            self._coordX=float(self._characterData)
            self._coordType += name
            #if self._tagLLast == "fixed":
            #    self._coordType |= GamaCoordStatus.fix_x
            #else: # "adjusted"
            #    self._coordType |= GamaCoordStatus.adj_X

        elif name=="y":
            self._coordY=float(self._characterData)
            self._coordType += name
            #if self._tagLLast == "fixed":
            #    self._coordType |= GamaCoordStatus.fix_y
            #else: # "adjusted"
            #    self._coordType |= GamaCoordStatus.adj_y

        elif name=="Y":
            self._coordY=float(self._characterData)
            self._coordType += name
            #if self._tagLLast == "fixed":
            #    self._coordType |= GamaCoordStatus.fix_y
            #else: # "adjusted"
            #    self._coordType |= GamaCoordStatus.adj_Y

        elif name=="z":
            self._coordZ=float(self._characterData)
            self._coordType += name
            #if self._tagLLast == "fixed":
            #    self._coordType |= GamaCoordStatus.fix_z
            #else: # "adjusted"
            #    self._coordType |= GamaCoordStatus.adj_z

        elif name=="Z":
            self._coordZ=float(self._characterData)
            self._coordType += name
            #if self._tagLLast == "fixed":
            #    self._coordType |= GamaCoordStatus.fix_z
            #else: # "adjusted"
            #    self._coordType |= GamaCoordStatus.adj_Z

        elif name=="point":
            # add point to PointDict

            point=PointLocalGama(id=self._id, 
                                  x=self._coordX, 
                                  y=self._coordY, 
                                  z=self._coordZ)

            if self._tagLast=="adjusted":
                point.status = gama_coord_status_attr_adj(self._coordType)
                # adds point with covmat
                index = [None, None, None] # rows in covmat
                if self._coordX != None: 
                    index[0] = self._covmatrow
                    self._covmatrow += 1
                if self._coordY != None: 
                    index[1] = self._covmatrow
                    self._covmatrow += 1
                if self._coordZ != None: 
                    index[2] = self._covmatrow
                    self._covmatrow += 1
                point.index = index
                self.data.pointListAdjCovMat.add_point(point)
            
            #elif self._tagLast=="approximate":
            #    # adds point without covmat 
            #    point.texttable = text_table_coor()
            #    self.data["pointApp"].add_point(point)
            #
            elif self._tagLast=="fixed":
                point.status = gama_coord_status_attr_fix(self._coordType)
                # adds point without covmat 
                self.data.pointListFix.add_point(point)

            # erase data
            self._coordX, self._coordY, self._coordZ = None, None, None
            self._coordType, self._coordNum = "", 0

        # orientation shifts
        #elif name=="approx": pass
            #self._orientationApprox=float(self._characterData)
        #elif name=="adj": pass
            #self._orientationAdj=float(self._characterData)
        #elif name=="orientation": pass
            # add orientation shift as point with status ori
            # approx "approximate" 
            # adj    "adjusted"
            
            #self.data["approximate"].add_ori_with_index(self._id, self._orientationApprox)
            #self.data["adjusted"   ].add_ori_with_index(self._id, self._orientationAdj)
        
        # stdev
        elif name=="apriori":
            self.data.pointListAdjCovMat.covmat.apriori = float(self._characterData)
        
        elif name=="aposteriori":
            self.data.pointListAdjCovMat.covmat.aposteriori = float(self._characterData)
        
        elif name=="used":
            self._characterData = self._characterData.strip()
            if self._characterData == "apriori":
                self.data.pointListAdjCovMat.covmat.useApriori = True
            elif self._characterData == "aposteriori":
                self.data.pointListAdjCovMat.covmat.useApriori = False
            else:
                print "*%s*" % self._characterData
                raise GamaLocalAdjParserError, "unknown data in tag <used>"

        elif name=="probability":
            self.data.stdev["probability"] = float(self._characterData)
        
        elif name=="degrees-of-freedom":
            self.data.stdev["df"] = int(self._characterData)
        
        # project equations
        elif name=="equations" or\
             name=="unknowns" or\
             name=="defect": 
            self.data.projEqn[name] = int(self._characterData)
        elif name=="sum-of-squares":
            self.data.projEqn[name] = float(self._characterData)
        
        # observation summary
        elif name=="distances" or\
             name=="directions" or\
             name=="angles" or\
             name=="xyz-coords" or\
             name=="h-diffs" or\
             name=="z-angles" or\
             name=="s-dists" or\
             name=="vectors":
            self.data.obsSummary[name] = int(self._characterData)
        
        # dim and band of covariance matrix
        elif name=="dim":
            self.data.pointListAdjCovMat.covmat.dim = int(self._characterData)
        elif name=="band":
            self.data.pointListAdjCovMat.covmat.band = int(self._characterData)

        # covariance matrix float numbers
        elif name=="flt":
            self.data.pointListAdjCovMat.covmat.append_value(\
                                float(self._characterData)/(Unit.distStdev**2))

        # cut of orientation shifts in covariance matrix
        elif name=="cov-mat":
            self.data.pointListAdjCovMat.covmat.slice(self.data.pointListAdjCovMat.get_num_coord())
        
            #for p in self.data.pointListAdjCovMat:
            #    print p.id, ">", p.index
            #    print p.id, "vc", p.var, p.cov
        
        self._characterData=""
        self._tagName=self._tagLast
        self._tagLast=self._tagLLast

    def _handle_char_data_all(self, data):
        '''character data handler for method all and info'''
        self._characterData+=data
    
    def _handle_start_element_info(self, name, attrs):
        '''start element handler for method info'''

        if name=="coordinates":
            # exit parser
            raise GamaLocalAdjParserInfoError() 

        self._tagLLast=self._tagLast
        self._tagLast=self._tagName
        self._tagName=name

        # save attributes
        if attrs:
            for key, val in attrs.items():
                self.data[name + "-" + key]=val
    
    def _handle_end_element_info(self, name):
        '''end element handler for method info'''

        if name=="description":
            self.data.description = self._characterData.strip()
        
        # float values
        elif name=="sum-of-squares" or\
             name=="apriori" or\
             name=="aposteriori" or\
             name=="probability" or\
             name=="ratio" or\
             name=="lower" or\
             name=="upper":
            self.data[self._tagLast + "-" + name]=float(self._characterData)
        
        # integer values
        elif name=="count-xyz" or\
             name=="count-xy" or\
             name=="count-z" or\
             name=="distances" or\
             name=="directions" or\
             name=="angles" or\
             name=="xyz-coords" or\
             name=="h-diffs" or\
             name=="z-angles" or\
             name=="s-dists" or\
             name=="vectors" or\
             name=="equations" or\
             name=="unknowns" or\
             name=="degrees-of-freedom" or\
             name=="defect" :
            self.data[self._tagLast + "-" + name]=int(self._characterData)
        
        # float values
        elif name=="sum-of-squares" or\
             name=="apriori" or\
             name=="aposteriori" or\
             name=="probability" or\
             name=="ratio" or\
             name=="lower" or\
             name=="upper" or\
             name=="confidence-scale":
            self.data[self._tagLast + "-" + name]=float(self._characterData)
        
        # string values
        elif name=="used":
            self.data[self._tagLast + "-" + name]=self._characterData.strip()

        elif name=="connected-network":
            self.data[self._tagLast + "-" + name]=True
        
        elif name=="disconnected-network":
            self.data[self._tagLast + "-connected-network"]=False
        
        elif name=="passed":
            self.data[self._tagLast + "-" + name]=True
        
        elif name=="failed":
            self.data[self._tagLast + "-passed"]=False

        self._characterData=""
        self._tagName=self._tagLast
        self._tagLast=self._tagLLast



if __name__=="__main__":

    print "see gizela.data.GamaLocalDataAdj.py for example"

