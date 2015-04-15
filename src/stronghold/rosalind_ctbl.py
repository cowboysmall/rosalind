import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

import files
import phylogeny


def main(argv):
    table  = phylogeny.create_table(files.read_line(argv[0]))

    print '\n'.join(''.join(str(r) for r in row) for row in table)


if __name__ == "__main__":
    main(sys.argv[1:])
