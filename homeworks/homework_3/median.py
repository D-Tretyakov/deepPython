import heapq as hq

class MedianFinder:
    def __init__(self) -> None:
        self.maxheap = [] # smaller than median
        self.minheap = [] # greater than median
        self.median = None

    def addNum(self, num: int) -> None:
        if self.median is None:
            hq.heappush(self.maxheap, -num)
            self.median = num
        else:
            if len(self.maxheap) > len(self.minheap):
                if num < self.median:
                    hq.heappush(self.minheap, -hq.heappop(self.maxheap))
                    hq.heappush(self.maxheap, -num)
                else:
                    hq.heappush(self.minheap, num)
                
                self.median = (-self.maxheap[0] + self.minheap[0]) / 2

            elif len(self.maxheap) == len(self.minheap):
                if num < self.median:
                    hq.heappush(self.maxheap, -num)
                    self.median = -self.maxheap[0]
                else:
                    hq.heappush(self.minheap, num)
                    self.median = self.minheap[0]
            
            else:
                if num > self.median:
                    hq.heappush(self.maxheap, -hq.heappop(self.minheap))
                    hq.heappush(self.minheap, num)
                else:
                    hq.heappush(self.maxheap, -num)
                
                self.median = (-self.maxheap[0] + self.minheap[0]) / 2                

    def findMedian(self) -> float:
        return self.median
