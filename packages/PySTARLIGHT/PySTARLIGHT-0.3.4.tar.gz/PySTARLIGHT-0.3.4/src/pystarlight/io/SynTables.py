'''
Created on 17/Sep/2012

@author: William Schoenell
@note: This reads tables SYN01 to SYN04 from Cid's Fortran code SC5-MakeTables

'''

import os
import gzip
import bz2

import asciitable
from atpy.asciitables import read_ascii

def read_SYN01(self, filename, include_names = None, exclude_names = None):
    '''
    Read Cids's synthesis SYN01 table file

    William@UFSC - 18/Sep/2012

    Optional keyword Arguments:
        include_names - List of columns to read. (Default: None - reads all).
        exclude_names - List of columns to skip. (Default: None - reads all).
    Valid names: 'id', 'x_PL', 'x_Y', 'x_I', 'x_O', 'mu_Y', 'mu_I', 'mu_O', 'A_V',
                 'v0', 'vd', 'chi2', 'adev', 'SN_w', 'SN_n', 'OSN_w', 'OSN_n',
                 'Nn0', 'NOl_eff', 'Nl_eff'
    
    '''
    
    self.reset()
    
    if not os.path.exists(filename):
        raise Exception('File not found: %s' % filename)

    if filename.endswith('.gz'):
        f = gzip.GzipFile(filename)
    elif filename.endswith('.bz2'):
        f = bz2.BZ2File(filename)
    else:
        f = open(filename)
        
    self.table_name = 'SYN01'
    self.keywords['filename'] = os.path.basename(filename)
        
    read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader, include_names = include_names, exclude_names = exclude_names, names=('id', 'x_PL', 'x_Y', 'x_I', 'x_O', 'mu_Y', 'mu_I', 'mu_O', 'A_V', 'v0', 'vd', 'chi2', 'adev', 'SN_w', 'SN_n', 'OSN_w', 'OSN_n', 'Nn0', 'NOl_eff', 'Nl_eff'))
    
def read_SYN02(self, filename, include_names = None, exclude_names = None):
    '''
    Read Cids's synthesis SYN02 table file

    William@UFSC - 18/Sep/2012

    Optional keyword Arguments:
        include_names - List of columns to read. (Default: None - reads all).
        exclude_names - List of columns to skip. (Default: None - reads all).
    Valid names: 'id', 'at_flux', 'at_mass', 'aZ_flux', 'aZ_mass', 'am_flux',
                 'am_mass', 'st_flux', 'st_mass', 'sZ_flux', 'sZ_mass', 'sm_flux',
                 'sm_mass', 'i_boc', 'boc_age', 'boc_Z', 'boc_chi2', 'boc_adev', 'boc_AV'
    
    '''    
    self.reset()
        
    if not os.path.exists(filename):
        raise Exception('File not found: %s' % filename)

    if filename.endswith('.gz'):
        f = gzip.GzipFile(filename)
    elif filename.endswith('.bz2'):
        f = bz2.BZ2File(filename)
    else:
        f = open(filename)
        
    self.table_name = 'SYN02'
    self.keywords['filename'] = os.path.basename(filename)
        
    read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader, include_names = include_names, exclude_names = exclude_names, names=('id', 'at_flux', 'at_mass', 'aZ_flux', 'aZ_mass', 'am_flux', 'am_mass', 'st_flux', 'st_mass', 'sZ_flux', 'sZ_mass', 'sm_flux', 'sm_mass', 'i_boc', 'boc_age', 'boc_Z', 'boc_chi2', 'boc_adev', 'boc_AV'))
    
    
    
def read_SYN03(self, filename, include_names = None, exclude_names = None):
    '''
    Read Cids's synthesis SYN03 table file

    William@UFSC - 18/Sep/2012

    Optional keyword Arguments:
        include_names - List of columns to read. (Default: None - reads all).
        exclude_names - List of columns to skip. (Default: None - reads all).
    Valid names: 'id', 'M2L_u', 'M2L_g', 'M2L_r', 'M2L_i', 'M2L_z', 'M2L_B', 'M2L_V', 'M2L_BOL'
    
    '''     

    self.reset()
    
    if not os.path.exists(filename):
        raise Exception('File not found: %s' % filename)

    if filename.endswith('.gz'):
        f = gzip.GzipFile(filename)
    elif filename.endswith('.bz2'):
        f = bz2.BZ2File(filename)
    else:
        f = open(filename)
        
    self.table_name = 'SYN03'
    self.keywords['filename'] = os.path.basename(filename)
        
    read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader, include_names = include_names, exclude_names = exclude_names, names=('id', 'M2L_u', 'M2L_g', 'M2L_r', 'M2L_i', 'M2L_z', 'M2L_B', 'M2L_V', 'M2L_BOL'))
    
    
    
    
def read_SYN04(self, filename, include_names = None, exclude_names = None):
    '''
    Read Cids's synthesis SYN04 table file

    William@UFSC - 18/Sep/2012

    Optional keyword Arguments:
        include_names - List of columns to read. (Default: None - reads all).
        exclude_names - List of columns to skip. (Default: None - reads all).
    Valid names: 'id', 'Mcor_fib', 'Mini_fib', 'Mret_fib', 'Mcor_gal', 'Mini_gal',
                 'Mret_gal', 'Den_Mcor', 'Den_Mini', 'Mpho_gal', 'fobs_norm',
                 'Flux_tot', 'log_Lnorm', 'log_Ltot', 'z', 'DL_Mpc', 'FibCor',
                 'HLR_kpc', 'Mz_gal', 'tz_lookback'
    
    '''
        
    self.reset()
    
    if not os.path.exists(filename):
        raise Exception('File not found: %s' % filename)

    if filename.endswith('.gz'):
        f = gzip.GzipFile(filename)
    elif filename.endswith('.bz2'):
        f = bz2.BZ2File(filename)
    else:
        f = open(filename)
        
    self.table_name = 'SYN04'
    self.keywords['filename'] = os.path.basename(filename)
        
    read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader, include_names = include_names, exclude_names = exclude_names, names=('id', 'Mcor_fib', 'Mini_fib', 'Mret_fib', 'Mcor_gal', 'Mini_gal', 'Mret_gal', 'Den_Mcor', 'Den_Mini', 'Mpho_gal', 'fobs_norm', 'Flux_tot', 'log_Lnorm', 'log_Ltot', 'z', 'DL_Mpc', 'FibCor', 'HLR_kpc', 'Mz_gal', 'tz_lookback'))
    
    
    
    