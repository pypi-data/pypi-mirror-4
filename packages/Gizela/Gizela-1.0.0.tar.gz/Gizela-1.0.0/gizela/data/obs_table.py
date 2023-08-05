# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: obs_table.py 57 2010-07-22 18:01:42Z kubin $


from gizela.text.TextTable import TextTable

def obs_none_table():
    return TextTable([("Table not set","%s")])

def obs_height_diff_table():
    return TextTable(
        [("type","%4s"),
         ("from","%12s"),
         ("to","%12s"),
         ("value","%10.5f"),
         ("dist","%4.0f"),
         ("stdev","%7.5f")],
         type="plain")

def obs_cluster_table():
    return TextTable(
        [("type","%10s"),
         ("from","%12s"),
         ("to","%12s"),
         ("from dh","%7.4f"),
         ("to dh","%7.4f"),
         ("value", "%10.5f"),
         ("stdev", "%7.5f")],
         type="plain")


def obs_vector_table():
    return TextTable(
        [("type","%4s"),
         ("from","%12s"),
         ("to","%12s"),
         ("dx","%10.3f"),
         ("dy","%10.3f"),
         ("dz","%10.3f")],
         type="plain")
    
def obs_vector_stdev_table():

    from math import sqrt
    
    fun = [lambda x:x[0], lambda x:x[1], 
           lambda x:x[2], lambda x:x[3], 
           lambda x:x[4], lambda x:x[5],
           lambda x:(x[6]==None and [None] or [sqrt(x[6])])[0],
           lambda x:(x[7]==None and [None] or [sqrt(x[7])])[0],
           lambda x:(x[8]==None and [None] or [sqrt(x[8])])[0]]
    
    return TextTable(
        [("type","%4s"),
         ("from","%12s"),
         ("to","%12s"),
         ("dx","%10.3f"),
         ("dy","%10.3f"),
         ("dz","%10.3f"),
         ("s_dx","%6.4f"),
         ("s_dy","%6.4f"),
         ("s_dz","%6.4f")],
         rowdatafun=fun, type="plain")

