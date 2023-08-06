'''
Created on 12/Nov/2012

@author: Natalia Vale Asari
@note: This reads Abilio's paramters tables

'''

import os

import asciitable
from atpy.asciitables import read_ascii

def read_parameters(self, filename, include_names = None, exclude_names = None):
    '''
    Read Abilio's parameters table file

    Natalia@IoA - 12/Nov/2012

    Optional keyword Arguments:
        include_names - List of columns to read. (Default: None - reads all).
        exclude_names - List of columns to skip. (Default: None - reads all).

    Valid names: 'aid', 'plate', 'mjd', 'fiber', 'ra', 'dec', 'z',
                 'eClass', 'm_u', 'm_g', 'm_r', 'm_i', 'm_z', 'fm_u',
                 'fm_g', 'fm_r', 'fm_i', 'fm_z', 'Mu', 'Mg', 'Mr',
                 'Mi', 'Mz', 'SB_50_r', 'CI_r', 'petrorad_r',
                 'petroR50_r', 'petroR90_r', 'expAB_r', 'deVAB_r',
                 'D', 'DA', 'R50', 'R90', 'DL', 'log_L', 'Mr_fiber',
                 'log_L_fiber', 'Mz_fiber', 'log_L_fiber_z',
                 'petrorad_z', 'petroR50_z', 'petroR90_z', 'DA_z',
                 'R50_z', 'R90_z', 'flag_duplicate'
    '''
    
    self.reset()
    
    if not os.path.exists(filename):
        raise Exception('File not found: %s' % filename)
        
    self.table_name = 'parameters'
    self.keywords['filename'] = os.path.basename(filename)
        
    read_ascii(self, filename, guess=False, Reader=asciitable.CommentedHeader, include_names = include_names, exclude_names = exclude_names, names=('aid', 'plate', 'mjd', 'fiber', 'ra', 'dec', 'z', 'eClass', 'm_u', 'm_g', 'm_r', 'm_i', 'm_z', 'fm_u', 'fm_g', 'fm_r', 'fm_i', 'fm_z', 'Mu', 'Mg', 'Mr', 'Mi', 'Mz', 'SB_50_r', 'CI_r', 'petrorad_r', 'petroR50_r', 'petroR90_r', 'expAB_r', 'deVAB_r', 'D', 'DA', 'R50', 'R90', 'DL', 'log_L', 'Mr_fiber', 'log_L_fiber', 'Mz_fiber', 'log_L_fiber_z', 'petrorad_z', 'petroR50_z', 'petroR90_z', 'DA_z', 'R50_z', 'R90_z', 'flag_duplicate'))
    
