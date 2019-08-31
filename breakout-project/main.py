import pygame
import entities


SCALE_FACTOR = 1
WINDOW_WIDTH = int(80 * SCALE_FACTOR)
WINDOW_HEIGHT = int(60 * SCALE_FACTOR)
BUTTON_WIDTH = 15 * SCALE_FACTOR
BUTTON_HEIGHT = 10 * SCALE_FACTOR
MENU_TEXT_SIZE = int(13 * SCALE_FACTOR)
BLOCKS_WIDTH = 8
BLOCKS_HEIGHT = 4
BLOCK_MARGINS = 1
BLOCK_WIDTH = (WINDOW_WIDTH - BLOCKS_WIDTH + 1) * BLOCK_MARGINS / BLOCKS_WIDTH
BLOCK_HEIGHT = 2 * SCALE_FACTOR
MAX_HEIGHT = 0 * SCALE_FACTOR
BALL_SIZE = 2 * SCALE_FACTOR
BLOCKS_STARTING_HEIGHT = 10 * SCALE_FACTOR
PLAYER_PATH = "players/main.p"

BACKGROUND_COLOUR = (0, 0, 0)
MENU_TEXT_COLOUR = (255, 255, 255)
PLAY_BUTTON_COLOUR = (255, 100, 100)
TRAIN_BUTTON_COLOUR = (100, 255, 100)
WATCH_BUTTON_COLOUR = (100, 100, 255)
ENTITIES_COLOUR = (255, 255, 255)

pygame.init()
pygame.display.set_caption(" ")
background = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


def menu():
    # font for the menu
    font = pygame.font.SysFont('Comic Sans MS', MENU_TEXT_SIZE)

    # initialize the buttons
    play_button = entities.Button(
        (WINDOW_WIDTH - 4 * BUTTON_WIDTH) / 2,
        (WINDOW_HEIGHT + 2.5 * BUTTON_HEIGHT) / 2,
        BUTTON_WIDTH, BUTTON_HEIGHT)
    train_button = entities.Button(
        (WINDOW_WIDTH - BUTTON_WIDTH) / 2,
        (WINDOW_HEIGHT + 2.5 * BUTTON_HEIGHT) / 2,
        BUTTON_WIDTH, BUTTON_HEIGHT)
    watch_button = entities.Button(
        (WINDOW_WIDTH + 2 * BUTTON_WIDTH) / 2,
        (WINDOW_HEIGHT + 2.5 * BUTTON_HEIGHT) / 2,
        BUTTON_WIDTH, BUTTON_HEIGHT)

    # control being in menu
    in_menu = True

    while in_menu:
        # refresh the background
        background.fill(BACKGROUND_COLOUR)

        # check if user wants to exit or check for mouse clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                choice = 'exit'
                in_menu = False
            if event.type == pygame.MOUSEBUTTONDOWN:    # mouse clicked
                mouse_position = event.pos
                if play_button.collidepoint(mouse_position):
                    choice = 'play'
                    in_menu = False
                elif train_button.collidepoint(mouse_position):
                    choice = 'train'
                    in_menu = False
                elif watch_button.collidepoint(mouse_position):
                    choice = 'watch'
                    in_menu = False

        # draw the text
        display_text(
            font, "Red = Play",
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 2 * MENU_TEXT_SIZE),
            MENU_TEXT_COLOUR, centered=True)
        display_text(
            font, "Green = Train",
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - MENU_TEXT_SIZE),
            MENU_TEXT_COLOUR, centered=True)
        display_text(
            font, "Blue = Watch",
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
            MENU_TEXT_COLOUR, centered=True)

        # draw the buttons
        pygame.draw.rect(background, PLAY_BUTTON_COLOUR, play_button)
        pygame.draw.rect(background, TRAIN_BUTTON_COLOUR, train_button)
        pygame.draw.rect(background, WATCH_BUTTON_COLOUR, watch_button)

        # update the window
        pygame.display.update()

    return choice


def play(choice):
    # font for the menu
    font = pygame.font.SysFont('Comic Sans MS', MENU_TEXT_SIZE)

    playing = True
    user_playing = True if choice == 'play' else False
    started = not user_playing

    # create the player entity based on the game mode
    if user_playing:
        player = entities.Player(
            (WINDOW_WIDTH - BLOCK_WIDTH) / 2,
            WINDOW_HEIGHT - BLOCK_HEIGHT,
            BLOCK_WIDTH, BLOCK_HEIGHT,
            ENTITIES_COLOUR)
    else:
        if choice == 'train':
            player = entities.QPlayer(
                (WINDOW_WIDTH - BLOCK_WIDTH) / 2,
                WINDOW_HEIGHT - BLOCK_HEIGHT,
                BLOCK_WIDTH, BLOCK_HEIGHT,
                ENTITIES_COLOUR)
        else:
            player = entities.QPlayer(
                (WINDOW_WIDTH - BLOCK_WIDTH) / 2,
                WINDOW_HEIGHT - BLOCK_HEIGHT,
                BLOCK_WIDTH, BLOCK_HEIGHT,
                ENTITIES_COLOUR, "players/main.p")
    # create the ball entity
    ball = entities.Ball(
        (WINDOW_WIDTH - BALL_SIZE) / 2,
        (player.y - WINDOW_HEIGHT / 4),
        BALL_SIZE, ENTITIES_COLOUR)
    # create the obstacle blocks entity
    obstacle_blocks = entities.Blocks(BLOCKS_WIDTH, BLOCKS_HEIGHT)
    for i in range(BLOCKS_HEIGHT):
        y = (BLOCK_HEIGHT + BLOCK_MARGINS) * i + BLOCKS_STARTING_HEIGHT
        for j in range(BLOCKS_WIDTH):
            x = (BLOCK_WIDTH + BLOCK_MARGINS) * j
            obstacle_blocks.add_block(entities.Block(
                x, y,
                BLOCK_WIDTH, BLOCK_HEIGHT,
                j, i,
                ENTITIES_COLOUR))
    """
    cnn_player = entities.CNNQPlayer(
        (WINDOW_WIDTH - BLOCK_WIDTH) / 2,
        WINDOW_HEIGHT - BLOCK_HEIGHT,
        BLOCK_WIDTH, BLOCK_HEIGHT,
        ENTITIES_COLOUR, (60, 80, 1))
    """

    while playing:
        # refresh the background
        background.fill(BACKGROUND_COLOUR)

        # check if user wants to exit or check for mouse clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False

        # handle keyboard input if there's a user
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            """
            if not user_playing:
                player.save_agent(PLAYER_PATH)
            """
            playing = False
        elif keys[pygame.K_SPACE]:
            started = True

        # allow the player to move
        if user_playing:
            player.move((0, WINDOW_WIDTH - BLOCK_WIDTH))
        else:
            player.move(
                [player.x + BLOCK_WIDTH / 2 - (ball.x + BALL_SIZE / 2),
                    player.y - (ball.y + BALL_SIZE)],
                (0, WINDOW_WIDTH - BLOCK_WIDTH))
        # move the ball
        if started:
            ball.move()
        else:
            display_text(
                font, "Press SPACE to start.",
                (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
                ENTITIES_COLOUR, centered=True)

        # handle collision
        for block in obstacle_blocks.hittable_blocks:
            if ball.colliderect(block):
                if ball.collidepoint(block.midleft) or\
                        ball.collidepoint(block.midright):
                    ball.x_direction *= -1
                else:
                    ball.y_direction *= -1
                obstacle_blocks.remove_block(block)

                if len(obstacle_blocks.hittable_blocks) == 0:
                    if user_playing:
                        started = False
                    ball.reset()
                    obstacle_blocks.reset()
                break
        if ball.y < MAX_HEIGHT:
            ball.y_direction *= -1
            player.update(
                0,
                [player.x + BLOCK_WIDTH / 2 - (ball.x + BALL_SIZE / 2),
                    player.y - (ball.y + BALL_SIZE)],
                False)
        elif ball.y > player.y:
            ball.reset()
            player.update(
                -10,
                [player.x + BLOCK_WIDTH / 2 - (ball.x + BALL_SIZE / 2),
                    player.y - (ball.y + BALL_SIZE)],
                True)
            player.reset()
            # print("epsilon = " + str(player.agent.epsilon))
        elif ball.x < 0 or ball.x > WINDOW_WIDTH - BALL_SIZE:
            ball.x_direction *= -1
            ball.x += ball.x_direction
            player.update(
                0,
                [player.x + BLOCK_WIDTH / 2 - (ball.x + BALL_SIZE / 2),
                    player.y - (ball.y + BALL_SIZE)],
                False)
        elif ball.colliderect(player):
            if ball.x + BALL_SIZE > player.x and\
                    ball.x < player.x + BLOCK_WIDTH:
                if ball.x + BALL_SIZE / 2 < player.x + BLOCK_WIDTH / 2:
                    ball.x_direction = -1
                else:
                    ball.x_direction = 1
                ball.y_direction *= -1
            player.update(
                10,
                [player.x + BLOCK_WIDTH / 2 - (ball.x + BALL_SIZE / 2),
                    player.y - (ball.y + BALL_SIZE)],
                False)
        else:
            player.update(
                0,
                [player.x + BLOCK_WIDTH / 2 - (ball.x + BALL_SIZE / 2),
                    player.y - (ball.y + BALL_SIZE)],
                False)

        # draw the ball, player, and obstacles
        player.draw(background)
        ball.draw(background)
        obstacle_blocks.draw(background)

        pygame.display.update()


# display text without a hassle
def display_text(font, text, position, colour, centered=False):
    # get the textview to do some positioning if needed
    text_view = font.render(text, True, colour)
    if position == 'center':    # position in center of screen
        background.blit(
            text_view,
            ((WINDOW_WIDTH - text_view.get_rect().width) / 2,
                WINDOW_HEIGHT / 2))
    elif not centered:  # position from top left
        background.blit(text_view, position)
    else:   # position the center at the position argument
        background.blit(
            text_view,
            (position[0] - text_view.get_rect().width / 2,
                position[1] - text_view.get_rect().height / 2))


if __name__ == "__main__":
    while True:
        choice = menu()
        if choice == 'exit':
            break
        else:
            play(choice)
    pygame.quit()
