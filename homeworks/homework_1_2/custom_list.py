class CustomList(list):
    def __sub__(self, other):
        if not isinstance(other, CustomList):
            raise TypeError(f"unsupported operand type(s) for -: \
                            '{type(self).__name__}' and '{type(other).__name__}'")

        max_len = max(len(self), len(other))
        min_len = min(len(self), len(other))

        return CustomList([self[i]-other[i] if i < min_len else -other[i] for i in range(max_len)])

    def __add__(self, other):
        if not isinstance(other, CustomList):
            raise TypeError(f"unsupported operand type(s) for +: \
                            '{type(self).__name__}' and '{type(other).__name__}'")

        max_len = max(len(self), len(other))
        min_len = min(len(self), len(other))

        return CustomList([self[i]+other[i] if i < min_len else other[i] for i in range(max_len)])

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
