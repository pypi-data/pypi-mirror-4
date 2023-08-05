
""" ``luhn`` module.
"""


def luhn_checksum(n):
    """ Calculates checksum based on Luhn algorithm, also known as
        the "modulus 10" algorithm.

        see http://en.wikipedia.org/wiki/Luhn_algorithm

        >>> luhn_checksum(1788827948)
        0
        >>> luhn_checksum(573852158)
        1
        >>> luhn_checksum(123456789)
        7
    """
    digits = digits_of(n)
    checksum = (sum(digits[-2::-2]) +
                sum(sum2digits(d << 1) for d in digits[-1::-2])) % 10
    return checksum and 10 - checksum or 0


def luhn_sign(n):
    """ Signs given number by Luhn checksum.

        >>> luhn_sign(78482748)
        784827487
        >>> luhn_sign(47380210)
        473802106
        >>> luhn_sign(123456789)
        1234567897
    """
    return luhn_checksum(n) + (n << 3) + (n << 1)


def is_luhn_valid(n):
    """
        >>> is_luhn_valid(1234567897)
        True
        >>> is_luhn_valid(473802106)
        True
        >>> is_luhn_valid(34518893)
        False
    """
    digits = digits_of(n)
    checksum = sum(digits[-1::-2]) + sum(sum2digits(d << 1)
                                         for d in digits[-2::-2])
    return checksum % 10 == 0


def digits_of(n):
    """ Returns a list of all digits from given number.

        >>> digits_of(123456789)
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return [int(d) for d in str(n)]


def sum2digits(d):
    """ Sum digits of a number that is less or equal 18.

        >>> sum2digits(2)
        2
        >>> sum2digits(17)
        8
    """
    return (d // 10) + (d % 10)
