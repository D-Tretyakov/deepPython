import unittest
from unittest.mock import patch
from functools import reduce
import random
from list_mul import mult

class Tests(unittest.TestCase):
    def test_example(self):
        a = [1, 2, 3, 4]
        res = mult(a)
        self.assertEqual(res, [24, 12, 8, 6])

    def test_case1(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        res = mult(a)
        self.assertEqual(res, [3628800, 1814400, 1209600, 
                               907200, 725760, 604800, 
                               518400, 453600, 403200, 362880])
    
    def test_case2(self):
        a = [3]*10
        res = mult(a)
        self.assertEqual(res, [19683, 19683, 19683, 
                               19683, 19683, 19683, 
                               19683, 19683, 19683, 19683])

    def test_case3(self):
        a = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        res = mult(a)
        self.assertEqual(res, [362880, 403200, 453600, 
                               518400, 604800, 725760, 
                               907200, 1209600, 1814400, 3628800])

    def test_case4(self):
        a = [1, 1, 1, 1, 1, 1, 1, 1, 1, 10]
        res = mult(a)
        self.assertEqual(res, [10, 10, 10, 10, 10, 10, 10, 10, 10, 1])

    def test_case5(self):
        a = [2, -3, 13, -67, 9, -36, 71, -78, 91, -10]
        res = mult(a)
        self.assertEqual(res, [-4266568902960, 2844379268640, -656395215840, 
                               127360265760, -948126422880, 237031605720, 
                               -120185039520, 109399202640, -93770745120, 853313780592])

    def test_random(self):
        for i in range(100):
            a = [random.randint(1, 100) for _ in range(10)]
            m = reduce(lambda x, y: x*y, a)
            b = [int(m / a[i]) for i in range(10)]
            self.assertEqual(mult(a), b)

    def test_empty_list(self):
        a = []
        res = mult(a)
        self.assertEqual(res, [])

    def test_one_el_list(self):
        a = [1]
        res = mult(a)
        self.assertEqual(res, [1])

    def test_list_with_zeros(self):
        a = [0, 2, 3, 4]
        res = mult(a)
        self.assertEqual(res, [24, 0, 0, 0])
        
        a = [0, 2, 4, 0, 5, 6, 0, 8, 9, 10, 0, 0]
        res = mult(a)
        self.assertEqual(res, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_ones(self):
        a = [1] * 1000
        res = mult(a)
        self.assertEqual(res, [1]*1000)

    def test_zeros(self):
        a = [0] * 1000
        res = mult(a)
        self.assertEqual(res, [0]*1000)

    def test_invalid_types(self):
        a = ['a', 2, 3]
        self.assertRaises(TypeError, mult, a)
    
    def test_invalid_types2(self):
        a = [[]]
        self.assertRaises(TypeError, mult, a)
    
    @patch('list_mul.mult', return_value=[1]*10000000)
    def test_very_large(self, mult):
        self.assertEqual(mult([1]*10000000), [1]*10000000)