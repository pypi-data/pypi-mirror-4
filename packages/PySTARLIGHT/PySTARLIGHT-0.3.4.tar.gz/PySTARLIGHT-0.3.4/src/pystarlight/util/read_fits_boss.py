'''
 This routine reads the FITS file from BOSS/DR9 and
 correct the extracted spectrum:

 1) Galactic extinction (CCM) 
 2) Cosmological correction: l/(1+z) and F_l*(1+z)^3
 3) Vacumn 2 Air 
 4) Resampling

 Created on Nov 5, 2012
                                                author: Marcus
'''
####################################################################
def read_fits_boss(infile,outfile,EBV,R_V,redshift,redlaw,li,lf,dl):

    from pystarlight.util.redenninglaws import calc_redlaw
    from pystarlight.util.tools_read_fits_boss import mask2flag
    from pystarlight.util.StarlightUtils import ReSamplingMatrixNonUniform
    import pyfits
    import scipy
    import numpy as np
    import matplotlib.pyplot as plt

    # Reading the fits file
 
    hdulist = pyfits.open(infile)

    # Extract the spectrum

    data=hdulist[1].data

    # Description of FITS data:
    # http://data.sdss3.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/spectra/PLATE4/spec.html

    # Calculating extinction

    q=calc_redlaw(data['loglam'],R_V,redlaw) 
    A_V = EBV * R_V
    A_lambda = A_V * q

    # Lambda vector

    lorig = 10 ** data['loglam']

    # FLUX vector 

    forig = data['flux'] #  (units 10^-17 erg/s/A/cm2)

    # MASK vector

    mask = data['and_mask']

    # IVAR vector (1./sigma^2)
    # Some data['ivar'] <= 0. -> ivar = 1e-10 (avoid divergences) - error =  10^5 (!)

    ivar = [1e-10 if x <= 0. else x for x in data['ivar']]
    error_orig = 1./np.sqrt(ivar)

    # Flux corrections

    forig = forig * 10. ** ( 0.4 * A_lambda)
    forig = forig * ( 1.0 + redshift ) ** 3

    # Flux error corrections 

    error_orig = error_orig * 10. ** ( 0.4 * A_lambda)
    error_orig = error_orig * ( 1.0 + redshift ) ** 3

    # lambda correction (Cosmology)

    lorig = lorig / ( 1.0 + redshift )

    # Vacuum 2 Air (http://www.sdss3.org/dr9/spectro/spectro_basics.php#vacuum, Morton, 1991, ApJS, 77, 119)

    lorig = lorig / (1.0 + 2.735182E-4 + 131.4182 / lorig**2 + 2.76249E8 / lorig**4)

    # Mask2Flag (following Abilio's code)

    flag=mask2flag(mask)

    # Resampling

    lresam = np.arange(li,lf,dl) # New lambda-vector
    matrix = ReSamplingMatrixNonUniform(lorig, lresam) # Resampling Matrix
    fresam = np.dot(matrix, forig)  # Resampling flux
    error_resam = np.dot(matrix, error_orig) # Resampling error
    flag_resam = np.zeros(len(lresam)) # Resampling -> flag
    idx = np.argmax(matrix, axis=1) # Flag from largest contribution to the NEW pixel    
    flag_resam = flag[idx]

    return lresam,fresam,error_resam,flag_resam
