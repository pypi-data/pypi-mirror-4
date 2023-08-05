"""
Module to project data from R^n to R^k, where k < n.
"""

import numpy


def create_projection_matrix(input_dim, output_dim, seed = 'random', method="normal"):
    """Makes a projection matrix from R^n to R^k, where k < n.

    Args:
        input_dim: dimension of the input space (n above)
        output_dim: dimension of the projected space (k above)
        method: string; what type of distribution for the projection matrix
        seed: what seed should be used

    Returns:
        A numpy.array of size (n x k)

    Example:
        >>> PP = create_projection_matrix(10, 2, method="normal", seed=2)
        >>> PP
        array([[-0.41675785, -0.05626683, -2.1361961 ,  1.64027081, -1.79343559,
                -0.84174737,  0.50288142, -1.24528809, -1.05795222, -0.90900761],
               [ 0.55145404,  2.29220801,  0.04153939, -1.11792545,  0.53905832,
                -0.5961597 , -0.0191305 ,  1.17500122, -0.74787095,  0.00902525]])
    """
    if seed == "random":
        seed = numpy.random.randint(1e6)

    numpy.random.seed(seed)
    try:
        if method == "normal":
            proj_mat = numpy.random.standard_normal((output_dim, input_dim))
        elif method == "unif":
            proj_mat = numpy.random.uniform(-1, 1, (output_dim, input_dim))
        elif method == "mean":
            proj_mat = numpy.ones((1, input_dim)) / float(input_dim)
    except ValueError:
        print("Please enter a valid method.")
    return(proj_mat)


def project_data(data,
                 projection):
    """Linear projection of data onto subspace

    Projects the data from original space to a lower-dimensional linear
    subspace using the projection matrix 'projection'.

    Args:
        data: data matrix of size nsamples * n
        projection: projection matrix of size n * k

    Return:
        A numpy array of size nsamples * k

    Examples:
    >>> # generate a projection matrix from 10 to 2 dimensional space
    >>> PP = create_projection_matrix(10, 2, method="normal")
    >>> # 100 samples from an exponential in 10 dim
    >>> data_in_10 = numpy.random.exponential(1, (100, 10))
    >>> # project on two dimensions and plot
    >>> data_proj_2 = project_data(data_in_10, projection)
    """
    return(numpy.dot(data, projection.T))


if __name__ == '__main__':
    pass
