
class OddBitLengthsOnly(ValueError):
    """Wrong number of bits
    
    Directional parity encoded values must have an odd number of bits.
    """

    @property 
    def bits(self):
        "The number of bits the user attempted to use."
        return self.__bits

    def __init__(self, bits):
        self.__bits = bits
        ValueError.__init__(self, "Directional Parity bit lengths must be an odd positive integer, not %d" % (self.bits))

    @classmethod
    def raise_if_qualifies(cls, bits):
        if bits % 2 == 0:
            raise cls(bits)


class OutOfRange(ValueError):
    """OutOfRange
    
    Attempted to encode a negative number or too large a positive number.  The directional parity encoding sceheme can only encode a value within the range [0, 2**(b-1) + 2**(b/2)] where b is the number of bits.
    """
                                
    def __init__(self, bits, value):
        self.__bits = bits
        self.__value = value
        if value < 0:
            problem = "%d is negative." % value 
        else:
            problem = "%d is too large." % value
        ValueError.__init__(self, "Can only encode positive numbers not greater than %d in an %d bit directional paritiy number.  %s" % (self.limit(bits), bits, problem))

    @staticmethod
    def limit(bits):
        if bits < 0:
            raise ValueError("The number of bits passed to %s.limit must be odd and greater than 2.  %d does not quality" % (self.__class__.__name__, bits))
        return 2**(bits-1) + 2**(bits//2) - 1

    @classmethod
    def raise_if_qualifies(cls, bits, value):
        OddBitLengthsOnly.raise_if_qualifies(bits)
        if value > cls.limit(bits):
            raise cls(bits, value)
        
