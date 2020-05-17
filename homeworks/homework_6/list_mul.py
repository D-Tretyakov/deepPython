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

    logging.info('Calculating values')
    res = list()
    for i in range(len(array)):
        tmp = array[i]
        array[i] = 1
        product = reduce(lambda x, y: x*y, array)
        res.append(product)
        array[i] = tmp
        logging.info(f'Product of all elements except {i} is {product}')
    
    logging.info('Finishing')
    return res
