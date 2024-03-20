import pygame as py
import math
import numpy as np
import time



class scene:

    def __init__(self, width, height):
        self.color = (0, 0, 0)
        self.caption = "Fluid Simulation"
        self.width = width
        self.height = height

        self.screen = py.display.set_mode((self.width, self.height)) 
        py.display.set_caption(self.caption)
        self.screen.fill(self.color)
    
    def update(self):
        py.display.flip()
    
    def clear(self):
        self.screen.fill(self.color)



class particle:

    dampingcoeff = 0.9

    def __init__(self, radius, x, y):
        self.radius = radius
        self.color = (0, 255, 0)
        self.posx = x
        self.posy = y

        self.velocity = [0, 0]


    def draw(self, scene):
        py.draw.circle(scene.screen, self.color, (self.posx, self.posy), self.radius)

    def updateVelocityWallColl(self, scene):
        if self.posx > scene.width - self.radius or self.posx < self.radius:
            self.velocity[0] *= -1*particle.dampingcoeff

        if self.posy > scene.height - self.radius or self.posy < self.radius:
            self.velocity[1] *= -1*particle.dampingcoeff

        self.velocity[0] = 0 if (self.posx >= scene.width - self.radius or self.posx <= self.radius) and abs(self.velocity[0]) < 0.05 else self.velocity[0]
        self.velocity[1] = 0 if (self.posy >= scene.height - self.radius or self.posy <= self.radius) and abs(self.velocity[1]) < 0.05 else self.velocity[1]

    def updateVelocityWithG(self, g, timeStep):

        self.velocity[1] += g*timeStep

    def updateVelocity(self, g, timeStep, scene):

        self.updateVelocityWithG(g, timeStep)
        self.updateVelocityWallColl(scene)
        

    def updatePosition(self, scene):

        self.posx = self.checkWallCollision(self.posx, self.velocity[0], scene.width)
        self.posy = self.checkWallCollision(self.posy, self.velocity[1], scene.height)


    def checkWallCollision(self, pos, velocity, wall):
        if pos <= wall-self.radius and pos >= self.radius:
            pos = pos + velocity
        else:
            pos = self.radius if pos < wall/10 else wall - self.radius
        
        return pos
        

def makeParticles(amnt, radius, scene):
    px = scene.width/2 - (round(amnt**0.5)*(radius*2))/2 + radius
    py = scene.height/2 - (round(amnt**0.5)*(radius*2))/2 + radius
    print(px, py)
    particles = []
    for i in range(0, amnt):
        particles.append(particle(radius, px, py))
        px += radius*2
        print(px)
        if px > scene.width/2 + (round(amnt**0.5)*(radius*2))/2:
            print("YES")
            px = scene.width/2 - (round(amnt**0.5)*(radius*2))/2 + radius
            py += radius*2

    
    return particles


def main():

    scene1 = scene(500, 500)
    particles = makeParticles(400, 10, scene1)
    
    g = 9.81

    timeStep = 0.001

    run = True
    animate = False

    for p in particles:
        p.draw(scene1)
    scene1.update()

    while run:



        for event in py.event.get():
            if event.type == py.QUIT: 
                run = False
        
            if event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    animate = not animate
        
        if animate:
            scene1.clear()
            for p in particles:
                p.updatePosition(scene1)
                p.updateVelocity(g, timeStep, scene1)
                p.draw(scene1)
  
            scene1.update()
            time.sleep(timeStep)

main()




