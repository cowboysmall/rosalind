import re
import math

from collections import defaultdict
from itertools   import combinations, product

import distance

DNA_COMPLEMENT = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
RNA_COMPLEMENT = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}


def dna_complement(string):
    dna = []

    for character in string:
        dna.append(DNA_COMPLEMENT[character])

    return ''.join(dna[::-1])


def dna_to_rna(string):
    rna_string = []

    for character in string:
        if character == 'T':
            rna_string.append('U')
        else:
            rna_string.append(character)

    return ''.join(rna_string)


def gc_content(string):
    return 100 * float(string.count('G') + string.count('C')) / len(string)


def gc_contents(strings):
    contents = []

    for label, string in strings.iteritems():
        contents.append((label, gc_content(string)))

    return contents


def kmer_composition(string, alpha, k):
    kmers = [''.join(p) for p in product(*[alpha] * k)]

    A = []
    for kmer in kmers:
        A.append(len(re.findall(r'(?=(%s))' % kmer, string)))

    return A


def kmer_frequency_table(string, k):
    stats = {}

    for i in xrange(len(string) - k + 1):
        kmer = string[i:i + k]
        if kmer not in stats:
            stats[kmer] = len(re.findall(r'(?=(%s))' % kmer, string))

    return stats


def kmer_frequency_table_mismatches(string, alpha, k, d):
    kmers = [''.join(p) for p in product(*[alpha] * k)]
    stats = {}

    for kmer in kmers:
        stats[kmer] = len(approximate_pattern_matching(kmer, string, d))

    return stats


def kmer_frequency_table_mismatches_and_complements(string, alpha, k, d):
    kmers = [''.join(p) for p in product(*[alpha] * k)]
    stats = defaultdict(int)

    for kmer in kmers:
        count1 = len(approximate_pattern_matching(kmer, string, d))
        count2 = len(approximate_pattern_matching(dna_complement(kmer), string, d))
        stats[kmer] = count1 + count2

    return stats


'''
    Here is the original version of the code I wrote - it ran, I 
    thought, quite quickly (around 5 seconds) but then I found this
    version on stack exchange, and was really impressed. I retain 
    both for reference.

    def kmer_clump(dna, k, L, t):
        kmers = []
        seen  = set()

        for i in xrange(len(dna) - k + 1):
            kmer  = dna[i:i + k]
            if kmer not in seen:
                found = [pos.start() for pos in re.finditer(r'(?=(%s))' % kmer, dna)]
                if len(found) >= t and min([found[i + t - 1] + k - found[i] for i in xrange(len(found) - t + 1)]) < L:
                    kmers.append(kmer)
                seen.add(kmer)

        return kmers

'''

def kmer_clump(dna, k, L, t):
    positions = defaultdict(list)
    kmers     = set()

    for i in xrange(len(dna) - k + 1):
        kmer = dna[i:i + k]
        if kmer not in kmers:
            while positions[kmer] and i + k - positions[kmer][0] > L:
                positions[kmer].pop(0)

            positions[kmer].append(i)
            if len(positions[kmer]) == t:
                kmers.add(kmer)

    return kmers


def kmer_reverse_frequency_table(table):
    freq = defaultdict(list)

    for kmer in table:
        freq[table[kmer]].append(kmer)

    return freq


def reverse_skew_table(genome):
    length = len(genome)

    counts = defaultdict(int)
    skew   = defaultdict(list)

    for i in xrange(length):
        counts[genome[i]] += 1
        skew[counts['G'] - counts['C']].append(i + 1)

    return skew


def skew_list(genome):
    length = len(genome)

    counts = defaultdict(int)
    skew   = [0 for _ in xrange(length)]

    for i in xrange(length):
        counts[genome[i]] += 1
        skew[i] = counts['G'] - counts['C']

    return skew


def approximate_pattern_matching(pattern, string, d):
    slength   = len(string)
    plength   = len(pattern)

    positions = []

    for i in xrange(slength - plength + 1):
        if distance.hamming(pattern, string[i:i + plength]) <= d:
            positions.append(i)

    return positions


def implanted_motifs(strings, k, d):
    length    = len(strings)
    motifs    = [''.join(p) for p in product('ACGT', repeat = k)]
    implanted = []

    counter = 0
    for motif in motifs:
        found = []

        for string in strings:
            if approximate_pattern_matching(motif, string, d):
                counter += 1

        if counter == length:
            implanted.append(motif)

        counter = 0

    return implanted


def check_occurences(rna):
    return rna.count('A') == rna.count('U') and rna.count('C') == rna.count('G')


"""
    Here are some earlier (and alternative) versions of the perfect 
    matcher:

    1) this was the original. It's a little nasty, but pretty 
    simple. Perhaps the start and end indexes are a little 
    confusing - especially around the recursive calls. I decided 
    I needed to at least think about making it a little easier 
    on the eyes and brain.

        def perfect_matchings(rna, start, end, A):
            if end < start:
                return 1
            elif A[start, end] == -1:
                A[start, end] = 0

                if check_occurences(rna[start:end + 1]):
                    for i in xrange(start + 1, end + 1, 2):
                        if rna[start] == COMPLEMENT[rna[i]]:
                            A[start, end] += matchings(rna, start + 1, i - 1, A) * matchings(rna, i + 1, end, A)
                            A[start, end] %= 1000000

            return A[start, end]


    2) here is a slightly altered version of 1 above - it is 
    constructed to hide the creation of the numpy array - called 
    A - used for sub-problem caching. The recursion step is also 
    hidden from view. It's still not perfect, but a step in the 
    right direction maybe. 

        import numpy as np

        def perfect_matchings(rna):
            N = len(rna)
            A = np.empty((N, N), dtype = int)
            A.fill(-1)

            def match(rna, start, end):
                if end < start:
                    return 1
                elif A[start, end] == -1:
                    A[start, end] = 0
                    if check_occurences(rna[start:end + 1]):
                        for i in xrange(start + 1, end + 1, 2):
                            if rna[start] == COMPLEMENT[rna[i]]:
                                A[start, end] += match(rna, start + 1, i - 1) * match(rna, i + 1, end)
                                A[start, end] %= 1000000
                return A[start, end]

            return match(rna, 0, N - 1)


    3) this was a version I wrote soon after - it seemed cleaner 
    to me because it used split strings, and no indexes were passed
    around. Also, it used a Python dictionary, rather than a numpy 
    array (not that I object to numpy in the slightest - on the 
    contrary, I love it - but I set myself the task of using standard 
    Python as much as possible on these solutions). The final version 
    is the one used below - it's same as this version, but as above 
    the sub-problem cache and recursion steps are now hidden.

        def perfect_matchings(rna, A):
            if len(rna) == 0:
                return 1
            elif rna not in A:
                A[rna] = 0
                if check_occurences(rna):
                    for i in xrange(1, len(rna), 2):
                        if rna[0] == COMPLEMENT[rna[i]]:
                            A[rna] += matchings(rna[1:i], A) * matchings(rna[i + 1:], A)
                            A[rna] %= 1000000
            return A[rna]


    4) and just out of interest, here is a version, based on a 
    version written in Ruby that I found in the forums, and 
    translated into Python. It is much slower, but I find it 
    fascinating. For some reason, examples of Dynamic Programming 
    always tend to turn my brain inside out, and this example is no 
    different in that respect.

        def perfect_matchings(rna):
            A = np.zeros((len(rna), len(rna)), dtype = int)

            for i in xrange(len(rna)):
                for j in xrange(i - 1, -1, -1):
                    if rna[i] == COMPLEMENT[rna[j]]:
                        A[i, j] = A[i - 1, j + 1] if j + 1 <= i - 1 else 1

                for j in xrange(i):
                    for k in xrange(j):
                        A[i, k] += A[i, j] * A[j - 1, k]
                        A[i, k] %= 1000000

            return A


    I have no idea what's going on here :-)

"""

def perfect_matchings(rna):
    A = {}

    def match(rna):
        if len(rna) < 2:
            return 1
        elif rna not in A:
            A[rna] = 0
            if check_occurences(rna):
                for i in xrange(1, len(rna), 2):
                    if rna[0] == RNA_COMPLEMENT[rna[i]]:
                        A[rna] += match(rna[1:i]) * match(rna[i + 1:])

        return A[rna]

    return match(rna)


def matchings(rna):
    A = {}

    def match(rna):
        if len(rna) < 2:
            return 1
        elif rna not in A:
            A[rna]  = match(rna[1:])
            A[rna] %= 1000000
            for i in xrange(1, len(rna)):
                if rna[0] == RNA_COMPLEMENT[rna[i]]:
                    A[rna] += match(rna[1:i]) * match(rna[i + 1:])

        return A[rna]

    return match(rna)


def check_wobble(rna1, rna2):
    return (rna1 == 'U' and rna2 == 'G') or (rna1 == 'G' and rna2 == 'U')


def wobble_matchings(rna):
    A = {}

    def match(rna):
        if len(rna) < 4:
            return 1
        elif rna not in A:
            A[rna]  = match(rna[1:])
            for i in xrange(4, len(rna)):
                if rna[0] == RNA_COMPLEMENT[rna[i]] or check_wobble(rna[0], rna[i]):
                    A[rna] += match(rna[1:i]) * match(rna[i + 1:])

        return A[rna]

    return match(rna)


def encode_protein(rna, table):
    encode = ''

    for chunk in [rna[i:i + 3] for i in xrange(0, len(rna), 3)]:
        if len(chunk) == 3:
            amino = table[chunk]
            if amino != 'Stop':
                encode += amino
            else:
                break

    return encode


def protein_mass(protein, table):
    total = 0.0

    for p in protein:
        total += table[p]

    return total


def complete_spectrum(protein, table):
    S = []

    for i in xrange(1, len(protein) + 1):
        S.append(protein_mass(protein[:i], table))
        S.append(protein_mass(protein[-i:], table))

    return S


def masses_from_cyclo_spectrum(spectrum):
    length = int((1 + math.sqrt(4 * len(spectrum) - 7)) / 2)
    masses = []

    for i in xrange(1, length + 1):
        masses.append([spectrum[i]])

    return masses


def cyclo_spectrum(masses, table):
    length   = len(masses)
    spectrum = [0, sum(masses)]
    masses   = masses * 2

    for i in xrange(length):
        for j in xrange(i + 1, i + length):
            spectrum.append(sum(masses[i:j]))

    return sorted(spectrum)


def linear_spectrum(masses, table):
    length   = len(masses)
    spectrum = [0, sum(masses)]

    for i in xrange(1, length):
        for j in xrange(length - i + 1):
            spectrum.append(sum(masses[j:j + i]))

    return sorted(spectrum)


def matching_peptides(masses, spectrum, table):
    candidates = masses[:]
    matches    = []

    while candidates:
        for candidate in candidates[:]:
            if set(linear_spectrum(candidate, table)) < set(spectrum):
                if sum(candidate) == spectrum[-1]:
                    matches.append(candidate)
                    candidates.remove(candidate)
            else:
                candidates.remove(candidate)
        candidates = [c + w for c in candidates for mass in masses]

    return matches


'''
    LEADERBOARDCYCLOPEPTIDESEQUENCING(Spectrum, N)
            Leaderboard = {0-peptide}
            LeaderPeptide = 0-peptide
            while Leaderboard is non-empty
                Leaderboard = Expand(Leaderboard)
                for each Peptide in Leaderboard
                    if Mass(Peptide) = ParentMass(Spectrum)
                        if Score(Peptide, Spectrum) > Score(LeaderPeptide, Spectrum)
                            LeaderPeptide = Peptide
                    else if Mass(Peptide) > ParentMass(Spectrum)
                        remove Peptide from Leaderboard
                Leaderboard = Cut(Leaderboard, Spectrum, N)
            output LeaderPeptide
'''

def leaderboard_matching_peptides(masses, spectrum, N, table):
    leader  = (0, [])
    leaders = [leader]

    def score(spectrum1, spectrum2):
        return len(set(spectrum1) & set(spectrum2))

    def expand():
        expanded = []
        for leader in leaders:
            for mass in masses:
                expand = leader[1] + mass
                if sum(expand) <= spectrum[-1]:
                    expanded.append((score(cyclo_spectrum(expand, table), spectrum), expand))
        return expanded

    def cut(candidates, count):
        if len(candidates) <= count:
            return candidates

        candidates = sorted(candidates, reverse = True)
        value      = candidates[count][0]
        while count < len(candidates) and candidates[count][0] == value:
            count += 1
        return sorted(candidates[:count])

    while leaders:
        candidates = []
        for candidate in expand():
            if sum(candidate[1]) == spectrum[-1]:
                if candidate[0] > leader[0]:
                    leader = candidate
            candidates.append(candidate)
        leaders = cut(candidates, N)

    return leader


def convolution_counts(spectrum):
    counts = defaultdict(int)

    for pair in combinations(sorted(spectrum), 2):
        difference = pair[1] - pair[0]
        if difference != 0:
            counts[difference] += 1

    return counts


def convolution_list(counts):
    convolution = []

    for item in sorted(counts.iteritems(), key = lambda x: x[1], reverse = True):
        convolution.extend([item[0]] * item[1])

    return convolution


def convolution_frequent(counts, M):
    ordered = sorted([(freq, mass) for mass, freq in counts.iteritems() if 57 <= mass <= 200], reverse = True)

    value = ordered[M][0]
    while M < len(ordered) and ordered[M][0] == value:
        M += 1

    return [[item[1]] for item in ordered[:M]]


def count_rnas_from_protein(protein, table):
    total = 3

    for c in protein:
        total *= table[c]
        total %= 1000000

    return total


def count_peptides_with_mass(mass, table):
    M       = [0 for _ in xrange(mass + 1)]
    M[0]    = 1

    masses  = set(table.values())

    for i in xrange(min(masses), mass + 1):
        for m in masses:
            if 0 <= i - m <= mass:
                M[i] += M[i - m]

    return M[mass]


def find_locations_in_protein(protein, motif):
    return [match.start() + 1 for match in re.compile(motif).finditer(protein)]


def find_locations_in_protein_data(data, motif):
    locations = []

    for protein in data:
        found = find_locations_in_protein(protein[1], motif)
        if found:
            locations.append((protein[0], found))

    return locations


def find_peptides_in_dna(dna, amino, table):
    dlength = len(dna)
    alength = len(amino) * 3
    chunks  = []

    for i in xrange(dlength - alength + 1):
        chunk   = dna[i:i + alength]

        rna     = dna_to_rna(chunk)
        protein = encode_protein(rna, table)
        if protein == amino:
            chunks.append(chunk)

        dnac    = dna_complement(chunk)
        rna     = dna_to_rna(dnac)
        protein = encode_protein(rna, table)
        if protein == amino:
            chunks.append(chunk)

    return chunks

