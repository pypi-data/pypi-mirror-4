
""" ``feistel`` module.
"""


def make_feistel_number(f):
    """ Generate pseudo random consistent reversal number
        per Feistel cypher algorithm.

        see http://en.wikipedia.org/wiki/Feistel_cipher

        >>> feistel_number = make_feistel_number(sample_f)
        >>> feistel_number(1)
        573852158
        >>> feistel_number(2)
        1788827948
        >>> feistel_number(123456789)
        1466105040

        Reversable

        >>> feistel_number(1466105040)
        123456789
        >>> feistel_number(1788827948)
        2
        >>> feistel_number(573852158)
        1
    """
    def feistel_number(n):
        l = (n >> 16) & 65535
        r = n & 65535
        for i in (1, 2, 3):
            l, r = r, l ^ f(r)
        return ((r & 65535) << 16) + l
    return feistel_number


def sample_f(x):
    return int((((1366 * x + 150889) % 714025) * 32767) // 714025)
