table = {'RUB': 10, 'USD': 1, 'JPN': 2, 'KZN': 3, 'BLR': 45}

class Money:
    def __init__(self, value, currency=None):
        self.value = value

        if currency.upper() not in table:
            raise KeyError
        self.currency = currency.upper()

    def convert(self, currency):
        self.value *= table[currency.upper()] / table[self.currency]
        self.currency = currency.upper()

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Money(self.value + other, self.currency)
        elif isinstance(other, Money):
            if self.currency != other.currency:
                new_value = self.value + \
                            other.value * table[self.currency] / table[other.currency]
            else:
                new_value = self.value + other.value
            return Money(new_value, self.currency)
        else:
            raise TypeError("unsupported operand type(s) for +:" \
                            f"'{type(self).__name__}' and '{type(other).__name__}'")

    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Money(self.value - other, self.currency)
        elif isinstance(other, Money):
            if self.currency != other.currency:
                new_value = self.value - \
                            other.value * table[self.currency] / table[other.currency] 
            else:
                new_value = self.value - other.value
            return Money(new_value, self.currency)
        else:
            raise TypeError("unsupported operand type(s) for -:" \
                            f"'{type(self).__name__}' and '{type(other).__name__}'")

    def __str__(self):
        return f'{self.value:.4f} {self.currency}'

    def __repr__(self):
        return f"Money({self.value}, '{self.currency}')"
