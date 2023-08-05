"""
A function to relabel lists with integer labels.  Is used to make functions
start with '0' after merging and have consecutive numbers without gaps
in between.
"""

import numpy
import operator
from pylicors.utils.array2frequencies import count_table

def relabel_list(labels, sort=True, start_label=0):
    """Relabels a list

    Relabels a list so it starts from 'start_label' and has no gaps in between.

    Args:
        labels: a Python list containing integer labels
        sort: indicator, if 'True' the labels are sorted in decreasing order
        start_label: integer specifying the start of the labels
    Return:
        A list of relabeled integers

    Examples:
    >>> relabel_list([1, 2, 5, 5, 5, 5, 2, 3, 2, 3])
    [0, 2, 3, 3, 3, 3, 2, 1, 2, 1]
    """
    labels_array = numpy.array(labels, 'int')
    unique_labels = numpy.unique(labels)
    nclusters = len(unique_labels)
    count_dict = count_table(numpy.array(labels))

    niter = 0
    # if sort = True, then new labels are ordered by descending frequency
    # of original list
    if sort:
        sorted_x = sorted(count_dict.iteritems(), key=operator.itemgetter(1))
        for elem in sorted_x:
            if elem[1] > 0:
                numpy.place(labels_array,
                            labels_array == elem[0],
                            niter + 2 * nclusters)
                niter += 1
    # if sort = False, then just relabel them to get rid of the 0s
    else:
        for elem in unique_labels:
            if count_dict[elem] > 0:
                numpy.place(labels_array,
                            labels_array == elem,
                            niter + 2 * nclusters)
                niter += 1

    labels_array -= 2 * nclusters
    labels_array += start_label
    return(list(labels_array))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
