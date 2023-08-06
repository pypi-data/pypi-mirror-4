""" @module
This module contains the admitted diagnostics.
Diagnostics are stored in a dictionary. Keys are literal descriptions of the diagnostic 
(e.g. '[NI] 5198/5200') and items are tuples including a label ('N1'), an expression for the line ratio ('L(5198)/L(5200)',
and an expression for the uncertainty on the line ratio as a function of the uncertainty on the individual lines ('RMS([E(5200),E(5198)])')

"""
import numpy as np
import pyneb as pn
from pyneb.utils.misc import int_to_roman, parseAtom
from pyneb.utils.init import BLEND_LIST

diags_dict = {}

diags_dict['[CIII] 1909/1907'] = ('C3', 'L(1909)/L(1907)', 'RMS([E(1909),E(1907)])')
diags_dict['[NI] 5198/5200'] = ('N1', 'I(3, 1)/I(2, 1)', 'RMS([E(5200),E(5198)])')
diags_dict['[NII] 5755/6548'] = ('N2', 'L(5755)/L(6548)', 'RMS([E(6548),E(5755)])')
diags_dict['[NII] 5755/6584'] = ('N2', 'L(5755)/L(6583)', 'RMS([E(6583),E(5755)])')
diags_dict['[NII] 5755/6584+'] = ('N2', 'L(5755)/(L(6548)+L(6583))', 'RMS([E(6548)*L(6548)/(L(6548)+L(6583)),E(6583)*L(6583)/(L(6583)+L(6548)),E(5755)])')
diags_dict['[NII] 121m/20.5m'] = ('N2', 'L(1214747)/L(2054427)', 'RMS([E(2054427)/E(1214747)])')
diags_dict['[NIII] 1750/57.4m'] = ('N3', 'L(1750)/L(574000)', 'RMS([E(574000),E(1750)])')
#diags_dict[''] = ('N3','L(1749)/L(1752)','RMS([E(1749),E(1752)])')
diags_dict['[OI] 63m/147m'] = ('O1', 'L(632000)/L(1455000)', 'RMS([E(632000),E(1455000)])')
diags_dict['[OI] 5579/6302'] = ('O1', 'L(5579)/L(6302)', 'RMS([E(6302),E(5579)])')
diags_dict['[OI] 5579/6300+'] = ('O1', 'L(5579)/(L(6302)+L(6366))', 'RMS([E(6302)*L(6302)/(L(6302)+L(6366)),E(6366)*L(6366)/(L(6302)+L(6366)),E(5579)])')
diags_dict['[OII] 3726/3729'] = ('O2', 'L(3726)/L(3729)', 'RMS([E(3729),E(3726)])')
diags_dict['[OII] 3727+/7325+'] = ('O2','(L(3726)+L(3729))/(B("7319A+")+B("7330A+"))',
              'RMS([E(3726)*L(3726)/(L(3726)+L(3729)),E(3729)*L(3729)/(L(3726)+L(3729)),BE("7319A+")*B("7319A+")/(B("7319A+")+B("7330A+")),BE("7330A+")*B("7330A+")/(B("7319A+")+B("7330A+"))])')
#diags_dict['[OII] 3727+/7325+'] = ('O2', '(L(3726)+L(3729))/(B("7325A+"))', 'RMS([E(3726)*L(3726)/(L(3726)+L(3729)),E(3729)*L(3729)/(L(3726)+L(3729)),BE("7325A+")])')
diags_dict['[OIII] 4363/5007'] = ('O3', 'L(4363)/L(5007)', 'RMS([E(5007),E(4363)])')
diags_dict['[OIII] 4363/5007+'] = ('O3', 'L(4363)/(L(5007)+L(4959))', 'RMS([E(5007)*L(5007)/(L(5007)+L(4959)),E(4959)*L(4959)/(L(5007)+L(4959)),E(4363)])')
diags_dict['[OIII] 5007/88m'] = ('O3', 'L(5007)/L(876000)', 'RMS([E(876000),E(5007)])')
diags_dict['[OIII] 51m/88m'] = ('O3', 'L(518000)/L(876000)', 'RMS([E(876000),E(518000)])')
diags_dict['[OIII] 1666/5007+'] = ('O3', 'L(1666)/(L(5007)+L(4959))', 'RMS([E(5007)*L(5007)/(L(5007)+L(4959)),E(4959)*L(4959)/(L(5007)+L(4959)),E(1666)])')
diags_dict['[OIII] 1666/5007'] = ('O3', 'L(1666)/L(5007)', 'RMS([E(5007),E(1666)])')
diags_dict['[OIII] 1666/4363'] = ('O3', 'L(1666)/L(4363)', 'RMS([E(4363),E(1666)])')
diags_dict['[OIV] 1401/1405'] = ('O4', 'L(1401)/L(1405)', 'RMS([E(1401),E(1405)])')
diags_dict['[SII] 6731/6716'] = ('S2', 'L(6731)/L(6716)', 'RMS([E(6716),E(6731)])')
diags_dict['[SII] 4069/4076'] = ('S2', 'L(4069)/L(4076)', 'RMS([E(4069),E(4076)])')
diags_dict['[SII] 4072+/6720+'] = ('S2', '(L(4069)+L(4076))/(L(6716)+L(6731))',
              'RMS([E(6716)*L(6716)/(L(6716)+L(6731)),E(6731)*L(6731)/(L(6716)+L(6731)),E(4069)*L(4069)/(L(4069)+L(4076)),E(4076)*L(4076)/(L(4069)+L(4076))])')
diags_dict['[SIII] 18.7m/33.6m'] = ('S3', 'L(187000)/L(336000)', 'RMS([E(336000),E(187000)])')
diags_dict['[SIII] 6312/18.7m'] = ('S3', 'L(6312)/L(187000)', 'RMS([E(187000),E(6312)])')
diags_dict['[SIII] 9069/18.7m'] = ('S3', 'L(9069)/L(187000)', 'RMS([E(187000),E(9069)])')
diags_dict['[SIII] 6312/9200+'] = ('S3', 'L(6312)/(L(9069)+L(9532))', 'RMS([E(9069)*L(9069)/(L(9069)+L(9532)),E(9532)*L(9532)/(L(9069)+L(9532)),E(6312)])')
diags_dict['[SIII] 6312/9069'] = ('S3', 'L(6312)/L(9069)', 'RMS([E(9069),E(6312)])')
diags_dict['[NeIII] 15.6m/36.0m'] = ('Ne3', 'L(156000)/L(360000)', 'RMS([E(156000),E(360000)])')
diags_dict['[NeIII] 3869/15.6m'] = ('Ne3', 'L(3869)/L(156000)', 'RMS([E(156000),E(3869)])')
diags_dict['[NeIII] 3930+/15.6m'] = ('Ne3', '(L(3869)+L(3967))/L(156000)', 'RMS([E(156000),E(3869)*L(3869)/(L(3869)+L(3967)),E(3967)*L(3967)/(L(3869)+L(3967))])')
diags_dict['[NeIII] 3344/3930+'] = ('Ne3', 'L(3344)/(L(3869)+L(3967))', 'RMS([E(3869)*L(3869)/(L(3869)+L(3967)),E(3967)*L(3967)/(L(3869)+L(3967)),E(3344)])')
diags_dict['[NeV] 2975/3370+'] = ('Ne5', 'L(2975)/(L(3426)+L(3346))', 'RMS([E(3426)*L(3426)/(L(3426)+L(3346)),E(3346)*L(3346)/(L(3426)+L(3346)),E(2975)])')
diags_dict['[NeV] 1575/3426'] = ('Ne5', 'L(1575)/L(3426)', 'RMS([E(1575),E(3426)])')
diags_dict['[NeV] 14.3m/24.2m'] = ('Ne5', 'L(143000)/L(242000)', 'RMS([E(143000),E(242000)])')
diags_dict['[ClIII] 5538/5518'] = ('Cl3', 'L(5538)/L(5518)', 'RMS([E(5518),E(5538)])')
diags_dict['[ClIV] 5323/7531'] = ('Cl4', 'L(5323)/L(7531)', 'RMS([E(7531),E(5323)])')
diags_dict['[ClIV] 5323/7700+'] = ('Cl4', 'L(5323)/(L(7531)+L(8046))', 'RMS([E(7531)*L(7531)/(L(7531)+L(8046)),E(8046)*L(8046)/(L(7531)+L(8046)),E(5323)])')
diags_dict['[ArIII] (7751+7136)/9m'] = ('Ar3', '(L(7751)+L(7136))/L(90000)', 'RMS([E(90000),E(7751)*L(7751)/(L(7751)+L(7136)),E(7136)*L(7136)/(L(7751)+L(7136))])')
diags_dict['[ArIII] 7136/9m'] = ('Ar3', 'L(7136)/L(90000)', 'RMS([E(90000),E(7136)])')
diags_dict['[ArIII] 5192/7300+'] = ('Ar3', 'L(5192)/(L(7751)+L(7136))', 'RMS([E(7751)*L(7751)/(L(7751)+L(7136)),E(7136)*L(7136)/(L(7751)+L(7136)),E(5192)])')
diags_dict['[ArIII] 5192/7136'] = ('Ar3', 'L(5192)/L(7136)', 'RMS([E(7136),E(5192)])')
diags_dict['[ArIII] 9.0m/21.8m'] = ('Ar3', 'L(89897)/L(218000)', 'RMS([E(89897),E(218000)])')
diags_dict['[ArIV] 4740/4711'] = ('Ar4', 'L(4740)/L(4711)', 'RMS([E(4711),E(4740)])')
diags_dict['[ArIV] 2860+/4720+'] = ('Ar4', '(L(2854)+L(2868))/(L(4711)+L(4740))',
              'RMS([E(4711)*L(4711)/(L(4711)+L(4740)),E(4740)*L(4740)/(L(4711)+L(4740)),E(2854)*L(2854)/(L(2854)+L(2868)),E(2868)*L(2854)/(L(2854)+L(2868))])')
diags_dict['[ArIV] 7230+/4720+'] = ('Ar4', '(L(7170)+L(7262))/(L(4711)+L(4740))',
              'RMS([E(4711)*L(4711)/(L(4711)+L(4740)),E(4740)*L(4740)/(L(4711)+L(4740)),E(7170)*L(7170)/(L(7170)+L(7262)),E(7262)*L(7262)/(L(7170)+L(7262))])')
diags_dict['[ArV] 4626/6600+'] = ('Ar5', 'L(4626)/(L(6435)+L(7006))', 'RMS([E(6435)*L(6435)/(L(6435)+L(7006)),E(7006)*L(7006)/(L(6435)+L(7006)),E(4626)])')

diags_dict['[FeIII] 5272/4987'] = ('Fe3', 'L(5272)/L(4987)', 'RMS([E(5272),E(4987)])')
diags_dict['[FeIII] 5272/4926'] = ('Fe3', 'L(5272)/L(4926)', 'RMS([E(5272),E(4926)])')
diags_dict['[FeIII] 5272/4882'] = ('Fe3', 'L(5272)/L(4882)', 'RMS([E(5272),E(4882)])')
diags_dict['[FeIII] 5272/5013'] = ('Fe3', 'L(5272)/L(5013)', 'RMS([E(5272),E(5013)])')
diags_dict['[FeIII] 5272/4932'] = ('Fe3', 'L(5272)/L(4932)', 'RMS([E(5272),E(4932)])')
diags_dict['[FeIII] 5272/4659'] = ('Fe3', 'L(5272)/L(4659)', 'RMS([E(5272),E(4659)])')
diags_dict['[FeIII] 5272/4703'] = ('Fe3', 'L(5272)/L(4703)', 'RMS([E(5272),E(4703)])')
diags_dict['[FeIII] 5272/4735'] = ('Fe3', 'L(5272)/L(4735)', 'RMS([E(5272),E(4735)])')
diags_dict['[FeIII] 5272/4009'] = ('Fe3', 'L(5272)/L(4009)', 'RMS([E(5272),E(4009)])')
diags_dict['[FeIII] 4987/4926'] = ('Fe3', 'L(4987)/L(4926)', 'RMS([E(4987),E(4926)])')
diags_dict['[FeIII] 4987/4882'] = ('Fe3', 'L(4987)/L(4882)', 'RMS([E(4987),E(4882)])')
diags_dict['[FeIII] 4987/5013'] = ('Fe3', 'L(4987)/L(5013)', 'RMS([E(4987),E(5013)])')
diags_dict['[FeIII] 4987/4932'] = ('Fe3', 'L(4987)/L(4932)', 'RMS([E(4987),E(4932)])')
diags_dict['[FeIII] 4987/4659'] = ('Fe3', 'L(4987)/L(4659)', 'RMS([E(4987),E(4659)])')
diags_dict['[FeIII] 4987/4703'] = ('Fe3', 'L(4987)/L(4703)', 'RMS([E(4987),E(4703)])')
diags_dict['[FeIII] 4987/4735'] = ('Fe3', 'L(4987)/L(4735)', 'RMS([E(4987),E(4735)])')
diags_dict['[FeIII] 4987/4009'] = ('Fe3', 'L(4987)/L(4009)', 'RMS([E(4987),E(4009)])')
diags_dict['[FeIII] 4926/4882'] = ('Fe3', 'L(4926)/L(4882)', 'RMS([E(4926),E(4882)])')
diags_dict['[FeIII] 4926/5013'] = ('Fe3', 'L(4926)/L(5013)', 'RMS([E(4926),E(5013)])')
diags_dict['[FeIII] 4926/4932'] = ('Fe3', 'L(4926)/L(4932)', 'RMS([E(4926),E(4932)])')
diags_dict['[FeIII] 4926/4659'] = ('Fe3', 'L(4926)/L(4659)', 'RMS([E(4926),E(4659)])')
diags_dict['[FeIII] 4926/4703'] = ('Fe3', 'L(4926)/L(4703)', 'RMS([E(4926),E(4703)])')
diags_dict['[FeIII] 4926/4735'] = ('Fe3', 'L(4926)/L(4735)', 'RMS([E(4926),E(4735)])')
diags_dict['[FeIII] 4926/4009'] = ('Fe3', 'L(4926)/L(4009)', 'RMS([E(4926),E(4009)])')
diags_dict['[FeIII] 4882/5013'] = ('Fe3', 'L(4882)/L(5013)', 'RMS([E(4882),E(5013)])')
diags_dict['[FeIII] 4882/4932'] = ('Fe3', 'L(4882)/L(4932)', 'RMS([E(4882),E(4932)])')
diags_dict['[FeIII] 4882/4659'] = ('Fe3', 'L(4882)/L(4659)', 'RMS([E(4882),E(4659)])')
diags_dict['[FeIII] 4882/4703'] = ('Fe3', 'L(4882)/L(4703)', 'RMS([E(4882),E(4703)])')
diags_dict['[FeIII] 4882/4735'] = ('Fe3', 'L(4882)/L(4735)', 'RMS([E(4882),E(4735)])')
diags_dict['[FeIII] 4882/4009'] = ('Fe3', 'L(4882)/L(4009)', 'RMS([E(4882),E(4009)])')
diags_dict['[FeIII] 5013/4932'] = ('Fe3', 'L(5013)/L(4932)', 'RMS([E(5013),E(4932)])')
diags_dict['[FeIII] 5013/4659'] = ('Fe3', 'L(5013)/L(4659)', 'RMS([E(5013),E(4659)])')
diags_dict['[FeIII] 5013/4703'] = ('Fe3', 'L(5013)/L(4703)', 'RMS([E(5013),E(4703)])')
diags_dict['[FeIII] 5013/4735'] = ('Fe3', 'L(5013)/L(4735)', 'RMS([E(5013),E(4735)])')
diags_dict['[FeIII] 5013/4009'] = ('Fe3', 'L(5013)/L(4009)', 'RMS([E(5013),E(4009)])')
diags_dict['[FeIII] 4932/4659'] = ('Fe3', 'L(4932)/L(4659)', 'RMS([E(4932),E(4659)])')
diags_dict['[FeIII] 4932/4703'] = ('Fe3', 'L(4932)/L(4703)', 'RMS([E(4932),E(4703)])')
diags_dict['[FeIII] 4932/4735'] = ('Fe3', 'L(4932)/L(4735)', 'RMS([E(4932),E(4735)])')
diags_dict['[FeIII] 4932/4009'] = ('Fe3', 'L(4932)/L(4009)', 'RMS([E(4932),E(4009)])')
diags_dict['[FeIII] 4659/4703'] = ('Fe3', 'L(4659)/L(4703)', 'RMS([E(4659),E(4703)])')
diags_dict['[FeIII] 4659/4735'] = ('Fe3', 'L(4659)/L(4735)', 'RMS([E(4659),E(4735)])')
diags_dict['[FeIII] 4659/4009'] = ('Fe3', 'L(4659)/L(4009)', 'RMS([E(4659),E(4009)])')
diags_dict['[FeIII] 4703/4735'] = ('Fe3', 'L(4703)/L(4735)', 'RMS([E(4703),E(4735)])')
diags_dict['[FeIII] 4703/4009'] = ('Fe3', 'L(4703)/L(4009)', 'RMS([E(4703),E(4009)])')
diags_dict['[FeIII] 4735/4009'] = ('Fe3', 'L(4735)/L(4009)', 'RMS([E(4735),E(4009)])')
diags_dict['[FeIII] 4659+/4987+'] = ('Fe3', '(L(4659)+L(4735)+L(4009))/(L(4987)+L(4989))', 'RMS([E(4659),E(4987)])')

class Diagnostics(object):
    """
    Diagnostics is the class used to manage the diagnostics and to computed physical conditions 
        (electron temperatures and densities) from them. 
    It is also the class that plots the diagnostic Te-Ne diagrams.

    """    
    def __init__(self, addAll=False, OmegaInterp='Cheb'):
        """
        Diagnostics constructor
        Parameters:
            - addAll:    switch to include all defined diagnostics (default = False)
            - OmegaInterp: parameter sent to Atom, default is 'Cheb', other can be 'linear'
            
        """
        self.log_ = pn.log_ 
        self.calling = 'Diagnostics'
        ##            
        # @var diags
        # The dictionnary containing the diagnostics
        self.diags = {}
        ##
        # @var atomDict
        # The dictionnary containing the atoms used for the diagnostics        
        self.atomDict = {}
        self.OmegaInterp = OmegaInterp
        if addAll:
            self.addAll()

    def getDiagFromLabel(self, label):
        """
        Return the definition of a diagnostic (the 3 or 4 elements tuple)
        
        Usage:
            diags.getDiagFromLabel('[NII] 5755/6548')
        
        Parameter:
            -label a diagnostic label 
        """
        if label in self.diags:
            return self.diags[label]
        else:
            self.log_.warn('{0} not in diagnostic'.format(label), calling=self.calling)
            return None
        
    def getDiags(self):
        """
        Return the definitions (tuples) of all the diagnostics defined in the Object.
        No parameter.
        """
        return [self.getDiagFromLabel(label) for label in self.diags]
            
    def getDiagLabels(self):
        """
        Return the labels of all the diagnostics defined in the Object
        No parameter.
        """
        return self.diags.keys()    
    
    def getAllDiags(self):
        """
        Return the definitions (tuples) of all the possible diagnostics.
        No parameter.
        """
        return diags_dict
            
    def getAllDiagLabels(self):
        """
        Return the labels of all the possible diagnostics.
        No parameter.
        """
        return diags_dict.keys()    
    
    def getUniqueAtoms(self):
        """
        Return a numpy.ndarray of the ions needed by the diagnostics. Unique is applied to the list before returning.
        No parameter.
        """
        return np.unique([self.diags[d][0] for d in self.diags if self.diags[d] is not None])

    def addDiag(self, label, diag_tuple=None):
        """
        Method to add a diagnostic to the list of available diagnostics
        Parameters:
            - label: a string or a list of strings describing the diagnostic, e.g. '[OIII] 4363/5007'. 
            If it is a key of diags_dict (a diagnostic define by PyNeb), no need for diag_tuple
            - diag_tuple: a 3 elements tuple containing :
                + the atom, e.g. 'Ar5'
                + the algebraic description of the diagnostic, in terms of line wavelengths or blends or levels, 
                  e.g. '(L(6435)+L(7006))/L(4626)'
                + the algebraic description of the error, e.g. 
                    'RMS([E(6435)*L(6435)/(L(6435)+L(7006)),E(7006)*L(7006)/(L(6435)+L(7006)),E(4626)])'

        """
        atom = None
        if type(label) is list:
            for lab in label:
                self.addDiag(lab)
        elif label in self.diags:
            self.log_.warn('{0} already in diagnostic'.format(label), calling=self.calling)
        elif label in diags_dict:
            self.diags[label] = diags_dict[label]
            atom = diags_dict[label][0]
        elif type(diag_tuple) is tuple:
            if len(diag_tuple) == 3:    
                self.diags[label] = diag_tuple
                atom = diag_tuple[0]
            else:
                self.log_.error('{0} is not in the list of diagnostics. The 2nd argument must be a 3-elements tuple describing the diagnostic'.format(label), 
                                calling = self.calling + '.addDiag')
        else:
            self.log_.error('{0} is not in the list of diagnostics. The 2nd argument must be a tuple describing the diagnostic'.format(label), 
                            calling = self.calling + '.addDiag')
        if atom is not None:
            if atom not in self.atomDict:
                self.atomDict[atom] = pn.Atom(parseAtom(atom)[0], parseAtom(atom)[1])
    
    def addAll(self):
        """
        Insert all the possible diagnostics in the Object.
        No parameter.
        """
        for label in diags_dict:
            self.addDiag(label)
            
    def delDiag(self, label):
        """
        Remove a diagnostic, based on its label.
        Parameter:
            - label  the diagnostic label
        """
        if label in self.diags:
            del self.diags[label]
        else:
            self.log_.warn('{0} not in diagnostic, cannot be removed'.format(label), calling=self.calling)
    
    def __setDiagsFromObs(self, obs):
        """
        Not implemented
        
        L = lambda wave: obs.getLine(elem, spec, wave).corrIntens
        def I(i, j):
            wave = atom.wave_Ang[i-1, j-1]
            return obs.getLine(elem, spec, wave).corrIntens
        def B(label, I=I, L=L):
            full_label = elem + spec + '_' + label
            corrIntens = obs.getLine(label=full_label).corrIntens
            return corrIntens
        """
        for label in diags_dict:
            atom, diag_expression, error = diags_dict[label]
            if atom not in self.atomDict:
                self.atomDict[atom] = pn.Atom(parseAtom(atom)[0], parseAtom(atom)[1])
            
            
            # Here we must have a test to see if the lines are in the observations.
            self.addDiag(label)
    
    def setAtoms(self, atom_dic):
        """
        Define the dictionary containing the atoms used for the diagnostics.
        A dictionary of atom instantiations refereed by atom strings, for example:
        {'O3' : pn.Atom('O', 3)}
        """
        if type(atom_dic) != type({}):
            self.log_.error('the parameter must be a dictionary.', calling=self.calling + '.setAtoms')
            return None
        for atom in atom_dic:
            if not isinstance(atom_dic[atom], pn.Atom):
                self.log_.error('the parameter must be a dictionary of Atom.', calling=self.calling + '.setAtoms')
                return None
        self.atomDict = atom_dic
    
    def addClabel(self, label, clabel):
        """
        Add an alternative label to a diagnostic that can be used when plotting diagnostic diagrams.
        """
        if label in self.diags:
            self.diags[label] = (self.diags[label][0], self.diags[label][1], self.diags[label][2], clabel)
        else:
            pn.log_.warn('Try to add clabel in undefined label {0}'.format(label), calling=self.calling)
    
    def plot(self, emis_grids, obs, quad=True, i_obs=None, alpha=0.3):
        """
        PLotting tool to generate Te-Ne diagrams.
        
        Usage:
            diags.plot(emisgrids, obs, i_obs=3)
        Parameters:
            - emis_grids:    A dictionary of EmisGrid objects refereed by their atom strings (e.g. 'O3')
                            This can for example be the output of pn.getEmisGridDict()
            - obs:         A pn.Observation object that is supposed to contain the line intensities
                            used for the plot (corrected intensities).
            - quad:        If True (default) the sum of the error is quadratic,otherwise is linear.
            - i_obs:        reference for the observation to be plotted, in case there is more than one
                            in the obs object
            - alpha:        Transparency for the error bands in the plot
        """
        if not pn.config.INSTALLED['plt']: 
            pn.log_.error('Matplotlib not available, no plot', calling=self.calling + '.plot')
            return None
        else:
            import matplotlib.pyplot as plt
        if type(emis_grids) != type({}):
            self.log_.error('the first parameter must be a dictionary', calling=self.calling + '.plot')
            return None
        for em in emis_grids:
            if not isinstance(emis_grids[em], pn.EmisGrid):
                self.log_.error('the first parameter must be a dictionary of EmisGrid', calling=self.calling + '.plot')
                return None
        if not isinstance(obs, pn.Observation):
            self.log_.error('the second parameter must be an Observation', calling=self.calling + '.plot')
            return None
        if (i_obs is None) and (obs.n_obs != 1):
            self.log_.error('i_obs must be specified when obs is multiple. try i_obs=0', calling = self.calling)
            return None
        
        X = np.log10(emis_grids[emis_grids.keys()[0]].den2D)
        Y = emis_grids[emis_grids.keys()[0]].tem2D
        for label in self.diags:
            diag = self.diags[label]
            atom = diag[0]
            def I(i, j):
                return emis_grids[atom].getGrid(lev_i=i, lev_j=j)
            def L(wave):
                return emis_grids[atom].getGrid(wave=wave)
            def B(label, I=I, L=L):
                full_label = atom + '_' + label
                if full_label in BLEND_LIST:
                    to_eval = BLEND_LIST[full_label]
                else:
                    self.log_.warn('{0} not in BLEND_LIST'.format(full_label), calling=self.calling)
                    return None
                return eval(to_eval)
            try:
                diag_map = eval(diag[1])
            except:
                diag_map = None
                self.log_.warn('diag {0} {1} not used'.format(diag[0], diag[1]), calling=self.calling)
            if diag_map is not None:
                sym, spec = parseAtom(atom)
                def I(i, j):
                    wave = emis_grids[atom].atom.wave_Ang[i-1, j-1]
                    corrIntens = obs.getLine(sym, spec, wave).corrIntens
                    if i_obs is None:
                        return corrIntens
                    else:
                        return corrIntens[i_obs]
                def L(wave):
                    corrIntens = obs.getLine(sym, spec, wave).corrIntens
                    if i_obs is None:
                        return corrIntens
                    else:
                        return corrIntens[i_obs]
                def B(label):
                    full_label = atom + '_' + label
                    corrIntens = obs.getLine(label=full_label).corrIntens
                    if i_obs is None:
                        return corrIntens
                    else:
                        return corrIntens[i_obs]
                try:
                    diag_value = eval(diag[1])
                except:
                    diag_value = None
                    self.log_.warn('No line for diag {0}, using {1}, {2}'.format(diag[1], sym, spec), 
                                   calling=self.calling)
                if diag_value is not None and not np.isnan(diag_value) and not np.isinf(diag_value):
                    def E(wave):
                        err = obs.getLine(sym, spec, wave).corrError
                        if i_obs is None:
                            return err
                        else:
                            return err[i_obs]
                    def BE(label):
                        full_label = atom + '_' + label
                        err = obs.getLine(label=full_label).corrError
                        if i_obs is None:
                            return err
                        else:
                            return err[i_obs]
                    if quad is True:
                        RMS = lambda err: np.sqrt((np.asarray(err) ** 2.).sum())
                    else:
                        RMS = lambda err: (np.asarray(err)).sum() 
                    tol_value = eval(diag[2])
                    col_dic = {'C':'cyan', 'N':'blue', 'O':'green', 'Ne':'magenta',
                               'Ar':'red', 'Cl':'magenta', 'S':'black', 'Fe':'blue'}
                    col = col_dic[atom[:-1]]
                    style_dic = {'1':'-', '2':'--', '3':':', '4':'-.', '5':'-', '6':'--'}
                    style = style_dic[atom[-1]]
                    if tol_value > 0.:
                        levels = [(1 - tol_value) * diag_value, (1 + tol_value) * diag_value]
                        CS = plt.contourf(X, Y, diag_map, levels=levels, alpha=alpha, colors=col)
                    CS = plt.contour(X, Y, diag_map, levels=[diag_value], colors=col, linestyles=style)
                    plt.xlabel(r'log(n$_{\rm e}$) [cm$^{-3}$]')
                    plt.ylabel(r'T$_{\rm e}$ [K]')
                    if len(diag) >= 4:
                        fmt = diag[3]
                    else:
                        fmt = '[{0}{1}]'.format(atom[0:-1], int_to_roman(int(atom[-1])))
                    plt.clabel(CS, inline=True, fmt=fmt, fontsize=15, colors=col)
                    if type(diag_value) is np.ndarray:
                        diag_value = diag_value[0]
                    self.log_.message('plotting {0}: {1} = {2:.2} with error of {3:.2} %'.format(fmt, label, diag_value, tol_value * 100), 
                                      calling=self.calling)
        
    def getCrossTemDen(self, diag_tem, diag_den, value_tem=None, value_den=None, obs=None,
                       guess_tem=10000, tol_tem=1., tol_den=1., max_iter=5, maxError=1e-3,
                       start_tem= -1, end_tem= -1, start_den= -1, end_den= -1):
        """
        Cross-converge the temperature and density derived from two sensitive line ratios, by inputting the quantity 
        derived with one line ratio into the other and then iterating.
        The temperature- and density-sensitive ratios can be input directly or as an Observation object
    
        Usage:
            tem, den = getCrossTemDen('[OIII] 5007/4363', '[SII] 6716/6731', 50., 1.0, 
                                     initial_tem=10000, tol_tem = 1., tol_den = 1., max_iter = 5)
    
        - diag_tem   temperature-sensitive diagnostic line ratio
        - diag_den   density-sensitive diagnostic line ratio
        - value_tem  value of the temperature-sensitive diagnostic
        - value_den  value of the density-sensitive diagnostic
        - obs        Observation object containing the relevant line ratios
        - diag_tem   algebraic expression describing the temperature-sensitive diagnostic
        - initial_tem  temperature assumed in the first iteration, in K
        - tol_tem    tolerance of the temperature result, in %
        - tol_den    tolerance of the density result, in %
        - max_iter   maximum number of iterations to be performed, after which the function will throw a result
        - maxError   maximum error in the calls to getTemDen, in %
        - guess_tem, end_tem  lower and upper limit of the explored temperature range 
        - start_den, end_den  lower and upper limit of the explored density range 
    
        """
        ##
        # @todo Add management of blends.
        if diag_tem not in self.diags:
            self.addDiag(diag_tem)
        atom_tem = self.diags[diag_tem][0]
        elem_tem, spec_tem = parseAtom(atom_tem)
        if atom_tem not in self.atomDict:
            self.atomDict[atom_tem] = pn.Atom(elem_tem, spec_tem, self.OmegaInterp)
        atom_tem = self.atomDict[atom_tem]
        if diag_den not in self.diags:
            self.addDiag(diag_den)
        atom_den = self.diags[diag_den][0]
        elem_den, spec_den = parseAtom(self.diags[diag_den][0])
        if (atom_den) not in self.atomDict:
            self.atomDict[atom_den] = pn.Atom(elem_den, spec_den, self.OmegaInterp)
        atom_den = self.atomDict[atom_den]
        eval_tem = self.diags[diag_tem][1]
        eval_den = self.diags[diag_den][1]
        calling = 'Diag.getCrossTemDen %s %s'%(diag_tem, diag_den)
        if value_tem is None:
            L = lambda wave: obs.getLine(elem_tem, spec_tem, wave).corrIntens
            def I(i, j):
                wave = atom_tem.wave_Ang[i-1, j-1]
                return obs.getLine(elem_tem, spec_tem, wave).corrIntens
            def B(label, I=I, L=L):
                full_label = elem_tem + spec_tem + '_' + label
                corrIntens = obs.getLine(label=full_label).corrIntens
                return corrIntens
            #pn.log_.debug('to eval is {0}'.format(eval_tem), calling=calling + 'TEST')
            try:
                value_tem = eval(eval_tem)
                #pn.log_.debug('to eval = {0}'.format(value_tem), calling=calling + 'TEST')
            except:
                pn.log_.warn(' no value for {0} {1}: {2} in obs'.format(elem_tem, spec_tem, diag_tem), calling=calling)
                return None
        else:
            if type(value_tem) == type([]): value_tem = np.asarray(value_tem)
        if value_den is None:
            L = lambda wave: obs.getLine(elem_den, spec_den, wave).corrIntens
            def I(i, j):
                wave = atom_den.wave_Ang[i-1, j-1]
                pn.log_.debug('wave is {0}'.format(wave), calling=calling + 'TEST3')
                return obs.getLine(elem_den, spec_den, wave).corrIntens
            def B(label, I=I, L=L):
                full_label = elem_den + spec_den + '_' + label
                corrIntens = obs.getLine(label=full_label).corrIntens
                return corrIntens
            #pn.log_.debug('to eval is {0}'.format(eval_den), calling=calling + ' TEST')
            try:
                value_den = eval(eval_den)
                #pn.log_.debug('to eval = {0}'.format(value_den), calling=calling + ' TEST1')
            except:
                pn.log_.warn(' no value for {0} {1}: {2} in obs'.format(elem_den, spec_den, diag_den), calling=calling)
                return None
        else:
            if type(value_den) == type([]): value_den = np.asarray(value_den)
        den = atom_den.getTemDen(value_den, tem=guess_tem, to_eval=eval_den,
                                 maxError=maxError, start_x=start_den, end_x=end_den)
        
        tem = atom_tem.getTemDen(value_tem, den=den, to_eval=eval_tem,
                                 maxError=maxError, start_x=start_tem, end_x=end_tem)
#        self.log_.debug('tem: ' + str(tem) + ' den :' + str(den), calling='getCrossTemDen')
        no_conv = np.ones_like(den).astype(bool)
        n_tot = np.asarray(value_tem).size
        for i in np.arange(max_iter):
            if type(tem) == type(1.):
                tem_old = tem
            else:
                tem_old = tem.copy()
            if type(den) == type(1.):
                den_old = den
            else:
                den_old = den.copy()
            
            if n_tot > 1:
                den[no_conv] = atom_den.getTemDen(value_den[no_conv], tem=tem_old[no_conv],
                                                  to_eval=eval_den, start_x=start_den, end_x=end_den)
                tem[no_conv] = atom_tem.getTemDen(value_tem[no_conv], den=den_old[no_conv],
                                                  to_eval=eval_tem, start_x=start_tem, end_x=end_tem)
            else:
                den = atom_den.getTemDen(value_den, tem=tem_old, to_eval=eval_den, start_x=start_den, end_x=end_den)
                tem = atom_tem.getTemDen(value_tem, den=den_old, to_eval=eval_tem, start_x=start_tem, end_x=end_tem)
                
            no_conv = ((abs(den_old - den) / den * 100) > tol_den) | ((abs(tem_old - tem) / tem * 100) > tol_tem)
            if type(no_conv) == type(True):
                n_no_conv = int(no_conv)
            else:
                n_no_conv = no_conv.sum()
            
            pn.log_.message('{0} (max={1}): not converged {2} of {3}.'.format(i, max_iter, n_no_conv, n_tot),
                            calling=calling)
            if n_no_conv == 0:
                return tem, den
        if n_tot == 1:
            tem = np.nan
            den = np.nan
        else:
            tem[no_conv] = np.nan
            den[no_conv] = np.nan
        return tem, den

        
