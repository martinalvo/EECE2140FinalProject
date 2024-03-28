import pygame as py
import math
import numpy as np
import time


#window class, for drawing drawing the background of the simulation
class window:

    #Initializing the window class with a certain width and height. Setting the color of the scene to black
    #And the caption of the window aswell
    def __init__(self, width, height):
        self.color = (0, 0, 0)
        self.caption = "Fluid Simulation"
        self.width = width
        self.height = height

        py.display.init()
        self.screen = py.display.set_mode((self.width, self.height)) 
        py.display.set_caption(self.caption)
        self.screen.fill(self.color)
    
    #Method to update the window
    def updateScreen(self):

        py.display.update()
    
    #Method to clear the window
    def clear(self):
        self.screen.fill(self.color)


#Class for a particle
class particle:

    #Initializing the particle class with the atributes of each particle inclduing x and y positions, aswell as 
    #radius and color
    def __init__(self, radius, x, y, color):
        self.radius = radius
        self.color = color
        self.posx = x
        self.posy = y
        self.velocityMag = 0

        self.velocity = [0, 0]

    #Drawing the particles onto the screen
    def draw(self, background):
        py.draw.ellipse(background.screen, self.color, (self.posx-self.radius, self.posy-self.radius, 2*self.radius + 1, 2*self.radius + 1))
    
    #Velocity Methods
    #====================================
        
    #Method to add random velocity to each particle
    def updateVelocityRandom(self, timeStep):
        self.velocity[0] += 3*timeStep*np.random.standard_normal()
        self.velocity[1] += 3*timeStep*np.random.standard_normal()

    #Method to update the velocity of a particle if it collides into a wall
    def updateVelocityWallColl(self, background, dampingcoeff):
        if self.posx >= background.width - self.radius - 1 or self.posx <= self.radius:
            self.velocity[0] *= -1*dampingcoeff

        if self.posy >= background.height - self.radius - 1 or self.posy <= self.radius:
            self.velocity[1] *= -1*dampingcoeff

    #Method to update the y velocity of a particle with gravity
    def updateVelocityWithG(self, g, timeStep):
        self.velocity[1] += g*timeStep
    
    #Method to update the velocity of a particle using the vector field.
    def updateVelocityVField(self, timeStep, densityVal, vField):
        radius = vField.radius
        px = round(self.posx)
        py = round(self.posy)

        #Calculating bounds to use for vector field matrix and distanceMultiplier matrix so that no idex error occurse
        #(would happen if the particles are close to the edges and they try to use indexes not in the scene)
        xmin, rxmin = (max(0, px-radius), max(0, radius-px))
        xmax, rxmax = (min(vField.vectorWidth, px+radius), min(2*radius, radius + vField.vectorWidth-px))
        ymin, rymin = (max(0, py-radius), max(0, radius-py))
        ymax, rymax = (min(vField.vectorWidth, py+radius), min(2*radius, radius + vField.vectorHeight-py))

        #Updating x velocity of the particle with sum of all x vectors of vector field, multiplied by how far away they are from the particle
        #(distanceMultipliier matrix), aswell as the timeStep, and the density which will affect how powerfull they are
        self.velocity[0] += np.sum(vField.field[ymin:ymax, xmin:xmax, 0]*vField.distanceMultiplier[rymin:rymax, rxmin:rxmax])*timeStep*densityVal
        
        #Same for y velocity of the particle
        self.velocity[1] += np.sum(vField.field[ymin:ymax, xmin:xmax, 1]*vField.distanceMultiplier[rymin:rymax, rxmin:rxmax])*timeStep*densityVal
    
    #Method to decelerate particles to attempt to simulate surface tensiono
    def updateVelocityDeceleration(self, dField):

        radius = dField.smoothingRadius
        px = round(self.posx)
        py = round(self.posy)

        #Calculating bounds to use for density field matrix
        xmin= max(0, px-radius)
        xmax= min(dField.fieldWidth, px+radius)
        ymin= max(0, py-radius)
        ymax= min(dField.fieldHeight, py+radius)

        #setting the multiplier that will affect the particles velocity proportional to how dense the field is around the particle
        #with a limit of 0.8
        multiplier = 1 - 0.2*np.sum(dField.field[ymin:ymax, xmin:xmax])/((2*radius+1)**2)

        #multiplying the velocities by the multiplier to decrease them
        self.velocity[0] *= multiplier
        self.velocity[1] *= multiplier
    
    #Method to update the velocity of the particles using all of the different velocity methods
    def updateVelocity(self, g, dampingcoeff, timeStep, background, gtrue, rtrue, dtrue, densityVal, vField, densityF):
        #If statements to check which velocity methods should be used to affect the particle
        if gtrue:
            self.updateVelocityWithG(g, timeStep)
        if rtrue:
            self.updateVelocityRandom(timeStep)
        if dtrue:
            self.updateVelocityDeceleration(densityF)

        #Update the velocity of using the vector field
        self.updateVelocityVField(timeStep, densityVal, vField)
        
        #Find the magnitude of the velocity of the particle
        self.velocityMag = (self.velocity[0]**2 + self.velocity[1]**2)**0.5

        #Update the velocity using teh wall collision method
        self.updateVelocityWallColl(background, dampingcoeff)
    #====================================

    #Position Methods
    #====================================
        
    #Method to update the position with the particles velocity. It simoltenusly checks for wall collisions
    def updatePosition(self, background):

        self.posx = self.checkWallCollision(self.posx, self.velocity[0], background.width)
        self.posy = self.checkWallCollision(self.posy, self.velocity[1], background.height)
    
    #Method to check if a particle has collided into a wall
    def checkWallCollision(self, pos, velocity, wall):
        #Checking if the particles position +- its radius is outside one of the walls bounds
        #If so, not adding velocity but making it touch the wall dirrectly
        #Also reversing its velocity so it bounces backwards
        if pos + velocity >= self.radius and pos + velocity <= wall - 1 - self.radius:
            pos = pos + velocity
        else:
            pos = self.radius if pos < wall/10 else wall - self.radius - 1
        
        return pos
    #====================================
    #Method to update the color of the particle based on its velocity
    def updateColor(self):
        newColor = list(self.color)

        newColor[0] = round(255 * min(1, self.velocityMag/10))
        self.color = tuple(newColor)

class densityField():

    def __init__(self, width, height, radius):
        self.fieldWidth = width
        self.fieldHeight = height
        self.field = np.zeros((height, width))
        self.smoothingRadius = radius

        self.addDensity = np.zeros((2*radius+1, 2*radius+1))
        self.addDensityMatrix()

    def addDensityMatrix(self):
        pixelx = -self.smoothingRadius
        pixely = -self.smoothingRadius
       
        for i in range(0, round((2*self.smoothingRadius+1)**2)):
            distance = (pixelx**2 + pixely**2)**0.5
            if distance <= self.smoothingRadius:
                self.addDensity[pixely+self.smoothingRadius, pixelx+self.smoothingRadius] += (1.0001 - (distance/self.smoothingRadius)**3)**6

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

        self.field[ymin:ymax, xmin:xmax] += self.addDensity[rymin:rymax, rxmin:rxmax]

    def normalizeField(self):
        self.field /= 5
        

    def clearField(self):
        self.field = np.zeros((self.fieldHeight, self.fieldWidth))

    def drawDensityField(self, background):
        
        py.surfarray.blit_array(background.screen, (self.field.T/self.field.max()) *255)
        

class vectorField():

    def __init__(self, width, height, radius):
        self.vectorWidth = width
        self.vectorHeight = height
        self.field = np.zeros((height, width, 2))
        self.xGrid3D, self.yGrid3D = vectorField.initializeVectorField(height, width)
        self.radius = radius
        self.distanceMultiplier = vectorField.initializeDistanceMatrix(radius)

    def initializeVectorField(h, w):
        xGrid3D = np.stack([np.full((h, w), -1), np.ones((h, w)), np.zeros((h, w)), np.zeros((h, w))], axis=2)
        yGrid3D = np.stack([np.zeros((h, w)), np.zeros((h, w)), np.ones((h, w)), np.full((h, w), -1)], axis=2)

        return xGrid3D, yGrid3D
    
    def initializeDistanceMatrix(radius):
        pixelx = -radius
        pixely = -radius

        distanceMultiplier = np.zeros((2*radius+1, 2*radius+1))
        
        for i in range(0, round((2*radius+1)**2)):
            distance = (pixelx**2 + pixely**2)**0.5
            if distance <= radius:
                distanceMultiplier[pixely+radius, pixelx+radius] += (1.0001 - (distance/radius)**3)**6

            pixelx += 1
            if pixelx > radius:
                pixelx = -radius
                pixely += 1
        
        return distanceMultiplier
    
        

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

        self.field = np.stack([xVectorsWDensity, yVectorsWDensity], axis=2)
    


    def drawVectorField(self, background):

        normalField = self.field / self.field.max()

        py.surfarray.blit_array(background.screen, normalField[:,:,1].T*255 + normalField[:,:,0].T*255**2)
        
class changeVectorField():

    def __init__(self, radius, strength):
        self.radius = radius
        self.strength = strength
        self.vectorRadiusDensity = self.initializeRadiusMatrix()

    def initializeRadiusMatrix(self):
        pixelx = -self.radius
        pixely = -self.radius
        vectorX = 1
        vectorY = 1

        vectorRadiusDensityX = np.zeros((2*self.radius+1, 2*self.radius+1))
        vectorRadiusDensityY = np.zeros((2*self.radius+1, 2*self.radius+1))
       
        for i in range(0, round((2*self.radius+1)**2)):
            distance = (pixelx**2 + pixely**2)**0.5
            if  pixelx < 0:
                vectorX = 1
            elif pixelx == 0:
                vectorX = 0
            else:
                vectorX = -1

            if pixely < 0:
                vectorY = 1
            elif pixely == 0:
                vectorY = 0
            else:
                vectorY = -1
            
            if distance <= self.radius:
                vectorRadiusDensityX[pixely+self.radius, pixelx+self.radius] += vectorX * self.strength  * (1 + 2*abs(pixely)/(2*self.radius)) * (1.0001 - (1.0001 - (distance/self.radius)**1)**21)
                vectorRadiusDensityY[pixely+self.radius, pixelx+self.radius] += vectorY * self.strength  * (1 + 2*abs(pixely)/(2*self.radius)) *(1.0001 - (1.0001 - (distance/self.radius)**1)**21)

            pixelx += 1
            if pixelx > self.radius:
                pixelx = -self.radius
                pixely += 1
            
            vectorRadiusDensity = np.stack([vectorRadiusDensityX, vectorRadiusDensityY], axis=2)

        return vectorRadiusDensity

    def updateVectorMatrix(self, px, py, vField, mouseRight):
        
        xmin, rxmin = (max(0, px-self.radius), max(0, self.radius-px))
        xmax, rxmax = (min(vField.vectorWidth, px+self.radius), min(2*self.radius, self.radius + vField.vectorWidth-px))
        ymin, rymin = (max(0, py-self.radius), max(0, self.radius-py))
        ymax, rymax = (min(vField.vectorHeight, py+self.radius), min(2*self.radius, self.radius + vField.vectorHeight-py))

        reverse = 1
        if mouseRight:
            reverse = -1
        
        vField.field[ymin:ymax, xmin:xmax, 0] += self.vectorRadiusDensity[rymin:rymax, rxmin:rxmax, 0] * reverse
        vField.field[ymin:ymax, xmin:xmax, 1] += self.vectorRadiusDensity[rymin:rymax, rxmin:rxmax, 1] * reverse

        return vField
 

def makeParticles(amnt, radius, color, background):
    px = round(background.width/2 - (round(amnt**0.5)*(radius*2+1))/2 + radius )
    py = round(background.height/2 - (round(amnt**0.5)*(radius*2+1))/2 + radius )
    
    particles = []
    for i in range(0, amnt):
        particles.append(particle(radius, px, py, color))
        px += radius*2+1

        if px > background.width/2 + (round(amnt**0.5)*(radius*2+1))/2:
            
            px = round(background.width/2 - (round(amnt**0.5)*(radius*2+1))/2 + radius)
            py += radius*2+1

    
    return particles


def main():

    sceneWidth = 500
    sceneHeight = 500

    g = 9.81*7
    dampingcoeff = 0.7
    densityVal = 5

    timeStep = 0.01

    particles = 500 
    particleColor = (0, 163, 108)
    particleR = 4
    vectorRadiusMultiplier = 12 

    smoothingR = 20

    background = window(sceneWidth, sceneHeight)
    particles = makeParticles(particles, particleR, particleColor, background)
    
    dField = densityField(sceneWidth, sceneHeight, smoothingR)
    vField = vectorField(sceneWidth, sceneHeight, vectorRadiusMultiplier)
    clickMouse = changeVectorField(100, 0.25)


    run = True
    animate = False
    drawParticles = True
    drawField = False
    drawPVelocity = True
    addTimeDelay = False
    useGravity = True
    useRandom = False
    useVField = True
    useDecel = True
    drawVField = False
    clickLeft = False
    clickRight = False
    addMore = False

    moreDelay = 0

    for p in particles:
        p.draw(background)
    
    background.updateScreen()

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
                if event.key == py.K_d:
                    drawField = not drawField
                if event.key == py.K_t:
                    addTimeDelay = not addTimeDelay
                if event.key == py.K_g:
                    useGravity = not useGravity
                if event.key == py.K_r:
                    useRandom = not useRandom
                if event.key == py.K_v:
                    drawVField = not drawVField
                if event.key == py.K_f:
                    useDecel = not useDecel
                if event.key == py.K_m:
                    addMore = not addMore
                if event.key == py.K_a:
                    drawPVelocity = not drawPVelocity
                    for p in particles:
                        p.color = particleColor

            if event.type == py.MOUSEBUTTONDOWN:
                if py.mouse.get_pressed()[0]:
                    clickLeft = True
                    clickRight = False
                elif py.mouse.get_pressed()[2]:
                    clickRight = True
                    clickLeft = False
            

            elif event.type == py.MOUSEBUTTONUP:
                clickLeft = False
                clickRight = False

        

        if animate:
            background.clear()
            dField.clearField()

            if addMore:
                if moreDelay == 0:
                    particles.append(particle(particleR, particleR+5, particleR+5, particleColor))
                    particles[-1].velocity[0] += 3

                    moreDelay = -1
                moreDelay += 1

            #=====
            for p in particles:
    
                dField.updateField(p)

            dField.normalizeField() 
            if drawField:
                dField.drawDensityField(background)
            #=====
            vField.updateVectorField(dField.field)
            if clickLeft or clickRight:
                mousepos = py.mouse.get_pos()
                vField.vectorField = clickMouse.updateVectorMatrix(mousepos[0], mousepos[1], vField, clickRight)

            if drawVField:
                vField.drawVectorField(background)
            #=====
            for p in particles:
                p.updateVelocity(g, dampingcoeff, timeStep, background, useGravity, useRandom, useDecel, densityVal, vField, dField)
                p.updatePosition(background)
                if drawPVelocity:
                    p.updateColor()
                if drawParticles:
                    p.draw(background)
            #=====
            if addTimeDelay:
                py.draw.rect(background.screen, (255, 0, 0), (0, 0, 24, 24))

            background.updateScreen()
            if addTimeDelay:

                time.sleep(timeStep)

main()




