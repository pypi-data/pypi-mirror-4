# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: point_text_table.py 73 2010-09-23 18:24:53Z tomaskubin $


from gizela.text.TextTable import TextTable

# text tables for PointGeodetic

def geo_coor_table():
    return TextTable(\
        [("id","%12s"),\
         ("lat (deg)","%13.9f"),\
         ("lon (deg)","%14.9f"),\
         ("height (m)","%8.3f")],\
         type="plain")

# text tables for PointCart* points

def coor_table():
    return TextTable(\
        [("id","%12s"),\
         ("x","%11.3f"),\
         ("y","%11.3f"),\
         ("z","%11.3f")],\
         type="plain")
    
def coor_var_table():
    return TextTable(\
        [("id","%12s"),\
         ("x","%11.3f"),\
         ("y","%11.3f"),\
         ("z","%11.3f"),\
         ("var_x","%6.4f"),\
         ("var_y","%6.4f"),\
         ("var_z","%6.4f")],\
         type="plain")

def coor_cov_table():
    """return output text table - variances and covariances"""
    return TextTable(\
        [("id","%12s"),\
         ("x","%11.3f"),\
         ("y","%11.3f"),\
         ("z","%11.3f"),\
         ("var_x","%6.4f"),\
         ("var_y","%6.4f"),\
         ("var_z","%6.4f"),\
         ("cov_xy","%7.4f"),\
         ("cov_xz","%7.4f"),\
         ("cov_yz","%7.4f")],\
         type="plain")

def coor_stdev_table():
    """returns output text table - standard deviations = sqrt(var)"""
    
    from math import sqrt
    
    fun = [ lambda x:x[0], lambda x:x[1], lambda x:x[2], lambda x:x[3],\
        lambda x:sqrt(x[4]), lambda x:sqrt(x[5]), lambda x:sqrt(x[6]) ]
    
    return TextTable(\
        [("id","%12s"),\
         ("x","%11.3f"),\
         ("y","%11.3f"),\
         ("z","%11.3f"),\
         ("s_x","%6.4f"),\
         ("s_y","%6.4f"),\
         ("s_z","%6.4f")],\
         rowdatafun=fun, type="plain")


# text tables for PointLocalGama

def gama_coor_table():
    tt = coor_table()
    tt.insert_col(4, [("status","%8s")])
    tt.set_default_rowdatafun()
    return tt

def gama_coor_var_table():
    """returns output text table - coordinates and sqrt of variances"""
    
    tt = coor_var_table()
    tt.insert_col(4, [("status","%8s")])
    tt.set_default_rowdatafun()
    return tt

def gama_coor_cov_table():
    """returns output text table - variances and covariances"""
    
    tt = coor_cov_table()
    tt.insert_col(4, [("status","%8s")])
    tt.set_default_rowdatafun()
    return tt

def gama_coor_stdev_table():
    """returns output text table - standard deviations = sqrt(var)"""
    
    tt = coor_stdev_table()
    tt.insert_col(4, [("status","%8s")])
    
    from math import sqrt
    
    rdf = tt.rowdatafun
    rdf[4:] = (lambda x: x[4],
               lambda x:(x[5]==None and [None] or [sqrt(x[5])])[0],
               lambda x:(x[6]==None and [None] or [sqrt(x[6])])[0])
    rdf.append(lambda x:(x[7]==None and [None] or [sqrt(x[7])])[0])
    tt.rowdatafun = rdf
    
    return tt
