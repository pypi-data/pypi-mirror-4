'''
Created on May 17, 2012

@author: william
@summary: This set of classes does the STARLIGHT diverse post-processing calculations such as those that are on the old SYN* tables. 
'''

import os
import inspect

import numpy as np
import pyfits as pf

import pystarlight
from pystarlight.util.redenninglaws import calc_redlaw
from pystarlight.io.readfilter import readfilterfile
from pystarlight.util.constants import d_sun, L_sun


class popvec(object):
    '''
        This class does the population vector related calculations, such as at_flux, aZ_flux, etc ... 
    '''

    def __init__(self, ts):
        '''
        @param ts: atpy STARLIGHT instance
        '''
        self.ts = ts
        
    def at_flux(self):
        '''
        Mean Stellar Age (Light fraction)
        Equation (2), Cid Fernandes et al 2005.
            LATEX:
                \begin{equation}
                \rm at\_flux =
                \langle \log t_\star \rangle_{\rm Light} = 
                \frac{\sum x_j \log t_j}{\sum x_j}
                \end{equation}
        '''
        return np.sum( (self.ts.population.popx/np.sum(self.ts.population.popx)) * np.log10(self.ts.population.popage_base) )
    
    def at_mass(self):
        '''
        Mean Stellar Age (Stellar mass fraction)
        Equation (3), Cid Fernandes et al 2005.
            LATEX:
                \begin{equation}
                \rm at\_mass = 
                \langle \log t_\star \rangle_{\rm Mass} = 
                \frac{\sum \mu^{cor}_j \log t_j}{\sum \mu^{cor}_j}
                \end{equation}
        '''
        return np.sum( (self.ts.population.popmu_cor/np.sum(self.ts.population.popmu_cor)) * np.log10(self.ts.population.popage_base) )
    
    def am_flux(self, Zsun=0.02):
        '''
        Mean Stellar Metallicity (Light Fraction)
        Equation (4), Cid Fernandes et al 2005. 
            LATEX:
                \begin{equation}
                \rm am\_flux = 
                \langle Z_\star/Z_\odot \rangle_{\rm Light} = 
                \frac{\sum x_j Z_j/Z_\odot}{\sum x_j}
                \end{equation}
        '''
        return np.sum( (self.ts.population.popx/np.sum(self.ts.population.popx)) * self.ts.population.popZ_base/Zsun) 
    
    def am_mass(self, Zsun=0.02):
        '''
        Mean Stellar Metallicity (Stellar Mass Fraction)
        Equation (5), Cid Fernandes et al 2005.
            LATEX:
                \begin{equation}
                \rm am\_mass = 
                \langle Z_\star/Z_\odot \rangle_{\rm Mass} = 
                \frac{\sum \mu^{cor}_j Z_j/Z_\odot}{\sum \mu^{cor}_j}
                \end{equation}
        '''
        return np.sum( (self.ts.population.popmu_cor/np.sum(self.ts.population.popmu_cor)) * self.ts.population.popZ_base/Zsun)
    
    
class massvec(object):
    '''
        This class calculates mass-related stuff such as M/L
    '''
    
    def __init__(self, ts, base, redlaw='CCM'):
        '''
        @param ts: atpy STARLIGHT instance
        @param tb: atpy BaseDir instance
        '''
        self.ts = ts
        self.base = base
        self.redlaw = redlaw
      
    def read_filterfile(self):
        '''
            This will return the t_lambda (i.e. the NORMALIZED filter transmission curve)
        '''
       
        self.filtercurve = readfilterfile(self.filterfile, norm=True) # Reads the  filterfile
         
    def calc_LsunFilter(self):
        '''
            Calculates the solar luminosity on self.filter in the same way as Bruzual does in Galaxev.
                    NVA helped on this!
        '''
        #The solar spectra is located on the data directory which comes with the pystarlight distribution:
        data_dir = os.path.dirname(inspect.getfile(pystarlight))+'/../../data/solar_spectrum/'
        sun_spec, header_sun_spec = pf.getdata(data_dir+'sun_reference_stis_001.fits', header=True) #Read Solar Spectrum
        Lsun_corr = np.interp(self.filtercurve['lambda'], sun_spec['WAVELENGTH'], sun_spec['FLUX']) # Correct to filter lambdas
        self.LsunFilter = np.trapz(Lsun_corr * self.filtercurve['transm'], self.filtercurve['lambda']) # Calc solar luminosity (ergs/s/cm2)
        self.LsunFilter = ( self.LsunFilter * 4*np.pi * d_sun**2 ) / L_sun # Convert: erg/s/cm2 --> L_sun
        
    def L2Mcor_spec(self):
        ''' 
            Calculates the mass-to-light ratio for a Starlight ts output spectra.
            Uses the mu_cor vector which means the "corrected" mass vector.
            This correction takes in account the returned mass, so the mass here is the mass ACTUALLY in stars.
        '''
        popmu_cor = self.ts.population.popmu_cor / np.sum(self.ts.population.popmu_cor) # Normalize to 1!!!
        q_redlaw = calc_redlaw(self.base.l_ssp__l, 3.1, redlaw=self.redlaw)
        popMstars__tZ = self.base.from_j_to_tZ(self.ts.population.popMstars)
        popmu_cor__tZ = self.base.from_j_to_tZ(popmu_cor)
        L2M_cor = (popmu_cor__tZ * (self.base.f_ssp__tZl / popMstars__tZ) * 10.**(-.4 * self.ts.keywords['A_V'] * q_redlaw)).sum(axis=1).sum(axis=0)
        return L2M_cor
    
    def M2Lcor_filter(self, filterfile):
        '''
            Calculates Mass-to-Light Ratio for a given filter.
            Uses M2Lcor_spec to calculate the spectra and, then, apply filter curves.
        '''
        L2M_spec = self.L2Mcor_spec() # Eval L2M for the spectra.
        self.filterfile = filterfile # Read filter
        self.read_filterfile() # --
        #Define s.e.d. lambda and flux on the filter response window
        L2M_spec = np.interp(self.filtercurve['lambda'], self.base.l_ssp__l, L2M_spec)
        L2M_filter = np.trapz(L2M_spec * self.filtercurve['transm'], self.filtercurve['lambda'])
        self.calc_LsunFilter() #Calc Lsun on filter
        L2M_filter = L2M_filter / self.LsunFilter # Correct by Solar luminosity in the filter
        
        return 1.0 / L2M_filter