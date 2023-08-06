'''
Created on May 17, 2012

@author: william
'''

import numpy as np
import atpy
import os

def read(self, basefile, basedir='', read_basedir=False):
    '''
        Reads StarlightChains_v04.for basefile
        @param basefile: Starlight input basefile.
    '''
    self.reset()
    self.keywords['arq_base'] = os.path.basename(basefile)
    
    dt = np.dtype([ ('sspfile', 'S60'), ('age_base', '>f8'), ('Z_base', '>f8'), ('Mstars', '>f8'), ('YA_V', '>i4'), ('aFe', '>f8') ])
    bdata = np.loadtxt( basefile, dtype=dt, skiprows=1, usecols=(0,1,2,4,5,6) )
    
    self.table_name = 'basefiles'
    self.add_column('sspfile', bdata['sspfile'])
    self.add_column('age_base', bdata['age_base'])
    self.add_column('Z_base', bdata['Z_base'])
    self.add_column('Mstars', bdata['Mstars'])
    self.add_column('YA_V', bdata['YA_V'])
    self.add_column('aFe', bdata['aFe'])
    
    # If read_basedir is True, reads also the basedir spectra:
    if(read_basedir):
        f = []
        l = []
        for ssp_file in self.sspfile:
            t = atpy.Table(os.path.join(basedir, ssp_file) , type='ascii', name='SSP_spec', names=('wavelength', 'f_ssp')) #Here we remove any extension to the filename by split()
            f.append(t.f_ssp)
            l.append(t.wavelength)
        self.add_column('f_ssp', f)
        self.add_column('l_ssp', l)
