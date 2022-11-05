#   File: main.py
#C

from pygame import *;
from game import *;
# from menu import *;
from new_menu import *;
from highs import *
import os;
import pickle

STATE_MENU = 1
STATE_GAME = 2
STATE_DEMO = 3
STATE_HIGH = 4
STATE_KILL = 5

Q_table = np.random.randn(50, 36, 36, 5) # Size = Distance to Inruder(50 pixels), Angle to Intruder(36 bins), Relative heading to intruder (36 bins), actions (5)
N_table = np.zeros((50, 36, 36, 5))
class Main:

    BG_COLOR = (0, 0, 0)

    def __init__(self):
        #Init the modules we need
        display.init()
        pygame.mixer.init()
        font.init()
        
        if(Config.GAME_FULLSCREEN == True):
            self.screen = display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = display.set_mode((1024, 768))
            
        display.set_caption('ATC Version 0.1')

        self.menu = Menu(self.screen)
        self.high = HighScore(self.screen)
        # Number of airplanes
        self.n_airplanes = Config.NUMBEROFAIRCRAFT
        self.learning_rate = None
        self.discount_factor = None
        self.exploration = None
        self.n_episodes = 0
        self.choice = None
        self.Q_table = None
        self.N_table = None

    def run(self):
        state = STATE_MENU ####
        exit = 0
        score = 0

        while (exit == 0):
            if (state == STATE_MENU):
                menuEndCode = None
                menuEndCode = self.menu.start()
                if menuEndCode == Config.CODE_KILL:
                    exit = 1
                    pygame.quit()
                    break
                # Getting all these values from user
                if self.menu.n_planes != '':
                    self.n_airplanes = int(self.menu.n_planes)
                if self.menu.n_spawn_points != '':
                    Config.NUMBEROFSPAWNPOINTS = int(self.menu.n_spawn_points)
                if self.menu.n_destinations != '':
                    Config.NUMBEROFDESTINATIONS = int(self.menu.n_destinations)
                if self.menu.n_obstacles != '':
                    Config.NUMBEROFOBSTACLES = int(self.menu.n_obstacles)
                self.learning_rate = float(self.menu.learning_rate)
                self.discount_factor = float(self.menu.discount_factor)
                self.exploration = float(self.menu.explration_probability)
                self.choice = int(self.menu.model)
                if self.menu.q == '':
                    self.Q_table = np.random.randn(50, 36, 36, 5)
                else:
                    with open(self.menu.q + '.pickle', 'rb') as f:
                        self.Q_table = pickle.load(f)
                if self.choice == 0:
                    self.N_table = np.zeros((50, 36, 36, 5))
                if (menuEndCode == Config.MENU_CODE_START):
                    state = STATE_GAME

            elif (state == STATE_GAME):
                game = Game(self.screen, False)
                (gameEndCode, score, Q_values_used) = game.start(n_episode = self.n_episodes, n_airplanes = self.n_airplanes, epsilon = self.exploration, Q_table = self.Q_table, N_table = self.N_table, choice = self.choice, alpha = self.learning_rate, gamma = self.discount_factor)
                # if (gameEndCode == Config.GAME_CODE_TIME_UP):
                #     state = STATE_GAME ###
                # elif (gameEndCode == Config.CODE_KILL):
                #     state = STATE_GAME ###
                # elif (gameEndCode == Config.GAME_CODE_USER_END):
                #     state = STATE_MENU
                #     self.menu.menuEnd = 0
                # elif (gameEndCode == Config.GAME_CODE_AC_COLLIDE):
                #     state = STATE_GAME ###1
                for value in Q_values_used:
                    self.Q_table[value] += score/len(Q_values_used)
                if gameEndCode == Config.GAME_CODE_USER_END:
                    if self.choice == 0:
                        with open('Q_table_e_greedy.pickle', 'wb') as f:
                            pickle.dump(Q_table, f)
                    else:
                        with open('Q_table_sarsa.pickle', 'wb') as f:
                            pickle.dump(Q_table, f)
                    state = STATE_MENU
                    self.menu.menuEnd = 0
                self.n_episodes += 1
                # if self.n_episodes < 15:
                #     if gameEndCode == Config.GAME_CODE_USER_END:
                #         state = STATE_MENU
                #         self.menu.menuEnd = 0
                    # else:
                    #     state = STATE_GAME
                    #     self.n_episodes += 1
                # else:
                #     if self.choice == 0:
                #         with open('Q_table_e_greedy.pickle', 'wb') as f:
                #             pickle.dump(Q_table, f)
                #     else:
                #         with open('Q_table_sarsa.pickle', 'wb') as f:
                #             pickle.dump(Q_table, f)
                #     state = STATE_MENU
                #     self.menu.menuEnd = 0

            
if __name__ == '__main__':
    game_main = Main()
    game_main.run()
