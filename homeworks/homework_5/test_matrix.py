import matrix
import pytest

def test_creation():
    m = matrix.Matrix([[5, 6], [0, 7]])
    assert m.values == [[5, 6], [0, 7]]

def test_reassigning():
    m = matrix.Matrix([[5, 6], [0, 7]])
    m.values = [[1, 2], [3, 4]]
    assert m.values == [[1, 2], [3, 4]]

def test_str_repr():
    m = matrix.Matrix([[5, 6], [0, 7]])
    assert str(m) == '[[5, 6],\n [0, 7]]'
    assert repr(m) == 'Matrix([[5, 6], [0, 7]])'

def test_subscription():
    m = matrix.Matrix([[5, 6], [0, 7]])
    array = [[5, 6], [0, 7]]
    for i in range(2):
        for j in range(2):
            assert m[(i, j)] == array[i][j]

def test_add():
    m = matrix.Matrix([[5, 6], [0, 7]])
    n = m + 1
    assert n.values == [[6.0, 7.0], [1.0, 8.0]]

def test_sub():
    m = matrix.Matrix([[5, 6], [0, 7]])
    n = m - 1
    assert n.values == [[4.0, 5.0], [-1.0, 6.0]]

def test_div():
    m = matrix.Matrix([[5, 6], [0, 7]])
    n = m / 2
    assert n.values == [[2.5, 3.0], [0.0, 3.5]]