"""
Contains a simple metaclass for dropping into unittest.TestCase that makes failing
cases fail persistently.
"""


from __future__ import print_function
import random 
import types
import multiprocessing
import shelve
try:
    import numpy.random
    _has_numpy_rand = True
except ImportError:
    _has_numpy_rand = False


class _ExecRecorder(object):
    def __init__(self):
        self._l = multiprocessing.Lock()
        self._exec = 'ok'
        self._hist = shelve.open('.unittest_rand_state_db')

    @staticmethod
    def _key(module_name, cls_name, fn_name):
        return
     
    def get_state(self, reset_state, get_state, set_state, key):
        with self._l:
            if key in self._hist:
                set_state(self._hist[key])
                self._exec = 'resuming'
            elif self._exec == 'resuming':
                self._exec = 'ok'
                reset_state()
               
            return get_state()

    def notify_ok(self, key):
        with self._l:
            if key in self._hist:
                del self._hist[key]
            self._hist.sync()                

    def notify_failure(self, key, state):
        with self._l:
            self._hist[key] = state
            self._hist.sync()                


_exec_recorder = _ExecRecorder()         
     

def _get_state_save_wrapper(reset_state, get_state, set_state, module_name, cls_name, fn):
    def wrapped(*args, **kwargs):
        key = ','.join((module_name, cls_name, fn.__name__))
        state = _exec_recorder.get_state(
            reset_state, get_state, set_state, key)
        try:
            fn(*args, **kwargs)
            _exec_recorder.notify_ok(key)          
        except:
            _exec_recorder.notify_failure(key, state)
            raise         
    wrapped.__name__ = fn.__name__     
    wrapped.__doc__ = fn.__doc__     
    return wrapped 


class Saver(type):
    """
    Drop this into unittest.TestCase as a metaclass, to make failing cases fail consistently.
   
    The library may be extended by dropping as a metaclass, a subclass supplying three class methods:
   
    * ``reset_state``: A method specifying the meaning of resetting the random-generation state (e.g., ``random.seed``)
    * ``get_state``: A method specifying the query to call for getting the current random-generation state (e.g., ``random.getstate``)
    * ``set_state``: A method specifying the function to call to restore the random-generation state using the value returned by ``get_state`` (e.g., ``random.setstate``)
    """
   
    if _has_numpy_rand:
        reset_state = staticmethod(lambda : (random.seed(), numpy.random.seed()))
        get_state = staticmethod(lambda : (random.getstate(), numpy.random.get_state()))
        set_state = staticmethod(lambda state: (random.setstate(state[0]), numpy.random.set_state(state[1])))
    else:
        reset_state = random.seed
        get_state = random.getstate
        set_state = random.setstate
     
    def __new__(cls, name, bases, dict_):
        new_dict = {}
        for attrib_name, attrib in dict_.items():
            if type(attrib) == types.FunctionType and attrib_name.find('test') == 0:
                new_dict[attrib_name] = _get_state_save_wrapper(
                    cls.reset_state, cls.get_state, cls.set_state,
                    cls.__module__, name, attrib)
            else:
                new_dict[attrib_name] = attrib                   
        return type.__new__(cls, name, bases, new_dict)
