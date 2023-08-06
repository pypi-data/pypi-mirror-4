class CST(object):
    BOLTZMANN = 1.3806488e-16 # erg/K - NIST 2010
    CLIGHT = 2.99792458e10 # cm/s - NIST 2010
    HPLANCK = 6.62606957e-27 # erg s - NIST 2010
    EMASS = 9.10938291e-28 # g - NIST 2010
    ECHARGE = 1.602176565e-19 # Electron charge in Coulomb - NIST 2010
    PI = 3.141592653589793238462643
    BOLTZMANN_ANGK = (BOLTZMANN) / (HPLANCK * CLIGHT * 1.e8) # Boltzmann constant in (Ang * Kelvin) ** -1
    RYD = 109737.31568539 # Rydberg constant in cm^-1 - NIST 2010 
    RYD_EV = HPLANCK * CLIGHT * RYD * 1.e-7 / ECHARGE # infinite mass Rydberg in eV
    RYD_ANG = 1.e8 / RYD # infinite mass Rydberg in A
    KCOLLRATE = pow((2 * PI / BOLTZMANN), 0.5) * pow(HPLANCK / (2 * PI), 2) / pow(EMASS, 1.5) # constant of collisional rate equation

IP = {}
IP['H2'] = 13.598
IP['C1'] = 0.0
IP['C2'] = 11.26
IP['C3'] = 24.38
IP['C4'] = 47.89
IP['C5'] = 64.49
IP['N1'] = 0.0
IP['N2'] = 14.53
IP['N3'] = 29.60
IP['N4'] = 47.45
IP['N5'] = 77.47
IP['O1'] = 0.0
IP['O2'] = 13.62
IP['O3'] = 35.12
IP['O4'] = 54.94
IP['S1'] = 0.0
IP['S2'] = 10.36
IP['S3'] = 23.34
IP['S4'] = 34.79
IP['S5'] = 47.22
IP['Ne1'] = 0.0
IP['Ne2'] = 21.56
IP['Ne3'] = 40.96
IP['Ne4'] = 63.45
IP['Ne5'] = 97.12
IP['Ne6'] = 126.21
IP['Cl1'] = 0.0
IP['Cl2'] = 12.97
IP['Cl3'] = 23.81
IP['Cl4'] = 39.61
IP['Ar1'] = 0.0
IP['Ar2'] = 15.76
IP['Ar3'] = 27.63
IP['Ar4'] = 40.74
IP['Ar5'] = 59.81
IP['Ba1'] = 0.00
IP['Ba2'] = 5.21
IP['Ba4'] = 35.84
IP['Xe1'] = 0.00
IP['Xe3'] = 20.98
IP['Xe4'] = 31.05
IP['Mg1'] = 0.00
IP['Mg2'] = 7.65
IP['Mg3'] = 15.03
IP['Mg4'] = 80.14
IP['Mg5'] = 109.26
IP['Fe1'] = 0.0
IP['Fe2'] = 7.90 
IP['Fe3'] = 16.188
IP['Fe4'] = 30.652
IP['Fe5'] = 54.8
IP['Fe6'] = 75.0

sym2name = {
            'H': 'hydrogen',
            'He': 'helium',
            'B': 'boron',
            'C': 'carbon',
            'N': 'nitrogen',
            'O': 'oxygen',
            'F': 'fluorine',
            'Ne': 'neon',
            'Na': 'sodium',
            'Mg': 'magnesium',
            'Al': 'aluminium',
            'Si': 'silicon',
            'P': 'phosphorus',
            'S': 'sulfur',
            'Cl': 'chlorine',
            'Ar': 'argon',
            'K': 'potassium',
            'Ca': 'calcium',
            'Cr': 'chromium',
            'Fe': 'iron',
            'Co': 'cobalt',
            'Ni': 'nickel',
            'Cu': 'copper',
            'Zn': 'zinc',
            'Kr': 'krypton',
            'Ag': 'silver',
            'Au': 'gold',
            'Ba': 'barium',
            'Xe': 'xenon'
            }

gsDict = {
            'p1': ['C2', 'N3', 'O4', 'Si2', 'S4', 'Se4'],
            'p2': ['N2', 'O3', 'Ne5', 'S3', 'Cl4', 'Ar5', 'Se3', 'Kr5'],
            'p3': ['N1', 'O2', 'Ne4', 'Na5', 'S2', 'Cl3', 'Ar4', 'K5', 'Se2', 'Kr4', 'Xe4'],
            'p4': ['O1', 'Ne3', 'Na4', 'Mg5', 'Cl2', 'Ar3', 'K4', 'Ca5', 'Kr3', 'Xe3'],
            'p5': ['Ne2', 'Na3', 'Si6', 'Cl1', 'Ar2', 'K3', 'Ba4'],
            's1': ['C4', 'N5', 'Ba2'],
            's2': ['C3', 'N4', 'O5', 'Si3']
            }


_predefinedDataFileDict = {'IRAF_09':
                           {'H1': {'rec': 'h_i_rec_SH95.fits'},
                            'He1': {'rec': 'he_i_rec_P12corr13.fits'},
                            'He2': {'rec': 'he_ii_rec_SH95.fits'},
                            'Al2': {'atom': 'al_ii_atom_JSP86-HK87-VVF96-KS86.fits', 'coll': 'al_ii_coll_KHAF92-TBK85-TBK84.fits'},
                            'Ar2': {'atom': 'ar_ii_atom_Bal06.fits', 'coll': 'ar_ii_coll_PB95.fits'},
                            'Ar3': {'atom': 'ar_iii_atom_B60-M83-KS86.fits', 'coll': 'ar_iii_coll_GMZ95.fits'},
                            'Ar4': {'atom': 'ar_iv_atom_B60-MZ82a-KS86.fits', 'coll': 'ar_iv_coll_ZBL87.fits'},
                            'Ar5': {'atom': 'ar_v_atom_B60-LL93-MZ82-KS86.fits', 'coll': 'ar_v_coll_GMZ95.fits'},
                            'C1': {'atom': 'c_i_atom_B60-NS84-FFS85.fits', 'coll': 'c_i_coll_JBK87-PA76.fits'},
                            'C2': {'atom': 'c_ii_atom_MG93-PP95-NS81-GMZ98.fits', 'coll': 'c_ii_coll_BP92.fits'},
                            'C3': {'atom': 'c_iii_atom_BK93-G83-NS78-WFD96.fits', 'coll': 'c_iii_coll_Bal85.fits'},
                            'Ca5': {'atom': 'ca_v_atom_B60-M83-KS86.fits', 'coll': 'ca_v_coll_GMZ95.fits'},
                            'Cl3': {'atom': 'cl_iii_atom_M83-KS86.fits', 'coll': 'cl_iii_coll_BZ89.fits'},
                            'Cl4': {'atom': 'cl_iv_atom_B60-H85-KS86-MZ82-EM84.fits', 'coll': 'cl_iv_coll_GMZ95.fits'},
                            'K4': {'atom': 'k_iv_atom_B60-M83-KS86.fits', 'coll': 'k_iv_coll_GMZ95.fits'},
                            'K5': {'atom': 'k_v_atom_B60-M83-KS86.fits', 'coll': 'k_v_coll_BZL88.fits'},
                            'Mg5': {'atom': 'mg_v_atom_Bal06-B60-GMZ97.fits', 'coll': 'mg_v_coll_BZ94.fits'},
                            'Mg7': {'atom': 'mg_vii_atom_Bal06-B60-BD95-GMZ97.fits', 'coll': 'mg_vii_coll_LB94-U.fits'},
                            'N1': {'atom': 'n_i_atom_B60-KS86-F75-WFD96.fits', 'coll': 'n_i_coll_PA76-DMR76.fits'},
                            'N2': {'atom': 'n_ii_atom_MG93-B60-PP95-GMZ97-WFD96.fits', 'coll': 'n_ii_coll_LB94.fits'},
                            'N3': {'atom': 'n_iii_atom_MG93-BFFJ95-BP92-GMZ98.fits', 'coll': 'n_iii_coll_BP92.fits'},
                            'N4': {'atom': 'n_iv_atom_NS79-WFD96.fits', 'coll': 'n_iv_coll_RBHB94.fits'},
                            'Na4': {'atom': 'na_iv_atom_Bal06-B60-GMZ97.fits', 'coll': 'na_iv_coll_BZ94.fits'},
                            'Na6': {'atom': 'na_vi_atom_Bal06-B60-GMZ97.fits', 'coll': 'na_vi_coll_LB94.fits'},
                            'Ne2': {'atom': 'ne_ii_atom_Bal06.fits', 'coll': 'ne_ii_coll_GMB01.fits'},
                            'Ne3': {'atom': 'ne_iii_atom_Bal06-B60-GMZ97.fits', 'coll': 'ne_iii_coll_BZ94.fits'},
                            'Ne4': {'atom': 'ne_iv_atom_E84-BBZ89-BK88.fits', 'coll': 'ne_iv_coll_G81.fits'},
                            'Ne5': {'atom': 'ne_v_atom_Bal06-B60-M83-GMZ97-U-BD93.fits', 'coll': 'ne_v_coll_LB94.fits'},
                            'Ne6': {'atom': 'ne_vi_atom_Bal06-KS86-MVGK95.fits', 'coll': 'ne_vi_coll_ZGP94.fits'},
                            'O1': {'atom': 'o_i_atom_M83b-WFD96.fits', 'coll': 'o_i_coll_BK95.fits'},
                            'O2': {'atom': 'o_ii_atom_B60-KS86-F75-WFD96.fits', 'coll': 'o_ii_coll_P76-McLB93-v1.fits'},
                            'O3': {'atom': 'o_iii_atom_MG93-B60-M85-GMZ97-NIST.fits', 'coll': 'o_iii_coll_LB94.fits'},
                            'O4': {'atom': 'o_iv_atom_U-U-GMZ98b.fits', 'coll': 'o_iv_coll_BP92.fits'},
                            'O5': {'atom': 'o_v_atom_BJ68-B80-H80-NS79.fits', 'coll': 'o_v_coll_BBDK85.fits'},
                            'S2': {'atom': 's_ii_atom_B60-VVF96-KHOC93.fits', 'coll': 's_ii_coll_RBS96.fits'},
                            'S3': {'atom': 's_iii_atom_B60-Sal84-LL93-HSC95-MZ82b-KS86.fits', 'coll': 's_iii_coll_GMZ95.fits'},
                            'S4': {'atom': 's_iv_atom_BDF80-JKD86-DHKD82.fits', 'coll': 's_iv_coll_DHKD82.fits'},
                            'Si2': {'atom': 'si_ii_atom_Dal91-BL93-CSB93-N77.fits', 'coll': 'si_ii_coll_DK91.fits'},
                            'Si3': {'atom': 'si_iii_atom_WL95-M83-OKH88-FW90-KS86.fits', 'coll': 'si_iii_coll_DK94.fits'},
                            },
                           'PYNEB_13_01':
                            {'H1': {'rec': 'h_i_rec_SH95.fits'},
                             'He1': {'rec': 'he_i_rec_P12corr13.fits'},
                             'He2': {'rec': 'he_ii_rec_SH95.fits'},
                             'Al2': {'atom': 'al_ii_atom_JSP86-HK87-VVF96-KS86.fits', 'coll': 'al_ii_coll_KHAF92-TBK85-TBK84.fits'},
                             'Ar2': {'atom': 'ar_ii_atom_Bal06.fits', 'coll': 'ar_ii_coll_PB95.fits'},
                             'Ar3': {'atom': 'ar_iii_atom_B60-M83-KS86.fits', 'coll': 'ar_iii_coll_GMZ95.fits'},
                             'Ar4': {'atom': 'ar_iv_atom_MZ82.fits', 'coll': 'ar_iv_coll_RB97.fits'},
                             'Ar5': {'atom': 'ar_v_atom_B60-LL93-MZ82-KS86.fits', 'coll': 'ar_v_coll_GMZ95.fits'},
                             'Ba2': {'atom': 'ba_ii_atom_C04.fits', 'coll': 'ba_ii_coll_SB98.fits'},
                             'Ba4': {'atom': 'ba_iv_atom_SC10-BHQZ95.fits', 'coll': 'ba_iv_coll_SB98.fits'},
                             'C1': {'atom': 'c_i_atom_B60-NS84-FFS85.fits', 'coll': 'c_i_coll_JBK87-PA76.fits'},
                             'C2': {'atom': 'c_ii_atom_MG93-PP95-NS81-GMZ98.fits', 'coll': 'c_ii_coll_BP92.fits'},
                             'C3': {'atom': 'c_iii_atom_BK93-G83-NS78-WFD96.fits', 'coll': 'c_iii_coll_Bal85.fits'},
                             'C4': {'atom': 'c_iv_atom_M83-WFD96.fits', 'coll': 'c_iv_coll_AK04.fits'},
                             'Ca5': {'atom': 'ca_v_atom_B60-M83-KS86.fits', 'coll': 'ca_v_coll_GMZ95.fits'},
                             'Cl2': {'atom': 'cl_ii_atom_RK74-M83.fits', 'coll': 'cl_ii_coll_T04.fits'},
                             'Cl3': {'atom': 'cl_iii_atom_M83-KS86.fits', 'coll': 'cl_iii_coll_BZ89.fits'},
                             'Cl4': {'atom': 'cl_iv_atom_B60-H85-KS86-MZ82-EM84.fits', 'coll': 'cl_iv_coll_GMZ95.fits'},
                             'Fe3': {'atom': 'fe_iii_atom_Q96.fits', 'coll': 'fe_iii_coll_Q96.fits'},
                             'K4': {'atom': 'k_iv_atom_B60-M83-KS86.fits', 'coll': 'k_iv_coll_GMZ95.fits'},
                             'K5': {'atom': 'k_v_atom_B60-M83-KS86.fits', 'coll': 'k_v_coll_BZL88.fits'},
                             'Mg5': {'atom': 'mg_v_atom_Bal06-B60-GMZ97.fits', 'coll': 'mg_v_coll_BZ94.fits'},
                             'Mg7': {'atom': 'mg_vii_atom_Bal06-B60-BD95-GMZ97.fits', 'coll': 'mg_vii_coll_LB94-U.fits'},
                             'N1': {'atom': 'n_i_atom_B60-KS86-F75-WFD96.fits', 'coll': 'n_i_coll_PA76-DMR76.fits'},
                             'N2': {'atom': 'n_ii_atom_MG93-B60-PP95-GMZ97-WFD96.fits', 'coll': 'n_ii_coll_T11.fits'},
                             'N3': {'atom': 'n_iii_atom_MG93-BFFJ95-BP92-GMZ98.fits', 'coll': 'n_iii_coll_BP92.fits'},
                             'N4': {'atom': 'n_iv_atom_NS79-WFD96.fits', 'coll': 'n_iv_coll_RBHB94.fits'},
                             'Na4': {'atom': 'na_iv_atom_Bal06-B60-GMZ97.fits', 'coll': 'na_iv_coll_BZ94.fits'},
                             'Na6': {'atom': 'na_vi_atom_Bal06-B60-GMZ97.fits', 'coll': 'na_vi_coll_LB94.fits'},
                             'Ne2': {'atom': 'ne_ii_atom_Bal06.fits', 'coll': 'ne_ii_coll_GMB01.fits'},
                             'Ne3': {'atom': 'ne_iii_atom_Bal06-B60-GMZ97.fits', 'coll': 'ne_iii_coll_McLB00.fits'},
                             'Ne4': {'atom': 'ne_iv_atom_E84-BBZ89-BK88.fits', 'coll': 'ne_iv_coll_G81.fits'},
                             'Ne5': {'atom': 'ne_v_atom_Bal06-B60-M83-GMZ97-U-BD93.fits', 'coll': 'ne_v_coll_LB94.fits'},
                             'Ne6': {'atom': 'ne_vi_atom_Bal06-KS86-MVGK95.fits', 'coll': 'ne_vi_coll_ZGP94.fits'},
                             'O1': {'atom': 'o_i_atom_M83b-WFD96.fits', 'coll': 'o_i_coll_BK95.fits'},
                             'O2': {'atom': 'o_ii_atom_B60-KS86-F75-Z82-WFD96.fits', 'coll': 'o_ii_coll_P06-T07.fits'},
                             'O3': {'atom': 'o_iii_atom_B60-M85-WFD96-SZ00-NIST.fits', 'coll': 'o_iii_coll_AK99.fits'},
                             'O4': {'atom': 'o_iv_atom_U-U-GMZ98b.fits', 'coll': 'o_iv_coll_BP92.fits'},
                             'O5': {'atom': 'o_v_atom_BJ68-B80-H80-NS79.fits', 'coll': 'o_v_coll_BBDK85.fits'},
                             'S2': {'atom': 's_ii_atom_B60-VVF96-PKW09.fits', 'coll': 's_ii_coll_TZ10.fits'},
                             'S3': {'atom': 's_iii_atom_B60-Sal84-PKW09.fits', 'coll': 's_iii_coll_GMZ95.fits'},
                             'S4': {'atom': 's_iv_atom_BDF80-JKD86-DHKD82.fits', 'coll': 's_iv_coll_DHKD82.fits'},
                             'Si2': {'atom': 'si_ii_atom_Dal91-BL93-CSB93-N77.fits', 'coll': 'si_ii_coll_DK91.fits'},
                             'Si3': {'atom': 'si_iii_atom_WL95-M83-OKH88-FW90-KS86.fits', 'coll': 'si_iii_coll_DK94.fits'},
                             'Xe3': {'atom': 'xe_iii_atom_M93-BHQZ95.fits', 'coll': 'xe_iii_coll_SB98.fits'},
                             'Xe4': {'atom': 'xe_iv_atom_S04-BHQZ95.fits', 'coll': 'xe_iv_coll_SB98.fits'}
                             }
                           } 
