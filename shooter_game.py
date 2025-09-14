from pygame import *
from random import randint
from time import time as timer
 
#parent class for other sprites
class GameSprite(sprite.Sprite):
    #class constructor
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # parent's class constructor (Sprite):
        sprite.Sprite.__init__(self)
 
        #each sprite must store an image property
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
 
        #each sprite must store the rect property it is inscribed in
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
 
    #method that draws the character in the window
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
 
#child class
class Player(GameSprite):
    #method for controlling the player with the keyboard arrows
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    #this method (use the player's place to create a bullet there)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

#enemy sprite class  
class Enemy(GameSprite):
    #enemy movement
    def update(self):
        self.rect.y += self.speed
        global lost
        #disappears upon reaching the screen edge
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1

#bullet sprite class
class Bullet(GameSprite):
    #bullet movement
    def update(self):
        self.rect.y += self.speed
        #disappiers if the bullet reaches the edge of the screen
        if self.rect.y < 0:
            self.kill()

#pictures that we have to load
img_back = "galaxy.jpg" #game background
img_hero = "rocket.png" #character
img_enemy = "ufo.png" #enemy
img_bullet = "bullet.png" #bullet
img_asteroid = "asteroid.png" #asteroid

#create the window
win_width = 700
win_height = 500
display.set_caption('Shooter Game')
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
 
#background music
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound("fire.ogg")
 
#counter
score = 0 #ships destroyed
lost = 0 #ships missed
goal = 10 #maximum score
max_lost = 3 #lost if this many missed enemies
life = 3 #life points

#fonts and captions
font.init()
font1 = font.SysFont("Arial", 80)
win = font1.render('YOU WIN!', True, (0, 255, 0))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.SysFont("Arial", 36)
 
#create sprites
ship = Player(img_hero, 5, win_height-100, 80, 100, 10) #player
enemies = sprite.Group() #enemies
for i in range(1, 6):
    enemy = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    enemies.add(enemy)

#creating a group of asteroid sptites()
asteroids = sprite.Group()
for i in range(1, 3):
    asteroid = Enemy(img_asteroid, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(asteroid)

bullets = sprite.Group() #bullets

#the flag is cleared with the close window
run = True #the flag is cleared with the close window button
#the "game over" variable: if it is True, the sprites stop working in the main loop
finish = False
 
rel_time = False #flag in charge of reload
num_fire = 0 #variable to count shots

while run:
    #if the close button is pressed, exit the program
    for e in event.get():
        if e.type == QUIT:
            run = False
        #press on the space bar event - the sprite fires
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                #check how many shots been fired and whether reload is in progress
                    if num_fire < 5 and rel_time == False:
                        num_fire = num_fire + 1
                        fire_sound.play()
                        ship.fire()

                    if num_fire >= 5 and rel_time == False: #if the player fired 5 shots
                        last_time = timer() #record time this happened
                        rel_time = True #set the reload flag

    if not finish:
        #refresh background
        window.blit(background, (0,0))
 
        #write text on the screen
        score_text = font2.render("Score: " + str(score), 1, (255, 255, 255))
        window.blit(score_text, (10, 20))
 
        lose_text = font2.render("Missed: " + str(lost), 1, (255, 255, 255))
        window.blit(lose_text, (10, 50))
 
        #player movement
        ship.update()
 
        #enemies movement
        enemies.update()
        asteroids.update()

        #bullets movement
        bullets.update()

        #updating them at a new location on each iterration of the loop
        ship.reset()
        enemies.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        #reload 
        if rel_time == True:
            now_time = timer() #read time
            if now_time - last_time < 3: #before 3 seconds are over, display reload message
                reload = font2.render("Wait, reload...", 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0 #set the bullets counter to zore 
                rel_time = False #reset the reload flag

        #bullet-monster collisions check (both monster and bullet disappear)
        collides = sprite.groupcollide(enemies, bullets, True, True)
        for c in collides:
            score += 1
            enemy = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            enemies.add(enemy)

        #possible lose: missed too many enemies or the player collide with the enemy
        if sprite.spritecollide(ship, enemies, False) or lost >= max_lost:
            finish = True 
            window.blit(lose, (200, 200))

        #win check : how many points did you score
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        #set a different color depending on the number of lives
        if life == 3:
            life_color = (0, 150, 0)
        if life == 2:
            life_color = (150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)

        #render in screen
        text_life = font2.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10))

        display.update()
    
    #the loop runs every 0.05 sec
    time.delay(50) #miliseconde