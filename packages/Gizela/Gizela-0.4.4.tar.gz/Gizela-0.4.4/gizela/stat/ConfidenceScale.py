# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.Error import Error

class ConfidenceScaleError(Error): pass

class ConfidenceScale(object):
    """
    class with methods for computing 
    confidence scales of confidence regions/intervals
    """

    @staticmethod
    def get_scale(confProb, apriori, dim, df=0):
        """
        returns confidence scale for
        apriori: True/False: apriori/aposteriori standard deviation
        dimension dim
        df: degrees of freedom
        """

        if apriori:
            # for apriori standard deviations
            from scipy.stats import chi2
            from math import sqrt

            return sqrt(chi2.ppf(confProb, dim))
        else:
            if df == 0:
                raise ConfidenceScaleError, "Zero degrees of freedom"

            # for aposteriori standard deviations
            from scipy.stats import f
            from math import sqrt

            return sqrt(dim*f.ppf(confProb, dim, df))


if __name__ == "__main__":

    print ConfidenceScale.get_scale(0.95, apriori=True, dim=1)
    print ConfidenceScale.get_scale(0.95, apriori=False, dim=1, df=1000)
    print ConfidenceScale.get_scale(0.95, apriori=True, dim=2)
    print ConfidenceScale.get_scale(0.95, apriori=False, dim=2, df=1000)
