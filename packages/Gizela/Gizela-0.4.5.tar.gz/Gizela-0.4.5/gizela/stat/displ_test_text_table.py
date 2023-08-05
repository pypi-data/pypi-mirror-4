# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: displ_test_text_table.py 103 2010-11-29 00:06:19Z tomaskubin $

"""
text tables for class with displacements and test results
"""

from gizela.text.TextTable       import TextTable


def displ_text_table():
    """
    text table for PointDisplBase instance
    """
    return TextTable([("id","%12s"),
            ("dx","%7.4f"),
            ("dy","%7.4f"),
            ("dz","%7.4f"),
            ("vdx","%6.4f"),
            ("vdy","%6.4f"),
            ("vdz","%6.4f")])

def test_text_table():
    """
    text table for TestResult instance
    """
    return TextTable([("stat","%10.3e"),
            ("p-val","%5.1f"),
            ("reliab","%6.1f"),
            ("type","%4s"),
            ("dim","%3i"),
            ("result","%6s")])

# PointLocalGamaDisplTest data order:
#
#           0  1  2  3       4   5   6   7   8   9  10   11   12   13
#    data: id, x, y, z, status, vx, vy, vz, dx, dy, dz, vdx, vdy, vdz,
#                14          15          16               17        18       19
#          testStat, testPassed, testPValue, testReliability, testType, testDim

def point_test_table():
    """
    text table for PointLocalGamaDisplTest instance
    with test results only
    """
    fun = [lambda x:x[0],
           lambda x:x[14], lambda x:x[16], lambda x:x[17], lambda x:x[18],
           lambda x:x[19], lambda x:x[15]]
    return TextTable([("id","%12s"),
                      ("stat","%10.3e"),
                      ("p-val","%5.1f"),
                      ("reliab","%6.1f"),
                      ("type","%4s"),
                      ("dim","%3i"),
                      ("result","%6s")],rowdatafun=fun)

def point_displ_text_table():
    """
    text table for PointLocalGamaDisplTest instance
    with displacements only
    """
    from math import sqrt

    fun = [lambda x:x[0],
           lambda x:x[8], lambda x:x[9], lambda x:x[10], 
           lambda x:(x[8]==None and [None] or [sqrt(x[8]**2 + x[9]**2)])[0],
           lambda x:((x[8]==None or x[10]==None) and [None] or \
                     [sqrt(x[8]**2 + x[9]**2 + x[10]**2)])[0],
           lambda x:(x[11]==None and [None] or [sqrt(x[11])])[0],
           lambda x:(x[12]==None and [None] or [sqrt(x[12])])[0],
           lambda x:(x[13]==None and [None] or [sqrt(x[13])])[0]]
    return TextTable([("id","%12s"),
            ("dx","%7.4f"),
            ("dy","%7.4f"),
            ("dz","%7.4f"),
            ("dxy","%7.4f"),
            ("dxyz","%7.4f"),
            ("sdx","%6.4f"),
            ("sdy","%6.4f"),
            ("sdz","%6.4f")], rowdatafun=fun)


def displ_test_text_table():
    """
    text table for PointLocalGamaDisplTest class
    with displacements and some test results
    """

    from math import sqrt

    def get_passed(x):
        if x is None:
            return ""
        elif x:
            return "passed"
        else:
            return "failed"

    fun = [lambda x:x[0],
           lambda x:x[8], lambda x:x[9], lambda x:x[10], 
           lambda x:(x[11]==None and [None] or [sqrt(x[11])])[0],
           lambda x:(x[12]==None and [None] or [sqrt(x[12])])[0],
           lambda x:(x[13]==None and [None] or [sqrt(x[13])])[0],
           lambda x:x[18], lambda x:x[16],
           lambda x:x[14],
           lambda x:get_passed(x[15])]
    
    return TextTable([("id","%12s"),
            ("dx","%7.4f"),
            ("dy","%7.4f"),
            ("dz","%7.4f"),
            ("sdx","%6.4f"),
            ("sdy","%6.4f"),
            ("sdz","%6.4f"),
            ("type","%4s"),
            ("pval","%4.2f"),
            ("stat","%9.2e"),
            ("test","%6s")],
                    rowdatafun=fun)

