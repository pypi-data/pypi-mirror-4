realm=__name__.split('.')[-2]
input_type=__name__.split('.')[-1]

from ... import pyteos_interface
import sys

desc={}
desc['temperature']="absolute temperature (K).\n\n\
Note that this function is not an exact inverse of :func:`pyteos_air.liq_ice_air.g.entropy`. \
At the freezing point, this function assumes that a combination of liquid water and ice will \
combine to make sure that the temperature is constant between the Isentropic Freezing level \
:func:`pyteos_air.liq_ice_air.il.ifl` and the Isentropic Melting Level :func:`pyteos_air.liq_ice_air.il.iml`"

__all__=desc.keys()

docstring="""
:param A: dry air massfraction (kg/kg)
:type A: np.array.
:param eta: wet air entropy obtained from :func:`pyteos_air.liq_ice_air.g.entropy` (J/K)
:type eta: np.array.
:param p: total pressure (Pa)
:type p: np.array.
:returns: {0}

This is for wet air with ice and liquid.
"""

for function_name in __all__:
    def __tool(A,eta,p):
        return pyteos_interface.attribute_to_function(realm+'_'+input_type,function_name,A,eta,p)
    __tool.__name__=function_name
    __tool.__doc__=docstring.format(desc[function_name])
    setattr(sys.modules[__name__], function_name, __tool)
