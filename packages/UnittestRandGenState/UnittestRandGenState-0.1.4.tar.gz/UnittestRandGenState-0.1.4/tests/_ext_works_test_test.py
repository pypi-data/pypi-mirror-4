import unittest
import sys
import random
import numpy.random
import os.path

if sys.version_info < (3, 0):    
    from _ext_base2 import ExtRandStateSaverBase as ExtRandStateSaverBase
else:     
    from _ext_base3 import ExtRandStateSaverBase as ExtRandStateSaverBase
    

class TestExtWorks(unittest.TestCase, ExtRandStateSaverBase):
    def test_0(self):
        with open('ext_works_0_part_ok.txt', 'w') as f:
            f.write('ok')
        
    def test_1(self):
        with open('ext_works_1_part_ok.txt', 'w') as f:
            f.write('ok')
        ddd


if __name__ == '__main__':
    unittest.main()
