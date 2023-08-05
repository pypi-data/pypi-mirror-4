"""
Convertes spatial dimension (r,t) to a one-dimensional index set.
"""

import itertools


def spatial2onedim(indices):
    """
    This function converts the spatial index set of an ndim space to a
    one-dimensional sequence (numbering the indices one-by-one).
    E.g. for a 2D index set (element position in a matrix) it iterates
    first over the rows, and in each row over the columns. If the
    matrix is of size (n x m) then the output sequence is a dictionary of
    length n*m, with keys from 1 ... n*m, and each key refers
    to a unique pair (i,j) of the matrix.

    Args:
        indices: list of indices in each dimension

    Return:
        a dictionary of length n_1 * n_2 * ... * n_k, where k is the number of
        dimensions, and n_j are the number of indices in dimension j

    Examples:
        >>> bb = spatial2onedim(indices = (range(2), range(1)))
        >>> bb
        {'dict': {0: (0, 0), 1: (1, 0)},
        'iter': <itertools.product object at 0x0EE23A58>}
        >>> print(bb.values())
        [{0: (0, 0), 1: (1, 0)}, <itertools.product object at 0x0EE23A58>]
    """
    ndim = len(indices)

    if ndim == 1:
        index_tuple = indices[0]
    elif ndim == 2:
        index_tuple = itertools.product(indices[0], indices[1])
    else:
        print("not supported yet")
        return()
    spatial_dict = {}
    niter = 0
    for iter_tup in index_tuple:
        spatial_dict[niter] = iter_tup
        niter += 1

    return{'dict': spatial_dict,
           'iter': index_tuple}
