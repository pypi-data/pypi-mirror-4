realm=__name__.split('.')[-2]
input_type=__name__.split('.')[-1]

from ... import pyteos_interface
import sys

desc={}
desc['pottemp']="potential tempeature (K) at **pref**."
desc['pottempequisat']="saturation equivalent potential temperature (K) at **pref**."
desc['pottempequipseudo']="pseudo equivalent potential temperature (K) at **pref**.\n\n\
Integrates the pseudo adiabat until the temperature falls\
outside the range of validity of TEOS-10."
desc['pottempequi']="equivalent potential tempeature (K) at **pref**."

__all__=desc.keys()

docstring="""
:param A: dry air massfraction (kg/kg)
:type A: np.array.
:param T: absolute temperature (K)
:type T: np.array.
:param p: total pressure (Pa)
:type p: np.array.
:param pref: reference total pressure (Pa)
:type pref: np.array.
:returns: {0}

This is for wet air with ice and liquid.
"""

for function_name in __all__:
    def __tool(A,T,p,pref):
        return pyteos_interface.attribute_to_function(realm+'_'+input_type,function_name,A,T,p,pref)
    __tool.__name__=function_name
    __tool.__doc__=docstring.format(desc[function_name])
    setattr(sys.modules[__name__], function_name, __tool)
