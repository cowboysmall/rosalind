import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

import files


def main(argv):
    lines = files.read_lines(argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
