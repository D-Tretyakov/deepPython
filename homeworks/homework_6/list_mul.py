import logging
from functools import reduce

FORMAT_STR = '%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'
LOG_FILE = "func_mult.log"
logging.basicConfig(format=FORMAT_STR, filename=LOG_FILE, level=logging.INFO)

def mult(array):
    logging.info('Checking list elements types')
    if not all(isinstance(i, (int, float)) for i in array):
        logging.error('All the elements of the list have to be integers')
        raise TypeError('Not all elments of list are int or float')
    logging.info('OK')

    logging.info('Checking list size')
    if len(array) <= 1:
        logging.warning('List size is 1 or 0, so returning list itself')
        return array
    logging.info('OK')

    logging.info('Calculating')
    n = len(array) 
    res = [1 for _ in range(n)] 
    left = right = 1
    for i in range(n): 
        res[i] *= left 
        left *= array[i] 
    for i in reversed(range(n)): 
        res[i] *= right 
        right *= array[i]
    
    logging.info('Finishing')
    return res
