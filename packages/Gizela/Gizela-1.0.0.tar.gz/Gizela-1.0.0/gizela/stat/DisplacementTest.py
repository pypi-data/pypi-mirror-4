# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.Error import Error
from gizela.stat.DisplacementTestType import DisplacementTestType
from gizela.stat.PointLocalGamaDisplTest import PointLocalGamaDisplTest


class DisplacementTestError(Error): pass


class DisplacementTest(object):
    """
    class for testing of displacements
    """

    def __init__(self, apriori=True, confProb = 0.95, reliabProb = 0.95):
        """
        apriori: apriori test? True=apriori, False=aposteriori
        confProb: confidence probability 0-1
        confProb: confidence probability 0-1
        reliabProb: power of test - reliability 0-1
        """

        self.apriori = apriori
        self.confProb = confProb
        self.reliabProb = reliabProb
        self.detTol = 1e-15 
            # singularity of covariance matrix - numeric tolerance


    def compute_test(self, epochPointList, pointId=None,
                     testType=None):
        """
        epochPointList: epochPointList instance
        pointId: iterable object of point ids
        testType: DisplacementTestType instance : test types xyz, xy, z
        """
        
        if pointId is None:
            pointId = epochPointList.iter_id()

        for id in pointId:
    	    #import sys
	    #print >>sys.stderr, ">> TEST Point: %s" % id

            for point in epochPointList.iter_point(id, withNone=False):
		#import sys
		#print >>sys.stderr, ">> Epoch %i:" % point.epochIndex

                if not isinstance(point, PointLocalGamaDisplTest):
                    import sys
                    print >>sys.stderr, "Wrong type '%s' of point '%s'" \
                            % (type(point), point.id)
                    continue

                if testType is None:
                    if point.is_set_xyz() and point.displ.is_set_xyz():
                        point.testType = DisplacementTestType.xyz
                        self._make_test(point)
                    
                    elif point.is_set_xy() and point.displ.is_set_xy():
                        point.testType = DisplacementTestType.xy
                        self._make_test(point)
                   
                    elif point.is_set_z() and point.displ.is_set_z():
                        point.testType = DisplacementTestType.z
                        self._make_test(point)
                   
                    else:
                        pass
                        #import sys
                        #print >>sys.stderr, "Point id='%s' is not tested" % id

                else:
                    if testType is DisplacementTestType.xyz and\
                            point.is_set_xyz() and\
                            point.displ.is_set_xyz():
                        point.testType = DisplacementTestType.xyz
                        self._make_test(point)

                    elif testType is DisplacementTestType.xy and\
                            point.is_set_xy() and\
                            point.displ.is_set_xy():
                        point.testType = DisplacementTestType.xy
                        self._make_test(point)

                    elif testType is DisplacementTestType.z and\
                            point.is_set_z() and\
                            point.displ.is_set_z():
                        point.testType = DisplacementTestType.z
                        self._make_test(point)
                    else:
			pass
                        #import sys
                        #print >>sys.stderr, "is point set xy:",\
                        #    point.is_set_xy()
                        #print >>sys.stderr, "is displ. set xy:",\
                        #    point.displ.is_set_xy()
                        #print >>sys.stderr, point
			#print >>sys.stderr, point.displ
                        #print >>sys.stderr, \
                        #    "Point id='%s' epoch=%s not tested with test %s" % \
                        #        (id, 
                        #         point.epochIndex,
                        #         DisplacementTestType.get_string(testType)) 


    def _compute_test_stat(self, point):
        """
        computes test statistic
        todo: test for aporiori covariance matrix
        """
        if point.testType is DisplacementTestType.z:
            if not point.displ.covmat.useApriori:
                point.displ.covmat.useApriori = True
                varz = point.displ.varz
                point.displ.covmat.useApriori = False
            else:
                varz = point.displ.varz

            dz = point.displ.z
            point.testStat = dz*dz/varz
        
        elif point.testType is DisplacementTestType.xy:
            # standard deviations
            if not point.displ.covmat.useApriori:
                point.displ.covmat.useApriori = True
                var = point.displ.var
                cov = point.displ.cov
                varz = point.displ.varz
                point.displ.covmat.useApriori = False
            else:
                var = point.displ.var
                cov = point.displ.cov

            sxx = var[0]
            syy = var[1]
            sxy = cov[0]

            det = sxx*syy - sxy*sxy # determinant

   	    #import sys
	    #print >>sys.stderr, 'Test xy: Point "%s" in epoch %i' % (point.id, point.epochIndex)
	    #print >>sys.stderr, "    var: %f %f, cov: %f" % (point.displ.var[0], point.displ.var[1], point.displ.cov[0])
            if abs(det) < self.detTol:
                import sys
                print >>sys.stderr, 'Test xy: Point "%s" in epoch %i not tested. Covariance matrix close to singular. Det = %.5e' % (point.id, point.epochIndex, det)
		print >>sys.stderr, "    var: %f %f, cov: %f" % (point.displ.var[0], point.displ.var[1], point.displ.cov[0])
                return

            dx = point.displ.x # x displacement
            dy = point.displ.y # y displacement
            point.testStat = (dx*dx*syy - 2*dx*dy*sxy + dy*dy*sxx)/det
            #print point.id, ":t_xy:", var, cov, det 

        elif point.testType is DisplacementTestType.xyz:
            if not point.displ.covmat.useApriori:
                point.displ.covmat.useApriori = True
                var = point.displ.var
                cov = point.displ.cov
                varz = point.displ.varz
                point.displ.covmat.useApriori = False
            else:
                var = point.displ.var
                cov = point.displ.cov

            sxx = var[0]
            syy = var[1]
            szz = var[2]
            sxy = cov[0]
            sxz = cov[1]
            syz = cov[2]

            dx = point.displ.x
            dy = point.displ.y
            dz = point.displ.z

            det = 2*sxy*sxz*syz - szz*sxy*sxy - syy*sxz*sxz \
                  - sxx*syz*syz + sxx*syy*szz # determinant

            if abs(det) < self.detTol:
                import sys
                print >>sys.stderr, "Test xyz: Point id='%s'" % point.id, \
                        "not tested. Covariance matrix close to singular."
                return

            point.testStat = (    dx*dx*syy*szz -   dx*dx*syz*syz \
                              - 2*dx*dy*sxy*szz + 2*dx*dy*sxz*syz \
                              + 2*dx*dz*sxy*syz - 2*dx*dz*sxz*syy \
                              -   dy*dy*sxz*sxz +   dy*dy*sxx*szz \
                              + 2*dy*dz*sxy*sxz - 2*dy*dz*sxx*syz \
                              -   dz*dz*sxy*sxy +   dz*dz*sxx*syy ) / det 
            #print point.id, ":t_xyz:", var, cov, det 

        else:
            raise DisplacementTestError, "Test %s not supported" %\
                            point.testType.get_string()

    def _compute_pvalue(self, point):
        'computes p-value for dimension dim and test self.apriori=True/False'
        if self.apriori:
            from scipy.stats import chi2
            point.testPValue = float(chi2.cdf(point.testStat,
                                              DisplacementTestType.get_dim(point.testType)))
            #print point.testStat
            #print point.id, ": test:",\
            #DisplacementTestType.get_string(point.testType), ": dim:",\
            #DisplacementTestType.get_dim(point.testType)

        else: # aposteriori
            point.testPValue = 1 # not implemented

    def _compute_reliability(self, point):
        'computes reliability ratio for the test'
        #point.testReliability =
        pass

    def _make_test(self, point):
        self._compute_test_stat(point)
        if point.testStat is not None:
            self._compute_pvalue(point)
            self._compute_reliability(point)
            if point.testPValue > self.confProb:
                point.testPassed = False
            else:
                point.testPassed = True

