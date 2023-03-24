import pygame
import os
import random
import neat

pygame.init()
GEN = 0

SCREEN_WIDTH, SCREEN_HEIGHT = 640*2, 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Light in the Space")
file_dir = 'Your local images file'

def loadImage(spr):
    return pygame.image.load(os.path.join(f"{file_dir}/{spr}"))

##IMAGES
RUNNING  = [loadImage("spr_player1.png"),
            loadImage("spr_player2.png")]

JUMPING = loadImage("spr_player_jump.png")

SMALL_SPIKES = loadImage("spr_shortSpikes.png")
TALL_SPIKES =  loadImage("spr_tallSpikes.png")

CLOUD = [loadImage("spr_clouds1.png"),
        loadImage("spr_clouds2.png"),
        loadImage("spr_clouds3.png"),
        loadImage("spr_clouds3.png"),]

BG = pygame.transform.scale((loadImage("spr_bg.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))

class Man:
    X_POS = 32
    Y_POS = 260
    JUMP_VEL = 8.5

    def __init__(self):
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.man_run = True
        self.man_jump = False
        
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.man_rect = self.image.get_rect()
        self.man_rect.x = self.X_POS
        self.man_rect.y = self.Y_POS

    def update(self, jump):
        if self.man_run:
            self.run()
        if self.man_jump:
            self.jump()
        
        if self.step_index >= 10:
            self.step_index = 0

        if jump and not self.man_jump and self.man_rect.y == 260:
            self.man_run = False
            self.man_jump = True
        elif not (self.man_jump):
            self.man_jump = False
            self.man_run = True

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.man_rect = self.image.get_rect()
        self.man_rect.x = self.X_POS
        self.man_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.man_jump:
             self.man_rect.y -= self.jump_vel * 4
             self.jump_vel -= 0.6
        if self.jump_vel < - self.JUMP_VEL:
            self.man_jump = False
            self.jump_vel = self.JUMP_VEL
        
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.man_rect.x, self.man_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD[random.randint(0, 3)]
        self.width = self.image.get_width()
        self.step_index = 0

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)
    
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()
    
    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)

class SmallSpikes(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 370

class TallSpikes(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 350

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Man())
        g.fitness = 0
        ge.append(g)


    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    cloud = Cloud()
    game_speed = 14
    x_pos_bg = 0
    y_pos_bg = 0
    points = 0
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = [SmallSpikes(SMALL_SPIKES)]

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            for g in ge:
                g.fitness += 1
                game_speed += 1/len(players)
        
        text = font.render(f"Points: {points}", True, (0,0,0))
        textRect = text.get_rect()
        textRect.midleft = (600, 50)
        SCREEN.blit(text, textRect)

        gen = font.render(f"GEN: {GEN}", True, (0,0,0))
        genRect = text.get_rect()
        genRect.midleft = (40, 50)
        SCREEN.blit(gen, genRect)

    def background():
        global x_pos_bg,y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg,y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg,y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg,y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run and len(players) >  0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        SCREEN.fill((255,255,255))
        userInput = False

        background()

        for x, player in enumerate(players):
            player.draw(SCREEN)
            
            if len(obstacles) > 0:
                output = nets[x].activate((player.man_rect.x, abs(player.man_rect.x - obstacles[0].rect.x), abs(player.man_rect.y - obstacles[0].rect.y)))

            if output[0] > 0.5:
                userInput = True

            player.update(userInput)

        if len(obstacles) == 0:
            if random.randint(0, 1) == 0:
                obstacles.append(SmallSpikes(SMALL_SPIKES))
            elif random.randint(0, 1) == 1:
                obstacles.append(TallSpikes(TALL_SPIKES))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for x, player in enumerate(players):
                if player.man_rect.colliderect(obstacle.rect):
                    ge[x].fitness -= 1
                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
        

        cloud.draw(SCREEN)
        cloud.update()
        
        score()

        clock.tick(30)
        pygame.display.update()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)