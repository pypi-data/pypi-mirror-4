'''
Created on May 21, 2012

@author: william
'''

import os

import numpy as np
import atpy

def readfilterfile(filterfile, norm=True):
    f = atpy.Table(filterfile , type='ascii', name=os.path.basename(filterfile).split('.')[0]) #Here I strip the directory name and the extension.
    f.keywords['filterfile'] = os.path.basename(filterfile) # Stripping the directory.
    f.rename_column('col1', 'lambda')
    f.rename_column('col2', 'transm')
    if (norm): f['transm'] = f['transm']/np.trapz(f['transm'], f['lambda'])
    return f