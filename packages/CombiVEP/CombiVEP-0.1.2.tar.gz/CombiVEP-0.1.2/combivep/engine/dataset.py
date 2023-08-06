import numpy as np

class DataSet(object):
    """

    For manipulating 3 kinds of dataset, training, validation, and test dataset

    """


    def __init__(self, file_name):
        object.__init__(self)

        __data = np.loadtxt(file_name, dtype='S20')
        self.n_data, self.n_cols = __data.shape
        self.n_features          = self.n_cols - 2
        self.keys                = __data[:,0]

        #Transpose the matrixes so that it can be easily understood by MLP
        self.feature_vectors     = __data[:,1:self.n_cols-1].astype(np.float).T
        self.targets             = __data[:,self.n_cols-1].astype(np.int).T


