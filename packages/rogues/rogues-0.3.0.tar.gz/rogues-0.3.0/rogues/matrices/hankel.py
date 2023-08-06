import numpy as np
import warnings

def hankel(a, b=None):
    """
    hankel(a) returns a toeplitz matrix given "a", the first row of the
    matrix.  This matrix is defined as:

         [[   a[0], a[1], a[2], a[3], ..., a[n-1], a[n] ]]
          [   a[1], a[2], a[3], a[4], ...,   a[n],   0  ]
          [   a[2], a[3], a[4], ...,     ]
          ...
          [ a[n-2], a[n-1], a[n],  0,   ...
          [ a[n-1], a[n],      0,  0,   ...           0
          [   a[n],    0,      0,  0,   ...           0 ] ]


    Note that all the non-zero anti-diagonals are constant

    If called as hankel(a, b) then create the hankel matrix where a is the
    first column and b is the last row.  If a[-1] != b[0], a[-1] is chosen
    but a warning message is printed.  For example

    >>> import numpy as np
    >>> from rogues import hankel
    >>> a = np.arange(10)
    >>> b = np.arange(10,20)
    >>> h = hankel(a, b)
    Warning: a[-1] != b[0]. a[-1] is chosen
    >>> h
    array([[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
           [ 1,  2,  3,  4,  5,  6,  7,  8,  9, 11],
           [ 2,  3,  4,  5,  6,  7,  8,  9, 11, 12],
           [ 3,  4,  5,  6,  7,  8,  9, 11, 12, 13],
           [ 4,  5,  6,  7,  8,  9, 11, 12, 13, 14],
           [ 5,  6,  7,  8,  9, 11, 12, 13, 14, 15],
           [ 6,  7,  8,  9, 11, 12, 13, 14, 15, 16],
           [ 7,  8,  9, 11, 12, 13, 14, 15, 16, 17],
           [ 8,  9, 11, 12, 13, 14, 15, 16, 17, 18],
           [ 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]])
    """
    # Error checking...
    try:
        m, = a.shape
        if b != None:
            n, = b.shape
    except (ValueError, AttributeError):
        raise ValueError("Input arrays must be one dimensional")

    if b == None:
        b = np.zeros_like(a)
        n = m
    elif a[-1] != b[0]:
        warnings.warn("a[-1] != b[0]. a[-1] is chosen")

    k = np.r_[a, b[1:]]
    h = k[:n]
    for i in range(1, m):
        h = np.vstack((h, k[i:i + n]))

    return h
