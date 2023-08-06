import unittest_rand_gen_state


def _seed():
    pass
    
def _get_state():
    return 13
    
def _set_state(state):
    assert sttae == 13
    
    
class _Ext(unittest_rand_gen_state.Saver):
    reset_state = _seed
    get_state = _get_state    
    set_state = _set_state    


class ExtRandStateSaverBase(object, metaclass = _Ext):
    pass

