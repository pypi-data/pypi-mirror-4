# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 

from gizela.util.Error import Error
from gizela.stat.ConfidenceScale import ConfidenceScale

class StandardDeviationError(Error):pass


class StandardDeviation(object):
    """
    class for handing standart deviations
    and confidence scales
    """

    def __init__(self, 
                 apriori=None,
                 aposteriori=None,
                 useApriori=True, 
                 confProb=0.95, 
                 df=0):

        self.apriori = apriori
        if isinstance(aposteriori, float) or aposteriori is None:
            self.aposteriori = aposteriori
        else:
            raise StandardDeviationError('aposteriori is not float')
        self.useApriori = useApriori
        self.df = df # degrees of freedom of aposteriori standard deviation

        # confidence
        self.confProb = confProb

    def __str__(self):
        str = []
        if self.apriori is None:
            str.append("apriori: not set")
        else:
            str.append("apriori:%.3f" % self.apriori)
        if self.aposteriori is None:
            str.append("aposteriori: not set")
        else:
            str.append("aposteriori:%.3f" % self.aposteriori)
        str.extend(["use: %s" % (self.useApriori and "apriori" or
                                   "aposteriori"),
                    "confidence: %.3f" % (self.confProb),
                    "degrees of freedom: %i" % self.df
                    ])

        return "\n".join(str)


    def get_conf_scale_1d(self): 
        return ConfidenceScale.get_scale(self.confProb,
                                         apriori=self.useApriori,
                                         dim=1,
                                         df=self.df)

    def get_conf_scale_2d(self):
        return ConfidenceScale.get_scale(self.confProb,
                                         apriori=self.useApriori,
                                         dim=2,
                                         df=self.df)

    def get_conf_scale_3d(self):
        return ConfidenceScale.get_scale(self.confProb,
                                         apriori=self.useApriori,
                                         dim=3,
                                         df=self.df)

    #def get_stdev(self, stdev):
    #    if self.usedApriori is self.useApriori:
    #        return stdev
    #    else:
    #        if self.useApriori:
    #            # recompute from aposteriori to apriori
    #            return stdev*self.apriori/self.aposteriori
    #        else:
    #            return stdev*self.aposteriori/self.apriori

    #def get_var(self, var):
    #    if self.usedApriori is self.useApriori:
    #        return var
    #    else:
    #        if self.useApriori:
    #            # recompute from aposteriori to apriori
    #            return var*self.apriori**2/self.aposteriori**2
    #        else:
    #            return var*self.aposteriori**2/self.apriori**2

    #def set_var(self, var):
    #    """
    #    returs var recomputed from useApriori to usedApriori
    #    reverse function to get_var
    #    """
    #    if self.usedApriori is self.useApriori:
    #        return var
    #    else:
    #        if self.useApriori:
    #            # recompute from apriori to aposteriori
    #            return var*self.aposteriori**2/self.apriori**2
    #        else:
    #            return var*self.apriori**2/self.aposteriori**2


    #def set_used_apriori(self):
    #    self.usedApriori = True

    #def set_used_aposteriori(self):
    #    self.usedApriori = False

    def set_use_apriori(self, use):
        self.useApriori = use

    #def set_use_aposteriori(self):
    #    self.useApriori = False

    def get_use(self):
        if self.useApriori:
            return "apriori"
        else:
            return "aposteriori"

    def set_use(self, use):
        if use == "apriori":
            self.set_use_apriori(True)
        elif use == "aposteriori":
            self.set_use_apriori(False)
        else:
            raise StandardDeviationError, "unknown use: %s" % use

    def set_conf_prob(self, confProb):
        self.confProb = confProb


if __name__ == "__main__":
        
    std = StandardDeviation()
    # apriori
    print std.get_conf_scale_1d()
    print std.get_conf_scale_2d()
    print std.get_conf_scale_3d()
    
    # aposteriori
    std.useApriori=False
    std.df=2
    #std.df=1000
    print std.get_conf_scale_1d()
    print std.get_conf_scale_2d()
    print std.get_conf_scale_3d()

