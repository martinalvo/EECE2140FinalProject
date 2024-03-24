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

        py.display.update()
    
    def clear(self):
        self.screen.fill(self.color)



class particle:

    dampingcoeff = 0.7

    def __init__(self, radius, x, y, color):
        self.radius = radius
        self.color = color
        self.posx = x
        self.posy = y

        self.velocity = [0, 0]


    def draw(self, scene):
        py.draw.ellipse(scene.screen, self.color, (self.posx-self.radius, self.posy-self.radius, 2*self.radius + 1, 2*self.radius + 1))
    
    #Velocity Methods
    #====================================
    def initializeRadiusMatrix(radius):
        pixelx = -radius
        pixely = -radius

        vectorRadiusDensity = np.zeros((2*radius+1, 2*radius+1))
       
        for i in range(0, round((2*radius+1)**2)):
            distance = (pixelx**2 + pixely**2)**0.5
            if distance <= radius:
                vectorRadiusDensity[pixely+radius, pixelx+radius] += (1.0001 - (distance/radius)**3)**6

            pixelx += 1
            if pixelx > radius:
                pixelx = -radius
                pixely += 1
        
        return vectorRadiusDensity
    
    def updateVelocityRandom(self, timeStep):
        self.velocity[0] += 3*timeStep*np.random.standard_normal()
        self.velocity[1] += 3*timeStep*np.random.standard_normal()
    
    def updateVelocityWallColl(self, scene):
        if self.posx >= scene.width - self.radius - 1 or self.posx <= self.radius:
            self.velocity[0] *= -1*particle.dampingcoeff

        if self.posy >= scene.height - self.radius - 1 or self.posy <= self.radius:
            self.velocity[1] *= -1*particle.dampingcoeff

    def updateVelocityWithG(self, g, timeStep):
        self.velocity[1] += g*timeStep
    
    def updateVelocityVField(self, timeStep, densityVal, vectorRadius ,radiusMatrix, vectorF, scene):
        px = round(self.posx)
        py = round(self.posy)

        xmin, rxmin = (max(0, px-vectorRadius), max(0, vectorRadius-px))
        xmax, rxmax = (min(scene.width, px+vectorRadius), min(2*vectorRadius, vectorRadius + scene.width-px))
        ymin, rymin = (max(0, py-vectorRadius), max(0, vectorRadius-py))
        ymax, rymax = (min(scene.height, py+vectorRadius), min(2*vectorRadius, vectorRadius + scene.height-py))

        self.velocity[0] += np.sum(vectorF[ymin:ymax, xmin:xmax, 0]*radiusMatrix[rymin:rymax, rxmin:rxmax])*timeStep*densityVal
        
        self.velocity[1] += np.sum(vectorF[ymin:ymax, xmin:xmax, 1]*radiusMatrix[rymin:rymax, rxmin:rxmax])*timeStep*densityVal
    

    def updateVelocity(self, g, timeStep, scene, gtrue, rtrue, vtrue, densityVal, vectorRadius, radiusMatrix, vectorF):
        if gtrue:
            self.updateVelocityWithG(g, timeStep)
        if vtrue:
            self.updateVelocityVField(timeStep, densityVal, vectorRadius, radiusMatrix, vectorF, scene)
        if rtrue:
            self.updateVelocityRandom(timeStep)
        
        self.velocity[0] *= 0.9
        self.velocity[1] *= 0.9

        self.updateVelocityWallColl(scene)
    #====================================

    #Position Methods
    #====================================
    def updatePosition(self, scene, vFieldTest):

        self.posx = self.checkWallCollision(self.posx, self.velocity[0], scene.width, vFieldTest)
        self.posy = self.checkWallCollision(self.posy, self.velocity[1], scene.height, vFieldTest)


    def checkWallCollision(self, pos, velocity, wall, vFieldTest):
        if pos + velocity >= self.radius and pos + velocity <= wall - 1 - self.radius:
            pos = pos + velocity
        else:
            pos = self.radius if pos < wall/10 else wall - self.radius - 1
        
        return pos
    #====================================

class densityField():

    def __init__(self, width, height, radius):
        self.fieldWidth = width
        self.fieldHeight = height
        self.field = np.zeros((height, width))
        self.smoothingRadius = radius

        self.radiusDensity = np.zeros((2*radius+1, 2*radius+1))
        self.initializeRadiusMatrix()

    def initializeRadiusMatrix(self):
        pixelx = -self.smoothingRadius
        pixely = -self.smoothingRadius
       
        for i in range(0, round((2*self.smoothingRadius+1)**2)):
            distance = (pixelx**2 + pixely**2)**0.5
            if distance <= self.smoothingRadius:
                self.radiusDensity[pixely+self.smoothingRadius, pixelx+self.smoothingRadius] += (1.0001 - (distance/self.smoothingRadius)**3)**6

            pixelx += 1
            if pixelx > self.smoothingRadius:
                pixelx = -self.smoothingRadius
                pixely += 1

    def updateField(self, particle):
        px = round(particle.posx)
        py = round(particle.posy)

        xmin, rxmin = (max(0, px-self.smoothingRadius), max(0, self.smoothingRadius-px))
        xmax, rxmax = (min(self.fieldWidth, px+self.smoothingRadius), min(2*self.smoothingRadius, self.smoothingRadius + self.fieldWidth-px))
        ymin, rymin = (max(0, py-self.smoothingRadius), max(0, self.smoothingRadius-py))
        ymax, rymax = (min(self.fieldHeight, py+self.smoothingRadius), min(2*self.smoothingRadius, self.smoothingRadius + self.fieldHeight-py))

        self.field[ymin:ymax, xmin:xmax] += self.radiusDensity[rymin:rymax, rxmin:rxmax]

    def normalizeField(self):
        self.field /= self.field.max()
        

    def clearField(self):
        self.field = np.zeros((self.fieldHeight, self.fieldWidth))

    def drawDensityField(self, scene):
        
        py.surfarray.blit_array(scene.screen, self.field.T *255)
        

class vectorField():

    def __init__(self, width, height):
        self.vectorWidth = width
        self.vectorHeight = height
        self.vectorField = np.zeros((height, width, 2))
        self.xGrid3D, self.yGrid3D = vectorField.initializeVectorField(height, width)

    def initializeVectorField(h, w):
        xGrid3D = np.stack([np.full((h, w), -1), np.ones((h, w)), np.zeros((h, w)), np.zeros((h, w))], axis=2)
        yGrid3D = np.stack([np.zeros((h, w)), np.zeros((h, w)), np.ones((h, w)), np.full((h, w), -1)], axis=2)

        return xGrid3D, yGrid3D
        

    def updateVectorField(self, dField):

        densityLEFT = np.hstack((dField[:,1:], np.ones((self.vectorHeight,1))))
        densityRIGHT = np.hstack((np.ones((self.vectorHeight,1)), dField[:,:-1]))
        densityDOWN = np.vstack((np.ones((1,self.vectorWidth)), dField[:-1,:]))
        densityUP = np.vstack((dField[1:,:], np.ones((1,self.vectorWidth))))

        densityStack = np.stack([densityLEFT, densityRIGHT, densityDOWN, densityUP], axis=2)
        densityPicks = np.argsort(densityStack, axis=2)

        xVectors = np.take_along_axis(self.xGrid3D, densityPicks, axis=2)[:,:,3]
        yVectors = np.take_along_axis(self.yGrid3D, densityPicks, axis=2)[:,:,3]

        xVectorsWDensity = xVectors * dField
        yVectorsWDensity = yVectors * dField

        self.vectorField = np.stack([xVectorsWDensity, yVectorsWDensity], axis=2)
    


    def drawVectorField(self, scene):

        normalField = self.vectorField / self.vectorField.max()

        py.surfarray.blit_array(scene.screen, normalField[:,:,1].T*255 + normalField[:,:,0].T*255**2)
        



def makeParticles(amnt, radius, color, scene):
    px = round(scene.width/2 - (round(amnt**0.5)*(radius*2+1))/2 + radius )
    py = round(scene.height/2 - (round(amnt**0.5)*(radius*2+1))/2 + radius )
    
    particles = []
    for i in range(0, amnt):
        particles.append(particle(radius, px, py, color))
        px += radius*2+1

        if px > scene.width/2 + (round(amnt**0.5)*(radius*2+1))/2:
            
            px = round(scene.width/2 - (round(amnt**0.5)*(radius*2+1))/2 + radius)
            py += radius*2+1

    
    return particles


def main():

    sceneWidth = 500
    sceneHeight = 500
    g = 9.81*7
    densityVal = 5

    timeStep = 0.01

    particles = 500 
    particleColor = (0, 163, 108)
    particleR = 4
    vectorRadiusMultiplier = 12 

    smoothingR = 25

    scene1 = scene(sceneWidth, sceneHeight)
    particles = makeParticles(particles, particleR, particleColor, scene1)
    
    densityField1 = densityField(sceneWidth, sceneHeight, smoothingR)
    vectorField1 = vectorField(sceneWidth, sceneHeight)
    vectorRadiusDensity = particle.initializeRadiusMatrix(vectorRadiusMultiplier)


    run = True
    animate = False
    drawParticles = True
    drawField = False
    addTimeDelay = True
    useGravity = True
    useRandom = False
    useVField = True
    calcVField = True
    drawVField = True

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
                if event.key == py.K_v:
                    calcVField = not calcVField
                if event.key == py.K_b:
                    drawVField = not drawVField

                # if event.key == py.K_m:
                #     method = not method


        

        if animate:
            scene1.clear()
            densityField1.clearField()

            for p in particles:
    
                densityField1.updateField(p)

            densityField1.normalizeField() 
            if drawField:
                densityField1.drawDensityField(scene1)
            
            if calcVField:
                vectorField1.updateVectorField(densityField1.field)

            if drawVField:
                vectorField1.drawVectorField(scene1)

            for p in particles:
                p.updateVelocity(g, timeStep, scene1, useGravity, useRandom, useVField, densityVal, vectorRadiusMultiplier, vectorRadiusDensity, vectorField1.vectorField)
                p.updatePosition(scene1, vectorField1.vectorField)
                if drawParticles:
                    p.draw(scene1)
            
            if addTimeDelay:
                py.draw.rect(scene1.screen, (255, 0, 0), (0, 0, 24, 24))

            scene1.updateScreen()
            if addTimeDelay:

                time.sleep(timeStep)

main()




