import pygame

import pyflap


def main():
    pygame.init()
    state = pyflap.State()
    game = pyflap.Game(state)

    while not state.should_quit:
        game.update()
        game.render()

    pygame.quit()


if __name__ == "__main__":
    main()
