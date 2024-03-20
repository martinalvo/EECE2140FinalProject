import pygame as py
import math
import numpy as np



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

    def __init__(self, radius, x, y):
        self.radius = radius
        self.color = (0, 255, 0)
        self.posx = x
        self.posy = y

    def draw(self, scene):
        py.draw.circle(scene.screen, self.color, (self.posx, self.posy), self.radius)



def main():

    scene1 = scene(500, 500)
    p1 = particle(10, 250, 250)

    run = True
    while run:



        for event in py.event.get():
            if event.type == py.QUIT: 
                run = False
        
            if event.type == py.KEYDOWN:
                if event.key == py.K_LEFT:
                    p1.posx -= 5
                if event.key == py.K_RIGHT:
                    p1.posx += 5
        
        scene1.clear()
        p1.draw(scene1)
        scene1.update()


main()




