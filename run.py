import pygame

import pyflap


def main():
    pygame.init()
    state = pyflap.State()
    game = pyflap.Game(state)

    while state.running:
        game.update()
        game.render()

    pygame.quit()


if __name__ == "__main__":
    main()
