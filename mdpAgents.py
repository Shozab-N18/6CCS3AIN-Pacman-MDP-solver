# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.makeMap(state)
        self.addWallsToMap(state)
        self.updateFoodInMap(state)
        self.map.display()
        
        self.utilities = []
        for x in range(self.map.getWidth()):
            row = []
            for y in range(self.map.getHeight()):
                row.append(0)
            self.utilities.append(row)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

        # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        
    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')
    
    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    if self.map.getWidth() > 10:
                        self.map.setValue(i, j, 0)
                    else:
                        self.map.setValue(i, j, 0) # 0
        # Set Food and capsule utilities
        food = api.food(state)
        for i in range(len(food)):
            if self.map.getWidth() > 10:
                self.map.setValue(food[i][0], food[i][1], 10)
            else:
                self.map.setValue(food[i][0], food[i][1], 1) # 15
    
    def setCapsuleValues(self, state):
        capsules = api.capsules(state)
        
        for capsule in capsules:
            self.map.setValue(capsule[0], capsule[1], 20) #50

    def valueIteration(self, state, max_iterations=10000, similarity_threshold=0.000001):
        if self.map.getWidth() > 10:
            discount_factor = 0.5
        else:
            discount_factor = 0.9647
        for i in range(max_iterations):
            change = 0
            for x in range(self.map.getWidth()):
                for y in range(self.map.getHeight()):
                    if self.map.getValue(x, y) != '%':
                        old_utility = self.utilities[x][y]
                        new_utility = self.calculateUpdatedUtility(state, x, y, discount_factor)
                        
                        change = max(change, abs(old_utility - new_utility))
                        self.utilities[x][y] = new_utility
            if change < similarity_threshold:
                # print "Converged", change
                break
    
    def calculateUpdatedUtility(self, state, x, y, discount_factor):
        reward = self.map.getValue(x, y)
        return reward + discount_factor * self.getBestNeighbourUtility(state, x, y)
    
    def getBestNeighbourUtility(self, state, x, y):
        # Get actions, remove stop
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        best_expected_value = float('-inf')
        
        for move in legal:
            # (a) All the possible outcomes for the legal move due to non-determinism.
            possible_moves = [move]
            
            if move == Directions.NORTH:
                possible_moves.extend([Directions.EAST, Directions.WEST])
            elif move == Directions.SOUTH:
                possible_moves.extend([Directions.EAST, Directions.WEST])
            elif move == Directions.EAST:
                possible_moves.extend([Directions.NORTH, Directions.SOUTH])
            elif move == Directions.WEST:
                possible_moves.extend([Directions.NORTH, Directions.SOUTH])
            
            # (b) The probability of each outcome.
            move_probability = [api.directionProb]
            move_probability.extend([(1-api.directionProb)/2, (1-api.directionProb)/2])
            
            # (c) The utility of each outcome.
            outcome_values = []
            
            # Determine pacmans new position for each possible move and add the utility of that position.
            for action in possible_moves:
                new_x, new_y = x, y
                
                if action == Directions.NORTH:
                    new_y += 1
                elif action == Directions.EAST:
                    new_x += 1
                elif action == Directions.SOUTH:
                    new_y -= 1
                elif action == Directions.WEST:
                    new_x -= 1
                outcome_values.append(self.utilities[new_x][new_y])
            
            # 3. Calculate the expected value of the move.
            expected_value = 0
            for i in range(len(possible_moves)):
                if outcome_values[i] != '%':
                    expected_value += move_probability[i] * outcome_values[i]
                else:
                    expected_value += move_probability[i] * self.utilities[x][y]
            
            # 4. Choose the highest expected value
            
            if expected_value > best_expected_value:
                best_expected_value = expected_value
        return best_expected_value
    
    def getAuraCoordinates(self, x, y, radius):
        coordinates = []
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                coordinates.append((int(x + i), int(y + j)))
        return coordinates
    
    def setGhostAura(self, state):
        height, width = self.map.getHeight(), self.map.getWidth()
        
        if width > 10: 
            aura_radius = 1
        
        ghosts_list = api.ghostStatesWithTimes(state)
        
        for ghost in ghosts_list:
            ((ghost_x, ghost_y), ghost_state) = ghost
            aura_points = self.getAuraCoordinates(ghost_x, ghost_y, aura_radius)
            
            if ghost_state == 0: # Unedible
                for point in aura_points:
                    x, y = point
                    if width > x >= 0  and height > y >= 0 and self.map.getValue(x, y) != '%':
                        self.map.setValue(x, y, self.map.getValue(x,y) - 500)
            else: # Edible
                for point in aura_points:
                    x, y = point
                    if width > x >= 0  and height > y >= 0 and self.map.getValue(x, y) != '%':
                        self.map.setValue(x, y, self.map.getValue(x,y) + 500)
    
    def chaseEdibleGhost(self, state):
        ghosts = api.ghostStatesWithTimes(state)
        for ghost in ghosts:
            ((x,y), ghost_state) = ghost
            if ghost_state == 0: # Unedible
                value = -9000
            else: # Edible
                value = 0
                if ghost_state > 30:
                    value = 2000
                elif ghost_state > 20:
                    value = 1000
                elif ghost_state > 10:
                    value = 500
                else:
                    value = 100
            self.map.setValue(int(x), int(y), value)

    def getAction(self, state):
        self.updateFoodInMap(state)
        self.setCapsuleValues(state)
        self.chaseEdibleGhost(state)
        if self.map.getWidth() > 10:
            self.setGhostAura(state)
        self.map.prettyDisplay()
        self.valueIteration(state)
        
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        best_move = None
        best_expected_value = float('-inf')
        
        for move in legal:
            # (a) All the possible outcomes for the legal move due to non-determinism.
            possible_moves = [move]
            if move == Directions.NORTH:
                possible_moves.extend([Directions.EAST, Directions.WEST])
            elif move == Directions.SOUTH:
                possible_moves.extend([Directions.EAST, Directions.WEST])
            elif move == Directions.EAST:
                possible_moves.extend([Directions.NORTH, Directions.SOUTH])
            elif move == Directions.WEST:
                possible_moves.extend([Directions.NORTH, Directions.SOUTH])
            
            # (b) The probability of each outcome.
            move_probability = [api.directionProb]
            move_probability.extend([(1-api.directionProb)/2, (1-api.directionProb)/2])
            
            # (c) The utility of each outcome.
            outcome_values = []
            
            for action in possible_moves:
                x, y = api.whereAmI(state)
                
                if action == Directions.NORTH:
                    y += 1
                elif action == Directions.EAST:
                    x += 1
                elif action == Directions.SOUTH:
                    y -= 1
                elif action == Directions.WEST:
                    x -= 1
                outcome_values.append(self.utilities[x][y])
            
            # 3. Calculate the expected Value of the move
            expected_value = 0
            for i in range(len(possible_moves)):
                if outcome_values[i] != '%':
                    expected_value += move_probability[i] * outcome_values[i]
                else:
                    expected_value += move_probability[i] * self.utilities[x][y] 
            
            # 4. Choose the move with the highest expected value
            
            if expected_value > best_expected_value:
                best_expected_value = expected_value
                best_move = move
        return api.makeMove(best_move, legal)
