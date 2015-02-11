from collections import defaultdict


def frequency_table(A):
    freq  = defaultdict(int)

    for a in A:
        freq[a] += 1

    return freq


def reverse_frequency_table(A):
    return [(value, key) for key, value in frequency_table(A).iteritems()]


def majority_element(A):
    l        = len(A)
    elements = filter(lambda x: x[0] > l / 2, reverse_frequency_table(A))

    return max(elements)[1] if elements else -1


def max_heapify(A, i, l):
    left    = 2 * i + 1
    right   = 2 * i + 2
    largest = i

    if left < l and A[largest] < A[left]:
        largest = left

    if right < l and A[largest] < A[right]:
        largest = right

    if largest != i:
        A[i], A[largest] = A[largest], A[i]
        max_heapify(A, largest, l)


def max_heap(A):
    l = len(A)

    for i in xrange(l // 2, -1, -1):
        max_heapify(A, i, l)

    return A


def min_heapify(A, i, l):
    left     = 2 * i + 1
    right    = 2 * i + 2
    smallest = i

    if left < l and A[smallest] > A[left]:
        smallest = left

    if right < l and A[smallest] > A[right]:
        smallest = right

    if smallest != i:
        A[i], A[smallest] = A[smallest], A[i]
        min_heapify(A, smallest, l)


def min_heap(A):
    l = len(A)

    for i in xrange(l // 2, -1, -1):
        min_heapify(A, i, l)

    return A


def count_inversions(A):
    l = len(A)
    c = 0

    for i in xrange(len(A) - 1):
        for j in xrange(i + 1, len(A)):
            if A[i] > A[j]:
                c += 1

    return c

