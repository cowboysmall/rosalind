import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

import files
import genetics


def main(argv):
    line   = files.read_line(argv[0])
    genome = [[int(val) for val in chromosome.split(' ')] for chromosome in line[1:-1].split(')(')]

    print ', '.join(str(c) for c in genetics.colored_edges_from_genome(genome))


if __name__ == "__main__":
    main(sys.argv[1:])
