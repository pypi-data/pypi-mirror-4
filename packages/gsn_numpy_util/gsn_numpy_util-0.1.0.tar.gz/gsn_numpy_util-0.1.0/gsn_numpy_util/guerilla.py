import scipy.special
import gsn_numpy_util as nu

def setattr_maybe(namespace, value, name=None):
    if name is None: name = value.__name__    
    if hasattr(namespace, name):
        raise AttributeError, "Package Authors have provided your functionality!"
    else:
        if hasattr(namespace, '__all__'):
            getattr(namespace, '__all__').append(name)
        setattr(namespace, name, value)

setattr_maybe(scipy.special, nu.y)
setattr_maybe(scipy.special, nu.ry)

