import pygame as py
import math
import numpy as np
import time



py.init()

class scene:

    def __init__(self, width, height):
        self.color = (0, 0, 0)
        self.caption = "Fluid Simulation"
        self.width = width
        self.height = height

        py.display.init()
        self.screen = py.display.set_mode((self.width, self.height)) 
        py.display.set_caption(self.caption)
        self.screen.fill(self.color)
    
    def updateScreen(self):
        # print(py.PixelArray(self.screen))
        # print(self.screen)
        py.display.update()
    
    def clear(self):
        self.screen.fill(self.color)



class particle:

    dampingcoeff = 0.9

    def __init__(self, radius, x, y, color):
        self.radius = radius
        self.color = color
        self.posx = x
        self.posy = y

        self.velocity = [0, 0]


    def draw(self, scene):
        py.draw.circle(scene.screen, self.color, (self.posx, self.posy), self.radius)
    
    #Velocity Methods
    #====================================
    def updateVelocityRandom(self, timeStep):
        self.velocity[0] += 3*timeStep*np.random.standard_normal()
        self.velocity[1] += 3*timeStep*np.random.standard_normal()
    
    def updateVelocityWallColl(self, scene):
        if self.posx > scene.width - self.radius or self.posx < self.radius:
            self.velocity[0] *= -1*particle.dampingcoeff

        if self.posy > scene.height - self.radius or self.posy < self.radius:
            self.velocity[1] *= -1*particle.dampingcoeff

        self.velocity[0] = 0 if (self.posx >= scene.width - self.radius or self.posx <= self.radius) and abs(self.velocity[0]) < 0.05 else self.velocity[0]
        self.velocity[1] = 0 if (self.posy >= scene.height - self.radius or self.posy <= self.radius) and abs(self.velocity[1]) < 0.05 else self.velocity[1]

    def updateVelocityWithG(self, g, timeStep):
        
        self.velocity[1] += g*timeStep


    def updateVelocity(self, g, timeStep, scene, gtrue, rtrue):
        if gtrue:
            self.updateVelocityWithG(g, timeStep)
        if rtrue:
            self.updateVelocityRandom(timeStep)

        self.updateVelocityWallColl(scene)
    #====================================

    #Position Methods
    #====================================
    def updatePosition(self, scene):

        self.posx = self.checkWallCollision(self.posx, self.velocity[0], scene.width)
        self.posy = self.checkWallCollision(self.posy, self.velocity[1], scene.height)


    def checkWallCollision(self, pos, velocity, wall):
        if pos <= wall-self.radius and pos >= self.radius:
            pos = pos + velocity
        else:
            pos = self.radius if pos < wall/10 else wall - self.radius
        
        return pos
    #====================================

class densityField():

    def __init__(self, width, height, radius, granularity):
        self.fieldWidth = width
        self.fieldHeight = height
        self.field = np.zeros((width, height))
        self.smoothingRadius = radius
        self.granularity = granularity

        self.radiusDensity = np.zeros((2*radius, 2*radius))
        self.initializeRadiusMatrix()

    def initializeRadiusMatrix(self):
        pixelx = -self.smoothingRadius
        pixely = -self.smoothingRadius
       
        for i in range(0, round((2*self.smoothingRadius/self.granularity)**2)):
            distance = (pixelx**2 + pixely**2)**0.5
            if distance <= self.smoothingRadius:
                self.radiusDensity[pixelx+self.smoothingRadius, pixely+self.smoothingRadius] += 1.001 - distance/self.smoothingRadius

            pixelx += self.granularity
            if pixelx >= self.smoothingRadius:
                pixelx = -self.smoothingRadius
                pixely += self.granularity


    def updateField(self, particle):
        px = int(particle.posx)
        py = int(particle.posy) 

        xmin, rxmin = (max(0, px-self.smoothingRadius), max(0, self.smoothingRadius-px))
        xmax, rxmax = (min(self.fieldWidth, px+self.smoothingRadius), min(2*self.smoothingRadius, self.smoothingRadius + self.fieldWidth-px))
        ymin, rymin = (max(0, py-self.smoothingRadius), max(0, self.smoothingRadius-py))
        ymax, rymax = (min(self.fieldHeight, py+self.smoothingRadius), min(2*self.smoothingRadius, self.smoothingRadius + self.fieldHeight-py))

        self.field[xmin:xmax, ymin:ymax] += self.radiusDensity[rxmin:rxmax, rymin:rymax]
        

    def normalizeField(self):
        self.field /= self.field.max()
        

    def clearField(self):
        self.field = np.zeros((self.fieldWidth, self.fieldHeight))

    def drawField(self, scene):
        
        py.surfarray.blit_array(scene.screen, self.field *255)
        
       




def makeParticles(amnt, radius, color, scene):
    px = scene.width/2 - (round(amnt**0.5)*(radius*2))/2 + radius
    py = scene.height/2 - (round(amnt**0.5)*(radius*2))/2 + radius
    
    particles = []
    for i in range(0, amnt):
        particles.append(particle(radius, px, py, color))
        px += radius*2
    
        if px > scene.width/2 + (round(amnt**0.5)*(radius*2))/2:
            
            px = scene.width/2 - (round(amnt**0.5)*(radius*2))/2 + radius
            py += radius*2

    
    return particles


def main():

    sceneWidth = 1000
    sceneHeight = 700
    g = 9.81
    timeStep = 0.01

    particles = 2500
    particleColor = (0, 163, 108)
    particleR = 5
    smoothingR = 35

    scene1 = scene(sceneWidth, sceneHeight)
    particles = makeParticles(particles, particleR, particleColor, scene1)
    
    densityField1 = densityField(sceneWidth, sceneHeight, smoothingR, 1)


    run = True
    animate = False
    drawParticles = True
    drawField = True
    method = True
    addTimeDelay = True
    useGravity = True
    useRandom = True

    for p in particles:
        p.draw(scene1)
    
    scene1.updateScreen()

    print("Done")
    while run:



        for event in py.event.get():
            if event.type == py.QUIT: 
                run = False
        
            if event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    animate = not animate
                if event.key == py.K_p:
                    drawParticles = not drawParticles
                if event.key == py.K_f:
                    drawField = not drawField
                if event.key == py.K_t:
                    addTimeDelay = not addTimeDelay
                if event.key == py.K_g:
                    useGravity = not useGravity
                if event.key == py.K_r:
                    useRandom = not useRandom
                # if event.key == py.K_m:
                #     method = not method


        

        if animate:
            scene1.clear()
            densityField1.clearField()

            if method:
                for p in particles:
        
                    densityField1.updateField(p)

                densityField1.normalizeField()
                if drawField:
                    densityField1.drawField(scene1)
        
                for p in particles:
                    p.updatePosition(scene1)
                    p.updateVelocity(g, timeStep, scene1, useGravity, useRandom)
                    if drawParticles:
                        p.draw(scene1)
            
            if addTimeDelay:
                py.draw.rect(scene1.screen, (255, 0, 0), (0, 0, 24, 24))

            scene1.updateScreen()
            if addTimeDelay:

                time.sleep(timeStep)

main()




