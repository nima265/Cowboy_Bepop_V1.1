import pygame
import os
import time
import random
pygame.font.init()
from pygame import mixer
from pygame.locals import *
pygame.init()

ic =pygame.image.load(os.path.join("images","icon.jpg"))
W, H = 720,700
window = pygame.display.set_mode((W,H))
pygame.display.set_caption("Cowboy Bepop")
pygame.display.set_icon(ic)


#space guns and lasers
red_laser = pygame.transform.scale(pygame.image.load(os.path.join("images","red_laser.png")),(50,50))
blue_laser = pygame.transform.scale(pygame.image.load(os.path.join("images","blue_laser.png")),(80,80))
green_laser = pygame.transform.scale(pygame.image.load(os.path.join("images","green_laser.png")),(100,100))
yellow_laser = pygame.transform.scale(pygame.image.load(os.path.join("images","yellow_laser.png")),(70,70))

#enemy spaceship
mid_enemy_spaceship = pygame.transform.scale(pygame.image.load(os.path.join("images","mid_enemy_spaceship.png")),(50,50))
sml_enemy_spaceship = pygame.transform.scale(pygame.image.load(os.path.join("images","sml_enemy_spaceship.png")),(40,40))
lrg_enemy_spaceship = pygame.transform.scale(pygame.image.load(os.path.join("images","lrg_enemy_spaceship.png")),(70,70))

#player spaceship
main_spaceship = pygame.transform.scale(pygame.image.load(os.path.join("images","main_spaceship.png")),(60,60))

#background
BC = pygame.transform.scale(pygame.image.load(os.path.join("images","BC.png")),(W,H))

mixer.music.load("main_music.wav")
bullet_sound1 = mixer.Sound("laser_sound.wav")
game_over = mixer.Sound("game_over.wav")

class Laser:
  def __init__(self,x,y,img):
    self.x = x
    self.y = y
    self.img = img
    self.mask = pygame.mask.from_surface(self.img)
  
  def draw(self,win):
    win.blit(self.img,(self.x,self.y))

  def move(self,vel):
    self.y += vel

  def off_screen(self,H):
    return not(self.y <= H and self.y >=0) 

  def collision(self,obj):
    return collide(self,obj)


class Ship:
  COOLDOWN = 30
  def __init__(self, x, y,health=100):
   self.x = x
   self.y = y
   self.health = health
   self.ship_img = None
   self.laser_img = None
   self.lasers = []
   self.cool_down_counter = 0
    
  def draw(self,win):
    win.blit(self.ship_img , (self.x, self.y))
    for laser in self.lasers:
     laser.draw(win)

  def move_lasers(self,vel,obj):
    self.cooldown()
    for laser in self.lasers:
      laser.move(vel)
      if laser.off_screen(H):
        self.lasers.remove(laser)  
      elif laser.collision(obj):
        obj.health -= 10
        self.lasers.remove(laser)



  def cooldown(self):
    if self.cool_down_counter >= self.COOLDOWN:
      self.cool_down_counter = 0
    elif self.cool_down_counter > 0 :
      self.cool_down_counter += 1  

  def shoot(self):
    if self.cool_down_counter == 0:
      laser= Laser(self.x,self.y,self.laser_img)
      self.lasers.append(laser)
      self.cool_down_counter = 1
      bullet_sound1.play()

  def get_width(self):
    return self.ship_img.get_width()

  def get_height(self):
    return self.ship_img.get_height()      

#class player
class Player(Ship):
  def __init__(self,x,y,health=100):
    super().__init__(x,y,health)
    self.ship_img = main_spaceship
    self.laser_img = yellow_laser  
    self.mask = pygame.mask.from_surface(self.ship_img)   
    self.max_health = health

  def move_lasers(self,vel,objs):
    self.cooldown()
    for laser in self.lasers:
      laser.move(vel) 
      if laser.off_screen(H):
        self.lasers.remove(laser)  
      else:
        for obj in objs:
          if laser.collision(obj):
            objs.remove(obj)
            if laser in self.lasers:
             self.lasers.remove(laser)
  
  def draw(self,win):
    super().draw(win)
    self.healthbar(win) 
            

  def healthbar(self, win):
    pygame.draw.rect(win, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
    pygame.draw.rect(win, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


#class enemy
class Enemy(Ship):
  class_map = {"small": (sml_enemy_spaceship,red_laser),"medium": (mid_enemy_spaceship,blue_laser),"large": (lrg_enemy_spaceship,green_laser)}
  
 
  def __init__(self,x,y,size,health=100):
    super().__init__(x, y, health)
    self.ship_img, self.laser_img = self.class_map[size]
    self.mask = pygame.mask.from_surface(self.ship_img)

  def move(self, vel):
   self.y += vel

  def shoot(self):
    if self.cool_down_counter == 0:
      laser= Laser(self.x-20,self.y,self.laser_img)
      self.lasers.append(laser)
      self.cool_down_counter = 1


def collide(obj1,obj2):
  offset_x = obj2.x - obj1.x
  offset_y = obj2.y - obj1.y
  return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None 



def mainloop():
  mixer.music.play(-1)
  run = True
  FPS = 60
  level=0
  lives=5
  main_font = pygame.font.SysFont("PressStart2P",12) #font 
  lost_font = pygame.font.SysFont("PressStart2P",40)
  enemies = []
  wave_length = 5
  enemy_vel = 1
  player_vel = 5          # how much pixels moves when push buttom 
  laser_vel = 5
  player = Player(300,650)
  clock = pygame.time.Clock()
  lost = False 
  lost_count = 0


  def refresh_window():
   window.blit(BC, (0,0))

   level_label = main_font.render(f"Level: {level}",1,(255,255,255))  # level 
   lives_label = main_font.render(f"Lives: {lives}",1,(255,255,255))  # lives
   window.blit(lives_label,(10,20))                                   # location of lives
   window.blit(level_label,(10,40))                                   # location of level
        
   for enemy in enemies:
     enemy.draw(window)

   player.draw(window) 

   if lost:
     lost_labale = lost_font.render("GAME OVER",1,(255,0,0))
     window.blit(lost_labale,(W/2 - lost_labale.get_width()/2,300))
     game_over.play()
     mixer.music.stop()
    

   pygame.display.update()
         
  while run :
    clock.tick(FPS)
    refresh_window()
    
    if lives <= 0 or player.health <= 0:
     lost = True
     lost_count += 1
    
    if lost:
     if lost_count > FPS * 1.5:
       run = False
     else:
        continue     

    if len(enemies) == 0:
     level += 1
     wave_length += 5
     for i in range(wave_length):
        enemy = Enemy(random.randrange(50,W-100),random.randrange(-1500,-100),random.choice(["small","medium","large"])) 
        enemies.append(enemy)
    
  
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        quit()


 
    keys = pygame.key.get_pressed()
  
    if keys[pygame.K_a] and player .x - player_vel > 0:                #left
      player.x -= player_vel 
    if keys[pygame.K_d] and player.x + player_vel + 60 < W:            #right
      player.x += player_vel
    if keys[pygame.K_w] and player.y - player_vel > 0:                 # up
      player.y -= player_vel
    if keys[pygame.K_s] and player.y + player_vel + 60 < H:             # down
      player.y += player_vel 
    
    if keys[pygame.K_SPACE]:
      player.shoot()


    for enemy in enemies[:]:
      enemy.move(enemy_vel)
      enemy.move_lasers(laser_vel,player)

      if random.randrange(0,240) == 1:
        enemy.shoot()
      
      if collide(enemy, player):
        player.health -= 10
        enemies.remove(enemy) 
      elif enemy.y + enemy.get_height() > H:
        lives-=1
        enemies.remove(enemy) 
    
    player.move_lasers(-laser_vel, enemies)
 
    
  
def main_menu():
 title_font1 = pygame.font.SysFont("PressStart2P", 50)
 title_font2 = pygame.font.SysFont("PressStart2P", 25)
 title_font3 = pygame.font.SysFont("PressStart2P", 20)
 title_font4 = pygame.font.SysFont("PressStart2P", 12)
 run = True
 Help = False
 Detail = False
 while run:
   window.blit(BC, (0,0))
   # mx , my = pygame.mouse.get_pos()
   title_label1 = title_font1.render("Cowboy Bepop",1 , (255,2,255))
   title_label2 = title_font3.render("Press the first letter to begin", 1, (255,255,255))
   title_label3 = title_font2.render("START", 1, (255,255,255))
   title_label4 = title_font2.render("How To Play", 1, (255,255,255))
   title_label5 = title_font2.render("Details", 1, (255,255,255))
   help_label1 = title_font3.render("W = up", 1, (255,255,255))
   help_label2 = title_font3.render("S = down", 1, (255,255,255))
   help_label3 = title_font3.render("A = left", 1, (255,255,255))
   help_label4 = title_font3.render("D = right", 1, (255,255,255))
   help_label5 = title_font3.render("SPACE = shoot", 1, (255,255,255))
   detail_label1 = title_font2.render("Developer and Designer", 1, (255,255,255))
   detail_label2 = title_font3.render("Nima Etemad Golestani", 1, (255,255,255))
   detail_label3 = title_font4.render("BS of computer engineering", 1, (255,255,255))
   esc_label = title_font4.render("Do you want to go back to the Menu? press esc ", 1, (255,255,255))
   window.blit(title_label1, (W/2 - title_label1.get_width()/2, 150))
   window.blit(title_label2, (W/2 - title_label2.get_width()/2 , 250))
   window.blit(title_label3, (W/2 - title_label3.get_width()/2 , 290)) 
   window.blit(title_label4, (W/2 - title_label4.get_width()/2 , 340))
   window.blit(title_label5, (W/2 - title_label5.get_width()/2 , 400))
   pygame.display.update()

   for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_s:
          mainloop()
        if event.key == pygame.K_h:
          Help = True
          while Help:
           window.blit(BC, (0,0))
           window.blit(help_label1, (W/2 - help_label1.get_width()/2 , 150))
           window.blit(help_label2, (W/2 - help_label2.get_width()/2 , 190))
           window.blit(help_label3, (W/2 - help_label3.get_width()/2 , 230))
           window.blit(help_label4, (W/2 - help_label4.get_width()/2 , 270))
           window.blit(help_label5, (W/2 - help_label5.get_width()/2 , 310))
           window.blit(esc_label, (W/2 - esc_label.get_width()/2 , 400))
           pygame.display.update()
           for event in pygame.event.get():
             if event.type == pygame.QUIT:
               quit()
             if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                 main_menu()  

        if event.key == pygame.K_d:
          Detail = True 
          while Detail :
           window.blit(BC, (0,0))
           window.blit(detail_label1, (W/2 - detail_label1.get_width()/2 , 180))
           window.blit(detail_label2, (W/2 - detail_label2.get_width()/2 , 220))
           window.blit(detail_label3, (W/2 - detail_label3.get_width()/2 , 260))
           window.blit(esc_label, (W/2 - esc_label.get_width()/2 , 300))
           pygame.display.update()       
           for event in pygame.event.get():
             if event.type == pygame.QUIT:
               quit()
             if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                 main_menu()          

         

 pygame.quit()
  
main_menu()















