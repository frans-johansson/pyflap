import pathlib
import random
import typing

import pygame

# Not needed for graphical environment
(WIDTH, HEIGHT) = (1280, 720)
PIPE_GAP = 250
PIPE_SCROLL_VELOCITY = 0.5
PIPE_SPAWN_FREQUENCY = 0.5
PIPE_WIDTH = 100
BIRD_SIZE = 50
BIRD_GRAVITY = 0.05
BIRD_BOOST = 20

# Needed for graphical environment
WINDOW_TITLE = "Pyflap"
BIRD_ANIMATION_DELAY = 100
FONT_SIZE = 48
UPDATE_SPRITE_EVENT = pygame.USEREVENT + 1
ASSETS = pathlib.Path("./assets")
# TODO: Consider if this should really be a part of the "config"
BIRD_IMAGES = [
    pygame.transform.scale(pygame.image.load(file), (BIRD_SIZE, BIRD_SIZE))
    for file in ASSETS.glob("bird/*.png")
]


class State:
    def __init__(self):
        self.reset()
        self.best_score = 0

    def reset(self):
        self.bird = pygame.Rect(0, 0, BIRD_SIZE, BIRD_SIZE)
        self.bird.center = (WIDTH // 3, HEIGHT // 2)
        self.pipes = spawn_pipe()
        self.bird_velocity = 0.0
        self.pipe_spawn_countup = 0.0
        self.score = 0
        self.bird_frame = 0
        self.running = True

    def update(self, dt):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_SPACE:
                    self.bird_velocity = -BIRD_BOOST

            if event.type == UPDATE_SPRITE_EVENT:
                self.bird_frame = (self.bird_frame + 1) % len(BIRD_IMAGES)

        self.bird_velocity += BIRD_GRAVITY * dt
        self.bird.move_ip(0, self.bird_velocity)
        if self.bird.bottom > HEIGHT:
            self.bird.bottom = HEIGHT
        if self.bird.top < 0:
            self.bird.top = 0
            self.bird_velocity = 0

        for pipe in self.pipes:
            pipe.move_ip(-PIPE_SCROLL_VELOCITY * dt, 0)

        self.pipe_spawn_countup += (dt / 1000) * PIPE_SPAWN_FREQUENCY
        if self.pipe_spawn_countup > 1:
            self.pipes.extend(spawn_pipe())
            self.score += 1
            self.pipe_spawn_countup = 0

        self.pipes = despawn_pipes(self.pipes)

        if bird_has_crashed(self.pipes, self.bird):
            self.best_score = max(self.best_score, self.score)
            self.reset()


class Game:
    def __init__(self, state: State) -> None:
        self.state = state
        self.font = pygame.font.Font(None, size=FONT_SIZE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)
        self.clock = pygame.time.Clock()
        self.dt = 0

        pygame.display.set_caption(title=WINDOW_TITLE)
        pygame.time.set_timer(UPDATE_SPRITE_EVENT, BIRD_ANIMATION_DELAY)

    def update(self) -> None:
        self.state.update(self.dt)
        self.dt = self.clock.tick(60)

    def render(self) -> None:
        self.screen.fill("lightblue")

        self.screen.blit(BIRD_IMAGES[self.state.bird_frame], self.state.bird)

        for pipe in self.state.pipes:
            pygame.draw.rect(surface=self.screen, color="darkgreen", rect=pipe)

        score = self.font.render(f"Score: {self.state.score}", True, "black")
        best_score = self.font.render(
            f"Best Score: {self.state.best_score}", True, "black"
        )
        self.screen.blit(score, (10, 10))
        self.screen.blit(best_score, (10, 10 + FONT_SIZE))

        pygame.display.flip()


def spawn_pipe() -> list[pygame.Rect]:
    height_lower = random.uniform(0, (HEIGHT - PIPE_GAP) / HEIGHT)
    lower = pygame.Rect(0, 0, PIPE_WIDTH, HEIGHT * height_lower)
    lower.midbottom = (WIDTH, HEIGHT)
    upper = pygame.Rect(0, 0, PIPE_WIDTH, HEIGHT - lower.height - PIPE_GAP)
    upper.midtop = (WIDTH, 0)
    return [lower, upper]


def despawn_pipes(pipes: list[pygame.Rect]) -> list[pygame.Rect]:
    return [pipe for pipe in pipes if pipe.right > 0]


def bird_has_crashed(pipes: list[pygame.Rect], bird: pygame.Rect) -> bool:
    # Enable this if you are a masochist c:
    # if bird.bottom > HEIGHT or bird.top < 0:
    #     return True

    for pipe in pipes:
        if pipe.colliderect(bird):
            return True

    return False
