import numpy as np
import pyneb as pn
from pyneb.utils.init import ELEM_LIST, SPEC_LIST


class ICF(object):

    def __init__(self):
        """
        ICF tool.
        No parameters for the instantiation.
        """
        
        self.log_ = pn.log_ 
        self.calling = 'ICF'
                
        self._init_all_icfs()
        
    def _init_all_icfs(self):
        # Dictionary of ICF recipes
        self.all_icfs = {'direct_He.2':{'elem': 'He',
                                       'atom': 'abun["He2"] + abun["He3"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_N.3':{'elem': 'N',
                                       'atom': 'abun["N2"] + abun["N3"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_N.4':{'elem': 'N',
                                       'atom': 'abun["N2"] + abun["N3"] + abun["N4"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_N.5':{'elem': 'N',
                                       'atom': 'abun["N2"] + abun["N3"] + abun["N4"] + abun["N5"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_O.3':{'elem': 'O',
                                       'atom': 'abun["O2"] + abun["O3"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_O.4':{'elem': 'O',
                                       'atom': 'abun["O2"] + abun["O3"] + abun["O4"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_O.5':{'elem': 'O',
                                       'atom': 'abun["O2"] + abun["O3"] + abun["O4"] + abun["O5"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_S.3':{'elem': 'S',
                                       'atom': 'abun["S2"] + abun["S3"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_S.4':{'elem': 'S',
                                       'atom': 'abun["S2"] + abun["S3"] + abun["S4"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_S.5':{'elem': 'S',
                                       'atom': 'abun["S2"] + abun["S3"] + abun["S4"] + abun["S5"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_Ne.3':{'elem': 'Ne',
                                       'atom': 'abun["Ne2"] + abun["Ne3"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_Ne.4':{'elem': 'Ne',
                                       'atom': 'abun["Ne2"] + abun["Ne3"] + abun["Ne5"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_Ne.5':{'elem': 'Ne',
                                       'atom': 'abun["Ne2"] + abun["Ne3"] + abun["Ne5"] + abun["Ne6"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_Cl.3':{'elem': 'Cl',
                                       'atom': 'abun["Cl2"] + abun["Cl3"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'direct_Cl.4':{'elem': 'Cl',
                                       'atom': 'abun["Cl2"] + abun["Cl3"] + abun["Cl4"]',
                                       'icf': '1', 
                                       'type': '',
                                       'comment': 'just summing visible ions'},
                         'TPP77_13': {'elem': 'O',
                                      'atom': 'abun["O2"] + abun["O3"]',
                                      'icf': '(abun["He2"] + abun["He3"]) / abun["He2"]',
                                      'type': 'PNe',
                                      'comment': ''},        
                         'TPP77_14': {'elem': 'N',
                                      'atom': 'abun["N2"]',
                                      'icf': '(abun["O2"] + abun["O3"]) / abun["O2"]',
                                      'type': 'PNe',
                                      'comment': ''},
                         'TPP77_15': {'elem': 'Ne',
                                      'atom': 'abun["Ne3"]',
                                      'icf': '(abun["O2"] + abun["O3"]) / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': ''},
                         'PHCD07_12': {'elem': 'Ne',
                                       'atom': 'abun["Ne2"]',
                                       'icf': '(abun["O2"] + abun["O3"]) / abun["O3"]',
                                       'type': 'HII',
                                       'comment': 'Based on a grid of photoionization models'},
                         'PHCD07_13': {'elem': 'Ne',
                                       'atom': 'abun["Ne2"]',
                                       'icf': '(0.753 + 0.142 * abun["O3"] / (abun["O2"] + abun["O3"]) + 0.171 / abun["O3"] * (abun["O2"] + abun["O3"]))',
                                       'type': 'HII',
                                       'comment': 'Based on a grid of photoionization models'},
                         'PHCD07_14': {'elem': 'Ar',
                                       'atom': '(abun["Ar2"] + abun["Ar3"])',
                                       'icf': '(0.99 + 0.091 * abun["O2"] / (abun["O2"] + abun["O3"]) - 1.14 * (abun["O2"] / (abun["O2"] + abun["O3"]))**2. + 0.077 * (abun["O2"] / (abun["O2"] + abun["O3"]))**3.)**-1.',
                                       'type': 'HII',
                                       'comment': 'Based on a grid of photoionization models'},
                         'PHCD07_15': {'elem': 'Ar',
                                       'atom': 'abun["Ar3"]',
                                       'icf': '(0.15 + 2.39 * abun["O2"] / (abun["O2"] + abun["O3"]) - 2.64 * (abun["O2"] / (abun["O2"] + abun["O3"]))**2.)**-1.',
                                       'type': 'HII',
                                       'comment': 'Based on a grid of photoionization models'},
                         'PTPR92_21':{'elem': 'He',
                                       'atom': 'abun["He2"]',
                                       'icf': '(1 + abun["S2"] / (elem_abun["KB94_A36.10"] -  abun["S2"]))',
                                       'type': 'HII',
                                       'comment': 'Bsed on ionization potentials'},
                         'KB94_A1.6': {'elem': 'N',
                                     'atom': 'abun["N2"]',
                                     'icf': 'elem_abun["KB94_A6"]  / abun["O2"]',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A1.8': {'elem': 'N',
                                     'atom': 'abun["N2"]',
                                     'icf': 'elem_abun["KB94_A8"]  / abun["O2"]',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A1.10': {'elem': 'N',
                                     'atom': 'abun["N2"]',
                                     'icf': 'elem_abun["KB94_A10"]  / abun["O2"]',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A6': {'elem': 'O',
                                     'atom': 'abun["O2"] + abun["O3"] + abun["O4"]',
                                      'icf': '1 / (1 - 0.95 * abun["N5"] / (abun["N2"] + abun["N3"] + abun["N4"] + abun["N5"]))',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A8': {'elem': 'O',
                                     'atom': 'abun["O2"] + abun["O3"]',
                                     'icf': '(abun["N2"] + abun["N3"] + abun["N4"] + abun["N5"]) / (abun["N2"] + abun["N3"])',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models. To be used if N5 detected and O4 not detected'},
                         'KB94_A10': {'elem': 'O',
                                      'atom': 'abun["O2"] + abun["O3"]',
                                      'icf': '((abun["He2"] + abun["He3"]) / abun["He2"])**(2./3.)',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if only O2 and O3 detected'},
                         'KB94_A10.5': {'elem': 'C',
                                        'atom': 'abun["C2"] + abun["C3"] + abun["C4"] + abun["C5"]',
                                        'icf': '1',
                                        'type': 'PNe',
                                        'comment': 'Based on a grid of photoionization models. To be used if no He3 detected and C2, C3, and C4 detected'},
                         'KB94_A12': {'elem': 'C',
                                      'atom': 'abun["C3"] + abun["C4"]',
                                      'icf': '(abun["O2"] + abun["O3"]) / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if no C II lines detected'},
                         'KB94_A13.6': {'elem': 'C',
                                      'atom': 'abun["C3"]',
                                      'icf': 'elem_abun["KB94_A6"] / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if no C II lines detected'},
                         'KB94_A13.8': {'elem': 'C',
                                      'atom': 'abun["C3"]',
                                      'icf': 'elem_abun["KB94_A8"] / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if no C II lines detected'},
                         'KB94_A13.10': {'elem': 'C',
                                      'atom': 'abun["C3"]',
                                      'icf': 'elem_abun["KB94_A10"] / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if no C II lines detected'},
                         'KB94_A16': {'elem': 'C',
                                      'atom': 'abun["C2"] + abun["C3"] + abun["C4"]',
                                      'icf': '1 / (1 - 2.7 * abun["N5"] / (abun["N2"] + abun["N3"] + abun["N4"] + abun["N5"]))',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid for high excitation PNe if icf < 5'},
                         'KB94_A19': {'elem': 'C',
                                      'atom': 'abun["C2"] + abun["C3"] + abun["C4"]',
                                      'icf': '(1 + abun["N5"] / (abun["N2"] + abun["N3"] + abun["N4"]))',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid for extremely high excitation PNe if icf > 5'},
                         'KB94_A21': {'elem': 'C',
                                      'atom': 'abun["C2"] + abun["C3"] + abun["C4"]',
                                      'icf': '((abun["He2"] + abun["He3"]) / abun["He2"])**(1./3.)',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if He3 present and N5 absent'},
                         'KB94_A26': {'elem': 'C',
                                      'atom': 'abun["C2"] + abun["C3"] + abun["C4"]',
                                      'icf': '(abun["O2"] + abun["O3"]) / abun["O3"] * ((abun["He2"] + abun["He3"]) / abun["He2"])**(1./3.)',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A27': {'elem': 'Ne',
                                      'atom': 'abun["Ne3"] + abun["Ne5"]',
                                      'icf': '1.5',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A28.6':{'elem': 'Ne',
                                     'atom': 'abun["Ne3"]',
                                     'icf': 'elem_abun["KB94_A6"]  / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A28.8':{'elem': 'Ne',
                                     'atom': 'abun["Ne3"]',
                                     'icf': 'elem_abun["KB94_A8"]  / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A28.10':{'elem': 'Ne',
                                     'atom': 'abun["Ne3"]',
                                     'icf': 'elem_abun["KB94_A10"]  / abun["O3"]',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A30.6': {'elem': 'Ar',
                                     'atom': 'abun["Ar3"] + abun["Ar4"] + abun["Ar5"]',
                                     'icf': 'elem_abun["KB94_A6"]  / abun["O2"]',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A30.8': {'elem': 'Ar',
                                     'atom': 'abun["Ar3"] + abun["Ar4"] + abun["Ar5"]',
                                     'icf': 'elem_abun["KB94_A8"]  / abun["O2"]',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A30.10': {'elem': 'Ar',
                                     'atom': 'abun["Ar3"] + abun["Ar4"] + abun["Ar5"]',
                                     'icf': 'elem_abun["KB94_A10"]  / abun["O2"]',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A32': {'elem': 'Ar',
                                     'atom': 'abun["Ar3"]',
                                     'icf': '1.87',
                                     'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. To be used if both O4 and N5 detected'},
                         'KB94_A36.6':{'elem': 'S',
                                     'atom': 'abun["S2"] + abun["S3"]',
                                     'icf': ' (1-(1 - abun["O2"]/elem_abun["KB94_A6"])**3)**(-1./3.)',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A36.8':{'elem': 'S',
                                     'atom': 'abun["S2"] + abun["S3"]',
                                     'icf': ' (1-(1 - abun["O2"]/elem_abun["KB94_A8"])**3)**(-1./3.)',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KB94_A36.10':{'elem': 'S',
                                     'atom': 'abun["S2"] + abun["S3"]',
                                     'icf': ' (1-(1 - abun["O2"]/elem_abun["KB94_A10"])**3)**(-1./3.)',
                                      'type': 'PNe',
                                      'comment': 'Based on a grid of photoionization models. Valid if N4 or N5 not seen'},
                         'KH01_4a': {'elem': 'He',
                                     'atom': 'abun["He2"] + abun["He3"]',
                                     'icf': '1',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4b': {'elem': 'O',
                                     'atom': 'abun["O2"] + abun["O3"]',
                                     'icf': '(abun["He2"] + abun["He3"]) / abun["He2"]',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4c': {'elem': 'N',
                                     'atom': 'abun["N2"]',
                                     'icf': '(abun["O2"] + abun["O3"]) / abun["O2"] * (abun["He2"] + abun["He3"]) / abun["He2"]',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4d': {'elem': 'Ne',
                                     'atom': 'abun["Ne3"]',
                                     'icf': '(abun["O2"] + abun["O3"]) / abun["O3"] * (abun["He2"] + abun["He3"]) / abun["He2"]',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4e': {'elem': 'S',
                                     'atom': 'abun["S2"] + abun["S3"]',
                                     'icf': '10**(-0.017+0.18*np.log10(elem_abun["KH01_4b"]/ abun["O2"])-0.11*np.log10(elem_abun["KH01_4b"]/ abun["O2"])**2+0.072*np.log10(elem_abun["KH01_4b"]/ abun["O2"])**3)',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4f': {'elem': 'Cl',
                                     'atom': 'abun["Cl3"] + abun["Cl4"]',
                                     'icf': '(abun["He2"] + abun["He3"]) / abun["He2"]',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4g': {'elem': 'Ar',
                                     'atom': 'abun["Ar3"] + abun["Ar4"]',
                                     'icf': '(abun["He2"] + abun["He3"]) / abun["He2"] / (1 -  abun["N2"] / (elem_abun["KH01_4c"]))',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models'},
                         'KH01_4txt': {'elem': 'Ar',
                                     'atom': 'abun["Ar3"]',
                                     'icf': '1',
                                     'type': 'PNe',
                                     'comment': 'Based on a grid of photoionization models. To be used when log(O/O2) <= 0.6'},
                         'Ial06_16': {'elem': 'O',
                                      'atom': 'abun["O2"] + abun["O3"]',
                                      'icf': '1',
                                      'type': 'HII',
                                      'comment': 'Based on a grid of photoionization models. To be used if no 4686 detected'},
                         'Ial06_17': {'elem': 'O',
                                      'atom': 'abun["O2"] + abun["O3"]',
                                      'icf': '1 + 0.5 * abun["He3"] / (abun["He2"] + abun["He3"])',
                                      'type': 'HII',
                                      'comment': 'Based on a grid of photoionization models. To be used if 4686 detected'},
                         'GRal04_10a': {'elem': 'He',
                                      'atom': 'abun["He2"]',
                                      'icf': '1.05',
                                      'type': 'HII',
                                      'comment': 'Based on ionization potential. To be used if t2 = 0.00'},
                         'PC69_40': {'elem': 'Ne',
                                    'atom': 'abun["Ne3"]',
                                   'icf': '(abun["O2"] + abun["O3"]) / abun["O3"]',
                                   'type': 'HII',
                                   'comment': 'High ionization degree'},
                         'S78_265b': {'elem': 'Ne',
                                      'atom': 'abun["Ne3"]',
                                      'icf': '(abun["O2"] + abun["O3"]) / (abun["O3"] - 0.2 * abun["O2"])',
                                      'type': 'HII',
                                      'comment': 'Based on photoionization models'},
                         'RR04_1': {'elem': 'Fe',
                                      'atom': 'abun["Fe3"]',
                                      'icf': '(abun["O2"] / abun["O3"])**0.09 * (abun["O2"] + abun["O3"]) / abun["O2"]',
                                      'type': 'HII',
                                      'comment': 'Based on photoionization models and the assumption (not in the original paper) that O/H = (O+ + O++) / H+'}}
        
        Ial06 = [('18a', 'N', 'N2', (-0.825, 0.718, 0.853), 'v', 'low Z'),
                 ('18b', 'N', 'N2', (-0.809, 0.712, 0.852), 'v', 'int Z'),
                 ('18c', 'N', 'N2', (-1.476, 1.752, 0.688), 'v', 'high Z'),
                 ('19a', 'Ne', 'Ne3', (-0.385, 1.365, 0.022), 'w', 'low Z'),
                 ('19b', 'Ne', 'Ne3', (-0.405, 1.382, 0.021), 'w', 'int Z'),
                 ('19c', 'Ne', 'Ne3', (-0.591, 0.927, 0.546), 'w', 'high Z'),
                 ('21a', 'Cl', 'Cl3', ( 0.756, 0.648, 0.022), 'v', 'low Z'),
                 ('21b', 'Cl', 'Cl3', ( 0.814, 0.620, 0.128), 'v', 'int Z'),
                 ('21c', 'Cl', 'Cl3', ( 1.186, 0.357, 0.131), 'v', 'high Z'),
                 ('22a', 'Ar', 'Ar3', ( 0.278, 0.836, 0.121), 'v', 'low Z'),
                 ('22b', 'Ar', 'Ar3', ( 0.285, 0.833, 0.051), 'v', 'int Z'),
                 ('22c', 'Ar', 'Ar3', ( 0.517, 0.763, 0.042), 'v', 'high Z'),
                 ('24a', 'Fe', 'Fe3', ( 0.036,-0.146, 1.386), 'v', 'low Z'),
                 ('24b', 'Fe', 'Fe3', ( 0.301,-0.259, 1.367), 'v', 'int Z'),
                 ('24c', 'Fe', 'Fe3', (-1.377, 1.606, 1.045), 'v', 'high Z'),
                 ('20a', 'S', 'S2+S3', ( 0.121, 0.511, 0.161), 'v', 'low Z'),
                 ('20b', 'S', 'S2+S3', ( 0.155, 0.849, 0.062), 'v', 'int Z'),
                 ('20c', 'S', 'S2+S3', ( 0.178, 0.610, 0.153), 'v', 'high Z'),
                 ('23a', 'Ar', 'Ar3+Ar4', ( 0.158, 0.958, 0.004), 'v', 'low Z'),
                 ('23b', 'Ar', 'Ar3+Ar4', ( 0.104, 0.980, 0.001), 'v', 'int Z'),
                 ('23c', 'Ar', 'Ar3+Ar4', ( 0.238, 0.931, 0.004), 'v', 'high Z')]
        
        for item in Ial06:
            key = 'Ial06_' + item[0]
            atom = 'abun["' + item[2] + '"]'
            icf = self._calcIal06(item[3], item[4])
            self.all_icfs[key] = {'elem': item[1], 'atom': atom, 'icf': icf, 'type': 'HII', 'comment': item[5]}

        # Quickest way to account for the special case of Eqs. 20 and 23
        for key in ['Ial06_20a', 'Ial06_20b', 'Ial06_20c']:
            self.all_icfs[key]['atom'] = '(abun["S2"] + abun["S3"])'
        for key in ['Ial06_23a', 'Ial06_23b', 'Ial06_23c']:
            self.all_icfs[key]['atom'] = '(abun["Ar3"] + abun["Ar4"])'
        

        self.all_icf_refs = {'direct':{'ref': 'Direct determination by summing observed ions',
                                       'url':''},
                             'TPP77': {'ref': 'Torres-Peimbert and Peimbert 1977, RMAA, 2, 181',
                                       'url': 'http://adsabs.harvard.edu/abs/1977RMxAA...2..181T'},
                             'PHCD07': {'ref': 'Perez-Montero, Haegele, Contini, and Diaz 2007, MNRAS, 381, 125',
                                        'url': 'http://adsabs.harvard.edu/abs/2007MNRAS.381..125P'},
                             'KB94': {'ref': 'Kinsburgh & Barlow 1994, MNRAS, 271, 257',
                                      'url': 'http://adsabs.harvard.edu/abs/1994MNRAS.271..257K'},
                             'KH01': {'ref': 'Kwitter & Henry 2001, ApJ, 562, 804',
                                      'url': 'http://adsabs.harvard.edu/abs/2001ApJ...562..804K'},
                             'Ial06': {'ref': 'Izotov et al 2006, A&A, 448, 955',
                                       'url': 'http://adsabs.harvard.edu/abs/2006A%26A...448..955I'},
                             'PC67': {'ref': 'Peimbert & Costero 1969, BOTT, 5, 3',
                                      'url': 'http://adsabs.harvard.edu/abs/1969BOTT....5....3P'},
                             'S78': {'ref': 'Stasinska 1978, A&A, 66, 257',
                                     'url': 'http://adsabs.harvard.edu/abs/1978A%26A....66..257S'},
                             'RR04': {'ref': 'Rodriguez & Rubin 2004, IAUS, 217, 188',
                                      'url': 'http://adsabs.harvard.edu/abs/2004IAUS..217..188R'}}

    def _calcIal06(self, coeff, degree):
        """
        Compute the analytical expressions of the Ial06 paper
        
        """
        if degree == 'v':
            k1 = 'abun["O2"] / (abun["O2"] + abun["O3"])'
            k2 = '(abun["O2"] + abun["O3"]) / abun["O2"]'
        else:
            k1 = 'abun["O3"] / (abun["O2"] + abun["O3"])'
            k2 = '(abun["O2"] + abun["O3"]) / abun["O3"]'
        return '(' + str(coeff[0]) + ' * ' + k1 + ' + ' + str(coeff[1]) + ' + ' + str(coeff[2]) + ' * ' + k2 + ')'


    def _getAtomExp(self, label):
        """
        Clean the ionic factor expressions for display purposes
        
        """
        return self.all_icfs[label]['atom'].replace('abun["', '').replace('"]', '')


    def _getIcfExp(self, label):
        """
        Clean the icf expressions for display purposes

        """        
        return self.all_icfs[label]['icf'].replace('elem_abun["', '').replace('abun["', '').replace('"]', '')

    
    def getAvailableICFs(self, elem_list=ELEM_LIST):
        """ 
        Get a list of all the available ICFs for the specified elements. 
        Details can be obtained by invoking getReference('label') and getExpression('label')
        
        Parameters:
            - elem_list    list of selected elements (default: all PyNeb elements)

        """        
        if elem_list.__class__ is str:
            elem_list = [elem_list]
        icf_dict = {}
        for elem in elem_list:
            # Each element is associated to an icf_list which holds all the icfs for that element 
            icf_list = []
            for key in self.all_icfs.keys():
                if (self.all_icfs[key]['elem'] == elem):
                    icf_list.append(key)
            if len(icf_list) > 0:
                icf_dict[elem] = icf_list        
        return icf_dict
   
    
    def printAllICFs(self):
        """ 
        Print a list of all the available ICFs. Details can be obtained by 
            invoking getReference('label') and getExpression('label')
        
        Parameters:
            - elem_list    list of selected elements (default: all PyNeb elements)

        """        
        for label in self.all_icfs:
            print(label + ': elem = ' + self.all_icfs[label]['elem'] + '; atom = ' + 
                  self._getAtomExp(label) + '; type = ' + self.all_icfs[label]['type'])
            
   
    def addICF(self, label, elem, atom, icf, type='', comment='', ref=None, url=None):
        """
        Add a new icf
        
        Parameters:
            - label    a label which identifies the new ICF. The suggested format for the label is "R_E.N", 
                        where R is a reference to the paper, E to the equation in the paper and optionnaly 
                        N is an indication of the higher ion need to compute the icf.  
            - elem     element whose abundance is computed
            - atom     ion or ions whose abundance is multiplied by the icf to get the elemenmt abundance
            - icf      the correcting expression
            - type     object class to which the icf is appliable (e.g. "PNe", "HII")
            - comment  additional comment, relevant to icf usage
            - ref      bibliographic reference, if any
            - url      URL of the source paper, if any
            
        Usage:
            icf.addICF(label='TEST_1',
                        elem='Ne',
                        atom ='abun["Ne2"] + abun["Ne3"]',
                        icf='(abun["O2"] + abun["O3"]) / abun["O2"]',
                        type='PNe',
                        comment='',
                        ref='PyNeb international conference, 2025',
                        url='http://www.iac.es')

        """
        if label in self.all_icfs:
            pn.log_.warn('{0} is already an entry of the ICF label dictionary', calling = self.calling)
            return None
        else:
            self.all_icfs[label] = {'elem': elem,
                                    'atom': atom,
                                    'icf': icf,
                                    'type': type,
                                    'comment': comment}
            paper = label.split('_')[0]
            self.all_icf_refs[paper] = {'ref': ref, 'url': url}
    
    
    def printInfo(self, label, filter='licores'): 
        """ 
        Return complete information on the required icf or paper
        
        Parameters:
            label    label of selected ICF recipe or paper
            filter   string with initials of required fields (substring of 'licores'; tabla periodicaall by default)   
                 
        """        
        for item in self.all_icfs:
            if (label in item):
                print '------------------------------------------------------------------------'
                if ('l' in filter): print 'Label:', item
                if ('e' in filter): print 'Element:', self.all_icfs[item]['elem']
                if ('r' in filter): print 'Required ions:',  self._getAtomExp(item)
                if ('i' in filter): print 'ICF expression:', self._getIcfExp(item)
                if ('o' in filter): print 'Object class:', self.all_icfs[item]['type']
                if ('c' in filter): print 'Comments:', self.all_icfs[item]['comment']
                if ('s' in filter): print 'Source:', self.getReference(item)
   
    
    def getReference(self, label): 
        """ 
        Return the reference of the selected ICF recipe 
        
        Parameters:
            label    label of selected ICF recipe or paper

        """        
        paper = label.split('_')[0]
        return self.all_icf_refs[paper]['ref']
   
    
    def getURL(self, label): 
        """ 
        Return the ADS URL of the selected ICF recipe 
        
        Parameters:
            label    label of selected ICF recipe or paper

        """        
        paper = label.split('_')[0]
        return self.all_icf_refs[paper]['url']
   
    
    def getExpression(self, label): 
        """ 
        Return the analytical expression of the selected ICF 
        
        Parameters:
            label    label of selected ICF expression

        """
        
        elem = self.all_icfs[label]['elem']
        atom = self._getAtomExp(label)
        icf_factor = self._getIcfExp(label)
        if icf_factor != '1':
            return elem + " = (" + atom + ") * " + icf_factor
        else:
            return elem + " = " + atom
     
             
    def getType(self, label): 
        """ 
        Return the kind of object for which the selected ICF is suitable. 
        
        Parameters:
            label    label of selected ICF expression

        """
        return self.all_icfs[label]['type']
        

    def getComment(self, label): 
        """ 
        Return the comment associated to the selected ICF. 
        
        Parameters:
            label    label of selected ICF expression

        """
        return self.all_icfs[label]['comment']

    def getElemAbundance(self, atom_abun, icf_list=[], absentIon=np.nan):
        """
        Compute elemental abundances from ionic abundances. The complete iventory is printed through pn.ICF().printAllICFs().
        See the ICF class for more details.
        Store the result in ICF.elem_abund
        
        Parameters: 
           - atom_abun    a dictionary of ionic abundances
           - icf_list     a list of selected ICFs (default: all)
    
        Usage:
            atom_abun = {'O2': 0.001, 'O3': 0.002, 'Ne3': 1.2e-5}
            pn.getElemAbundance(atom_abun)
         
        """
        if type(icf_list) == type(''):
            icf_list = [icf_list]
        # List of all existing atoms. Necessary to initialize the ionic abundance dictionary
        atom_list = []
        for elem in ELEM_LIST:
            for spec in SPEC_LIST:
                atom_list.append(elem + str(spec)) 
        atom_list.append('He2')
        atom_list.append('He3')
    
        # Initialize the ionic abundances so that the code does not crash when a specific abundance is invoked
        abun = {}
        for atom in atom_list:
            # Set those abundances which are different from 0. These determine which ICFs can be computed        
            if atom in atom_abun:
                abun[atom] = atom_abun[atom]
            else:
                abun[atom] = absentIon
        self.abun = abun
        # Initialize the lists of elemental abundances
        self.icf_value = {}
        elem_abun = {}
        # Compute either all the available ICFs or just a selected subset of them
        if len(icf_list) == 0:
            icf_list = self.all_icfs.keys()

        do_one_more_pass = True
        i_pass = 0
        max_pass = 3
        while (do_one_more_pass and (i_pass < max_pass)):
            do_one_more_pass = False
            i_pass += 1
            for icf_label in icf_list:
                atom = self.all_icfs[icf_label]['atom']
                try:
                    atom_value = eval(atom)
                except:
                    pass
                if self.all_icfs[icf_label]['elem'] is not None:
                    elem = self.all_icfs[icf_label]['elem']
                    try:
                        icf_value = eval(self.all_icfs[icf_label]['icf'])
                        self.icf_value[icf_label] = icf_value
                        elem_abun[icf_label] = atom_value * icf_value
                    except:
                        do_one_more_pass = True
                        if i_pass == max_pass:
                            pn.log_.warn('{0} can not be evaluated'.format(self.all_icfs[icf_label]['icf']), calling = self.calling)

        self.elem_abun = elem_abun
        return self.elem_abun

    def test(self):
        """ 
        Test function for the ICF class 

        """
        label1 = 'Ial06_18a'
        label2 = 'TPP77_14'
        label3 = 'KH01_4b'
        label4 = 'PHCD07_13'
        print 'All the available ICFs, listed by element:'   
        print self.getAvailableICFs()
        print '\nAll the available ICFs, with some detail:'   
        print self.printAllICFs()
        print '\nAll the available ICFs for S and Ne:'   
        print self.getAvailableICFs(['S', 'Ne'])
        print '\nAnalytical expression for ' + label1 + ':'
        print self.getExpression(label1)
        print '\nBibliographic reference for ' + label2 + ':'
        print self.getReference(label2)
        print '\nURL for ' + label3 + ':'
        print self.getURL(label3)
        print '\nType of object to which ' + label4 + ' can be applied:'
        print self.getType(label4)
        print '\nAdditional details of ' + label4 + ':'
        print self.getComment(label4) 

        atom_abun = {}
        atom_abun['O2'] = 0.001
        atom_abun['O3'] = 0.002
        atom_abun['Ne2'] = 1.0e-4
        atom_abun['Ne3'] = 1.2e-5
        atom_abun['Ar3'] = 4.e-6
        atom_abun['Ar4'] = 1.e-6
        atom_abun['N2'] = 1.e-4
        atom_abun['He2'] = 1.e-1
        atom_abun['He3'] = 1.e-2
        atom_abun['He2'] = 1.e-1
        atom_abun['Cl3'] = 4.e-6
        atom_abun['Cl4'] = 1.e-6
        atom_abun['Ar3'] = 6.e-5
        atom_abun['Ar4'] = 5.e-7
        atom_abun['S3'] = 1.e-5

        self.getElemAbundance(atom_abun, icf_list=[label4])

