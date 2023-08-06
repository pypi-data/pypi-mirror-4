#
# Copyright John Reid 2010
#


"""
Example to illustrate application of pybool.
"""

import numpy as N, matplotlib as M, logging, matplotlib.colors
from pybool.constraints import consecutive, combinations, gene_off, gene_on, BaseMetaData
from pybool import network, constraints



def svp_external_input(t, p):
    "External input function for svp. svp is on when t = 1."
    return 1 == t and 1 or 0


def X_external_input(t, p):
    "External input function for X. X is on when t < p."
    return int(t < p)


SVP = 0
HB  = 1
KR  = 2
PDM = 3
CAS = 4
X   = 5



class MetaData(BaseMetaData):
    """
    Meta-data for drosophila neurogenesis regulatory 
    networks in Nakajima paper.
    """

    def __init__(self):
        "Construct."
        
        BaseMetaData.__init__(self)

        self.genes = (
            'svp',  # 0
            'hb',   # 1
            'Kr',   # 2
            'pdm',  # 3
            'cas',  # 4
            'X',    # 5
        )
        "The gene names."

        self.G = len(self.genes)
        "The number of genes."

        self.T = 12
        "The number of time steps to realise."

        self.conditions = [
            'wt',
            'hb-',
            'Kr-',
            'pdm-',
            'cas-',
            'hb++',
            'Kr++',
            'pdm++',
            'cas++',
        ]
        "Conditions."

        self.condition_inputs = {
            'wt'    : { },
            'hb-'   : {  HB : gene_off },
            'Kr-'   : {  KR : gene_off },
            'pdm-'  : { PDM : gene_off },
            'cas-'  : { CAS : gene_off },
            'hb++'  : {  HB : gene_on },
            'Kr++'  : {  KR : gene_on },
            'pdm++' : { PDM : gene_on },
            'cas++' : { CAS : gene_on },
        }
        """
        Condition input functions that map genes 
        to fixed expression states (up or down).
        """

        self.default_condition = 'wt'
        "The condition to use if none specified."

        self.external_inputs = {
            # svp is on at time=1
            SVP : svp_external_input,
            
            # X is activated at time < parameter
              X : X_external_input,
        }
        """
        Default external inputs into the network (can be over-ridden
        when generating a realisation for a particular condition).
        """

        # All initial states are 0 except for HB and X
        self.initial_states = N.zeros((self.G,), dtype=int)
        "Initial expression states."
        self.initial_states[HB] = 1
        self.initial_states[X] = 1

        # set up the possible regulatory connections
        self.possible_Js = N.empty((self.G, self.G), dtype=object)
        "Possible values of J."        
        unconstrained = (-5, 0, 1)
        represses_or_none = (-5, 0)
        activates = (1,)
        represses = (-5,)
        no_regulation = (0,)
        
        # initialise all connections to unconstrained
        for g1 in xrange(self.G):
            for g2 in xrange(self.G):
                self.possible_Js[g1, g2] = no_regulation
        
        # X can regulate any of HB, KR, PDM and CAS
        self.possible_Js[  X, HB] = unconstrained
        self.possible_Js[  X, KR] = unconstrained
        self.possible_Js[  X,PDM] = unconstrained
        self.possible_Js[  X,CAS] = unconstrained
        
        # from Figure 1 in Nakajima paper
        self.possible_Js[SVP, HB] = represses
        self.possible_Js[ HB, KR] = activates
        self.possible_Js[ HB,PDM] = represses
        self.possible_Js[ HB,CAS] = represses_or_none
        self.possible_Js[ KR,PDM] = activates
        self.possible_Js[ KR,CAS] = represses
        self.possible_Js[PDM, KR] = represses
        self.possible_Js[PDM,CAS] = activates
        self.possible_Js[CAS,PDM] = represses        
        
        # possible constitutive expression levels
        self.possible_thetas = N.empty((self.G), dtype=object)
        "Possible values of theta."
        unconstrained = (0, 1)
        for g in xrange(self.G):
            # thetas for external inputs are irrelevant
            if g in self.external_inputs:
                self.possible_thetas[g] = (0,)
            else:
                self.possible_thetas[g] = unconstrained

        # set up all possible input parameters.
        self.possible_input_params = [(None,)] * self.G
        "The possible input parameters."
        self.possible_input_params[X] = N.arange(1, self.T)
        
        self.colours = N.array((
            M.colors.colorConverter.to_rgb('purple'),
            M.colors.colorConverter.to_rgb('green'),
            M.colors.colorConverter.to_rgb('darkblue'),
            M.colors.colorConverter.to_rgb('deepskyblue'),
            M.colors.colorConverter.to_rgb('#DD0000'),
            M.colors.colorConverter.to_rgb('black'),
        ))
        "Colours to use when plotting realisations, etc..."

        self.graph_positions = {
            SVP : ( 1, 1.5),
             HB : ( 0, 1.5),
             KR : (-1, 1  ),
            PDM : ( 0,  .5),
            CAS : (-1, 0  ),
              X : ( 1,  .5),
        }
        "Fixed positions of the genes in a graph."

        # make sure we don't allow regulation of inputs, etc..
        self._tighten_constraints_on_inputs()


    def evaluate_realisation_under_constraints(self, net, R, condition=None):
        "Take the realisation, calculate the change points and evaluate how well it satisfies the constraints."
        # use default condition if not specified
        if None == condition:
            condition = self.default_condition
    
        # calculate when genes go up and down
        checker = constraints.ChangePointChecker(R)
    
        mm = 0 # mismatches in constraints
    
        if 'wt' == condition:
            mm += checker.check_order_of_expression((HB, KR, PDM, CAS))
            mm += checker.check_consecutive_different((HB, KR, PDM, CAS))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'hb-' == condition:
            mm += checker.check_order_of_expression((KR, PDM, CAS))
            mm += checker.check_consecutive_different((KR, PDM, CAS))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'Kr-' == condition:
            mm += checker.check_order_of_expression((HB, PDM, CAS))
            mm += checker.check_consecutive_different((HB, PDM, CAS))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'pdm-' == condition:
            mm += checker.check_order_of_expression((HB, KR, CAS))
            mm += checker.check_consecutive_different((HB, KR, CAS))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'cas-' == condition:
            mm += checker.check_order_of_expression((HB, KR, PDM))
            mm += checker.check_consecutive_different((HB, KR, PDM))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'hb++' == condition:
            mm += checker.check_order_of_expression((HB, KR))
            mm += checker.check_null_expression(PDM)
            mm += checker.check_null_expression(CAS)
            mm += checker.check_consecutive_different((HB, KR))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'Kr++' == condition:
            mm += checker.check_order_of_expression((HB, KR, PDM))
            mm += checker.check_null_expression(CAS)
            mm += checker.check_consecutive_different((HB, KR, PDM))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'pdm++' == condition:
            mm += checker.check_order_of_expression((HB, PDM, CAS))
            mm += checker.check_null_expression(KR)
            mm += checker.check_consecutive_different((HB, PDM, CAS))
            mm += checker.check_on_to_off_switch(X)
    
        elif 'cas++' == condition:
            mm += checker.check_order_of_expression((HB, KR))
            mm += checker.check_null_expression(PDM)
            mm += checker.check_consecutive_different((HB, KR, CAS))
            mm += checker.check_on_to_off_switch(X)
    
        else:
            raise ValueError('Have not implemented constraints for condition: "%s"' % condition)
    
        # return the number of constraint mismatches
        return mm

