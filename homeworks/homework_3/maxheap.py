from typing import List

class MaxHeap:
    def __init__(self, iterable: List[int]) -> None:
        self._array = iterable

    def push(self, val: int) -> None:
        self._array.append(val)
        self.heapify()

    def pop(self) -> int:
        if len(self._array) < 1:
            raise IndexError('pop from empty queue')
        
        self._array[0], self._array[len(self._array)-1] = self._array[len(self._array)-1], self._array[0]
        maxel = self._array.pop()
        self.heapify()
        return maxel

    def heapify(self) -> None:
        for i in range(len(self._array)//2, -1, -1):
            self._rebuild(i)
    
    def _rebuild(self, start_index: int) -> None:
        n = len(self._array)
        i = start_index
        largest = i
        while True:
            r = 2*i + 2
            l = 2*i + 1

            if l < n and self._array[l] > self._array[largest]:
                largest = l

            if r < n and self._array[r] > self._array[largest]:
                largest = r

            if largest != i:
                self._array[i], self._array[largest] = self._array[largest], self._array[i]
                i = largest
                continue

            break
