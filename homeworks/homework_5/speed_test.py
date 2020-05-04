import matrix
import time

class PyMatrix():
    def __init__(self, values):
        self.values = values
    
    def __mul__(self, other):
        result = [[sum(a * b for a, b in zip(A_row, B_col))
                        for B_col in zip(*other.values)]
                                for A_row in self.values] 
        
        return PyMatrix(result)
    
    def __repr__(self):
        return str(self.values)

    def __str__(self):
        return "NP"

if __name__ == "__main__":
    A = [[12, 7, 3],  
         [4, 5, 6],  
         [7, 8, 9]]
    B = [[5, 8, 1, 2],  
        [6, 7, 3, 0],  
        [4, 5, 9, 1]]    

    start = time.time()
    for i in range(100000):
        PyMatrix(A) * PyMatrix(B)
    end = time.time()
    print(f"Pure python matmul took: {end-start}")
    
    start = time.time()
    for i in range(100000):
        matrix.Matrix(A) * matrix.Matrix(B)
    end = time.time()
    print(f"C ext matmul took: {end-start}")