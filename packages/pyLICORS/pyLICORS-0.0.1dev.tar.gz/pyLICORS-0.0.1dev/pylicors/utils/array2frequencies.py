"""
Collection of functions to convert arrays with factors to frequencies.
Similar in functionality to R's 'table()' function.
"""

import numpy


def count_table(xx, dictionary=True, start=0):
    """Create a table of counts of elements in 'xx'.

    Similar to R function 'table()'.

    Args:
        xx: numpy array
        dictionary: indicator, if 'True' returns a dictionary; otherwise an
                    array.
        start: integer; where should the labels for the dictionary start;
               default '0'
    Returns:
        Either a dictionary or array of counts.

    Examples:
    >>> count_table([1, 2, 5, 5, 5, 5, 1, 2, 3, 2, 3])
    {0: 0, 1: 2, 2: 3, 3: 2, 4: 0, 5: 4}
    >>> count_table([1, 2, 5, 5, 5, 5, 1, 2, 3, 2, 3], False)
    array([0, 2, 3, 2, 0, 4])
    """
    if isinstance(xx, list):
        xx = numpy.array(xx)

    counts = numpy.bincount(xx)
    counts = counts[start:]
    if dictionary:
        return(dict(zip(range(start, len(counts) + start), counts)))
    else:
        return(counts)


def frequency_table(xx, dictionary=True, remove_zeros=False):
    """
    Make a table with frequencies of the elements in xx.

    Args:
        xx: numpy array
        dictionary: indicator, if 'True' returns a dictionary; otherwise an
                    array.
        remove_zeros: indicator; if 'True' labels that never occur are removed
                      from the dictionary (only for 'dictionary=True').
    Returns:
        Either a dictionary or array of counts.
    """
    if isinstance(xx, list):
        xx = numpy.array(xx)
    counts = numpy.bincount(xx)
    frequencies = numpy.array(counts, float) / sum(counts)
    if remove_zeros:
        frequencies = frequencies[frequencies > 0]
    if dictionary:
        return(dict(zip(range(len(frequencies)), frequencies)))
    else:
        return(frequencies)


def array2frequencies(array):
    """Converts an array of integers to frequencies at corresponding positions

    Args:
        array: an array containing integers

    Returns:
        array where labels are replace by frequencies

    Examples:
    >>> array2frequencies(numpy.array([1, 2, 3, 1, 3]))
    array([ 0.4,  0.2,  0.4,  0.4,  0.4])
    """

    f_table = frequency_table(array)
    frequency_array = numpy.empty(len(array), "float")
    for ii, freq in f_table.iteritems():
        frequency_array[array == ii] = freq
    return(frequency_array)

if __name__ == '__main__':
    pass
