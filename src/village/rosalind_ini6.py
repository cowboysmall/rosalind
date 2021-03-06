import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

import files
import arrays


def main(argv):
    words = files.read_line_of_words(argv[0])
    freq  = arrays.frequency_table(words)

    print '\n'.join('%s %s' % (w, f) for w, f in freq.iteritems())


if __name__ == "__main__":
    main(sys.argv[1:])
