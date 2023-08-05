realm=__name__.split('.')[-2]
input_type=__name__.split('.')[-1]

from ... import pyteos_interface
import sys

desc={}
desc['entropy']="wet air entropy (J/K).\n\n\
At the freezing temperature, this function assumes that half of the condensate is in liquid phase and\
that the other half is in ice phase."
desc['cond_entropy']="wet air entropy with all the moisture in condensed phase (J/K)"
desc['temperatureequi']="equivalent temperature (K)"
desc['rh_wmo']="relative humidity using WMO definition"

__all__=desc.keys()

docstring="""
:param A: dry air massfraction (kg/kg)
:type A: np.array.
:param T: absolute temperature (K)
:type T: np.array.
:param p: total pressure (Pa)
:type p: np.array.
:returns: {0}

This is for wet air with ice and liquid.
"""

for function_name in __all__:
    def __tool(A,T,p):
        return pyteos_interface.attribute_to_function(realm+'_'+input_type,function_name,A,T,p)
    __tool.__name__=function_name
    __tool.__doc__=docstring.format(desc[function_name])
    setattr(sys.modules[__name__], function_name, __tool)
