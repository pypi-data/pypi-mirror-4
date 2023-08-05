realm=__name__.split('.')[-2]
input_type=__name__.split('.')[-1]

from ... import pyteos_interface
import sys

desc={}
desc['ifl']="isentropic freezing level (Pa).\n\n\
For pressures higher than the **ifl**, there can be only liquid water."
desc['iml']="isentropic melting level (Pa).\n\n\
For pressures lower than the **iml**, there can be only ice."

__all__=desc.keys()

docstring="""
:param A: dry air massfraction (kg/kg)
:type A: np.array.
:param eta: wet air entropy obtained from :func:`pyteos_air.liq_ice_air.g.entropy` (J/K)
:type eta: np.array.
:returns: {0}

This is for wet air with ice and liquid.
"""

for function_name in __all__:
    def __tool(A,eta):
        return pyteos_interface.attribute_to_function(realm+'_'+input_type,function_name,A,eta)
    __tool.__name__=function_name
    __tool.__doc__=docstring.format(desc[function_name])
    setattr(sys.modules[__name__], function_name, __tool)
