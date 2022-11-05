#   File: game.py
#   Description: An instance of one game of ATC
import pygame;
import numpy as np
import random;
import math;
import pygame;
from config import *;
from destination import *;
from aircraft import *;
from obstacle import *;
from aircraftspawnevent import *;
from utility import *;
from pgu import gui;
from flightstrippane import *;

class Game:

    SCREEN_W = 0                #Width of the screen
    SCREEN_H = 0                #Height of the screen

    AERIALPANE_W = 0            #Width of the aerial pane
    AERIALPANE_H = 0            #Height of the aerial pane

    FSPANE_LEFT = 0             #LHS of the flight strip pane (AERIALPANE_W + 3)
    FSPANE_TOP = 200            #Top of the flight strip pane

    FS_W = 0
    FS_H = 0

    RADAR_CIRC_COLOR = (0, 0x44, 0)
    RADAR_RADIUS = 0

    COLOR_SCORETIME = (20, 193, 236)    #Score/time counter colour

    

    def __init__(self, screen, demomode):
        #Screen vars
        Game.SCREEN_W = screen.get_size()[0]
        Game.SCREEN_H = screen.get_size()[1]
        Game.AERIALPANE_W = Game.SCREEN_H
        Game.AERIALPANE_H = Game.SCREEN_H
        Game.FSPANE_LEFT = Game.AERIALPANE_W + 3
        Game.FSPANE_H = Game.SCREEN_H - Game.FSPANE_TOP
        Game.FS_W = Game.SCREEN_W - Game.FSPANE_LEFT
        Game.FS_H = 60
        Game.RADAR_RADIUS = (Game.AERIALPANE_H - 50) / 2
        AircraftSpawnEvent.spawnpoint = Config.NUMBEROFSPAWNPOINTS
        #Imagey type stuff
        self.font = pygame.font.Font(None, 30)
        self.screen = screen
               
        #Aircraft/destination state vars
        self.demomode = demomode
        self.gameEndCode = 0
        self.ms_elapsed = 0
        self.score = 0
        self.aircraft = []
        self.obstacles = []
        self.destinations = []
        self.aircraftspawntimes = []
        self.aircraftspawns = []
        self.Q_table_values_used = []

        #UI vars
        self.ac_selected = None
        self.way_clicked = None

        # Double click
        self.last_click_time = None

        #Generations functions
        self.__generateDestinations()
        self.__generateObstacles()
        self.__generateAircraftSpawnEvents()

        self.app = gui.App()
        self.cnt_main = gui.Container(align=-1,valign=-1)
        
        if not self.demomode:
            self.btn_game_end = gui.Button(value="End Game", width=Game.FS_W-3, height=60)
            self.btn_game_end.connect(gui.CLICK, self.__callback_User_End)        
            self.cnt_main.add(self.btn_game_end, Game.FSPANE_LEFT, Game.FSPANE_TOP - 65)
        
        self.cnt_fspane = FlightStripPane(left=Game.FSPANE_LEFT, top=Game.FSPANE_TOP, width=Game.FS_W, align=-1, valign=-1)
        self.cnt_main.add(self.cnt_fspane, Game.FSPANE_LEFT, Game.FSPANE_TOP)

        self.app.init(self.cnt_main, self.screen)

    def start(self, n_episode, n_airplanes, epsilon, Q_table, N_table, choice, alpha, gamma):
        clock = pygame.time.Clock()
        #nextDemoEventTime = random.randint(10000,20000)
        nextDemoEventTime = 6000 # first demo event time is 6 seconds after start of demo
        randAC = None
        # Delta speed -- shouldn't be hardcoded...
        ds = 3

        #The main game loop
        while self.gameEndCode == 0:
            timepassed = clock.tick(Config.FRAMERATE)

            #Handle any UI stuff
            self.__handleUserInteraction()

            if (self.demomode and self.aircraft):
                if (self.ms_elapsed > nextDemoEventTime):
                    nextDemoEventTime += random.randint(10000,20000)
                    # Select an aircraft at random
                    randIndex = random.choice(range(0,len(self.aircraft)))
                    randAC = self.aircraft[randIndex]
                    randAC.requestSelected()
                elif (randAC):
                    # Ramp the current aircraft's speed up and down
                    if (randAC.getSpeed() < 110 or randAC.getSpeed() > 990):
                        ds *= -1 
                    randAC.setSpeed(randAC.getSpeed() + ds)

            
            #Draw background
            pygame.draw.rect(self.screen, (0, 0, 0), self.screen.get_rect())

            #Draw obstacles
            for x in self.obstacles:
                x.draw(self.screen)

            #Draw radar circles
            pygame.draw.circle(self.screen, Game.RADAR_CIRC_COLOR, (int(Game.AERIALPANE_W / 2), int(Game.AERIALPANE_H / 2)), int(Game.RADAR_RADIUS * 1/3), 1)
            pygame.draw.circle(self.screen, Game.RADAR_CIRC_COLOR, (int(Game.AERIALPANE_W / 2), int(Game.AERIALPANE_H / 2)), int(Game.RADAR_RADIUS * 2/3), 1)
            pygame.draw.circle(self.screen, Game.RADAR_CIRC_COLOR, (int(Game.AERIALPANE_W / 2), int(Game.AERIALPANE_H / 2)), int(Game.RADAR_RADIUS), 1)

            #Draw destinations
            for x in self.destinations:
                x.draw(self.screen)

            #Move/redraw/collide aircraft
            self.__update(n_airplanes, epsilon, Q_table, N_table, choice, alpha, gamma)
            self.__handleAircraftObstacleCollisions()

            #Draw black rect over RHS of screen, to occult bits of plane/obstacle that may be there
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect((Game.FSPANE_LEFT, 0), (Game.SCREEN_W - 1 - Game.FSPANE_LEFT, Game.FSPANE_TOP - 4)))
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect((Game.FSPANE_LEFT, Game.FSPANE_TOP), (Game.SCREEN_W - 1 - Game.FSPANE_LEFT, Game.SCREEN_H - Game.FSPANE_TOP)))
            pygame.draw.line(self.screen, (255, 255, 255), (Game.AERIALPANE_W + 1, 0), (Game.AERIALPANE_W + 1, Game.SCREEN_H), 3)
            pygame.draw.line(self.screen, (255, 255, 255), (Game.FSPANE_LEFT, Game.FSPANE_TOP - 2), (Game.SCREEN_W, Game.FSPANE_TOP - 2), 3)

            if self.demomode == False:
                #if self.score is negative cap it at 0.
                if self.score <= 0:
                    self.score = 0
                #Draw score/time indicators
                sf_score = self.font.render("Score: " + str(self.score), True, Game.COLOR_SCORETIME)
                sf_time = self.font.render("Time: " + str( math.floor((Config.GAMETIME - self.ms_elapsed) / 1000) ), True, Game.COLOR_SCORETIME)
                sf_episode = self.font.render("Episode : " + str( n_episode + 1 ), True, Game.COLOR_SCORETIME)

                self.screen.blit(sf_score, (Game.FSPANE_LEFT + 30, 10))
                self.screen.blit(sf_time, (Game.FSPANE_LEFT + 30, 40))
                self.screen.blit(sf_episode, (Game.FSPANE_LEFT + 30, 70))
            else:
                #if (self.ms_elapsed / 1000) % 2 == 0:
                    sf_demo = pygame.font.Font(None, 50).render("DEMO MODE!", True, (255, 100, 100))
                    self.screen.blit(sf_demo, (Game.FSPANE_LEFT + 15, 10))

                    mvmouse_demo = pygame.font.Font(None, 50).render("Move mouse!", True, (255, 100, 100))
                    self.screen.blit(mvmouse_demo, (Game.FSPANE_LEFT + 15, 50))
                    
            #Recalc time and check for game end
            self.ms_elapsed = self.ms_elapsed + timepassed
            if(self.ms_elapsed >= Config.GAMETIME and not self.demomode):
                self.gameEndCode = Config.GAME_CODE_TIME_UP
                
            #Flip the framebuffers
            self.app.repaint()
            self.app.update(self.screen)
            pygame.display.flip()

        #Game over, display game over message
        # self.__displayPostGameDialog()

        return (self.gameEndCode, self.score, self.Q_table_values_used)
        
    #Request a new selected aircraft
    def requestSelected(self, ac):
        self.ac_selected = ac
        # Deselect all aircraft first
        for a in self.aircraft:
            if(a != self.ac_selected):
                a.setSelected(False)
        # Then reselect the active aircraft 
        if(self.ac_selected != None):
            self.ac_selected.setSelected(True)
            
    def __update(self, n_airplanes, epsilon, Q_table, N_table, choice, alpha, gamma):

        #1: Update the positions of all existing aircraft
        #2: Check if any aircraft have collided with an obstacle
        #3: Check if any aircraft have reached a destination
        ac_removal = []

        for n in range(0, len(self.aircraft)):
            a = self.aircraft[n]

            #Update positions and redraw
            reachdest = a.update()
            if(reachdest == True):
                #Schedule aircraft for removal
                ac_removal.append(a)
                self.score += Config.SCORE_REACHDEST
            else:
                a.draw(self.screen)

            # #Check collisions
            # self.__highlightImpendingCollision(a, epsilon, Q_table, N_table)
            # for ac_t in self.aircraft:
            #     if(ac_t != a):
            #         self.__handleAircraftCollision(ac_t, a)

        for a in ac_removal:
            if(self.ac_selected == a):
                self.requestSelected(None)
            self.aircraft.remove(a)
            self.cnt_fspane.remove(a.getFS())

        for n in range(0, len(self.aircraft)):
            #Check collisions
            a = self.aircraft[n]
            self.__highlightImpendingCollision(a, epsilon, Q_table, N_table, choice, alpha, gamma)
            for ac_t in self.aircraft:
                if(ac_t != a):
                    self.__handleAircraftCollision(ac_t, a)
        #4: Spawn new aircraft due for spawning
        if(len(self.aircraftspawntimes) != 0 and len(self.aircraft) < n_airplanes): ### Change 2 to number of airplanes
            if self.ms_elapsed >= self.aircraftspawntimes[0]:
                sp = self.aircraftspawns[0]
                if(len(self.aircraft) < math.floor(Game.FSPANE_H / 60)):
                    ac = Aircraft(self, sp.getSpawnPoint(), Config.AC_SPEED_DEFAULT, sp.getDestination(), "BA" + str(random.randint(1, 100)))
                    self.aircraft.append(ac)
                    self.cnt_fspane.addNewFlightStrip(ac)
                self.aircraftspawns.remove(sp)
                self.aircraftspawntimes.remove(self.aircraftspawntimes[0])

    def __handleUserInteraction(self):

        for event in pygame.event.get():

            self.app.event(event)
            
            if self.demomode:
                if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.gameEndCode = Config.GAME_CODE_USER_END
                    return
            else:
                if(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
    			# MOUSEBUTTONDOWN event has members pos and button
                    if (self.last_click_time and pygame.time.get_ticks() -  self.last_click_time < 400):
                        dbl_click = True
                    else:
                        dbl_click = False
                    self.last_click_time = pygame.time.get_ticks()
    
                    clickedac = self.__getACClickedOn(event.pos)
                    if(clickedac != None):
                        #Clicked an aircraft
                        self.requestSelected(clickedac)
                    else:
                        if(self.ac_selected != None):
                            #Not clicked aircraft, check waypoints of currently selected ac
                            wclick = False
                            for x in range(0, len(self.ac_selected.getWaypoints()) - 1):
                                w = self.ac_selected.getWaypoints()[x]
                                if(w.clickedOn(event.pos) == True):
                                    if (dbl_click):
                                        # Use del list[index] instead?
                                        self.ac_selected.waypoints.remove(w)     
                                        wclick = True
                                        break
                                    else:
                                        self.way_clicked = w
                                        wclick = True
                            if wclick == False:
                                #Not clicked waypoint, check lines
                                way_added = False
                                # Still not very Pythonesque...
                                ac = self.ac_selected
                                listy = [ac.getLocation()]
                                listy = listy + list(map(Waypoint.getLocation,ac.getWaypoints()))
                                for x in range(0, len(listy)-1):
                                    currP = listy[x]
                                    nextP = listy[x+1]
                                    (intersect, dist) = Utility.getPointLineIntersect(currP, nextP, event.pos)
                                    if((intersect != None) and (dist <= 40)):
                                        newway = Waypoint(event.pos)
                                        self.ac_selected.addWaypoint(newway, x)
                                        self.way_clicked = newway
                                        way_added = True
                                        break
                                #TW Fix this as it is sh*t
                                if (way_added == False and 0 < event.pos[0] < Game.AERIALPANE_W ):
                                    self.requestSelected(None)
    
                elif(event.type == pygame.MOUSEBUTTONUP and event.button == 1):
    
                    if(self.way_clicked != None):
                        self.way_clicked = None
    
                elif(event.type == pygame.MOUSEMOTION):
    			# MOUSEMOTION event has members pos, rel and buttons
    
                    if(self.way_clicked != None):
                        if(event.pos[0] >= Game.AERIALPANE_W - 3):
                            self.way_clicked.setLocation((Game.AERIALPANE_W - 3, event.pos[1]))
                        else:
                            self.way_clicked.setLocation(event.pos)
    
                elif(event.type == pygame.KEYDOWN):    

                    if(event.key == pygame.K_ESCAPE):
                        self.gameEndCode = Config.GAME_CODE_USER_END
    
    def __callback_User_End(self):
        self.gameEndCode = Config.GAME_CODE_USER_END

    def __handleAircraftObstacleCollisions(self):
        for o in self.obstacles:
            newCollides = o.collideAircraft(self.aircraft)
            self.score += (newCollides * Config.SCORE_OBS_COLLIDE)

    def __handleAircraftCollision(self, ac1, ac2):
        if( Utility.locDistSq(ac1.getLocation(), ac2.getLocation()) < (Config.AC_COLLISION_RADIUS ** 2) ):
            if not self.demomode:
                self.gameEndCode = Config.GAME_CODE_AC_COLLIDE
            self.score += Config.SCORE_AC_COLLIDE
            # Highlight the collided aircraft
            ac1.image = Aircraft.AC_IMAGE_NEAR # later set to Aircraft.AC_IMAGE_COLLIDED
            ac2.image = Aircraft.AC_IMAGE_NEAR

    ## Collision
    def __highlightImpendingCollision(self, a, epsilon, Q_table, N_table, choice, alpha, gamma):
        for at in self.aircraft:
            # Skip current aircraft or currently selected aircraft (because it remains orange)
            if ((at != a) and (not a.selected)):
                if (Utility.locDistSq(a.getLocation(), at.getLocation()) < ((3 * Config.AC_COLLISION_RADIUS) ** 2) ):
                    #a.state = Aircraft.AC_STATE_NEAR
                    
                    a.image = Aircraft.AC_IMAGE_NEAR
                    if self.demomode == False:
                        sound = pygame.mixer.Sound("data/sounds/warning.ogg")
                        channel = sound.play()
                    #channel.set_volume(1, 1)
                    
                    
                    # 'a' is intruder 
                    distance_to_intruder = int(Utility.locDist(a.getLocation(), at.getLocation())/3)
                    (x0, y0) = at.getLocation()
                    (x1, y1) = a.getLocation()
                    (x1_w, y1_w) = a.waypoints[0].getLocation()
                    rho = self.getAngle(x0= x0, y0=y0, x1=x1, y1=y1)
                    theta = self.getAngle(x0= x1, y0=y1, x1=x1_w, y1=y1_w)
                    ##### Model here
                    if choice == 0:   # Epsilon Greedy
                        if np.random.rand() < epsilon:
                            action = np.random.randint(0, 5)
                        else:
                            action = np.argmax(Q_table[distance_to_intruder, rho, theta])
                        # radius = 200
                        reward = a.step(action, distance_to_intruder)
                        N_table[distance_to_intruder, rho, theta, action] += 1
                        Q_table[distance_to_intruder, rho, theta, action] = Q_table[distance_to_intruder, rho, theta, action] + 1/N_table[distance_to_intruder, rho, theta, action] * (reward - Q_table[distance_to_intruder, rho, theta, action])
                        self.Q_table_values_used.append([distance_to_intruder, rho, theta, action])
                    elif choice == 1:     # Sarsa
                        if np.random.rand() < epsilon:
                            action = np.random.randint(0, 5)
                        else:
                            action = np.argmax(Q_table[distance_to_intruder, rho, theta])
                        old_values = [distance_to_intruder, rho, theta, action]
                        reward = a.step(action, distance_to_intruder)
                        self.Q_table_values_used.append([distance_to_intruder, rho, theta, action])
                        new_location_a = a.NewLocation(a.location, a.heading, a.speed)
                        new_location_at = at.NewLocation(at.location, at.heading, at.speed)
                        (x1_w, y1_w) = a.waypoints[0].getLocation()
                        distance_to_intruder_prime = int(Utility.locDist(new_location_a, new_location_at)/3)
                        rho_prime = self.getAngle(x0= new_location_a[0], y0=new_location_a[1], x1=new_location_at[0], y1=new_location_at[1])
                        theta_prime = self.getAngle(x0= new_location_at[0], y0=new_location_at[1], x1=x1_w, y1=y1_w)
                        if np.random.rand() < epsilon:
                            action_prime = np.random.randint(0, 5)
                        else:
                            action_prime = np.argmax(Q_table[distance_to_intruder_prime, rho_prime, theta_prime])
                        Q_table[old_values] = Q_table[old_values] + alpha * (reward + gamma * Q_table[distance_to_intruder_prime, rho_prime, theta_prime, action_prime] - Q_table[old_values])
                    break
                else:
                    if (a.selected):
                        a.image = Aircraft.AC_IMAGE_SELECTED
                    else:
                        a.image = Aircraft.AC_IMAGE_NORMAL

    def __getACClickedOn(self, clickpos):
        foundac = None
        mindistsq = 100
        for i in range(0, len(self.aircraft)):
            ac = self.aircraft[i]
            distsq = ac.getClickDistanceSq(clickpos)
            if( distsq < mindistsq ):
                foundac = ac
                mindistsq = distsq
        return foundac

    def __generateAircraftSpawnEvents(self):
        (self.aircraftspawntimes, self.aircraftspawns) = AircraftSpawnEvent.generateGameSpawnEvents(Game.AERIALPANE_W, Game.AERIALPANE_H, self.destinations, Config.NUMBEROFSPAWNPOINTS)
        while self.__areSpawnEventsTooClose(self.aircraftspawntimes, self.aircraftspawns) == True and Config.NUMBEROFSPAWNPOINTS > 1:
            (self.aicraftspawntime, self.aircraftspawns) = AircraftSpawnEvent.generateGameSpawnEvents(Game.AERIALPANE_W, Game.AERIALPANE_H, self.destinations, Config.NUMBEROFSPAWNPOINTS)

    def __areSpawnEventsTooClose(self, times, spawns):
        ret = False
        if len(times) == len(spawns):
            x = 0
            y = 0
            brk = False
            while x < len(spawns) and (brk == False):
                while y < len(spawns) and (brk == False):
                    if(x != y):
                        dist = Utility.locDistSq(spawns[x].getSpawnPoint(), spawns[y].getSpawnPoint())
                        dt = math.fabs(times[x] - times[y])
                        if ((dist < 25 ** 2) and (dt < 6000)):
                            ret = True;
                            brk = True;
                    y += 1
                x += 1
        else:
            ret = True
        return ret
                        

    def __generateDestinations(self):
        self.destinations = Destination.generateGameDestinations(Game.AERIALPANE_W, Game.AERIALPANE_H)

    def getAngle(self, x0, y0, x1, y1):
        if x1 - x0 > 0:
            angle = 270 + np.arctan((y1 - y0)/(x1 - x0))*180/np.pi
            if y1 - y0 == 0:
                angle = 270
        elif x1 - x0 < 0:
            angle = 90 + np.arctan((y1 - y0)/(x1 - x0))*180/np.pi
            if y1 - y0 == 0:
                angle = 90
        else:
            if y1 - y0 > 0:
                angle = 0
            else:
                angle = 180
        return int(angle/36)

    def __generateObstacles(self):
        self.obstacles = Obstacle.generateGameObstacles(Game.AERIALPANE_W, Game.AERIALPANE_H, self.destinations)

    # def __displayPostGameDialog(self):
        #Do post-loop actions (game over dialogs)
        # if(self.gameEndCode != Config.GAME_CODE_USER_END and self.gameEndCode != Config.CODE_KILL):
        #     l = gui.Label("Game Over!")
        #     b = gui.Button("OK")
           
        #     # Not nice... but one way of passing by reference!
        #     # A list is a mutable object, while an int isn't -- that's why I'm using a list
        #     # Wait for Python 3 to allow assigning non-global variable in outer scope (keyword: nonlocal)
        #     bob = [False]
        #     def okcb(b):
        #         b[0] = True 

        #     b.connect(gui.CLICK,okcb,bob)
        #     c = gui.Container()


        #     if(self.gameEndCode == Config.GAME_CODE_AC_COLLIDE):
        #         # load a sound file into memory
        #         sound = pygame.mixer.Sound("data/sounds/boom.wav")
        #         channel = sound.play()
        #         channel.set_volume(2, 2)
        #         c.add(gui.Label("COLLISION!!!!"), 0, 0)
        #     elif(self.gameEndCode == Config.GAME_CODE_TIME_UP):
        #         c.add(gui.Label("Time up!"), 0, 0)

        #     c.add(b,0,30)

        #     d = gui.Dialog(l, c)
        #     d.open()
            # self.app.update(self.screen)
            # pygame.display.flip()
        #     #pygame.time.delay(3000)
        #     clock = pygame.time.Clock()
        #     while(not bob[0]):
        #         timepassed = clock.tick(Config.FRAMERATE)
        #         for e in pygame.event.get():
        #             self.app.event(e)
        #         self.app.repaint()
        #         self.app.update(self.screen)
        #         pygame.display.flip()


