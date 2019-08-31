import os
import pickle
import pygame
import agent as dqn
# import cnn_agent as cdqn

from random import randint


class Button(pygame.Rect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)


class Blocks():
    def __init__(self, blocks_width, blocks_height):
        self.blocks = [
            [None for i in range(blocks_width)] for i in range(blocks_height)]
        self.original_blocks = [
            [None for i in range(blocks_width)] for i in range(blocks_height)]
        self.blocks_width = blocks_width
        self.blocks_height = blocks_height

    def add_block(self, block):
        self.blocks[block.block_y][block.block_x] = block
        if sum([blocks_row.count(None) for blocks_row in self.blocks])\
                == 0:
            self.original_blocks = [
                [item for item in row] for row in self.blocks]
            self.__update_hittable_blocks()

    def remove_block(self, block):
        self.blocks[block.block_y][block.block_x] = None
        self.__update_hittable_blocks()

    def draw(self, background):
        for i in range(self.blocks_height):
            for j in range(self.blocks_width):
                current_block = self.blocks[i][j]
                if current_block is not None:
                    pygame.draw.rect(
                        background,
                        current_block.colour,
                        current_block)

    def reset(self):
        self.blocks = [[item for item in row] for row in self.original_blocks]
        self.__update_hittable_blocks()

    def __update_hittable_blocks(self):
        self.hittable_blocks = [
            block for block_row in self.blocks
            for block in block_row if block is not None]


class Block(pygame.Rect):
    def __init__(self, x, y, width, height, block_x, block_y, colour):
        super().__init__(x, y, width, height)
        self.block_x = block_x
        self.block_y = block_y
        self.colour = colour


class Ball(pygame.Rect):
    def __init__(self, x, y, size, colour):
        super().__init__(x, y, size, size)
        self.colour = colour
        self.start_x = x
        self.start_y = y
        self.x_velocity = 1
        self.y_velocity = 1
        self.x_direction = 1
        self.y_direction = -1

    def draw(self, background):
        pygame.draw.rect(background, self.colour, self)

    def move(self):
        self.x += self.x_direction * self.x_velocity
        self.y += self.y_direction * self.y_velocity

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.x_velocity = 1
        self.y_velocity = -1
        self.x_direction = 2 * randint(0, 1) - 1
        self.y_direction = -1


class Player(pygame.Rect):
    STEP = 2

    def __init__(self, x, y, width, height, colour):
        super().__init__(x, y, width, height)
        self.colour = colour
        self.start_x = x
        self.start_y = y

    def draw(self, background):
        pygame.draw.rect(background, self.colour, self)

    def move(self, limits):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > limits[0]:
            self.move_left()
        elif keys[pygame.K_RIGHT] and self.x < limits[1]:
            self.move_right()

    def update(self, reward, new_state, done):
        pass

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y

    def move_left(self):
        self.x -= self.STEP

    def move_right(self):
        self.x += self.STEP


class QPlayer(Player):
    def __init__(self, x, y, width, height, colour, path=""):
        super().__init__(x, y, width, height, colour)
        if not os.path.exists(path):
            self.agent = dqn.Agent([2, 8, 8, 8, 2], 1000, 50, 20)
        else:
            with open(path, 'rb') as f:
                self.agent = pickle.load(f)

    def move(self, state, limits):
        action = self.agent.get_action(state)
        if action == 0 and self.x > limits[0]:
            self.move_left()
        elif action == 1 and self.x < limits[1]:
            self.move_right()

    def update(self, reward, new_state, done):
        self.agent.observe_action(reward, new_state, done)

    def save_agent(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.agent, f)


"""
class CNNQPlayer(Player):
    def __init__(self, x, y, width, height, colour, input_shape, path=""):
        super().__init__(x, y, width, height, colour)
        if not os.path.exists(path):
            self.agent = cdqn.DQNAgent(input_shape)
        else:
            with open(path) as f:
                self.agent = pickle.load(f)

    def move(self, state, limits):
        self.action = self.agent.get_action(state)
        if self.action == 0 and self.x > limits[0]:
            self.move_left()
        elif self.action == 1 and self.x < limits[1]:
            self.move_right()
        self.current_state = state

    def update(self, reward, new_state, done):
        self.agent.update_replay_memory(
            [self.current_state, self.action, reward, new_state, done])
"""
