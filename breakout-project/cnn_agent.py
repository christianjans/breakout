import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Activation, Flatten
from keras.callbacks import TensorBoard
from keras.optimizers import Adam

from collections import deque

import numpy as np
import random
import time


REPLAY_MEMORY_SIZE = 1000
MIN_REPLAY_MEMORY_SIZE = 100
MINIBATCH_SIZE = 50
DISCOUNT = 0.99
UPDATE_TARGET_MODEL_EVERY = 5
MODEL_NAME = "8x2"


class DQNAgent:
    def __init__(self, input_shape):
        self.model = self.__create_model(input_shape)
        self.target_model = self.__create_model(input_shape)
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque([], REPLAY_MEMORY_SIZE)

        self.tensorboard = ModifiedTensorBoard(log_dir=f"logs/{MODEL_NAME}-{int(time.time())}")

        self.target_update_counter = 0

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def get_action(self, state):
        return np.argmax(self.model.predict(np.array(state).reshape(-1, *state.shape) / 255)[0])

    def get_q_values(self, state):
        print(np.array(state).reshape(-1, *state.shape) / 255)
        return self.model.predict(np.array(state).reshape(-1, *state.shape) / 255)[0]

    def train(self, terminal_state, step):
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        current_states = np.array([transition[0] for transition in minibatch]) / 255
        current_q_values_list = self.model.predict(current_states)

        new_current_states = np.arange([transition[3] for transition in minibatch]) / 255
        future_q_values_list = self.target_model.predict(new_current_states)

        X = []
        y = []

        for index,\
            (current_state, action, reward, new_current_state, done)\
                in enumerate(minibatch):
            if not done:
                max_future_q_value = np.max(future_q_values_list[index])
                new_q_value = reward + DISCOUNT * max_future_q_value
            else:
                new_q_value = reward

            current_q_values = current_q_values_list[index]
            current_q_values[action] = new_q_value

            X.append(current_state)
            y.append(current_q_values)

        self.model.fit(
            np.array(X) / 255,
            np.array(y),
            batch_size=MINIBATCH_SIZE,
            verbose=0,
            shuffle=False,
            callbacks=[self.tensorboard] if terminal_state else None)

        # updating to determine if we want to update target_model yet
        if terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter > UPDATE_TARGET_MODEL_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    def __create_model(self, input_shape):
        model = Sequential()

        model.add(Conv2D(
            8, (3, 3), input_shape=(60, 80, 1)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(2, 2))
        model.add(Dropout(0.2))

        model.add(Conv2D(8, (3, 3)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(2, 2))
        model.add(Dropout(0.2))

        model.add(Flatten())
        model.add(Dense(64))
        model.add(Dense(2, activation='linear'))

        model.compile(
            loss='mse',
            optimizer=Adam(lr=0.001),
            metrics=['accuracy'])

        return model


class ModifiedTensorBoard(TensorBoard):
    # override init to set inital step and writer (one log file for all .fit() calls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.FileWriter(self.log_dir)

    # overriding this method to stop creating default log writer
    def set_model(self, model):
        pass

    # override this with self.step so that .fit() will not write from the 0th step each time
    def on_epoch_end(self, epcoh, logs=None):
        self.update_stats(**logs)

    # override to train for one batch only, no need to save anything at epoch end
    def on_batch_end(self, batch, logs=None):
        pass

    # override so the writer doesn't close
    def on_train_end(self, _):
        pass

    # custom method for saving metrics --> creates writer, writes custom metrics, and then closes writer
    def update_stats(self, **stats):
        self._write_logs(stats, self.step)


if __name__ == "__main__":
    agent = DQNAgent((3, 6, 1, 1))
    print(agent.get_q_values(np.array([[[10, 40, 50, 11, 14, 27],
                               [12, 33, 54, 21, 95, 95],
                               [43, 23, 52, 42, 42, 84]]])))
