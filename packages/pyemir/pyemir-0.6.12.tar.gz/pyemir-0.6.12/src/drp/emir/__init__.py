#
# Copyright 2008-2012 Universidad Complutense de Madrid
# 
# This file is part of PyEmir
# 
# PyEmir is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyEmir is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PyEmir.  If not, see <http://www.gnu.org/licenses/>.
# 

'''The EMIR Data Reduction Pipeline'''

import logging
import pkgutil
import importlib
    
import yaml
from numina.core import BaseInstrument, BasePipeline, InstrumentConfiguration
from numina.core import import_object

import emir.recipes as recp
from emir import __version__

_modes = [i for i in yaml.load_all(pkgutil.get_data('emir.instrument',
                                                   'obsmodes.yaml'))
          if i.instrument == 'EMIR']

_equiv_class = {}

for _m in _modes:
    _m.recipe_class = import_object(_m.recipe)
    _equiv_class[_m.key] = _m.recipe_class

del _m
        
class EMIR_Pipeline(BasePipeline):
    def __init__(self):
        super(EMIR_Pipeline, self).__init__(name='default',
                version=__version__,
                recipes=_equiv_class)
        
class EMIR_Pipeline_ALT(BasePipeline):
    def __init__(self):
        super(EMIR_Pipeline_ALT, self).__init__(name='alternate',
                version=__version__,
                recipes=_equiv_class)

_conf1 = InstrumentConfiguration('default', yaml.load(pkgutil.get_data('emir.instrument', 'default.yaml')))
_conf2 = InstrumentConfiguration('alternate', yaml.load(pkgutil.get_data('emir.instrument', 'alt.yaml')))

class EMIR_Instrument(BaseInstrument):
    name = 'EMIR'
    configurations = {'default': _conf1,
                      'alt': _conf2}
    
    pipelines = {'default': EMIR_Pipeline(),
                'alternate': EMIR_Pipeline_ALT()}
    modes = _modes

    def __init__(self, configuration):
        super(EMIR_Instrument, self).__init__('EMIR',
                    configuration)

del _modes

