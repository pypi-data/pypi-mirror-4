import unittest
import os
import os.path
import warnings
try:
    import cPickle as pickle_
except ImportError:
    import pickle as pickle_    

import unittest_rand_gen_state


def _hash_triplets():
    os.system('python _consistency_works_test_test.py')       
    with open('from_test_test_0.txt', 'r') as f:
        hash_0 = f.read()
    with open('from_test_test_1.txt', 'r') as f:
        hash_1 = f.read()
    with open('from_test_test_2.txt', 'r') as f:
        hash_2 = f.read()
    return (hash_0, hash_1, hash_2)
   

class Test(unittest.TestCase):
    _f_name = unittest_rand_gen_state._state_f_name(
        'unittest_rand_gen_state', 'TestConsistencyWorks', 'test_1')

    def test_0(self):
        if os.path.exists('ok_now.txt'):
            os.remove('ok_now.txt')
           
        (hash_0_0, hash_1_0, hash_2_0) = _hash_triplets()

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           
        
        self.assertTrue(os.path.exists(Test._f_name))
       
        with open('ok_now.txt', 'w') as f:
            f.write('OK')

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           

        self.assertFalse(os.path.exists(Test._f_name))

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           

        self.assertFalse(os.path.exists(Test._f_name))

    def test_1(self):
        if os.path.exists('ok_now.txt'):
            os.remove('ok_now.txt')
           
        with open(unittest_rand_gen_state._state_f_name(
                'unittest_rand_gen_state', 'TestConsistencyWorks', 'test_1'), 'wb') as f:
            pickle_.dump(2, f)

        (hash_0_0, hash_1_0, hash_2_0) = _hash_triplets()
        
        with open(unittest_rand_gen_state._state_f_name(
                'unittest_rand_gen_state', 'TestConsistencyWorks', 'test_1'), 'wb') as f:
            pickle_.dump(2, f)

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           


if __name__ == '__main__':
    unittest.main()
