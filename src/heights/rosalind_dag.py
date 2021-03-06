import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))

import files
import graphs


def main(argv):
    k, Gs = files.read_graphs(argv[0])
    C     = []

    for G in Gs:
        n, m  = G[:2]
        edges = G[2]
        nodes = [n for n in xrange(1, n + 1)]
        C.append(graphs.acyclic(nodes, edges))

    print ' '.join('1' if C[n] else '-1' for n in xrange(k))


if __name__ == "__main__":
    main(sys.argv[1:])
