# breakout
A simplified version of Atari Breakout, played by you or an AI.

## how to use
1. Install pygame and numpy

   ```
   pip3 install pygame
   ```
  
   ```
   pip3 install numpy
   ```
   
2. Run main.py (using Python 3) from the appropriate directory

   ```
   python3 main.py
   ```
   
3. Play Breakout, train an AI to do it, or watch a pre-trained AI try and play the game!

## how it works
The AI is a Deep Q-Learning Network that responds to rewards and punishments from the moves it makes in the game environment. Whenever it hits the ball it gets a reward (gets a positive number), but whenever it misses the ball it is punished (gets a negative number).

In this current version, the AI can only see the x and y distance between itself and the ball, yet it still shows improvement over time! In a future version it would be great if the AI could see the whole board and trade its fully-connected neural network for a convolutional neural network. It is for this reason that I have left the game window quite small, so that hopefully one day the AI will be able to take in that full image (hopefully without much lag) and make a move.

More information about the project can be seen in this crude video: https://www.youtube.com/watch?v=nAjENKu2_6c
