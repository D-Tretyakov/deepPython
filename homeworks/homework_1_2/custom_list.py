class CustomList(list):
    def __sub__(self, other):
        if not isinstance(other, CustomList):
            raise TypeError("unsupported operand type(s) for -:" \
                            f"'{type(self).__name__}' and '{type(other).__name__}'")

        if len(self) < len(other):
            short = self
            long = other
            return CustomList([self[i]-other[i] if i < len(short) else -long[i] for i in range(len(long))])
        else:
            short = other
            long = self 
            return CustomList([self[i]-other[i] if i < len(short) else long[i] for i in range(len(long))])

    def __add__(self, other):
        if not isinstance(other, CustomList):
            raise TypeError("unsupported operand type(s) for +:" \
                            f"'{type(self).__name__}' and '{type(other).__name__}'")

        short = self if len(self) < len(other) else other
        long = self if len(self) > len(other) else other

        return CustomList([self[i]+other[i] if i < len(short) else long[i] for i in range(len(long))])

    def __eq__(self, other):
        return sum(self) == sum(other)

    def __ne__(self, other):
        return not sum(self) == sum(other)

    def __lt__(self, other):
        return sum(self) < sum(other)

    def __gt__(self, other):
        return sum(self) > sum(other)

    def __le__(self, other):
        return sum(self) <= sum(other)

    def __ge__(self, other):
        return sum(self) >= sum(other)
