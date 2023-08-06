"""Directional parity encoder.

Python implementation of the directional parity algorithum used in
Radio Lab's Cicada project (http://project.wnyc.org/cicadas)
"""
from errors import OutOfRange

def bitify(i, bits):
    """Convert a number into a base 2 series of bits.  LSB at the end."""
    try:
        v = map(bool, map(int, bin(i).replace('0b', '')))
        if len(v) < bits:
            v[:0] = [0] * (bits - len(v))
        return v
    except ValueError:
        raise ValueError("Bad %d" % i)

def encode_extended_range(bits, value):
    value -= 2 ** (bits-1)
    nibble =  bitify(value, bits//2)
    bits = []
    bits.extend(reversed(nibble))
    bits.append(True)
    bits.extend(nibble)
    return bits

def encode(bit_length, value):
    """Encode a value as a direction partiy encoded sequence of bits."""
    OutOfRange.raise_if_qualifies(bit_length, value)

    if value >= 2**(bit_length - 1):
        return encode_extended_range(bit_length, value)

    mask = 2**(bit_length/2) - 1
    lower = value & mask
    upper = (value >> bit_length//2) & mask
    center = lower > upper
    bits = bitify(lower, bit_length//2)
    bits.reverse()
    bits.append(center)
    bits.extend(bitify(upper, bit_length//2))
    map(bool, bits)
    return bits


def limit(bits):
    return OutOfRange.limit(bits)

def main(argv):
    if len(argv) not in (2,3):
        print "Usage: %s <# of bits> (<value>)\n"
        print 
        print "If value is provided, returns the encoding, otherwise returns the largest value that could be encoded."
        print
        print "See http://github.com/wnyc/directional_parity for more details"
        return 1
    argv = map(int, argv[1:])
    if len(argv) == 1:
        print limit(*argv)
    else:
        print ' '.join(map({True:'1', False: '0'}.get, encode(*argv)))
    return 0
