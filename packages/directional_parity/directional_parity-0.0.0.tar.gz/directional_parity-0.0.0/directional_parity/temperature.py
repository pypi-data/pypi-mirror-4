from decoder import decode

def main(argv):
    if len(argv) <= 1:
        print "Usage: %s bit0 bit1 bit2 ... bitn # (n is odd)" % (argv[0],)
        print
        print "See http://github.com/wnyc/directional_parity for more details"
    value = float(decode(map(int, argv[1:])))
    f = (value * 9.0 - 80.0) / 20.0
    c = (value / 4.0) - 20.0
    print "%0.2fC %0.2fF" % (c, f)
    return 0


