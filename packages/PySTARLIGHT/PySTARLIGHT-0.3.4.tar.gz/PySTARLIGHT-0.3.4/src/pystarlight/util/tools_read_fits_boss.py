'''
 These routines are used during the FITS extraction file 
 from BOSS and corrections of spectra. 
  
 1) Convert mask2flag (from Abilio's code)
 2) Make AID (BOSS/DR9 and older DRs formats)


  Created 05 Nov 2012                            author: Marcus                       
'''
################################################################
def mask2flag(mask):

  import numpy as np

#
# from ABILIO's code...
#
#     FLAGS:
#
#     0: normal pixel
#     1: emission line
#     > 1: problems...
#
  
  r=np.zeros(10)    
  r[0] = 262144      # FULLREJECT
  r[1] = 524288      # PARTIALREJ
  r[2] = 4194304     # NOSKY
  r[3] = 8388608     # BRIGHTSKY
  r[4] = 16777216    # NODATA
  r[5] = 33554432    # COMBINEREJ
  r[6] = 67108864    # BADFLUXFACTOR
  r[7] = 134217728   # BADSKYCHI
  r[8] = 268435456   # REDMONSTER
  r[9] = 1073741824  # EMLINE
#
  nl=len(mask)
  flag=np.zeros(nl)
#
  for i in range(0,nl):
   flag[i]=0 # pixel OK!
   if mask[i] >= r[9]: flag[i]=1 # EMLINE
   if mask[i] >= r[9]+r[0] and mask[i] < r[9]+r[1]: flag[i]=2 #EMLINE + FULLREJ
   if mask[i] >= r[9]+r[2] and mask[i] < r[9]+r[3]: flag[i]=3 #EMLINE + NOSKY
   if mask[i] >= r[9]+r[3] and mask[i] < r[9]+r[4]: flag[i]=4 #EMLINE + SKY
   if mask[i] >= r[9]+r[4] and mask[i] < r[9]+r[5]: flag[i]=5 #EMLINE + NODATA
   if mask[i] >= r[9]+r[7] and mask[i] < r[9]+r[8]: flag[i]=6 #EMLINE + BADSKY
   if mask[i] >= r[9]+r[7]+r[3] and mask[i] < r[9]+r[8]: flag[i]=7 #EMLINE + BADSKY + SKY
   if mask[i] >= r[0] and mask[i] < r[1]: flag[i]=8 #FULLREJECT
   if mask[i] >= r[2] and mask[i] < r[3]: flag[i]=9 # NOSKY
   if mask[i] >= r[3] and mask[i] < r[4]: flag[i]=10 #SKY
   if mask[i] >= r[3]+r[4] and mask[i] < r[5]: flag[i]=11 #SKY + NODATA
   if mask[i] >= r[4] and mask[i] < r[5]: flag[i]=12 #NODATA
   if mask[i] >= r[6] and mask[i] < r[7]: flag[i]=13 #BADFLUXFACTOR
   if mask[i] >= r[6]+r[4] and mask[i] < r[6]+r[5]: flag[i]=14 #BADFLUX + NODATA
   if mask[i] >= r[6]+r[3] and mask[i] < r[6]+r[4]: flag[i]=15 #BADFLUX + SKY
   if mask[i] >= r[7] and mask[i] < r[8]: flag[i]=16  #BADSKY
   if mask[i] >= r[7]+r[3] and mask[i] < r[7]+r[4]: flag[i]=17 #BADSKY + SKY
   if mask[i] >= r[7]+r[3]+r[0] and mask[i] < r[7]+r[3]+r[1]: flag[i]=18 #BADSKY + SKY + FULLREJ
   if mask[i] >= r[8] and mask[i] < r[9]: flag[i]=19 #REDMONSTER
#
  return flag
###########################################################################
'''
 This routine uses the plate, mjd and fiberID arrays from SDSS table 
 and makes the AID (plate.mjd.fiberID).


 Note: The BOSS has 10^3 fibers in the spectrograph, so if the 
 option BOSS is chosen, fiberID will present 4 digits. 
  
 Created on Nov 5, 2012
                                                @author: Marcus
'''
def make_aid(plate,mjd,fiber,DR):

 if len(plate) == len(mjd) & len(plate) == len(fiber):
  aid = []
  for i in range(0,len(plate)): 
   if DR == 'BOSS': # BOSS aid -> fiberID with 4 digits
    if fiber[i] < 10:                       # 1 digit
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+'000'+str(fiber[i]))   
    if fiber[i] >= 10 and fiber[i] < 100:   # 2 digits
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+'00'+str(fiber[i]))   
    if fiber[i] >= 100 and fiber[i] <= 999: # 3 digits
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+'0'+str(fiber[i]))   
    if fiber[i] == 1000:                    # 4 digits
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+str(fiber[i]))   
   else: # older DR -> fiberID with 3 digits
    if fiber[i] < 10:                       # 1 digit
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+'00'+str(fiber[i]))   
    if fiber[i] >= 10 and fiber[i] < 100:   # 2 digits
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+'0'+str(fiber[i]))   
    if fiber[i] >= 100 and fiber[i] <= 999: # 3 digits
     aid.append(str(plate[i])+'-'+str(mjd[i])+'-'+str(fiber[i]))
 return aid
