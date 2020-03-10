table = {'RUB': 1, 'USD': 67.5175, 'JPY': 63.777, 'KZT': 17.6482, 'BYN': 30.1592}

class Money:
    def __init__(self, value, currency=None):
        self.value = value

        if currency is None:
            self.currency = None
        elif currency.upper() not in table:
            raise KeyError
        else:
            self.currency = currency.upper()

    def convert(self, currency):
        self.value *= table[currency.upper()] / table[self.currency]
        self.currency = currency.upper()

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Money(self.value + other, self.currency)
        elif isinstance(other, Money):
            if other.currency is None:
                if self.currency is None:
                    raise TypeError("Both operands doesn't have currency")
                else:
                    return Money(self.value + other.value, self.currency)
            
            if self.currency is None:
                if other.currency is None:
                    raise TypeError("Both operands doesn't have currency")
                else:
                    return Money(self.value + other.value, other.currency)

            if self.currency != other.currency:
                new_value = self.value + \
                            other.value * table[other.currency] / table[self.currency]
            else:
                new_value = self.value + other.value
            return Money(new_value, self.currency)
        else:
            raise TypeError("unsupported operand type(s) for +:" \
                            f"'{type(self).__name__}' and '{type(other).__name__}'")

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Money(self.value - other, self.currency)
        elif isinstance(other, Money):
            if other.currency is None:
                if self.currency is None:
                    raise TypeError("Both operands doesn't have currency")
                else:
                    return Money(self.value - other.value, self.currency)
            
            if self.currency is None:
                if other.currency is None:
                    raise TypeError("Both operands doesn't have currency")
                else:
                    return Money(self.value - other.value, other.currency)

            if self.currency != other.currency:
                new_value = self.value - \
                            other.value * table[other.currency] / table[self.currency] 
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
