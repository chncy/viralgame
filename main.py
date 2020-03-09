from __future__ import division
import os
from enum import IntEnum
import pygame as pg
import random
import math

class State(IntEnum):
    HEALTHY = 0,
    INFECTED = 1,
    SICK = 2,
    DEAD = 3

color = [(255, 255, 255), (255, 255, 0), (52, 225, 0), (255, 0, 0)]

i_drawn = 0

width = 1920 - 32 * 4
height = 1000 - 32 * 4

grid = 32

fps = 30

class Folk():
    rect = pg.rect.Rect(0, 0, 2, 2)
    state = State.HEALTHY
    life = 100
    age = 0
    dead = 0
    reproduce = True

    def draw(self, screen):
        if(self.rect.top > height or self.rect.left > width or self.rect.top < 0 or self.rect.left < 0):
            return -1
        if(pg.rect.Rect(0, 0, 0, 0).collidepoint(self.rect.top, self.rect.left) or pg.rect.Rect(0, 0, 0, 0).collidepoint(self.rect.top + 1, self.rect.left + 1)):
            return -1
        
        pg.draw.rect(screen, color[self.state], self.rect)

density = 3

rows = [e for e in range(height // grid)]
cols = [e for e in range(width // grid)]
folks = [Folk() for e in range((len(rows) * len(cols)) * density)]
infected = []

def initFolks(screen):

    print("Folks initiated: ", (len(rows) * len(cols)) * density)
    
    i = 0
    for rowindex, row in enumerate(rows):
        for colindex, col in enumerate(cols):
            
            clusterpopulation = 0

            while(clusterpopulation < density):

                # Assign spawn position
                if((pg.time.get_ticks() * random.randint(1, 20)) % 2):
                    posX = random.randint(4, 18)
                    posY = random.randint(6, 22)
                elif((pg.time.get_ticks() * random.randint(1, 20)) % 4):
                    posX = random.randint(1, 10)
                    posY = random.randint(4, 32)
                elif((pg.time.get_ticks() * random.randint(1, 20)) % 5):
                    posX = random.randint(14, 32)
                    posY = random.randint(2, 13)
                else:
                    posX = random.randint(7, 17)
                    posY = random.randint(13, 32)
                posX += (grid * colindex)
                posY += (grid * rowindex)
                dudeid = i

                if(pg.rect.Rect(0, 0, 0, 0).collidepoint(posX, posY) or pg.rect.Rect(0, 0, 0, 0).collidepoint(posX + 1, posY + 1)):
                    continue
                
                folks[dudeid].state = State.HEALTHY

                folks[dudeid].rect = pg.rect.Rect(posX, posY, 2, 2)
                folks[dudeid].age = random.randint(0, 75)
                
                clusterpopulation += 1
                i += 1

    for i, guy in enumerate(folks):
            
        # Draw a pixel for everyone
        guy.draw(screen)

screen = pg.display.set_mode((width, height))
initFolks(screen)

def main():

    pg.init()

    pg.font.init()

    font = pg.font.SysFont("liberationsansnarrow", 32)
    font_small = pg.font.SysFont("liberationsansnarrow", 24)
    font_xsmall = pg.font.SysFont("freemono", 8)

    clock = pg.time.Clock()    

    running = True
    startedinfection = False
    tick = 0

    infected = []
    deathcount = 0
    newlyinfected = 0
    newlyrecovered = 0
    born = 0

    while running:

        # print(len(infected))

        year = 2018 + (tick // (2 * fps))

        if(year >= 2019 and not startedinfection):
            unlucky_feller = random.randint(0, len(folks))
            folks[unlucky_feller].state = State.INFECTED
            infected.append(folks[unlucky_feller].rect)
            startedinfection = True


        i_drawn = 0
        # infected, recovered and born are only counted ever so often
        if(tick % (2 * fps) == 0):
            newlyinfected = 0
            newlyrecovered = 0
            born = 0

        # fill screen with solid color then redraw everything
        screen.fill((20, 20, 20))

        # now draw grid lines for eye comfort
        for rowindex, row in enumerate(rows):
            
            # horizontal
            rowcolor = (42, 42, 42) if rowindex % 2 == 0 else (30, 30, 30)

            if not rowindex == len(rows) - 1: # we dont need to draw the last line
                pg.draw.line(screen, rowcolor, (0, 32 + (rowindex * 32)), (width, 32 + (rowindex * 32)))
            #
            #
            for colindex, col in enumerate(cols):
                
                # vertical
                colcolor = (42, 42, 42) if rowindex % 2 == 1 else (30, 30, 30)
                
                if not colindex == len(cols) - 1: # we dont need to draw the last line
                    pg.draw.line(screen, colcolor, (32 + (colindex * 32), 0), (32 + (colindex * 32), height))
                
        chance = (0.01 + (0.09 / ((1 + (3 * math.exp(-0.0008 * len(infected)))))))

        year_txt = font_small.render("Year {0}".format(year), True, (255, 255, 255))
        chance_txt = font_small.render("Chance {0} %".format(round(chance * 100, 2)), True, (154, 31, 49))
        infectedtext = font.render("INFECTED: {0}".format(len(infected)), True, (255, 255, 255))
        deadtext = font.render("DEAD: {0}".format(deathcount), True, (255, 255, 255))
        totaltext = font.render("TOTAL: {0}".format(len(folks)), True, (255, 255, 255))
        screen.blit(year_txt, (width // 2, 10))
        screen.blit(chance_txt, (width // 3, 10))
        screen.blit(infectedtext, (10, 10))
        screen.blit(deadtext, (10, 50))
        screen.blit(totaltext, (10, 90))

        if(tick % fps == 0):
            for i, guy in enumerate(folks):
                if(guy.rect.top > height or guy.rect.left > width):
                    folks.remove(guy)
                    if guy in infected:
                        infected.remove(guy)
                    continue

                if(guy.state is not State.DEAD):
                
                    # Become infected if an infected is close
                    guyX, guyY = guy.rect.right, guy.rect.top

                    if(guy.age > 16 and guy.rect.collidepoint(guyX - 1, guyY - 1) or guy.rect.collidepoint(guyX + 1, guyY - 1) or guy.rect.collidepoint(guyX - 1, guyY + 1) or guy.rect.collidepoint(guyX + 1, guyY + 1)):
                        if(random.random() < 0.008):
                            guy.reproduce = False
                            dude = Folk()
                            dude.rect = guy.rect
                            dude.rect.move_ip(2, 2)
                            dude.age = 0
                                
                            if(random.random() < 0.005):
                                del dude
                                continue
                            else:
                                folks.append(dude)
                                born += 1

                    if(year >= 2020 and random.random() < chance and guy.state is not State.INFECTED):
                        guy.state = State.INFECTED
                        newlyinfected += 1
                        continue


        for i, guy in enumerate(folks):
            if(guy.state is not State.DEAD):
                move = random.randint(0, 6)
                if move == 0 and guy.rect.top != 0:
                    guy.rect.move_ip(0, -2)
                elif move == 1 and guy.rect.left != width:
                    guy.rect.move_ip(2, 0)
                elif move == 2 and guy.rect.top != height:
                    guy.rect.move_ip(0, 2)
                elif move == 3 and guy.rect.left != 0:
                    guy.rect.move_ip(-2, 0)


        if(tick % (2 * fps) == 0):
            for i, guy in enumerate(folks):
                if(guy.age > 50 and guy.state is not State.DEAD):
                    guy.reproduce = False

                if not guy.reproduce and guy.age < 50:
                    guy.reproduce = True
                
                if(guy.age > 90 and guy.state is not State.DEAD):
                    guy.state = State.DEAD
                    deathcount += 1
                    continue

                if(guy.state is State.DEAD):
                    if(guy.dead >= 5):
                        folks.remove(guy)
                        # if guy in infected:
                        #    infected.remove(guy)
                        deathcount += 1
                        continue
                    else:
                        guy.dead += 1

                guy.age += 1
                if(guy.state == State.INFECTED or guy.state == State.SICK):
                    fate = random.random()
                    if fate < 0.2 and guy.state is not State.SICK:
                        guy.state = State.SICK
                    elif fate < 0.3 and guy.age < 65:
                        guy.state = State.HEALTHY
                        newlyrecovered += 1
                    elif fate < 0.33:
                        guy.state = State.DEAD
                        deathcount += 1
                        continue
                    elif fate < 0.4 and guy.state == State.SICK:
                        guy.state = State.DEAD
                        deathcount += 1
                        continue

            infected = [x for x in folks if x.state is State.INFECTED or x.state is State.SICK]
            new = font_small.render("Newly Infected / Recovered / Born: {0} -/- {1} -/- {2} ({3})".format(newlyinfected, newlyrecovered, born, newlyinfected - newlyrecovered - born), True, (255, 255, 255))

        for guy in folks:

            if i % 100 == 0 and i_drawn % 100 == 0:
                print(i, guy.rect, guy.state, guy.dead)
            if(guy.draw(screen) == -1):
                folks.remove(guy)
                continue
            i_drawn += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        ages_0_20 = sum(1 for x in folks if x.age <= 20) / len(folks)
        ages_21_40 = sum(1 for x in folks if x.age >= 21 and x.age <= 40) / len(folks)
        ages_41_60 = sum(1 for x in folks if x.age >= 41 and x.age <= 60) / len(folks)
        ages_61_90 = sum(1 for x in folks if x.age >= 61 and x.age <= 90) / len(folks)
        
        pg.draw.rect(screen, (42, 42, 42), [width - 152, height - 112, 124, 104])
        pg.draw.rect(screen, (21, 23, 176), [width - 150, height - 110, 120 * ages_0_20, 25])
        pg.draw.rect(screen, (50, 150, 21), [width - 150, height - 85, 120 * ages_21_40, 25])
        pg.draw.rect(screen, (176, 21, 21), [width - 150, height - 60, 120 * ages_41_60, 25])
        pg.draw.rect(screen, (73, 64, 14), [width - 150, height - 35, 120 * ages_61_90, 25])

        agetext_0_20 = font_xsmall.render("Ages 0 - 20 ({0} %)".format(round(ages_0_20 * 100, 1)), True, (255, 255, 255))
        agetext_21_40 = font_xsmall.render("Ages 21 - 40 ({0} %)".format(round(ages_21_40 * 100, 1)), True, (255, 255, 255))
        agetext_41_60 = font_xsmall.render("Ages 41 - 60 ({0} %)".format(round(ages_41_60 * 100, 1)), True, (255, 255, 255))
        agetext_61_90 = font_xsmall.render("Ages 61 - 90 ({0} %)".format(round(ages_61_90 * 100, 1)), True, (255, 255, 255))

        screen.blit(agetext_0_20, (width - 148, height - 100))
        screen.blit(agetext_21_40, (width - 148, height - 75))
        screen.blit(agetext_41_60, (width - 148, height - 50))
        screen.blit(agetext_61_90, (width - 148, height - 25))

        screen.blit(new, (10, height - 50))
        pg.display.flip()

        clock.tick(fps)
        tick += 1

def random_color():
    rgbl = [255, 0, 0]
    random.shuffle(rgbl)
    return tuple(rgbl)


if __name__ == "__main__":
    main()
