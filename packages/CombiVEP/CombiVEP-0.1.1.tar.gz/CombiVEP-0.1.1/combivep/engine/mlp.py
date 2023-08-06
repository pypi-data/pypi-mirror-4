import numpy as np
import combivep.settings as combivep_settings

class Mlp(object):
    """MultiLayer Perceptron class"""


    def __init__(self, n_features,
                       seed=combivep_settings.DEFAULT_SEED,
                       n_hidden_nodes=combivep_settings.DEFAULT_HIDDEN_NODES):
        object.__init__(self)
        #set initial configuration values and memorize input
        self.__n_features      = n_features
        self.__n_hidden_nodes  = n_hidden_nodes
        self.best_weights1     = []
        self.best_weights2     = []

        #set initial values of weight matrixs to random small values
        np.random.seed(seed)
        self.__weights1  = 0.01 * np.random.rand(n_hidden_nodes, self.__n_features+1)
        self.__weights2  = 0.01 * np.random.rand(1, n_hidden_nodes+1)

        #set initial values of momentum matrixs to zeros
        self.__momentums1 = np.zeros((n_hidden_nodes, self.__n_features+1))
        self.__momentums2 = np.zeros((1, n_hidden_nodes+1))

    def forward_propagation(self, dataset):
        #calculate sum of product in the hidden layer
#        print self.__weights1.shape
#        print dataset.feature_vectors.shape
        in1  = np.dot(self.__weights1,
                      np.concatenate((dataset.feature_vectors, 
                                      np.ones((1, dataset.n_data))
                                      ), 
                                     axis=0
                                     ) 
                      )

        #calculate outputs of hidden layer using non-linear function
        self.__out1 = np.concatenate((2/(1+np.exp(-in1))-1, 
                                      np.ones((1, dataset.n_data))
                                      ), 
                                     axis=0
                                     )

        #calculate sum of product in the output node
        in2 = np.dot(self.__weights2, self.__out1)

        #calculate output of mlp using non-linear function
        self.__out2 = 1/(1+np.exp(-in2))

        #return prediction result
        return self.__out2

    def backward_propagation(self, training_dataset):
        model_error = self.calculate_error(self.__out2, training_dataset.targets)
        self.__error_signal_output = np.multiply(model_error, 
                                                 np.multiply((1-self.__out2), 
                                                             self.__out2
                                                             )
                                                 )
        self.__error_signal_hidden = np.multiply(np.dot(self.__weights2.T, 
                                                        self.__error_signal_output
                                                        ), 
                                                 np.multiply((1+self.__out1), 
                                                             (1-self.__out1)
                                                             )
                                                 ) * 0.5
        self.__error_signal_hidden = self.__error_signal_hidden[0:self.__n_hidden_nodes]

        return np.sum(np.absolute(model_error), axis=1).item(0)

    def weight_update(self, training_dataset, coefficient=combivep_settings.MLP_COEFFICIENT, step_size=combivep_settings.STEP_SIZE):
        self.__momentums1 = np.subtract((self.__momentums1*coefficient),
                                        (np.dot(self.__error_signal_hidden, 
                                                np.concatenate((training_dataset.feature_vectors,
                                                                np.ones((1, training_dataset.n_data))
                                                                ), 
                                                               axis=0
                                                               ).T
                                                )
                                         )*(1-coefficient)
                                        )
        self.__momentums2 = np.subtract((self.__momentums2*coefficient),
                                        (np.dot(self.__error_signal_output, 
                                                self.__out1.T
                                                )
                                         )*(1-coefficient)
                                        )
        self.__weights1 = np.add(self.__weights1, np.multiply(self.__momentums1,
                                                              step_size)
                                 )
        self.__weights2 = np.add(self.__weights2, np.multiply(self.__momentums2,
                                                              step_size)
                                 )
        return self.__weights1, self.__weights2

    def calculate_error(self, actual_output, expected_output):
        return np.subtract(actual_output, expected_output)

    def export_best_parameters(self, params_file=combivep_settings.USER_PARAMETERS_FILE):
        np.savez(params_file, best_weights1=self.best_weights1, best_weights2=self.best_weights2)

    def import_parameters(self, params_file=combivep_settings.USER_PARAMETERS_FILE):
        params = np.load(params_file)
        self.__weights1 = params['best_weights1']
        self.__weights2 = params['best_weights2']

    def get_weights1(self):
        """for unit testing purpose"""
        return self.__weights1


