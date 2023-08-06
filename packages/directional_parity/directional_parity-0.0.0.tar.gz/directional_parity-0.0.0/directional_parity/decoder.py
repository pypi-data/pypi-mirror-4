"""Directional parity encoder.

Python implementation of the directional parity algorithum used in
Radio Lab's Cicada project (http://project.wnyc.org/cicadas)
"""
from errors import OddBitLengthsOnly


def to_int(seq):
    lookup = {True: '1', False: '0'}
    seq = list(seq)
    seq =  map(bool, map(int, seq))
    seq = map(lookup.get, seq)
    return int(''.join(seq), 2)

def decode(seq):
    """Decode a directional parity encodede value.
    
    Args: 
      seq: A sequence of "boolean looking" objects such as [0, 1, 0], [False, True, False] or "010"
    Returns:
      An integer representing its value
    """

    OddBitLengthsOnly.raise_if_qualifies(len(seq))
    seq = map(bool, map(int, seq))
    bits = len(seq)

    low =  to_int(list(reversed(seq[:bits//2])))
    center = seq[bits//2]
    high = to_int(seq[bits//2 + 1:])

    if center and low == high:
        return 2**(bits-1) + low
    
    if  center ^ (low > high):
        return decode(list(reversed(seq)))

    return low | high << (bits // 2)
    
    
def main(argv):
    if len(argv) <= 1:
        print "Usage: %s bit0 bit1 bit2 ... bitn # (n is odd)" % (argv[0],)
        print
        print "See http://github.com/wnyc/directional_parity for more details"
    print decode(map(int, argv[1:]))
    return 0


