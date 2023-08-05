"""
Security-related utilities
"""

def check_equal_constant_time(a, b):
    """
    Return ``True`` if string ``a`` is equal to string ``b``.

    If ``a`` and ``b`` are of the same length, this function will take the same
    amount of time to execute, regardless of whether or not a and b are equal.
    """
    if len(a) != len(b):
        return False
    result = 0
    for c1, c2 in zip(a, b):
        result |= ord(c1) ^ ord(c2)
    return result == 0
