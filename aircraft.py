#   File: aircraft.py

import math;
import pygame;
import os;
import string;
from config import *;
from waypoint import *;
from utility import *;
from game import *;
import numpy as np

class Aircraft:

    AC_IMAGE_NORMAL = pygame.image.load(os.path.join('data', 'aircraft.png'))
    AC_IMAGE_SELECTED = pygame.image.load(os.path.join('data', 'aircraft_sel.png'))
    AC_IMAGE_NEAR = pygame.image.load(os.path.join('data', 'aircraft_near.png'))

    AC_STATE_NORMAL = 1
    AC_STATE_SELECTED = 2
    AC_STATE_NEAR = 3

    EVENT_CLICK_AC = 0
    EVENT_CLICK_FS = 1
    
    FS_FONTSIZE = 18

	#Constructor!
    def __init__(self, game, location, speed, destination, ident):

        self.game = game

        #Game state vars
        self.location = location
        self.speed = speed
        self.altitude = 24000 # hardwired for now; measured in ft
        self.waypoints = []
        self.collisionRisk = []
        self.waypoints.append(destination)
        self.ident = ident
        self.selected = False
        self.state = Aircraft.AC_STATE_NORMAL
        self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())

        Aircraft.AC_IMAGE_NORMAL.convert_alpha()
        Aircraft.AC_IMAGE_SELECTED.convert_alpha()

        #Image/font vars
        self.image = Aircraft.AC_IMAGE_NORMAL
        self.font = pygame.font.Font(None, Aircraft.FS_FONTSIZE)
        self.fs_font_color = (255, 255, 255)

	#Add a new waypoint in the specified index in the list
    def addWaypoint(self, waypoint, index=0):
        if(len(self.waypoints) < Config.MAX_WAYPOINTS + 1):
            self.waypoints.insert(index, waypoint)
            self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())

	#Get the specified waypoint from the list
    def getWaypoint(self, index):
        return self.waypoints[index]
    
    def getWaypoints(self):
        return self.waypoints

    #Return current location
    def getLocation(self):
        return self.location

    #Return current heading
    def getHeading(self):
        ret = 0
        if self.heading < 0:
            ret = 360 + self.heading
        else:
            ret = self.heading
        return ret
        
    def getHeadingStr(self):
        hdg = self.getHeading()
        hdg_str = format(hdg, ">03")
        return hdg_str
        
    def getIdent(self):
        return self.ident

    def getSpeed(self):
        return self.speed

	#Set speed in pixels per frame
    def setSpeed(self, newspeed):
        self.speed = newspeed

    #Set whether I am the selected aircraft or not
    def setSelected(self, selected):
        self.selected = selected
        if(selected == True):
            self.image = Aircraft.AC_IMAGE_SELECTED
            self.fs.select()
        else:
            self.image = Aircraft.AC_IMAGE_NORMAL
            self.fs.deselect()
            
    def requestSelected(self):
        self.game.requestSelected(self)

	#Draw myself on the screen at my current position and heading
    def draw(self, surface):
        rot_image = pygame.transform.rotate(self.image, -self.heading)
        rect = rot_image.get_rect()
        rect.center = self.location
        surface.blit(rot_image, rect)

        if(Config.AC_DRAW_COLLISION_RADIUS == True):
            pygame.draw.circle(surface, (255, 255, 0), self.location, Config.AC_COLLISION_RADIUS, 1)

        #Draw lines and waypoints if selected
        if(self.selected == True):
            point_list = []
            point_list.append(self.location)
            for x in range(0, len(self.waypoints)-1):
                point_list.append(self.waypoints[x].getLocation())
                self.waypoints[x].draw(surface)
            point_list.append(self.waypoints[-1].getLocation())
            pygame.draw.aalines(surface, (255, 255, 0), False, point_list)

		# Draw the ident string next to the aircraft?
        x = self.location[0] + 20
        y = self.location[1]
        list = [self.ident, "FL" + str(self.altitude/100), str(self.speed) + "kts"]
        for line in list:
            id = self.font.render(line, False, self.fs_font_color)
            r = surface.blit(id, (x,y))
            y = y + self.font.get_height()

	#Location/heading update function
    def update(self):
        # print(self.waypoints)
        if(self.__reachedWaypoint(self.location, self.waypoints[0].getLocation())):
            #Reached next waypoint, pop it
            self.waypoints.pop(0)
            if( len(self.waypoints) == 0):
                #Reached destination, return True
                return True
		
		#Keep moving towards waypoint
        self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())
        self.location = self.__calculateNewLocation(self.location, self.heading, self.speed)
        self.fs.updateAllFields()

    def getClickDistanceSq(self, clickpos):
        return Utility.locDistSq(clickpos, self.location)
        
    def setFS(self, fs):
        self.fs = fs
        
    def getFS(self):
        return self.fs

	#Calculate heading based on current position and waypoint
    def __calculateHeading(self, location, waypoint):
        x_diff = waypoint[0] - location[0]
        y_diff = waypoint[1] - location[1]
		# Heading measured in degrees relative to North direction
        heading = math.degrees(math.atan2(y_diff, x_diff) + (math.pi / 2))
        return heading

	#Calculate new location based on current location, heading and speed
    def __calculateNewLocation(self, location, heading, speed):
        x_diff = (speed / Config.AC_SPEED_SCALEFACTOR) * math.sin(math.radians(heading))
        y_diff = -(speed / Config.AC_SPEED_SCALEFACTOR) * math.cos(math.radians(heading))
        location = (location[0] + x_diff, location[1] + y_diff)
        return location

    def NewLocation(self, location, heading, speed):
        x_diff = (speed / Config.AC_SPEED_SCALEFACTOR) * math.sin(math.radians(heading))
        y_diff = -(speed / Config.AC_SPEED_SCALEFACTOR) * math.cos(math.radians(heading))
        location = (location[0] + x_diff, location[1] + y_diff)
        return location

	#Check whether I have reached the given waypoint
    def __reachedWaypoint(self, location, waypoint):
        if Utility.locDistSq(location, waypoint) < ((self.speed/Config.AC_SPEED_SCALEFACTOR) ** 2):
            return True
        else:
            return False

    def click(self, clickpos):
        if(Utility.locDistSq(clickpos, self.location) <= 100):
            return True
        else:
            return False

    def step(self, action, distance_to_intruder):
        radius = 50
        (x, y) = self.getLocation()
        distance_to_waypoint = Utility.locDist(self.getLocation(), self.waypoints[0].getLocation())
        # print(f'Radius : {radius}')
        if distance_to_waypoint - radius < 5 and len(self.waypoints) > 1:
            if action == 1: # Hard Left
                location = (x + radius * np.cos(90 + 2*36*np.pi/180), y + radius * np.sin(90 + 2*36*np.pi/180))
                self.waypoints[0].setLocation(location)
                self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())
            elif action == 2: # Medium Left
                location = (x + radius * np.cos(90 + 36*np.pi/180), y + radius * np.sin(90 + 36*np.pi/180))
                self.waypoints[0].setLocation(location)
                self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())
            elif action == 3: # Medium Right
                location = (x + radius * np.cos(90 - 36*np.pi/180), y + radius * np.sin(90 - 36*np.pi/180))
                self.waypoints[0].setLocation(location)
                self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())
            elif action == 4: # Hard Right
                location = (x + radius * np.cos(90 - 2*36*np.pi/180), y + radius * np.sin(90 - 2*36*np.pi/180))
                self.waypoints[0].setLocation(location)
                self.heading = self.__calculateHeading(self.location, self.waypoints[0].getLocation())
        else:
            if action == 1: # Hard Left
                location = (x + radius * np.cos(90 + 2*36*np.pi/180), y + radius * np.sin(90 + 2*36*np.pi/180))
                waypoint = Waypoint(location)
                self.addWaypoint(waypoint)
            elif action == 2: # Medium Left
                location = (x + radius * np.cos(90 + 36*np.pi/180), y + radius * np.sin(90 + 36*np.pi/180))
                waypoint = Waypoint(location)
                self.addWaypoint(waypoint)
            elif action == 3: # Medium Right
                location = (x + radius * np.cos(90 - 36*np.pi/180), y + radius * np.sin(90 - 36*np.pi/180))
                waypoint = Waypoint(location)
                self.addWaypoint(waypoint)
            elif action == 4: # Hard Right
                location = (x + radius * np.cos(90 - 2*36*np.pi/180), y + radius * np.sin(90 - 2*36*np.pi/180))
                waypoint = Waypoint(location)
                self.addWaypoint(waypoint)
        intruder_reward = - (radius**2 - distance_to_intruder**2)/(radius**2/500)
        distance_reward = 100 - self.distanceToGo()
        return intruder_reward + distance_reward

    def distanceToGo(self):
        distance = Utility.locDist(self.getLocation(), self.waypoints[0].getLocation())
        for i in range(1, len(self.waypoints)):
            distance += Utility.locDist(self.waypoints[i - 1].getLocation(), self.waypoints[i].getLocation())
        return distance
        
