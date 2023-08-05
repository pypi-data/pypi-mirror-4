realm=__name__.split('.')[-2]
input_type=__name__.split('.')[-1]

from ... import pyteos_interface
import sys

desc={}
desc['massfraction_air']="saturation dry air massfraction (kg/kg)."

__all__=desc.keys()

docstring="""
:param T: absolute temperature (K)
:type T: np.array.
:param p: total pressure (Pa)
:type p: np.array.
:returns: {0}

This is for wet air with ice and liquid.
"""

for function_name in __all__:
    def __tool(T,p):
        return pyteos_interface.attribute_to_function(realm+'_'+input_type,function_name,T,p)
    __tool.__name__=function_name
    __tool.__doc__=docstring.format(desc[function_name])
    setattr(sys.modules[__name__], function_name, __tool)
