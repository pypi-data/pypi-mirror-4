'''
Created on May 21, 2012

@author: william
@summary: Calculates q_norm to a set of reddening laws. 
'''
import numpy as np


def Cardelli_RedLaw(l,R_V=3.1):
    '''
        @summary: Calculates q(lambda) to the Cardelli, Clayton & Mathis 1989 reddening law. Converted to Python from STALIGHT.
        @param l: Wavelenght vector (Angstroms)
        @param R_V: R_V factor. Default is R_V = 3.1.
    '''
# ###########################################################################
#     q = A_lambda / A_V for Cardelli et al reddening law
#     l = lambda, in Angstrons
#     x = 1 / lambda in 1/microns
#     q = a + b / R_V; where a = a(x) & b = b(x)
#     Cid@INAOE - 6/July/2004
#
    a = np.zeros(np.shape(l))
    b = np.zeros(np.shape(l))
    F_a = np.zeros(np.shape(l))
    F_b = np.zeros(np.shape(l))
    x = np.zeros(np.shape(l))
    y = np.zeros(np.shape(l))
    q = np.zeros(np.shape(l))
#
    for i in range(0,len(l)):
     x[i]=10000. / l[i]
     y[i]=10000. / l[i] - 1.82
#
#    x = 10000. / l
#
#     Far-Ultraviolet: 8 <= x <= 10 ; 1000 -> 1250 Angs 
    inter = np.bitwise_and(x >= 8, x <= 10)

    a[inter] = -1.073 - 0.628 * (x[inter] - 8.) + 0.137 * (x[inter] - 8.)**2 - 0.070 * (x[inter] - 8.)**3
    b[inter] = 13.670 + 4.257 * (x[inter] - 8.) - 0.420 * (x[inter] - 8.)**2 + 0.374 * (x[inter] - 8.)**3

#     Ultraviolet: 3.3 <= x <= 8 ; 1250 -> 3030 Angs 

    inter =  np.bitwise_and(x >= 5.9, x < 8)
    F_a[inter] = -0.04473 * (x[inter] - 5.9)**2 - 0.009779 * (x[inter] - 5.9)**3
    F_b[inter] =  0.2130 * (x[inter] - 5.9)**2 + 0.1207 * (x[inter] - 5.9)**3
    
    inter =  np.bitwise_and(x >= 3.3, x < 8)
    
    a[inter] =  1.752 - 0.316 * x[inter] - 0.104 / ((x[inter] - 4.67)**2 + 0.341) + F_a[inter]
    b[inter] = -3.090 + 1.825 * x[inter] + 1.206 / ((x[inter] - 4.62)**2 + 0.263) + F_b[inter]

#     Optical/NIR: 1.1 <= x <= 3.3 ; 3030 -> 9091 Angs ; 
    inter = np.bitwise_and(x >= 1.1, x < 3.3)
    
#    y = 10000. / l - 1.82
    
    a[inter] = 1.+ 0.17699 * y[inter] - 0.50447 * y[inter]**2 - 0.02427 * y[inter]**3 + 0.72085 * y[inter]**4 + 0.01979 * y[inter]**5 - 0.77530 * y[inter]**6 + 0.32999 * y[inter]**7
    b[inter] = 1.41338 * y[inter] + 2.28305 * y[inter]**2 + 1.07233 * y[inter]**3 - 5.38434 * y[inter]**4 - 0.62251 * y[inter]**5 + 5.30260 * y[inter]**6 - 2.09002 * y[inter]**7


#     Infrared: 0.3 <= x <= 1.1 ; 9091 -> 33333 Angs ; 
    inter = np.bitwise_and(x >= 0.3, x < 1.1)
    
    a[inter] =  0.574 * x[inter]**1.61
    b[inter] = -0.527 * x[inter]**1.61
    
    q = a + b / R_V

    return q


def calc_redlaw(l, R_V,redlaw):
    if(redlaw == 'CCM'): return Cardelli_RedLaw(l, R_V)
