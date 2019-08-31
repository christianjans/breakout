import numpy as np


class CJNeuralNetwork:

    def __init__(self, net_map, learning_rate):
        self.net_map = np.matrix(net_map)
        self.learning_rate = learning_rate
        self.reset_random()

    # reset the neural net with random weights
    def reset_random(self):
        self.weights = []
        self.biases = []

        for i in range(max(np.shape(self.net_map)) - 1):
            this_layer_nodes = self.net_map[0, i]
            next_layer_nodes = self.net_map[0, (i + 1)]

            self.weights.append(np.matrix(np.random.uniform(low = -1, high = 1, size = (next_layer_nodes, this_layer_nodes))))
            self.biases.append(np.matrix(np.random.uniform(low = -1, high = 1, size = (next_layer_nodes, 1))))

    # fit the neural net to the output give an input
    def fit(self, inputs, outputs):
        self.__feed_forward(inputs)
        self.__backpropagate(outputs)

    # get the index of the maximum value in the neural net's guess
    def action_guess(self, inputs):
        guess = self.__feed_forward(inputs).tolist()
        guess = [x[0] for x in guess]
        return guess.index(max(guess))

    # return the one-hot encoded vector of the neural net output
    def binary_guess(self, inputs):
        guess = self.__feed_forward(inputs)
        binary = np.zeros_like(guess)
        binary[np.where(guess == np.max(guess))] = 1
        return [int(number[0]) for number in binary]

    # return the actual output of the neural net (after softmax)
    def probability_guess(self, inputs):
        guess = self.__feed_forward(inputs).tolist()
        #print("guess = " + str(guess))
        return [x[0] for x in guess]

    # feed inputs through the matrices
    def __feed_forward(self, inputs):
        self.layer_vals = []
        self.layer_zs = []

        #print("inputs = " + str(inputs))

        input_mat = np.matrix(inputs)

        self.layer_vals.append(input_mat.reshape(max(np.shape(input_mat)), 1))
        self.layer_zs.append(self.layer_vals[0])
        last_index = len(self.weights) - 1

        for i in range(last_index):
            self.layer_vals.append(self.__sigmoid(np.add(np.matmul(self.weights[i], self.layer_vals[i]), self.biases[i])))
            self.layer_zs.append(np.add(np.matmul(self.weights[i], self.layer_vals[i]), self.biases[i]))

        self.layer_vals.append(self.__linear(np.add(np.matmul(self.weights[last_index], self.layer_vals[last_index]), self.biases[last_index])))
        self.layer_zs.append(np.add(np.matmul(self.weights[last_index], self.layer_vals[last_index]), self.biases[last_index]))

        return self.layer_vals[last_index + 1]

    # a public method for backpropagation
    def learn(self, targets):
        self.__backpropagate(targets)

    # backpropagate through the matrices, updating weights and biases
    def __backpropagate(self, targets):
        #print("targets = " + str(targets))

        targets_mat = np.matrix(targets)

        initial_targets = targets_mat.reshape((max(np.shape(targets_mat)), 1))
        last_layer = len(self.weights)

        initial_error = np.subtract(self.layer_vals[last_layer], initial_targets)
        #initial_error = np.subtract(self.layer_vals[last_layer], initial_targets)
        #print(initial_error)

        #for i in range(max(np.shape(initial_error))):
        #    print(initial_error[i, 0])
        #    initial_error[i, 0] = initial_error[i, 0] ** 2

        #initial_error = np.square(np.array(initial_error))
        #initial_error = np.multiply(initial_error, initial_error)

        #print("targets = " + str(initial_error) + "\n")

        delta = np.multiply(initial_error, self.__linear_deriv(self.layer_zs[last_layer]))
        weight_change = np.matmul(delta, np.transpose(self.layer_vals[last_layer - 1]))

        for i in range(last_layer - 1, -1, -1):
            self.weights[i] = np.subtract(self.weights[i], self.learning_rate * weight_change)
            self.biases[i] = np.subtract(self.biases[i], self.learning_rate * delta)

            delta = np.multiply(np.matmul(np.transpose(self.weights[i]), delta), self.__sigmoid_deriv(self.layer_zs[i]))
            weight_change = np.matmul(delta, np.transpose(self.layer_vals[i - 1]))

    # sigmoid function
    def __sigmoid(self, val):
        return 1 / (1 + np.exp(-val))

    # sigmoid derivative function
    def __sigmoid_deriv(self, val):
        sig = self.__sigmoid(val)
        return np.multiply(sig, 1 - sig)

    # softmax function
    def __softmax(self, val):
        column_exp_sum = np.sum(np.exp(val))
        return np.exp(val) / column_exp_sum

    # softmax derivative function
    def __softmax_deriv(self, val):
        soft = self.__softmax(val)
        return np.multiply(soft, 1 - soft)

    # linear function
    def __linear(self, val):
        return val

    # linear function derivative
    def __linear_deriv(self, val):
        return 1
