import unittest
import sys
import random
import numpy.random
import os.path    
import _other_module
import _yet_another_module
    

if __name__ == '__main__':
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(_other_module)
    suite.addTests(loader.loadTestsFromModule(_yet_another_module))

    runner = unittest.TextTestRunner()
    result = runner.run(suite)

