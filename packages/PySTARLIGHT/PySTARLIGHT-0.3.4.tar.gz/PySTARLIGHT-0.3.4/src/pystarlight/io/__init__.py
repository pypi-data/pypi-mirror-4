'''
Created on Mar 7, 2012

@author: Andre Luiz de Amorim

'''

from distutils.version import LooseVersion
from atpy import __version__ as atpy_version

if LooseVersion(atpy_version) >= LooseVersion('0.9.6'):
    from atpy.registry import register_set_reader #@UnresolvedImport
    from atpy.registry import register_reader #@UnresolvedImport
else:
    from atpy import register_set_reader #@UnresolvedImport @Reimport
    from atpy import register_reader #@UnresolvedImport @Reimport

import starlighttable
import starlighttablev4
import basefilev4
import EmissionLinesTable
import sdssinputfile
import SynTables
import ParametersTable

register_set_reader('starlight', starlighttable.read_set)
register_set_reader('starlightv4', starlighttablev4.read_set)
register_reader('starlightv4_base', basefilev4.read)
register_reader('newfits_el', EmissionLinesTable.read_newfits)
register_reader('starlight_el', EmissionLinesTable.read_starlight)
register_set_reader('starlight_input', sdssinputfile.read_set)
register_reader('starlight_syn01', SynTables.read_SYN01)
register_reader('starlight_syn02', SynTables.read_SYN02)
register_reader('starlight_syn03', SynTables.read_SYN03)
register_reader('starlight_syn04', SynTables.read_SYN04)
register_reader('starlight_param', ParametersTable.read_parameters)

