"""
Contains a simple metaclass for dropping into unittest.TestCase that makes failing
cases fail persistently.
"""


from __future__ import print_function
import types
import random 
import warnings
import os
try:
    import cPickle as pickle_
except ImportError:
    import pickle as pickle_    
try:
    import numpy.random
    _has_numpy_rand = True
except ImportError:
    _has_numpy_rand = False
    
    
def _state_f_name(module_name, cls_name, fn_name):
    return '.'.join([module_name, cls_name, fn_name] + ['_unittest_rand_gen_state.dat'])


class _TestRecorder(object):
    def __init__(self, reset_state, get_state, set_state, module_name, cls_name, fn_name):
        self._reset_state, self._get_state, self._set_state = reset_state, get_state, set_state
        self._f_name = _state_f_name(module_name, cls_name, fn_name)
     
    def get_state(self):
        if os.path.exists(self._f_name):
            self._exc = 'handling_err'
            try:
                with open(self._f_name, 'rb') as f:
                    state = pickle_.load(f)
                self._set_state(state)
            except Exception as e:                
                warnings.warn(str(e), RuntimeWarning)
                self._exc = 'handling_err_load_failed'
        else:
            self._exc = 'ok'                       
                
        return self._get_state()

    def notify_ok(self):
        assert self._exc in ['ok', 'handling_err', 'handling_err_load_failed']
        if self._exc == 'handling_err':
            try:
                os.remove(self._f_name)
            except Exception as e:
                warnings.warn(str(e), RuntimeWarning)
            self._reset_state()

    def notify_failure(self, state):
        assert self._exc in ['ok', 'handling_err', 'handling_err_load_failed']
        try:
            with open(self._f_name, 'wb') as f:
                pickle_.dump(state, f)
        except Exception as e:
            warnings.warn(str(e), RuntimeWarning)
        if self._exc == 'handling_err':
            self._reset_state()
     

def _get_state_save_wrapper(reset_state, get_state, set_state, module_name, cls_name, fn):
    def wrapped(*args, **kwargs):
        r = _TestRecorder(reset_state, get_state, set_state, module_name, cls_name, fn.__name__)        
        state = r.get_state()
        try:
            fn(*args, **kwargs)
            r.notify_ok()          
        except:
            r.notify_failure(state)
            raise         
    wrapped.__name__ = fn.__name__     
    wrapped.__doc__ = fn.__doc__     
    return wrapped 


__all__ = ['Saver']
class Saver(type):
    """
    Drop this into unittest.TestCase as a metaclass, to make failing cases fail consistently.
    
    For example:
    
    >>> import random
    >>> 
    >>> import unittest_rand_gen_state
    >>> 
    >>> 
    >>>     class TestMyAlgs(unittest.TestCase, metaclass = unittest_rand_gen_state.Saver):
    >>>         ...

    or, using an older Python version:

    >>> import random
    >>> 
    >>> import unittest_rand_gen_state
    >>> 
    >>> 
    >>> class TestMyAlgs(unittest.TestCase):
    >>>     __metaclass__ = unittest_rand_gen_state.Saver
    >>>     ...   
    
    
    The library may be extended by dropping as a metaclass, a subclass supplying three class methods:
   
    * ``reset_state``: A method specifying the meaning of resetting the random-generation state 
        (e.g., ``random.seed``)
    * ``get_state``: A method specifying the query to call for getting the current random-generation state 
        (e.g., ``random.getstate``)
    * ``set_state``: A method specifying the function to call to restore the random-generation state 
        using the value returned by ``get_state`` (e.g., ``random.setstate``)
    """
   
    if _has_numpy_rand:
        _reset_state = staticmethod(lambda : (random.seed(), numpy.random.seed()))
        _get_state = staticmethod(lambda : (random.getstate(), numpy.random.get_state()))
        _set_state = staticmethod(lambda state: (random.setstate(state[0]), numpy.random.set_state(state[1])))
    else:
        _reset_state = random.seed
        _get_state = random.getstate
        _set_state = random.setstate
        
    try:
        rs, gs, ss = cls.reset_state, cls.get_state, cls.set_state
        
        _reset_state = staticmethod(lambda : (cls.reset_state(), _reset_state()))
        _get_state = staticmethod(lambda : (cls.get_state(), _get_state()))
        _set_state = staticmethod(lambda state: (cls.set_state(state[0]), _set_state(state[1])))
    except NameError:
        pass        
     
    def __new__(cls, name, bases, dict_):
        new_dict = {}
        for attrib_name, attrib in dict_.items():
            if type(attrib) == types.FunctionType and attrib_name.find('test') == 0:
                new_dict[attrib_name] = _get_state_save_wrapper(
                    cls._reset_state, cls._get_state, cls._set_state,
                    cls.__module__, name, attrib)
            else:
                new_dict[attrib_name] = attrib                   
        return type.__new__(cls, name, bases, new_dict)
        
