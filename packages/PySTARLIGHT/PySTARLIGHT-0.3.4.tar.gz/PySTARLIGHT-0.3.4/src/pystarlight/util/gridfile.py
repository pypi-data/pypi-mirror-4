'''
Created on Aug 21, 2012

@author: Andre L. de Amorim
'''

from jinja2 import Template
from os import path
import sys
import copy
import random


class GridRun(object):
    inFile = ''
    outFile = ''
    configFile = ''
    baseFile = ''
    maskFile = ''
    reddening = 'CCM'
    etcInfoFile = ''
    lumDistanceMpc = 0.0
    v0_Ini = 0.0
    vd_Ini = 0.0
    
    def __init__(self, inFile='', etcInfoFile= '', lumDistanceMpc=0.0, configFile='',
                 baseFile='', maskFile='', reddening='CCM', v0_Ini=0.0, vd_Ini=0.0, outFile='', ):
        self.inFile = inFile
        self.outFile = outFile
        self.configFile = configFile
        self.baseFile = baseFile
        self.maskFile = maskFile
        self.reddening = reddening
        self.etcInfoFile = etcInfoFile
        self.lumDistanceMpc = lumDistanceMpc
        self.v0_Ini = v0_Ini
        self.vd_Ini = vd_Ini
        
    def clone(self):
        return copy.deepcopy(self)
    

class GridFile(object):
    _curdir = path.abspath(path.curdir)
    basesDir = _curdir  # [base_dir]
    obsDir = _curdir    # [obs_dir]
    maskDir = _curdir   # [mask_dir]
    etcDir = _curdir    # [etc_dir]
    outDir = _curdir    # [out_dir]
    randPhone = 0       # [random phone number]
    lLow_SN = 5350.0    # [llow_SN]   lower-lambda of S/N window <-- Not relevant when error-spectrum is provided
    lUpp_SN = 5850.0    # [lupp_SN]   upper-lambda of S/N window <-- Not relevant when error-spectrum is provided
    lLow_Syn = 3650.0   # [Olsyn_ini] lower-lambda for fit
    lUpp_Syn = 6850.0   # [Olsyn_fin] upper-lambda for fit
    dLambda = 1.0       # [Odlsyn]    delta-lambda for fit
    fScale_Chi2 = 1.0   # [fscale_chi2] fudge-factor for chi2
    fitFix = 'FIT'      # [FIT/FXK] Fit or Fix kinematics
    errSpecAvail = 1    #[IsErrSpecAvailable]  1/0 = Yes/No
    flagSpecAvail = 1   # [IsFlagSpecAvailable] 1/0 = Yes/No
    isPhoEnabled = 0    # [IsPHOcOn] 1/0 = Yes/No  <=== !PHO! ATT: still needs coding + testing!
    isQHREnabled = 0    # [IsQHRcOn] 1/0 = Yes/No  <=== !QHR!
    isFIREnabled = 0    # [IsFIRcOn] 1/0 = Yes/No  <=== !FIR!
    fluxUnit = 1e-16        # [flux_unit] multiply spectrum in arq_obs by this value to obtain ergs/s/cm2/Angs
    runs = []               # List of GridRun


    def __init__(self):
        pass


    def seed(self, range=0x8FFFFFFF):
        self.randPhone = random.randrange(1, range)

    
    def _loadFrom(self, gridFileName):
        l = open(gridFileName).read().splitlines()
        self.basesDir = l[1].split()[0]
        self.obsDir = l[2].split()[0]
        self.maskDir = l[3].split()[0]
        self.etcDir = l[4].split()[0]
        self.outDir = l[5].split()[0]
        self.randPhone = int(l[6].split()[0])
        self.lLow_SN = float(l[7].split()[0])
        self.lUpp_SN = float(l[8].split()[0])
        self.lLow_Syn = float(l[9].split()[0])
        self.lUpp_Syn = float(l[10].split()[0])
        self.dLambda = float(l[11].split()[0])
        self.fScale_Chi2 = float(l[12].split()[0])
        self.fitFix = l[13].split()[0]
        self.errSpecAvail = int(l[14].split()[0])
        self.flagSpecAvail = int(l[15].split()[0])
        self.isPhoEnabled = int(l[16].split()[0])
        self.isQHREnabled = int(l[17].split()[0])
        self.isFIREnabled = int(l[18].split()[0])
        self.fluxUnit = float(l[19].split()[0])
        for runs in l[20:]:
            rr = runs.split()
            self.runs.append(GridRun(rr[0], rr[1], float(rr[2]), rr[3], rr[4], rr[5],
                           rr[6], float(rr[7]), float(rr[8]), rr[9]))


    def loadFrom(self, gridFileName):
        try:
            self._loadFrom(gridFileName)
        except:
            print 'error reading grid file, values may be half filled.'

        
    def appendRun(self, inFile='', outFile='', configFile='', baseFile='', maskFile='', reddening='CCM'):
        self.runs.append(GridRun(inFile, outFile, configFile, baseFile, maskFile, reddening))
    
    
    def render(self):
        tplFile = path.join(path.dirname(__file__), 'gridfile.template')
        tpl = Template(open(tplFile).read())
        return tpl.render(grid=self)

        
    def write(self, gridFileName):
        open(gridFileName, 'w').write(self.render())
    

if __name__ == '__main__':
    grid = GridFile()
    grid.loadFrom(sys.argv[1])
    grid.seed()
    
    runTemplate = GridRun()
    
    newRun = runTemplate.clone()
    newRun.outFile = 'testOut_new'
    grid.runs.append(newRun)


    print grid.render()
    grid.write('grid.lala.in')
