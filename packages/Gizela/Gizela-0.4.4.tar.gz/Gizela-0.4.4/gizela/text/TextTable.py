# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: TextTable.py 68 2010-08-19 09:42:00Z tomaskubin $

'''
class TextTable:    makes text tables

'''

from gizela.util.Error import Error


class TextTableError(Error):
    '''Exception for class TextTable'''
    pass

class TextTable(object):
    '''Makes formatted text table
    '''

    __slots__ = ["_label", "_format", "width", "_rowdatafun",
            "_type",
            "corner_left",
            "corner_right",
            "corner_middle",
            "border_left",
            "border_right",
            "border_middle",
            "line_top",
            "line_second",
            "line_bottom",
            "header"]

    def _get_type(self): return self._type
    def _set_type(self, type):
        ''' sets type of table borders and headers '''

        if type=="border":
            '''+------+------+
               | lab1 | lab2 |
               +------+------+
               | val1 | val2 |
               | val1 | val2 |
               +------+------+
            '''
            self.corner_left=   "+-"
            self.corner_right= "-+"
            self.corner_middle="-+-"
            self.border_left=   "| "
            self.border_right= " |"
            self.border_middle=" | "
            self.line_top="-"
            self.line_second="-"
            self.line_bottom="-"
            self.header=True
        elif type=="plain":
            ''' lab1 | lab2 
               ------+------
                val1 | val2
                val1 | val2
            '''
            self.corner_left=  "-"
            self.corner_right= "-"
            self.corner_middle="-+-"
            self.border_left=  " "
            self.border_right= " "
            self.border_middle=" | "
            self.line_top=None
            self.line_second="-"
            self.line_bottom=None
            self.header=True
        elif type=="noborder":
            ''' lab1   lab2 
               ------+------
                val1   val2
                val1   val2
            '''
            self.corner_left=   " "
            self.corner_right=  " "
            self.corner_middle= "-+-"
            self.border_left=   " "
            self.border_right=  " "
            self.border_middle= "   "
            self.line_top=None
            self.line_second="-"
            self.line_bottom=None
            self.header=True
        elif type=="noheadings":
            ''' val1  val2
                val1  val2
            '''
            self.corner_left=   " "
            self.corner_right=  " "
            self.corner_middle= "  "
            self.border_left=   " "
            self.border_right=  " "
            self.border_middle= "  "
            self.line_top=None
            self.line_second=None
            self.line_bottom=None
            self.header=False
        else:
            raise TextTableError("Unknown type")
        self._type = type

    type = property(_get_type, _set_type)

    def _get_rowdatafun(self): return self._rowdatafun
    def _set_rowdatafun(self, rowdatafun):
        if len(self._label) == len(rowdatafun):
            self._rowdatafun = rowdatafun
        else:
            raise TextTableError, "The Number of labels does not equal to number of rowdatafun functions (%i!=%i)" % \
                    (len(self._label), len(rowdatafun))

    rowdatafun = property(_get_rowdatafun, _set_rowdatafun)

    def __init__(self, labform, rowdatafun=None, type="border"):
        '''labform ... labels and formats of columns [ ("label","%10.3f"),...]
        rowDataFun ... list of functions for getting values from data row
        type ... type of table border and headings
        '''

        self._label=[] # column labels
        self._format=[] # column formats
        self.width=[] # width of column

        self.type = type
        
        self.insert_col(0, labform)
        
        if rowdatafun:
            self.rowdatafun = rowdatafun
        else: # implicit functions
            self.set_default_rowdatafun()
            self._rowdatafun = [eval("lambda x: x[%i]" % i)\
                    for i in xrange(len(self._label))]
        

    def get_num_of_col(self):
        return len(self._label)

    def set_default_rowdatafun(self):
        self._rowdatafun = [eval("lambda x: x[%i]" % i)\
                    for i in xrange(len(self._label))]

    def insert_col(self, index, labform):
        "insert labform before index"

        # add labels and format strings
        labform.reverse()
        for lab, form in labform:
            try:
                self._label.insert(index,lab)
                self._format.insert(index,form)
            except IndexError:
                raise TextTableError, "Index out of range"
            try:
                lenform = len(form % 0)
            except ValueError:
                raise TextTableError("Bad format %s" % form)
            # add width
            self.width.insert(index, len(lab) > lenform and len(lab) or lenform)

    def append_col(self, labform):
        """
        append columns (label and format tuples)
        to the end of table
        """
        self.insert_col(len(self._label), labform)
        self.set_default_rowdatafun()


    def make_table_head(self):
        ''' makes table head '''

        str=""
        
        # 1st line
        if self.line_top!=None:
            str += self.corner_left + \
                self.corner_middle.join([self.line_top*width for width in self.width]) + \
                self.corner_right
        # 2nd line - header
        if self.header:
            str += "\n" + \
                self.border_left + \
                self.border_middle.join(["%*s" % (width, label) \
                    for width,label in zip(self.width,self._label)]) + \
                self.border_right

        # 3rd line
        if self.line_second!=None and self.header:
            str += "\n" + \
                self.corner_left + \
                self.corner_middle.join([self.line_second*width \
                    for width in self.width]) + \
                self.corner_right
        return str

    def make_table_foot(self):
        ''' makes table label and borders '''
        
        str=""
        
        # bottom line
        if self.line_bottom!=None:
            str += '\n' + \
                self.corner_left + \
                self.corner_middle.join([self.line_bottom*width \
                    for width in self.width]) + \
                self.corner_right
        return str


    def make_table_row(self, *data):
        """
        makes just one row of table
        data can be list of any length
        """
        
        if len(data)==1:
            if type(data[0]) == list or type(data[0]) == tuple:
                data=data[0]
        
        #if len(data) < len(self._label):
        #    raise TextTableError("Size of data < number of columns (%i<%i)" \
        #        % (len(data), len(self._label)))
        
        # make data of row

        if len(self._rowdatafun) != len(self._label):
            print self
            raise TextTableError, "rowdatafun does not corresponds to columns"

        datalen = len(data)
        if datalen > len(self._label): datalen = len(self._label)

        data_row = [] # formated data by _rowdatafun
        data_row_str = [] # string data
        for i in xrange(datalen):
            # format data by _rowdatafun
            try:
                data_row.append(self._rowdatafun[i](data))
            except Exception, e:
                print "Data: ", data
                print "Index: ", i
                print self
                raise TextTableError, "rowdatafunction call crashed: %s" % e

        #format by _format
        for i in xrange(len(self._label)):
            try:
                value = data_row[i]
                if value == None:
                    raise IndexError

                try:
                    data_row_str.append(self._format[i] % value)
                except TypeError:
                    print self
                    print data
                    raise TextTableError, 'index %i: value "%s" of type %s cannot be formatted by "%s"' % (i, value, type(value), self._format[i])
            except IndexError:
                data_row_str.append(" "*self.width[i])


        return "\n" +\
            self.border_left +\
            self.border_middle.join(data_row_str) +\
            self.border_right

    def __str__(self):
        return "\n".join(["TextTable instance:",\
                "\tNumber of columns: %i" % len(self._label),\
                "\tNumber of datarowfun: %i" % len(self._rowdatafun),\
                "\tLabels: " + " ".join('"%s"' % lab for lab in self._label)] )

    #def make_table_rows_by_columns(self, *data):
    #    ''' makes rows from data formed by columns 
    #    *data can by list of lists of data (or tuple)
    #    or each column vectors set separately
    #    '''
    #    
    #    str=""
    #    
    #    # data
    #    if len(data) == 1: # list of lists
    #        data=data[0]
    #    
    #    if isinstance(data[0],tuple) or isinstance(data[0],list):
    #        for ind in range(len(data[0])):
    #            row = [col[ind] for col in data]
    #            str += self.make_table_row(row)
    #    else: # just one row
    #        str = self.make_table_row(data)
    #    return str
    #
    #def make_table_rows_by_rows(self, *data):
    #    ''' makes rows from data formed by rows 
    #    *data can by list of lists of data (or tuple)
    #    or each column vectors set separately
    #    '''
    #    
    #    str=""
    #    
    #    # data
    #    if len(data) == 1: # list of lists
    #        data=data[0]
    #    
    #    if isinstance(data[0],tuple) or isinstance(data[0],list):
    #        for row in data:
    #            str += self.make_table_row(row)
    #    else: # just one row
    #        str = self.make_table_row(data)
    #    return str
        #
    #def make_table_by_columns(self, *data):
    #    ''' make whole table from data set by columns 
    #    data can by list of lists (or tuple)
    #    or each column vectors set separately
    #    '''
    #    if len(data) == 1: # list of lists
    #        data=data[0]
    #    
    #    str=""
    #    str += self.make_table_head()
    #    str += self.make_table_rows_by_columns(data)
    #    str += self.make_table_foot()
    #    return str
        #
    #def make_table_by_rows(self, *data):
    #    ''' make whole table from data set by rows
    #    data can by list of lists (or tuple)
    #    or each column vectors set separately
    #    '''
    #    if len(data) == 1: # list of lists
    #        data=data[0]
    #    
    #    str=""
    #    str += self.make_table_head()
    #    str += self.make_table_rows_by_rows(data)
    #    str += self.make_table_foot()
    #    return str


if __name__=="__main__":
    
    tab=TextTable([("id","%-10s"), ("dx","%5.1f")])
    print tab.make_table_head()
    print tab.make_table_row("a", 2.2)
    print tab.make_table_row("a")
    print tab.make_table_row("a", 2.2, 10.0)
    print tab.make_table_foot()

    # insert column
    tab.insert_col(2, [("dy", "%6.2f"), ("dz", "%6.2f")])
    #print tab.make_table_row("a", 2.2, 10.0)
    
    # rowdatafun
    from math import sqrt
    tab.rowdatafun = [lambda x: x[0], lambda x:sqrt(x[1]), lambda x:x[1]*x[2], lambda x:x[3]]
    print tab.make_table_head()
    print tab.make_table_row(["a", 2.2, 10.0, 20.0])
    print tab.make_table_row(("a", 2.2, 10.0))
    print tab.make_table_row(("a", 2.2, 10.0, 20.0, 30.0))
    print tab.make_table_foot()
    
