import os.path
import numpy as np
import matplotlib.pyplot as plt
import combivep.settings as combivep_settings
from combivep.engine.mlp import Mlp

class Trainer(Mlp):
    """This class is to produce parameters used by the Predictor class"""


    def __init__(self, training_dataset,
                       validation_dataset,
                       seed=combivep_settings.DEFAULT_SEED, 
                       n_hidden_nodes=combivep_settings.DEFAULT_HIDDEN_NODES, 
                       figure_dir=combivep_settings.DEFAULT_FIGURE_DIR):
        Mlp.__init__(self, training_dataset.n_features,
                                        seed=seed,
                                        n_hidden_nodes=n_hidden_nodes)

        self.__training_dataset   = training_dataset
        self.__validation_dataset = validation_dataset
        self.__n_hidden_nodes     = n_hidden_nodes
        self.__figure_dir         = figure_dir

    def train(self, iterations=combivep_settings.DEFAULT_ITERATIONS):
        self.__training_error   = []
        self.__validation_error = []
        running_round    = 0
        best_validation_error = 0.99
        while True:
            #tune up model parameters
            out = self.forward_propagation(self.__training_dataset)
            self.backward_propagation(self.__training_dataset)
            weights1, weights2 = self.weight_update(self.__training_dataset)
            self.__training_error.append(np.sum(np.absolute(self.calculate_error(out, 
                                                                                 self.__training_dataset.targets
                                                                                 )
                                                            ), 
                                         axis=1
                                         ).item(0) / self.__training_dataset.n_data)

            #evaluate model using validation dataset
            out = self.forward_propagation(self.__validation_dataset)
            self.__validation_error.append(np.sum(np.absolute(self.calculate_error(out,
                                                                                   self.__validation_dataset.targets
                                                                                   )
                                                              ),
                                           axis=1
                                           ).item(0) / self.__validation_dataset.n_data)

            #check ending condition (acceptable error rate and not much improvement in each iteration)
            current_validation_error = self.__validation_error[len(self.__validation_error)-1]
            if (current_validation_error < combivep_settings.MAXIMUM_ALLOWED_ERROR) and ((best_validation_error-current_validation_error) < combivep_settings.MINIMUM_IMPROVEMENT):
                break

            #otherwise save parameters and record last error
            best_validation_error = self.__validation_error[len(self.__validation_error)-1]
            self.best_weights1 = weights1
            self.best_weights2 = weights2

            #check if it reach maximum iteration
            running_round += 1
            if running_round >= iterations:
                break

        if self.__figure_dir:
            self.__save_figure()

        return best_validation_error

    def __save_figure(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.__training_error, label='training')
        ax.plot(self.__validation_error, label='validation')
        ax.set_ylabel('average error')
        ax.set_xlabel('iterations')
        ax.legend(bbox_to_anchor=(0, 0, 0.98, 0.98), loc=1, borderaxespad=0.)
        file_name = "%02d.eps" % (self.__n_hidden_nodes)
        fig.savefig(os.path.join(self.__figure_dir, file_name))

class Trainers:
    """

    This class is to make use of Trainer classes, each with different
    configuration, to find parameters with the best performance.

    """


    def __init__(self):
        pass

class Predictor(Mlp):
    """

    This class is to predict a probability how a variant likely to be deleterious.

    """


    def __init__(self):
        pass

    def predict(self, dataset):
        return self.forward_propagation(dataset)


