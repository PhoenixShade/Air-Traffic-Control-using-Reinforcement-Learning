# File: new_menu.py
# Description : An instance of new menu

import pygame
import os
import sys
import math
from config import *

pygame.font.init()

RED = (255, 0, 0)
MAGENTA = (255, 56, 156)
ORANGE = (240, 240, 0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLU = (83,190,255)
WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (127, 127, 127)
LGRAY = (200, 200, 200)
DGRAY = (55, 55, 55)

def texty(name, size):
    matched = pygame.font.match_font('verdana, airal')
    Texty = pygame.font.Font(matched, size)
    return Texty

class Menu :
    AIRPLANE_W = 795
    AIRPLANE_H = 768
    STRIPPANE_TOP = 152
    STRIPPANE_H = 44

    def __init__(self, screen):
        self.SCREEN_W = screen.get_size()[0]
        self.SCREEN_H = screen.get_size()[1]

        # Imagey type stuff
        self.font = pygame.font.Font(None, 30)
        self.screen = screen
        self.menuEnd = 0
        self.selection = 0
        self.timeWithoutUIEvent = 0

        #Number of planes
        self.n_planes = ''
        self.n_spawn_points = ''
        self.n_destinations = ''
        self.n_obstacles = ''
        self.learning_rate = ''
        self.discount_factor = ''
        self.explration_probability = ''
        self.model = ''
        self.q = ''

        self.active = {
            'n_planes' : False,
            'n_spawn_points' : False,
            'n_destinations' : False,
            'n_obstacles' : False,
            'learning_rate' : False,
            'discount_factor' : False,
            'exploration' : False,
            'model' : False,
            'q_table' : False,
            'start_game' : False,
            'end_game' : False
            }
        
    
    def __mouseMenuOver(self, pos):
        if ((self.SCREEN_W - 150 < pos[0] < self.SCREEN_W - 50) and (self.SCREEN_H - 100 < pos[1] < self.SCREEN_H - 50)):
            return 0
        elif ((50 < pos[0] < 200) and (self.SCREEN_H - 100 < pos[1] < self.SCREEN_H - 50)):
            return 1
        else:
            return -1
    
    def start(self):
        valid_num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        Texty = texty(None, 20)
        Bigtex = texty(None, 60) # Large text
        selection = 0
        shift = 50
        n_planes_name = Texty.render("Number of Planes : ", 0, WHITE)
        n_spawn_points_name = Texty.render("Number of Spawn Points : ", 0, WHITE)
        n_destinations_name = Texty.render("Number of Destinations : ", 0, WHITE)
        n_obstacles_name = Texty.render("Number of Obstacles : ", 0, WHITE)
        learning_rate_name = Texty.render("Learning Rate : ", 0, WHITE)
        discount_factor_name = Texty.render("Discount Factor : ", 0, WHITE)
        exploration_name = Texty.render("Exploration Probability : ", 0, WHITE)
        model_name = Texty.render("Epsilon Greedy(0)/ Sarsa(1) : ", 0, WHITE)
        q_name = Texty.render("Q_table : ", 0, WHITE)
        n_planes_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 0*shift, 150, 34)
        n_spawn_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 1*shift, 150, 34)
        n_destinations_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 2*shift, 150, 34)
        n_obstacles_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 3*shift, 150, 34)
        learning_rate_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 4*shift, 150, 34)
        discount_factor_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 5*shift, 150, 34)
        exploration_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 6*shift, 150, 34)
        model_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 7*shift, 150, 34)
        q_rect = pygame.Rect(4*self.SCREEN_W//8, self.SCREEN_H//8 + 8*shift, 150, 34)
        start_game_rect = pygame.Rect(self.SCREEN_W - 150, self.SCREEN_H - 100 , 100, 50)
        end_game_rect = pygame.Rect(50, self.SCREEN_H - 100 , 150, 50)
        color_active = pygame.Color('lightskyblue3')
        color_passive = pygame.Color('gray15')
        color = {
            'n_planes' : color_passive,
            'n_spawn_points' : color_passive,
            'n_destinations' : color_passive,
            'n_obstacles' : color_passive,
            'learning_rate' : color_passive,
            'discount_factor' : color_passive,
            'exploration' : color_passive,
            'model' : color_passive,
            'q_table' : color_passive,
            'start_game' : color_passive,
            'end_game' : color_passive
            }
        while self.menuEnd == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.__mouseMenuOver(pygame.mouse.get_pos()) == 0:
                    self.active['start_game'] = True
                else:
                    self.active['start_game'] = False

                if self.__mouseMenuOver(pygame.mouse.get_pos()) == 1:
                    self.active['end_game'] = True
                else:
                    self.active['end_game'] = False
                
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if n_planes_rect.collidepoint(event.pos):
                        self.active['n_planes'] = True
                    else:
                        self.active['n_planes'] = False
                    
                    if n_spawn_rect.collidepoint(event.pos):
                        self.active['n_spawn_points'] = True
                    else:
                        self.active['n_spawn_points'] = False
                    
                    if n_destinations_rect.collidepoint(event.pos):
                        self.active['n_destinations'] = True
                    else:
                        self.active['n_destinations'] = False
                    
                    if n_obstacles_rect.collidepoint(event.pos):
                        self.active['n_obstacles'] = True
                    else:
                        self.active['n_obstacles'] = False
                    
                    if learning_rate_rect.collidepoint(event.pos):
                        self.active['learning_rate'] = True
                    else:
                        self.active['learning_rate'] = False
                    
                    if discount_factor_rect.collidepoint(event.pos):
                        self.active['discount_factor'] = True
                    else:
                        self.active['discount_factor'] = False
                    
                    if exploration_rect.collidepoint(event.pos):
                        self.active['exploration'] = True
                    else:
                        self.active['exploration'] = False

                    if model_rect.collidepoint(event.pos):
                        self.active['model'] = True
                    else:
                        self.active['model'] = False

                    if q_rect.collidepoint(event.pos):
                        self.active['q_table'] = True
                    else:
                        self.active['q_table'] = False
                                        
                    if start_game_rect.collidepoint(event.pos):
                        self.active['start_game'] = True
                        self.menuEnd = Config.MENU_CODE_START
                    else:
                        self.active['start_game'] = False

                    if end_game_rect.collidepoint(event.pos):
                        self.active['end_game'] = True
                        self.menuEnd = Config.CODE_KILL
                    else:
                        self.active['end_game'] = False
                
                if event.type == pygame.KEYDOWN:
                    if self.active['n_planes']:
                        if event.key == pygame.K_BACKSPACE:
                            self.n_planes = self.n_planes[:-1]
                        else:
                            t = event.unicode 
                            if t in valid_num:
                                self.n_planes += t
                    
                    if self.active['n_spawn_points']:
                        if event.key == pygame.K_BACKSPACE:
                            self.n_spawn_points = self.n_spawn_points[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num:
                                self.n_spawn_points += t

                    if self.active['n_destinations']:
                        if event.key == pygame.K_BACKSPACE:
                            self.n_destinations = self.n_destinations[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num:
                                self.n_destinations += t

                    if self.active['n_obstacles']:
                        if event.key == pygame.K_BACKSPACE:
                            self.n_obstacles = self.n_obstacles[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num:
                                self.n_obstacles += t

                    if self.active['learning_rate']:
                        if event.key == pygame.K_BACKSPACE:
                            self.learning_rate = self.learning_rate[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num + ['.']:
                                self.learning_rate += t

                    if self.active['discount_factor']:
                        if event.key == pygame.K_BACKSPACE:
                            self.discount_factor = self.discount_factor[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num + ['.']:
                                self.discount_factor += t
                    
                    if self.active['exploration']:
                        if event.key == pygame.K_BACKSPACE:
                            self.explration_probability = self.explration_probability[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num + ['.']:
                                self.explration_probability += t

                    if self.active['model']:
                        if event.key == pygame.K_BACKSPACE:
                            self.model = self.model[:-1]
                        else:
                            t = event.unicode
                            if t in valid_num:
                                self.model += t
                    
                    if self.active['q_table']:
                        if event.key == pygame.K_BACKSPACE:
                            self.q = self.q[:-1]
                        else:
                            self.q += event.unicode
                    
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.menuEnd = Config.MENU_CODE_START
            
            self.screen.fill((0,0,0))

            # Setting Color
            if self.active['n_planes']:
                color['n_planes'] = color_active
            else:
                color['n_planes'] = color_passive
            
            if self.active['n_spawn_points']:
                color['n_spawn_points'] = color_active
            else:
                color['n_spawn_points'] = color_passive
            
            if self.active['n_destinations']:
                color['n_destinations'] = color_active
            else:
                color['n_destinations'] = color_passive
            
            if self.active['n_obstacles']:
                color['n_obstacles'] = color_active
            else:
                color['n_obstacles'] = color_passive
            
            if self.active['learning_rate']:
                color['learning_rate'] = color_active
            else:
                color['learning_rate'] = color_passive
            
            if self.active['discount_factor']:
                color['discount_factor'] = color_active
            else:
                color['discount_factor'] = color_passive
            
            if self.active['exploration']:
                color['exploration'] = color_active
            else:
                color['exploration'] = color_passive

            if self.active['model']:
                color['model'] = color_active
            else:
                color['model'] = color_passive
            
            if self.active['q_table']:
                color['q_table'] = color_active
            else:
                color['q_table'] = color_passive

            if self.active['start_game']:
                color['start_game'] = color_active
            else:
                color['start_game'] = color_passive

            if self.active['end_game']:
                color['end_game'] = color_active
            else:
                color['end_game'] = color_passive

            # Drawing Input Field
            pygame.draw.rect(self.screen, color['n_planes'], n_planes_rect, 2)
            pygame.draw.rect(self.screen, color['n_spawn_points'], n_spawn_rect, 2)
            pygame.draw.rect(self.screen, color['n_destinations'], n_destinations_rect, 2)
            pygame.draw.rect(self.screen, color['n_obstacles'], n_obstacles_rect, 2)
            pygame.draw.rect(self.screen, color['learning_rate'], learning_rate_rect, 2)
            pygame.draw.rect(self.screen, color['discount_factor'], discount_factor_rect, 2)
            pygame.draw.rect(self.screen, color['exploration'], exploration_rect, 2)
            pygame.draw.rect(self.screen, color['model'], model_rect, 2)
            pygame.draw.rect(self.screen, color['q_table'], q_rect, 2)
            pygame.draw.rect(self.screen, color['start_game'], start_game_rect)
            pygame.draw.rect(self.screen, color['end_game'], end_game_rect)

            # Writing text in input field
            n_planes_text = Texty.render(self.n_planes,True, (255,255,255))
            n_spawn_points_text = Texty.render(self.n_spawn_points,True, (255,255,255))
            n_destinations_text = Texty.render(self.n_destinations,True, (255,255,255))
            n_obstacles_text = Texty.render(self.n_obstacles,True, (255,255,255))
            learning_rate_text = Texty.render(self.learning_rate,True, (255,255,255))
            discount_factor_text = Texty.render(self.discount_factor,True, (255,255,255))
            exploration_text = Texty.render(self.explration_probability,True, (255,255,255))
            model_text = Texty.render(self.model,True, (255,255,255))
            q_text = Texty.render(self.q,True, (255,255,255))
            start_game_text = Texty.render("START",True, (255,255,255))
            end_game_text = Texty.render("END GAME",True, (255,255,255))

            n_planes_rect.w = max(n_planes_text.get_width() + 10, n_planes_rect.w)
            n_spawn_rect.w = max(n_spawn_points_text.get_width() + 10, n_spawn_rect.w)
            n_destinations_rect.w = max(n_destinations_text.get_width() + 10, n_destinations_rect.w)
            n_obstacles_rect.w = max(n_obstacles_text.get_width() + 10, n_obstacles_rect.w)
            learning_rate_rect.w = max(learning_rate_text.get_width() + 10, learning_rate_rect.w)
            discount_factor_rect.w = max(discount_factor_text.get_width() + 10, discount_factor_rect.w)
            exploration_rect.w = max(exploration_text.get_width() + 10, exploration_rect.w)
            model_rect.w = max(model_text.get_width() + 10, model_rect.w)
            q_rect.w = max(q_text.get_width() + 10, q_rect.w)
            name_shift = 300
            # Printing it all on screen

            # Index
            self.screen.blit(n_planes_name, (n_planes_rect.x - name_shift, n_planes_rect.y))
            self.screen.blit(n_spawn_points_name, (n_spawn_rect.x -name_shift, n_spawn_rect.y))
            self.screen.blit(n_destinations_name, (n_destinations_rect.x -name_shift, n_destinations_rect.y))
            self.screen.blit(n_obstacles_name, (n_obstacles_rect.x -name_shift, n_obstacles_rect.y))
            self.screen.blit(learning_rate_name, (learning_rate_rect.x -name_shift, learning_rate_rect.y))
            self.screen.blit(discount_factor_name, (discount_factor_rect.x -name_shift, discount_factor_rect.y))
            self.screen.blit(exploration_name, (exploration_rect.x -name_shift, exploration_rect.y))
            self.screen.blit(model_name, (model_rect.x -name_shift, model_rect.y))
            self.screen.blit(q_name, (q_rect.x -name_shift, q_rect.y))

            # Text inside
            self.screen.blit(n_planes_text, (n_planes_rect.x + 5, n_planes_rect.y + 2))
            self.screen.blit(n_spawn_points_text, (n_spawn_rect.x + 5, n_spawn_rect.y + 2))
            self.screen.blit(n_destinations_text, (n_destinations_rect.x + 5, n_destinations_rect.y + 2))
            self.screen.blit(n_obstacles_text, (n_obstacles_rect.x + 5, n_obstacles_rect.y + 2))
            self.screen.blit(learning_rate_text, (learning_rate_rect.x + 5, learning_rate_rect.y + 2))
            self.screen.blit(discount_factor_text, (discount_factor_rect.x + 5, discount_factor_rect.y + 2))
            self.screen.blit(exploration_text, (exploration_rect.x + 5, exploration_rect.y + 2))
            self.screen.blit(model_text, (model_rect.x + 5, model_rect.y + 2))
            self.screen.blit(q_text, (q_rect.x + 5, q_rect.y + 2))
            self.screen.blit(start_game_text, (start_game_rect.x + 15, start_game_rect.y + 10))
            self.screen.blit(end_game_text, (end_game_rect.x + 15, end_game_rect.y + 10))

            # Reloading Screen
            pygame.display.flip()
        return self.menuEnd
