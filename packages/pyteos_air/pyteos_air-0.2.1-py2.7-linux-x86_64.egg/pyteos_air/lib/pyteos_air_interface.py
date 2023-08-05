def interface(realm_name,function_name,*args):
    #This function simply provides an interface to the pure Fortan distribution
    from .. import teos_air
    return getattr(teos_air,realm_name)(function_name,*args)
