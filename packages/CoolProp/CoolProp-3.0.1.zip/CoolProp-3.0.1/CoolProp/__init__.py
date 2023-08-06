from __future__ import absolute_import
__version__='3.0.1'
__svnrevision__ =381
from . import CoolProp
from . import HumidAirProp
from . import State
__fluids__ = CoolProp.FluidsList()
def get_include_directory():
    import os
    head,file = os.path.split(__file__)
    return os.path.join(head,'include')