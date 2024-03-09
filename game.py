import pygame
import random

WINDOW_TITLE = "Pyflap"
(WIDTH, HEIGHT) = (1280, 720)
PIPE_GAP = 250
PIPE_SCROLL_VELOCITY = 0.5
PIPE_SPAWN_FREQUENCY = 0.5
PIPE_WIDTH = 100
BIRD_SIZE = 50
BIRD_GRAVITY = 0.05
BIRD_BOOST = 20
FONT_SIZE = 48


def spawn_pipe() -> list[pygame.Rect]:
    height_lower = random.uniform(0, (HEIGHT - PIPE_GAP) / HEIGHT)
    lower = pygame.Rect(0, 0, PIPE_WIDTH, HEIGHT * height_lower)
    lower.midbottom = (WIDTH, HEIGHT)
    upper = pygame.Rect(0, 0, PIPE_WIDTH, HEIGHT - lower.height - PIPE_GAP)
    upper.midtop = (WIDTH, 0)
    return [lower, upper]


def despawn_pipes(pipes: list[pygame.Rect]) -> list[pygame.Rect]:
    return [
        pipe for pipe in pipes if pipe.right > 0
    ]


def bird_has_crashed(pipes: list[pygame.Rect], bird: pygame.Rect) -> bool:
    # Enable this if you are a masochist c:
    # if bird.bottom > HEIGHT or bird.top < 0:
    #     return True

    for pipe in pipes:
        if pipe.colliderect(bird):
            return True

    return False


class GameState:
    def __init__(self):
        self.reset()
        self.best_score = 0

    def reset(self):
        self.bird = pygame.Rect(0, 0, BIRD_SIZE, BIRD_SIZE)
        self.bird.center = (WIDTH // 3, HEIGHT // 2)
        self.pipes = spawn_pipe()  # TODO: Can accidentally spawn walls 
        self.dt = 0
        self.bird_velocity = 0.0
        self.pipe_spawn_countup = 0.0
        self.score = 0



def main():
    pygame.init()
    pygame.display.set_caption(title=WINDOW_TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, size=FONT_SIZE)

    game_state = GameState()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_SPACE:
                    game_state.bird_velocity = -BIRD_BOOST

        screen.fill("lightblue")

        game_state.bird_velocity += BIRD_GRAVITY * game_state.dt
        game_state.bird.move_ip(0, game_state.bird_velocity)
        if game_state.bird.bottom > HEIGHT:
            game_state.bird.bottom = HEIGHT
        if game_state.bird.top < 0:
            game_state.bird.top = 0
            game_state.bird_velocity = 0

        pygame.draw.rect(surface=screen, color="orange", rect=game_state.bird)

        for pipe in game_state.pipes:
            pipe.move_ip(-PIPE_SCROLL_VELOCITY * game_state.dt, 0)
            pygame.draw.rect(surface=screen, color="darkgreen", rect=pipe)

        score = font.render(f"Score: {game_state.score}", True, "black")
        best_score = font.render(f"Best Score: {game_state.best_score}", True, "black")
        screen.blit(score, (10, 10))
        screen.blit(best_score, (10, 10 + FONT_SIZE))

        pygame.display.flip()

        game_state.pipe_spawn_countup += (game_state.dt / 1000) * PIPE_SPAWN_FREQUENCY
        if game_state.pipe_spawn_countup > 1:
            game_state.pipes.extend(spawn_pipe())
            game_state.score += 1
            game_state.pipe_spawn_countup = 0

        game_state.pipes = despawn_pipes(game_state.pipes)

        game_state.dt = clock.tick(60)

        if bird_has_crashed(game_state.pipes, game_state.bird):
            game_state.best_score = max(game_state.best_score, game_state.score)
            game_state.reset()

    pygame.quit()


if __name__ == "__main__":
    main()
