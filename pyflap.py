import pathlib
import random

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

class Bird():
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.velocity = 0.0
        self.sprite_frame = 0

    def update(self, dt: int) -> None:
        self.velocity += BIRD_GRAVITY * dt
        self.rect.move_ip(0, self.velocity)
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(BIRD_IMAGES[self.sprite_frame], self.rect)

    @classmethod
    def spawn(cls) -> "Bird":
        bird = pygame.Rect(0, 0, BIRD_SIZE, BIRD_SIZE)
        bird.center = (WIDTH // 3, HEIGHT // 2)
        return cls(bird)


class Pipes:
    def __init__(self, upper: pygame.Rect, lower: pygame.Rect) -> None:
        self.upper = upper
        self.lower = lower

    def update(self, dt: int) -> None:
        self.upper.move_ip(-PIPE_SCROLL_VELOCITY * dt, 0)
        self.lower.move_ip(-PIPE_SCROLL_VELOCITY * dt, 0)

    def render(self, screen: pygame.Surface):
        pygame.draw.rect(surface=screen, color="darkgreen", rect=self.upper)
        pygame.draw.rect(surface=screen, color="darkgreen", rect=self.lower)

    def check_collision(self, other: pygame.Rect) -> bool:
        return self.upper.colliderect(other) or self.lower.colliderect(other)

    @classmethod
    def spawn(cls) -> "Pipes":
        height_lower = random.uniform(0, (HEIGHT - PIPE_GAP) / HEIGHT)
        lower = pygame.Rect(0, 0, PIPE_WIDTH, HEIGHT * height_lower)
        lower.midbottom = (WIDTH, HEIGHT)
        upper = pygame.Rect(0, 0, PIPE_WIDTH, HEIGHT - lower.height - PIPE_GAP)
        upper.midtop = (WIDTH, 0)
        return cls(upper, lower)

    @staticmethod
    def despawn(pipes: list["Pipes"]) -> list["Pipes"]:
        return [pipe for pipe in pipes if pipe.lower.right > 0]


class State:
    def __init__(self):
        self.reset()
        self.best_score = 0

    def reset(self):
        self.bird = Bird.spawn()
        self.pipes = [Pipes.spawn()]
        self.pipe_spawn_countup = 0.0
        self.score = 0
        self.running = True

    def update(self, dt: int):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_SPACE:
                    self.bird.velocity = -BIRD_BOOST

            if event.type == UPDATE_SPRITE_EVENT:
                self.bird.sprite_frame = (self.bird.sprite_frame + 1) % len(BIRD_IMAGES)
        
        self.bird.update(dt)

        for pipe in self.pipes:
            pipe.update(dt)

        self.pipe_spawn_countup += (dt / 1000) * PIPE_SPAWN_FREQUENCY
        if self.pipe_spawn_countup > 1:
            self.pipes.append(Pipes.spawn())
            self.score += 1
            self.pipe_spawn_countup = 0

        self.pipes = Pipes.despawn(self.pipes)

        if any(pipe.check_collision(self.bird.rect) for pipe in self.pipes):
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

        self.state.bird.render(self.screen) 

        for pipe in self.state.pipes:
            pipe.render(self.screen)

        score = self.font.render(f"Score: {self.state.score}", True, "black")
        best_score = self.font.render(
            f"Best Score: {self.state.best_score}", True, "black"
        )
        self.screen.blit(score, (10, 10))
        self.screen.blit(best_score, (10, 10 + FONT_SIZE))

        pygame.display.flip()

