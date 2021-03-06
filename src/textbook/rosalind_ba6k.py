import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

import files
import genetics


def main(argv):
    lines   = files.read_lines(argv[0])
    P       = [int(val) for val in lines[0][1:-1].split(' ')]
    indices = [int(i) for i in lines[1].split(', ')]
    genome  = genetics.two_break_on_genome(P, *indices)

    print ' '.join('(%s)' % (' '.join('+%s' % c if c > 0 else '%s' % c for c in g)) for g in genome)


if __name__ == "__main__":
    main(sys.argv[1:])
