import unittest
import sys
import random
import numpy.random
import os.path

if sys.version_info < (3, 0):    
    from _base2 import RandStateSaverBase as RandStateSaverBase
else:     
    from _base3 import RandStateSaverBase as RandStateSaverBase


def _hash_rand():
    r = hash(','.join([str(random.randint(0, 99999)) for _ in xrange(1000)]))
    np_r = hash(numpy.random.shuffle(range(9999)))
    
    return str(hash((r, np_r)))
    

class TestConsistencyWorks(unittest.TestCase, RandStateSaverBase):
    def test_0(self):
        with open('from_test_test_0.txt', 'w') as f:
            f.write(_hash_rand())

    def test_1(self):
        with open('from_test_test_1.txt', 'w') as f:
            f.write(_hash_rand())
        if not os.path.exists('ok_now.txt'):
            ddd

    def test_2(self):
        with open('from_test_test_2.txt', 'w') as f:
            f.write(_hash_rand())


if __name__ == '__main__':
    unittest.main()
