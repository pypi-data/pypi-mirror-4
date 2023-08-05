# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: CompareObs.py 73 2010-09-23 18:24:53Z tomaskubin $

from gizela.util.Error              import Error
from gizela.text.TextTable          import TextTable
from gizela.data.ObsClusterList     import ObsClusterList
from gizela.data.ObsClusterVector   import ObsClusterVector
from gizela.data.ObsVector          import ObsVector
from gizela.data.CovMat             import CovMat


class CompareObsError(Error): pass


class CompareObs(object):
    """
    compares measured data
    """

    def __init__(self, data1, data2, revers=True):
        """
        data1, data2: observation data - GamaLocalDataObs instance
        revers: handle fromid_1 == toid_2 and toid_1 == fromid_2 
        """

        self.data1 = data1
        self.data2 = data2
        
        self.revers = revers

        self.compObsClList = ObsClusterList() # list of differences from comparison
        
        # data 1
        self.meanList1 = None # list of means 
        self.obsMeanList1 = None # list of observations for mean
        self.resList1  = None # list of residuals
        self.obsToComp1 = None # observations in cluster list to be compared
        
        # data 2
        self.meanList2 = None 
        self.obsMeanList2 = None
        self.resList2  = None
        self.obsToComp2 = None

        # make list of uncompared observations
        self.uncompObsClList1 = ObsClusterList() # cluster list with observations uncompared
        self.uncompObsClList2 = ObsClusterList()

        self._cluster = None # actual cluster


    def _mean_vector(self, data):
        "returns mean of vector with same fromid and toid"
        
        # add vectors to list
        lvec = [] # helper list of vectors
        for c in data:
            for v in c:
                lvec.append(v)

        datamean = ObsClusterList() 
        dmcluster = ObsClusterVector(covmat=CovMat(dim=0, band=2))
        datamean.append_cluster(dmcluster) 
        # list of vector means and single vectors (without mean)

        cll_mean = ObsClusterList()
        cll_obs = ObsClusterList()
        cll_res = ObsClusterList()
        
        if len(lvec) <= 1:
            return # nothink to compare
        while len(lvec) > 1:
            # find vectors with same fromid and toid
            v1 = lvec.pop()
            fromid = v1.fromid
            toid = v1.toid
            lvecm = [v1] # list of vectors for mean
            lsign = [1.0] # list of signs: for revers vectors -1.0
            for v2 in lvec:
                if v2.fromid == fromid and v2.toid == toid:
                    lvecm.append(v2)
                    lvec.remove(v2)
                    lsign.append(1.0)
                    continue
                if self.revers and\
                v2.fromid == toid and v2.toid == fromid:
                    lvecm.append(v2)
                    lvec.remove(v2)
                    lsign.append(-1.0)

            # compute mean
            if float(len(lvecm)) == 1:
                # nothink to compute
                vec = lvecm[0]
                covmat = vec.covmat
                dmcluster.append_obs(vec)
                dmcluster.covmat.extend_dim(3)
                vec.covmat = covmat
                continue

            
            from numpy import mat, mean
            
            ll = [mat([i.dx, i.dy, i.dz])*sign for i,sign in zip(lvecm,lsign)] 
            # row vectors of observ.

            #lm = mean(ll, axis=0)
            #print "Mean  0:", lm
            #print "covmat0:", lvecm[0].covmat.mat

            # compute covariance matrix 
            # covariances between vectors not handled
            
            sil = [i.covmat.mat.I for i in lvecm] 
            # covariance matrice inverses inv(Sigma)
            
            sill = [si*l.T for si,l in zip(sil,ll)]
            # product inv(Sigma)*l
            
            cmm = sum(sil).I # covariance matrix of mean
            mn = cmm * sum(sill) # mean value
            #print "Mean  1:", mn
            #print "covmat1:", cmm
        
            # append clusters 
            cl_mean = ObsClusterVector(covmat=CovMat(dim=3, band=2))
            cl_obs  = ObsClusterVector(covmat=CovMat(dim=0, band=2))
            cl_res  = ObsClusterVector(covmat=None)
            cll_mean.append_cluster(cl_mean)
            cll_obs.append_cluster(cl_obs)
            cll_res.append_cluster(cl_res)
            
            # append vector mean
            vec1 = ObsVector(fromid=lvecm[0].fromid, toid=lvecm[0].toid,
                            dx=float(mn[0]), dy=float(mn[1]), dz=float(mn[2]))
            vec2 = ObsVector(fromid=lvecm[0].fromid, toid=lvecm[0].toid,
                            dx=float(mn[0]), dy=float(mn[1]), dz=float(mn[2]))
            # vec1 == vec2
            cl_mean.append_obs(vec1)
            dmcluster.append_obs(vec2)

            # set covmat of mean
            covmat = CovMat(dim=3, band=2)
            covmat.mat = cmm
            vec1.covmat = covmat
            dmcluster.covmat.extend_dim(3)
            vec2.covmat = covmat
            
            # append observations with covmat
            for v in lvecm:
                vcovmat = v.covmat
                cl_obs.append_obs(v)
                cl_obs.covmat.extend_dim(3)
                v.covmat = vcovmat

            # append residuals
            for l,v,s in zip(ll,lvecm,lsign):
                res = (mn - l.T) * s
                vec = ObsVector(fromid=v.fromid, toid=v.toid,
                                dx=float(res[0]), 
                                dy=float(res[1]),
                                dz=float(res[2]))
                cl_res.append_obs(vec)
        
        return datamean, cll_mean, cll_obs, cll_res

    
    def _find_obs(self, obs, cl):
        """
        finds observation in cluster list
        returns found, observation, reversed
        """
        fromid = obs.fromid
        toid = obs.toid
        for c in cl:
            for o in c:
                if o.fromid == fromid and o.toid == toid:
                    return True, o, False
                if self.revers and \
                   o.fromid == toid and o.toid == fromid:
                    return True, o, True

        return False, None, False


    def compare_vector(self, mean=True, revers=True):
        """
        comparison of vectors
        
        mean: compute vector mean?
        revers: compare observations with revers id from and to?
        """
        
        self.revers =revers
        
        # find vectors in cluster list
        self.obsToComp1 = ObsClusterList() # cluster list with vectors
        self.obsToComp2 = ObsClusterList()

        for cl in self.data1.obsClusterList:
            if isinstance(cl, ObsClusterVector):
                self.obsToComp1.append_cluster(cl)
        
        for cl in self.data2.obsClusterList:
            if isinstance(cl, ObsClusterVector):
                self.obsToComp2.append_cluster(cl)
        
        if sum([len(c) for c in self.obsToComp1]) is 0:
            return
            #raise CompareObsError, "No vectors found in data #1"
        
        if sum([len(c) for c in self.obsToComp2]) is 0:
            return
            #raise CompareObsError, "No vectors found in data #2"
    
        if mean:
            self.obsToComp1, self.meanList1, self.obsMeanList1, self.resList1 =\
                self._mean_vector(self.obsToComp1)
    
            self.obsToComp2, self.meanList2, self.obsMeanList2, self.resList2 =\
                self._mean_vector(self.obsToComp2)

        # cluster for compared vectors
        # covariance matrix - initial zero dimension 
        self._cluster = ObsClusterVector(covmat=CovMat(dim=0, band=2))

        self.compObsClList.append_cluster(self._cluster)

        # find vectors with same fromid and toid and compare
        for c1 in self.obsToComp1:
            for vec1 in c1:
                found, vec2, reversed = self._find_obs(vec1, self.obsToComp2)
                if found:
                        self._cmp_vector(vec1, vec2, reversed=reversed)

        # find uncompared vectors
        self._uncompared_obs()
    
    
    def _uncompared_obs(self):

        for cl in self.obsToComp1:
            # add cluster to cluster list
            uc1 = cl.__class__()
            added = False # added some observation

            for obs in cl:
                found, x, x = self._find_obs(obs, self.compObsClList)
                if not found:
                    uc1.append_obs(obs)
                    added = True
            
            if added:
                self.uncompObsClList1.append_cluster(uc1)
        
        for cl in self.obsToComp2:
            # add cluster to cluster list
            uc2 = cl.__class__()
            added = False # added some observation
            
            for obs in cl:
                found, x ,x = self._find_obs(obs, self.compObsClList)
                if not found:
                    uc2.append_obs(obs)
                    added = True
            
            if added:
                self.uncompObsClList2.append_cluster(uc2)


    def _cmp_vector(self, vec1, vec2, reversed=False):
        "comparison of two vectors - dx, dy, dz, var_dx, var_dy, var_dz"
        if reversed:
            ddx = vec1.dx + vec2.dx
            ddy = vec1.dy + vec2.dy
            ddz = vec1.dz + vec2.dz
        else:
            ddx = vec1.dx - vec2.dx
            ddy = vec1.dy - vec2.dy
            ddz = vec1.dz - vec2.dz
        
        # variances
        var1 = vec1.var
        var2 = vec2.var
        var_ddx = var1[0] + var2[0]
        var_ddy = var1[1] + var2[1]
        var_ddz = var1[2] + var2[2]

        # covariances
        cov1 = vec1.cov
        cov2 = vec2.cov
        cov_xy = cov1[0] + cov2[0]
        cov_xz = cov1[1] + cov2[1]
        cov_yz = cov1[2] + cov2[2]

        #if excludeZero:
        #    if (ddx, ddy, ddz) == (0, 0, 0):
        #        return

        # append vector 
        vec = ObsVector(fromid=vec1.fromid, toid=vec1.toid,
                        dx=ddx, dy=ddy, dz=ddz)
        self._cluster.append_obs(vec)
        
        # extend covariance matrix and add values
        self._cluster.covmat.extend_dim(3)
        vec.var = (var_ddx, var_ddy, var_ddz)
        vec.cov = (cov_xy, cov_xz, cov_yz)

    
    def str_mean(self):
        str = ["\nObservations 1: mean and residuals",
               "=================================="]

        str.extend(["\nmean:%s\n\nobservations:%s\n\nresiduals:%s"\
                    % (mean, obs, res) \
                    for mean, obs, res in zip(self.meanList1,
                                              self.obsMeanList1,
                                              self.resList1)])

        str.extend(["\nObservations 2: mean and residuals",
                    "=================================="])

        str.extend(["\nmean:%s\n\nobservations:%s\n\nresiduals:%s"\
                    % (mean, obs, res) \
                    for mean, obs, res in zip(self.meanList2,
                                              self.obsMeanList2,
                                              self.resList2)])

        return "\n".join(str)

    def str_summary(self):
        tt = TextTable([("", "%10s"),
                        ("ep 0", "%4i"),
                        ("ep 1", "%4i")])
        str = [tt.make_table_head()]
        
        sum1 = sum([len(cl) for cl in self.obsToComp1])
        sum2 = sum([len(cl) for cl in self.obsToComp2])
        sumComp = sum([len(cl) for cl in self.compObsClList])
        sumu1 = sum([len(cl) for cl in self.uncompObsClList1])
        sumu2 = sum([len(cl) for cl in self.uncompObsClList2])
    

        str.append(tt.make_table_row("sum obs", sum1, sum2))
        str.append(tt.make_table_row("obs comp", sumComp, sumComp))
        str.append(tt.make_table_row("obs uncomp", sumu1, sumu2))

        str.append(tt.make_table_foot())

        return "".join(str)


    def str_uncompared(self):

        str = ["\nUncompared observations 1:",
               "=========================="]
        str.append(self.uncompObsClList1.__str__())
        str.extend(["\nUncompared observations 2:",
                    "=========================="])
        str.append(self.uncompObsClList2.__str__())

        return "\n".join(str)


    def str_compared(self):
        str = ["\nObservations compared:",
                 "======================"]
        
        str.append(self.compObsClList.__str__())
        return "\n".join(str)

    def __str__(self):
        return self.str_compared()


if __name__ == "__main__":

    from gizela.data.GamaLocalDataObs   import GamaLocalDataObs
    data1 = GamaLocalDataObs()
    data2 = GamaLocalDataObs()

    try:
        file1 = open("../../example/vec/vec2008j.gkf")
        file2 = open("../../example/vec/vec2008p.gkf")
    except Exception, e:
        print "Cannot open files"
        print e
        import sys
        sys.exit(1)

    data1.parse_file(file1)
    data2.parse_file(file2)

    cmp = CompareObs(data1, data2)
    cmp.compare_vector(mean=False)

    print cmp.str_summary()
    print cmp.str_compared()
    print cmp.str_uncompared()
    #print cmp.str_mean()

    # transformation
    from gizela.tran.Tran3D import Tran3D
    tr = Tran3D()
    
    from math import pi
    phi = (50.0 +  5.0/60 + 27.0/3600) * pi/180
    lam = (14.0 + 24.0/60 +  2.0/3600) * pi/180
    tr.rotation_xyz(0, phi - pi/2, lam - pi)
    
    for cl in cmp.compObsClList:
        print cl
        if isinstance(cl, ObsClusterVector):
            cl.transform_(tr)
    
    print "\nTransformed"
    print cmp.compObsClList

    #print cmp.compObsClList.make_gama_xml()
