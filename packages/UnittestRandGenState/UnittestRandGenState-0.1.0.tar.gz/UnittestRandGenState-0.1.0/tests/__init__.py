import unittest
import os
import os.path


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
    def test_0(self):
        if os.path.exists('ok_now.txt'):
            os.remove('ok_now.txt')
           
        (hash_0_0, hash_1_0, hash_2_0) = _hash_triplets()

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           
       
        with open('ok_now.txt', 'w') as f:
            f.write('OK')

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           

        (hash_0_1, hash_1_1, hash_2_1) = _hash_triplets()
        self.assertNotEqual(hash_0_0, hash_0_1)           
        self.assertNotEqual(hash_1_0, hash_1_1)           
        self.assertNotEqual(hash_2_0, hash_2_1)           


if __name__ == '__main__':
    unittest.main()
