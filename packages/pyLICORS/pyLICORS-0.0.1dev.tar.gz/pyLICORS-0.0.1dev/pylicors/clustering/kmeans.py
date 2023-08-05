"""
Kmeans on data matrix.  Wrapper for several python implementations including:
    - pyopencv or cv
    - scikits.learn or sklearn
    - Pycluster
"""

import time
import numpy
import scipy
import sys
from pylicors.utils.array2frequencies import count_table
from pylicors.utils import relabel_list


def kmeans(data,
           nclusters,
           whiten=False,
           method="pyopencv",
           max_iter=10,
           median=False,
           ntries=5,
           verbose=True):
    """Kmeans

    A general interface for Kmeans on a data matrix 'data' in R^{n * p}, where
    each row contains the samples in p dimensional space.

    Args:
        data: numpy array of size (n x p), where n are the number of samples
              and p is the dimension
        nclusters: number of clusters (aka k)
        whiten: indicator, if 'True' data is whitened
        method: string; which method should be used
        max_iter: int; maximum number of iterations
        median: indicator; if 'True' it uses a kmedian (only for
                 method='PyCluster')
        ntries: how many random starts should be used
        verbose: indicator; if 'True' output is shown in the console

    Returns:
        - labels: array of length n containing the labels of each point
        - centroids: array of size 'nclusters * p' containing the centroids of
                     each cluster
        - intertia: the residual sum of squares of this solution (only for
                    method = 'scikits'

    Examples:
    >>> numpy.random.seed(10)
    >>> XX = numpy.random.normal(size = (100, 5))
    >>> out = kmeans(XX, 3, method = "sklearn")
    """

    nsamples = data.shape[0]
    ndim = data.shape[1]

    centroids = numpy.zeros((nclusters, data.shape[1]))

    if whiten:
        data = scipy.cluster.vq.whiten(data)

    inertia = 0
    start = time.time()
    if method == "scipy":
        centroids, labels = scipy.cluster.vq.kmeans2(data,
                                                     nclusters,
                                                     iter=max_iter)
    elif method == "Pycluster":
        try:
            import Pycluster
        except ImportError:
            sys.exit("Error: Package " + method + " not found.")
        if median:
            labels = Pycluster.kcluster(data,
                                        nclusters=nclusters,
                                        method='m')[0]
            for c_iter in xrange(nclusters):
                centroids[c_iter] = numpy.median(data[labels == c_iter],
                                                 axis=0)
        else:
            labels = Pycluster.kcluster(data, nclusters=nclusters)[0]

    elif method == "sklearn":
        try:
            import sklearn.cluster as skc
        except ImportError:
            sys.exit("Error: Package " + method + " not found.")
        centroids, labels, inertia = skc.k_means_.k_means(data,
                                                          k=nclusters,
                                                          n_init=ntries,
                                                          max_iter=max_iter)
    elif method == "pyopencv":
        # pyopencv is faster (boost library) than cv
        # if pyopencv is not installed, try to load cv
        try:
            import pyopencv
        except ImportError:
            try:
                method = "cv"
            except ImportError:
                sys.exit("Error: Package " + method + " must be installed.")

        # see http://www.aishack.in/2010/08/k-means-clustering-in-opencv/
        data = pyopencv.asMat(data.reshape(nsamples,
                                           ndim).astype('float32'))
        # K Means Clustering
        clusters = pyopencv.Mat(data.size(), pyopencv.CV_32SC1)
        criteria = pyopencv.TermCriteria(pyopencv.TermCriteria.EPS +
                                         pyopencv.TermCriteria.MAX_ITER,
                                         10, 1.0)
        criteria.MAX_ITER = max_iter
        criteria.eps = 0.1

        centroids = pyopencv.kmeans(data, nclusters, clusters,
                                    criteria, ntries,
                                    pyopencv.KMEANS_PP_CENTERS)[1]
        labels = numpy.array(clusters[:, 0])
        centroids = centroids.ndarray

    if method == "cv":
        try:
            import cv
        except ImportError:
            sys.exit("Error: You must have at least a working 'cv' module.")
        data = cv.fromarray(data.astype('float32'))
        # K Means Clustering
        clusters = cv.CreateMat(nsamples, 1, cv.CV_32SC1)
        criteria = (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, max_iter, 0.1)
        inertia = cv.KMeans2(data, nclusters, clusters, criteria)
        labels = numpy.array(clusters[:, 0]).ravel()
        data = numpy.array(data).reshape(nsamples, ndim)

    if not centroids:
        for c_iter in xrange(nclusters):
            centroids[c_iter] = numpy.mean(data[labels == c_iter], axis=0)

    elapsed = (time.time() - start)

    if verbose:
        prefix = "Running time for Kmeans:"
        if elapsed > 60:
            print prefix + str(numpy.round(elapsed / 60, 2)) + "minutes."
        elif elapsed > 1e-3:
            print prefix + str(numpy.round(elapsed, 4)) + "seconds."
        else:
            print prefix + numpy.round(elapsed / 1000.0, 4) + "ms."

    return{'labels': numpy.array(labels),
           'centroids': centroids,
           'inertia': inertia}


def remove_small_clusters(min_size, centroids, labels):
    """
    Removes clusters with less points than 'min_size'. It does this
    by merging this very small group to its closest group (comparing
    respective centroids.

    Args:
        min_size: minimum size of clusters
        centroids: array of centroids
        labels: array of labels

    Return:
        a list with new centroids and labels

    """
    counts = count_table(labels, dictionary=False)
    # if no group has less than 'min_size' points, then return original labels
    # and centroids
    if min(counts) > min_size:
        return{'labels': labels, 'centroids': centroids}

    labels = numpy.array(labels)
    unique_labels = numpy.unique(labels)

    ind = (counts < min_size)

    centroids_of_small_groups = centroids[ind]

    temp_tree = scipy.spatial.cKDTree(centroids)
    niter = 0
    for label in list(unique_labels):
        if ind[label]:
            ndx = temp_tree.query(centroids_of_small_groups[niter],
                                  k=2, p=2, eps=0)['i']
            numpy.place(labels, labels == label, ndx[1])
            niter += 1
            # after merging labels, don't forget to also adjust centroids.
            # Since this is done by averaging, we can compute a weighted mean
            # of original centroids and it is not necessary to collect all data
            # again.
            big_centroid_weight = counts[ndx[1]]
            big_centroid_weight /= float(counts[label] + counts[ndx[1]])
            # centroids[ndx[1]] = centroids[ndx[1]] * big_centroid_weight
            # + (1-big_centroid_weight) * centroids[ii]
            centroids[ndx[1]] *= big_centroid_weight
            centroids[ndx[1]] += (1 - big_centroid_weight) * centroids[label]

    return{'labels': numpy.array([relabel_list(labels)]),
           'centroids': centroids[not numpy.array(ind)]}

if __name__ == '__main__':
    pass
