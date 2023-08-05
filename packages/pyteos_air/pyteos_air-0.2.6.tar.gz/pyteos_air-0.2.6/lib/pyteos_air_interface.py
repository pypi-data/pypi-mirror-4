from .. import teos_air
import numpy as np

class Realm:
    """
    :param realm_name: a thermodynamic realm to use. 
    :type realm_name: str.
    :returns: a module with different thermodynamics functions associated with the chosen realm.

    Available wet air realms are:
        #. 'liq_ice_air', for liquid / ice / humid air mixture;
    Future available wet air realms are:
        #. 'air' for unsaturated humid air;
        #. 'liq_air' for liquid / humid air mixture;
        #. 'ice_air' for ice / humid air mixture.

    Further help for each realm is generated when the class is initialized:

    >>> print pa.Realm('liq_ice_air').__doc__
    Available interfaces: g,g_ref,h,il,sat
    >>> help(pa.Realm('liq_ice_air').g)

    Will give a short description of available 
    functions and the input parameters required.

    .. note::
      This class is **not** supposed to be compatible with :mod:`pickle`. Use at your own risk.
    
    """

    def __init__(self,realm_name):
        available_realms=['liq_ice_air','air','liq_air','ice_air']

        if realm_name not in available_realms:
            raise NameError('Class Realm in pyteos_air: '+realm_name+' is not a valid realm')
        realm_methods=[]
        for method_name in dir(teos_air):
            if method_name[:len(realm_name)]==realm_name:
                if method_name[5:]!='_desc':
                    if method_name+'_desc' in dir(teos_air):
                        realm_methods.append(method_name.replace(realm_name+'_',''))

        setattr(self,'__doc__','Available interfaces: '+','.join(realm_methods))
        for method_name in realm_methods:
            setattr(self,method_name,self._Method(realm_name+'_'+method_name))

    class _Method:
        """
        class Method(method_name) returns a suite of thermodynamics state functions
                                    for the wet air combination specified by teos_real_name

        """
        def __init__(self,method_name):
            func_list = getattr(teos_air,method_name+'_desc')('list').rstrip().split(',')
            func_long_name_list = getattr(teos_air,method_name+'_desc')('long_name').rstrip().split(',')

            self.__doc__='Available functions: '+getattr(teos_air,method_name+'_desc')('list').rstrip()

            for function_index, function_name in enumerate(func_list):
                setattr(self,function_name,setfunc(method_name,function_name))
                setattr(getattr(self,function_name),'__doc__',getattr(teos_air,method_name+'_desc')('description').rstrip().format(function_name,func_long_name_list[function_index]))
                setattr(getattr(self,function_name),'__name__',function_name)

def setfunc(method_name,function_name):
    return (lambda *input_args: attribute_to_function(method_name,function_name,*input_args))
            
def attribute_to_function(method_name,function_name,*args):
    return np.squeeze(getattr(teos_air,method_name)(function_name,*np.broadcast_arrays(*np.atleast_3d(*args))))
