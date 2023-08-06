import unittest
import os
import os.path
import warnings
import sys
try:
    import cPickle as pickle_
except ImportError:
    import pickle as pickle_    

import unittest_rand_gen_state


_python_str = 'python3' if sys.version_info > (3, 0) else 'python'


def _hash_triplets():
    os.system('%s _consistency_works_test_test.py' % _python_str)
    with open('from_test_test_0.txt', 'r') as f:
        hash_0 = f.read()
    with open('from_test_test_1.txt', 'r') as f:
        hash_1 = f.read()
    with open('from_test_test_2.txt', 'r') as f:
        hash_2 = f.read()
    return (hash_0, hash_1, hash_2)
    

class Test(unittest.TestCase):
    _f_name = unittest_rand_gen_state._state_f_name(
        '__main__', 'TestConsistencyWorks', 'test_1')

    def test_0(self):
        if os.path.exists('ok_now.txt'):
            os.remove('ok_now.txt')
           
        (hash_0_0, hash_1_0, hash_2_0) = _hash_triplets()

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           
        
        self.assertTrue(os.path.exists(Test._f_name), Test._f_name)
       
        with open('ok_now.txt', 'w') as f:
            f.write('OK')

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           

        self.assertFalse(os.path.exists(Test._f_name), Test._f_name)

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           

        self.assertFalse(os.path.exists(Test._f_name), Test._f_name)

    def test_1(self):
        if os.path.exists('ok_now.txt'):
            os.remove('ok_now.txt')
           
        with open(unittest_rand_gen_state._state_f_name(
                '__main__', 'TestConsistencyWorks', 'test_1'), 'wb') as f:
            pickle_.dump(2, f)

        (hash_0_0, hash_1_0, hash_2_0) = _hash_triplets()
        
        with open(unittest_rand_gen_state._state_f_name(
                '__main__', 'TestConsistencyWorks', 'test_1'), 'wb') as f:
            pickle_.dump(2, f)

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1, hash_0_0)           
        self.assertNotEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           
        
    def test_2(self):
        for i in range(2):
            if os.path.exists('ext_works_0_part_ok.txt'):
                os.remove('ext_works_0_part_ok.txt')
            if os.path.exists('ext_works_1_part_ok.txt'):
                os.remove('ext_works_1_part_ok.txt')
                
            os.system('%s _ext_works_test_test.py' % _python_str)       
            
            self.assertTrue(os.path.exists('ext_works_0_part_ok.txt'))
            self.assertTrue(os.path.exists('ext_works_1_part_ok.txt'))
            
    def test_3(self):
        f_name_0 = unittest_rand_gen_state._state_f_name(
            '_other_module', 'DuplicateNameTest', 'test_0')
        f_name_1 = unittest_rand_gen_state._state_f_name(
            '_yet_another_module', 'DuplicateNameTest', 'test_0')

        for f_name in [f_name_0, f_name_1]:
            if os.path.exists(f_name):
                os.remove(f_name)

        os.system('%s _duplicate_name_test_test.py' % _python_str)               

        for f_name in [f_name_0, f_name_1]:
            self.assertTrue(os.path.exists(f_name), f_name)


if __name__ == '__main__':
    unittest.main()
