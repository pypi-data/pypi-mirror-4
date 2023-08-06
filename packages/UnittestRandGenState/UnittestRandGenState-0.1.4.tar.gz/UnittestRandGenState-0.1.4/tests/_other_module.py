import unittest
import sys

import unittest_rand_gen_state            
if sys.version_info < (3, 0):    
    from _ext_base2 import ExtRandStateSaverBase as ExtRandStateSaverBase
else:     
    from _ext_base3 import ExtRandStateSaverBase as ExtRandStateSaverBase    
    

class DummyTest(unittest.TestCase, ExtRandStateSaverBase):
    def test_0(self):
        pass


class DuplicateNameTest(unittest.TestCase, ExtRandStateSaverBase):
    def test_0(self):
        ggg

