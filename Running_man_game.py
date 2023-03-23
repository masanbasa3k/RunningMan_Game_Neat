import pygame
import os
import random

pygame.init()

GLB_SPD = 10
STAT_FONT = pygame.font.SysFont("comicsans", 50)

SCREEN_WIDTH, SCREEN_HEIGHT = 640*2, 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Light in the Space")
file_dir = '/Users/beyazituysal/Documents/PythonProjects/PygameGames/TestAiGame/imgs/jump_assets'

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
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = GLB_SPD
    JUMP_VEL = 10.5

    def __init__(self,x,y):
        self.run_img = RUNNING
        self.jump_img = JUMPING
        
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.run_img[0]
        self.jump_vel = self.JUMP_VEL

        self.man_run = True 
        self.man_jump = False

    def jump(self):
        self.img = self.jump_img
        if self.man_jump:
             self.y -= self.jump_vel * 4
             self.jump_vel -= 0.4
        if self.jump_vel < - self.JUMP_VEL:
            self.jump_vel = self.JUMP_VEL
            self.man_jump = False
    
    def update(self, userInput):
        if self.man_run:
            self.move()
        if self.man_jump:
            self.jump()

        if userInput[pygame.K_SPACE] and not self.man_jump:
            self.man_run = False
            self.man_jump = True
        elif not (self.man_jump):
            self.man_jump = False
            self.man_run = True

    def move(self):
        self.tick_count += 1
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if self.y + self.img.get_height() >= 400:
            self.y  = 400 - self.img.get_height()
        
    def draw(self, win):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.run_img[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.run_img[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.run_img[1]
        elif self.img_count < self.ANIMATION_TIME*3+1:
            self.img = self.run_img[0]
            self.img_count = 0

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_img,new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
class Base:
    VEL = GLB_SPD
    WIDTH = BG.get_width()
    IMG = BG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, player, obs, base, score):
    base.draw(win)
    for ob in obs:
        ob.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (85,0,0))
    win.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))

    
    player.draw(win)
    pygame.display.update()

class Obstacle:
    VEL = GLB_SPD
    def __init__(self, image, x,y):
        self.x = x
        self.y = y
        self.image = image
        self.passed = False

    def move(self):
        self.x -= self.VEL
        
    
    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def collide(self, player):
        player_mask = player.get_mask()
        mask = pygame.mask.from_surface(self.image)

        offset = (self.x - player.x, self.y - round(player.y))

        point = player_mask.overlap(mask, offset)

        if point:
            return True
        
        return False

def main():
    run = True
    
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Man(40,0)
    base = Base(0)
    
    game_speed = 14
    x_pos_bg = 0
    y_pos_bg = 0
    points = 0
    obstacles = [Obstacle(SMALL_SPIKES,SCREEN_WIDTH-10,370)]

    score = 0

    while run:
        
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()     
                quit()

        keys = pygame.key.get_pressed()
        player.update(keys)  

        add_obs = False
        rem = []
        for obs in obstacles:
            if obs.collide(player):
                run = False
            
            if obs.x < -64:
                rem.append(obs)

            if not obs.passed and obs.x < player.x:
                obs.passed = True
                add_obs = True
            obs.move()
        
        if add_obs:
            img = SMALL_SPIKES
            y = 370
            score += 10
            if random.randrange(0,2) == 0:
                img = SMALL_SPIKES
                y = 370
            else:
                img = TALL_SPIKES
                y = 350
            obstacles.append(Obstacle(img,SCREEN_WIDTH-10,y))
        
        for r in rem:
            obstacles.remove(r)

        player.move()
        base.move()
        draw_window(win, player, obstacles, base, score)
    pygame.quit()     
    quit()

if __name__ == '__main__':
    main()
