
import unittest
import sys
import os

sys.path.append(os.getcwd())

with open('phase_5_results.txt', 'w') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_phase_5_addiction.py')
    result = runner.run(suite)
    
print("Tests executed. Check phase_5_results.txt")
