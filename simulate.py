import itertools

import pygame

import pyflap


def main():
    pygame.init()
    state = pyflap.State()
    game = pyflap.Simulation(state)

    initial_state, runner = game.run_until_state(pyflap.GameState.GAME_OVER, 1000)
    print("Initial state:", initial_state)

    # Since the runners are generators that accept callback values
    # we inject input by invoking `send` with a lambda that in turn
    # calls the `input_key` helper function
    runner.send(pygame.K_RETURN)

    # The runner will otherwise act as a normal iterator yielding frames
    # of state data
    for i, state in enumerate(runner):
        if i > 10:
            break
        print("Bird:", state.bird.rect.y)

    # Let's try to get the bird to jump
    runner.send(pygame.K_SPACE)

    for i, state in enumerate(runner):
        # The y coordinate should now decrease as the bird approaches the
        # top of the screen (i.e., y = 0)
        print("Bird:", state.bird.rect.y)

    # Eventually, the bird will hit a pipe which sets the game state to GAME_OVER
    # which in turn stops the runner from generating any more states
    pygame.quit()


if __name__ == "__main__":
    main()
