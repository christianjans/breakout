import random
import cjnn

from collections import deque


class Agent():

    def __init__(self, net_map, memory_capacity, training_size, training_rate):
        # memory variables
        self.memories = deque([], memory_capacity)
        self.training_size = training_size
        self.training_rate = training_rate
        self.frames = 0

        # neural net initialization
        self.num_inputs = net_map[0]
        self.num_outputs = net_map[len(net_map) - 1]
        self.policy_network = cjnn.CJNeuralNetwork(net_map, 0.01)
        self.target_network = cjnn.CJNeuralNetwork(net_map, 0.01)
        self.__update_networks()

        # event variable --> [old_state, action, reward, new_state]
        self.current_event = []

        # q learning variables
        self.epsilon = 1
        self.delta_epsilon = 0.00001
        #self.delta_epsilon = 0.00002
        self.min_epsilon = 0.05
        self.discount = 0.99

    def get_action(self, current_state):
        self.current_event.append(current_state)
        move = None

        # apply epsilon-greedy strategy
        if random.random() > self.epsilon:
            # do a non-random move
            #print("non-random")
            move = self.policy_network.action_guess(current_state)
        else:
            # do a random move
            #print("random")
            move = random.randint(0, self.num_outputs - 1)
        # add the move to the current event
        self.current_event.append(move)

        # decrease the epsilon if necessary
        self.epsilon -= self.delta_epsilon\
            if self.epsilon > self.min_epsilon else 0

        return move

    def observe_action(self, reward, new_state, done):
        # add the reward, new state, and done boolean to the current event
        self.current_event.append(reward)
        self.current_event.append(new_state)
        self.current_event.append(done)

        # add the current event to memories
        self.memories.append(self.current_event)

        # clear the current event
        self.current_event = []

        # train on memories if allowed
        if self.frames % self.training_rate == 0\
                and len(self.memories) >= self.training_size:
            self.__learn_from_memories()

        # increase or reset the frames count
        self.frames = self.frames + 1\
            if self.frames < self.training_rate else 0

    def guess(self, inputs):
        # return the value straight from the policy net
        return self.policy_network.probability_guess(inputs)

    def __learn_from_memories(self):
        # get a random sample of memories
        select_memories = random.sample(self.memories, self.training_size)
        # ensure there isn't a None memory
        if None not in select_memories:
            # loop through the memories
            for [old_state, action, reward, new_state, done]\
                    in select_memories:
                # update the networks to have the same weights
                self.__update_networks()
                # train the policy network
                output = self.policy_network.probability_guess(old_state)
                q_value = reward if done else reward + self.discount\
                    * max(self.target_network.probability_guess(new_state))
                output[action] = q_value
                self.policy_network.learn(output)

    def __update_networks(self):
        # update target network with the policy networks weights and biases
        self.target_network.weights = self.policy_network.weights
        self.target_network.biases = self.policy_network.biases
