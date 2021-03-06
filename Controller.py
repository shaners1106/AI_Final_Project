# Stephen Haugland and Shane Snediker
# Artificial Intelligence Spring 2020
# This file links our agent with our graphical grid
# Controller also contains the main program loop

import Agent        # import user defined agent class to represent maze navigating agents
import Maze         # import user defined Maze class to represent the environment
import Population   # import user defined Population Class
import pygame       # import pygame library to display graphics
import copy         # import the copy library used for making deep copies of variables
import os           # Allows us to control where the maze window pops up on the screen

# Define our maze colors
BLACK = (0, 0, 0)          # Background color
RED = (255, 0, 0)          # Maze obstacle colors
WHITE = (255, 255, 255)    # Agent test color
BLUE = (50, 50, 255)       # Agent test color
TEAL = (0, 128, 128)       # Stat counters

# I'd like to control the positioning of the screen - like where it pops up on the computer screen
x_win_loc = 100     # Represents the x coordinate of the upper left corner of the pop up window
y_win_loc = 50      # Represents the y coordinate of the upper left corner of the pop up window
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (x_win_loc, y_win_loc)  # Tell the window where to pop up 

# global variables that control the time clock and the drawable screen
clock = None
screen = None

# Function that initializes pygame object which allows us to draw a maze to the screen
# Parameter:  maze: a maze object containing the graphical maze data
def pygame_setup(maze):
    # Initialize the pygame library that facilitates the graphical maze
    pygame.init()
    # create a screen to draw the maze on
    global screen
    screen = pygame.display.set_mode([maze.MAZE_SIZE[0], maze.MAZE_SIZE[1] + 100])
    # Set title of screen
    pygame.display.set_caption("Artificial Intelligence Final Project Spring 2020")
    # Declaration of a clock variable that utilizes a clock function
    # from the pygame library that mediates the speed of the screen updates
    global clock
    clock = pygame.time.Clock()
    # Set the screen background
    screen.fill(BLACK)

# Function that paints our graphical maze to the screen
# Parameter:  maze: a maze object containing the graphical maze data
def draw_maze(maze): 
    # Draw the maze one time before entering the game loop
    # For every one of the 41 rows in the grid
    for row in range(41):
        # And every one of the 70 columns as well              
        for column in range(70):
            # Let's make the background black
            color = BLACK
            # Now we iterate through our 2 dimensional array and print obstacle locations in red              
            if maze.MAZE_GRID[row][column] == 1:
                color = BLUE
            # The pygame draw.rect function takes 3 primary arguments:
            # The first argument is the surface on which the rectangle will be drawn
            # The second is the desired color of the rectangle
            # The third is a list/tuple with the following values in this order:
            # x coordinate, y coordinate, width of rectangle, Height of rectangle, and the thickness of the rectangle lines
            # If no argument is given for the thickness parameter (like in our case), then the default is to fill the rectangle with the color argument
            pygame.draw.rect(screen,
                             color,
                             # x coordinate is the product of the cell width and the current column 
                             [maze.CELL_SIZE * column,   
                             # y coordinate is the product of the cell height and the current row     
                             maze.CELL_SIZE * row,     
                             # rectangle width
                             maze.CELL_SIZE,             
                             # rectangle height
                             maze.CELL_SIZE])
    # Update the screen with what has been drawn
    pygame.display.update()        

# Function to move every agent in a population one time
# Parameter:  pop: a population object representing the population of agents traversing the maze
#             a_divisor: divides amount of agents displayed by this number      (cuts down complexity for larger samples)
#             dna_divisor: divides the amount of actions displayed by this number (cuts down complexity for larger samples)
def move_population_once(pop,a_divisor = 1,dna_divisor = 1):
    # Boolean flag that gets set if an agent was able to move and changed positions
    Moved = False
    # Declare a couple of global variables to track the agent's traversal through their DNA sequence 
    global actionNumber, done_moving
    # Check if agents still have moves to execute
    if (actionNumber < pop.agent_DNA_length):
        # move every agent once
        for x in range(pop.pop_size):
            # Capture each agent in the population's movement status
            Moved = pop.Agent_quiver[x].move(actionNumber,pop.maze)
            # If an agent changes positions, update the screen
            if (Moved == True) and (actionNumber % dna_divisor == 0) and ((x == (pop.pop_size -1)) or (x % a_divisor == 0)):
                # pop.Agent_quiver[x] == pop.Agent_quiver[pop.pop_size-1]
                #change the previous position to black
                color = BLACK
                #Peek line 59 for draw.rect() argument explanation
                pygame.draw.rect(screen, color, [pop.maze.CELL_SIZE * pop.Agent_quiver[x].previous_position[0], pop.maze.CELL_SIZE * pop.Agent_quiver[x].previous_position[1], pop.maze.CELL_SIZE, pop.maze.CELL_SIZE])
                #update the new position to Red
                color = RED
                pygame.draw.rect(screen, color, [pop.maze.CELL_SIZE * pop.Agent_quiver[x].current_position[0], pop.maze.CELL_SIZE * pop.Agent_quiver[x].current_position[1], pop.maze.CELL_SIZE, pop.maze.CELL_SIZE])
                # Update the screen with what has been drawn
                pygame.display.update()
        # increment which DNA gene is firing (which action the agent is taking)
        actionNumber += 1
    # Now the agent has exhausted their sequence of gene instructions
    else:
        done_moving = True

# Function that resets the maze erasing the previous generation of agents and placing the new generation at the maze entrance
# Parameter:  pop: a population object representing a population of agents traversing the maze
def clear_screen(pop):
    # Draw over all agents with black, clean the board
    for x in range(pop.pop_size):
        # change the previous position to black
        color = BLACK
        pygame.draw.rect(screen, color, [pop.maze.CELL_SIZE * pop.Agent_quiver[x].current_position[0], pop.maze.CELL_SIZE * pop.Agent_quiver[x].current_position[1], pop.maze.CELL_SIZE, pop.maze.CELL_SIZE])
    # update what we've drawn
    pygame.display.update()
 

# Allows text objects to be generated using a string and a font
def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

 # Button function adapted from: https://pythonprogramming.net/pygame-button-function-events/
 # creates a clickable button that executes a passed in function
 # Params: msg: button text, x:x, y:y, w:width, h:height, ic:inactive color, ac:active color, action: on click function
def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    # mouse is on top of button, change color
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            # display text on button and return color to inactive
            pygame.draw.rect(screen, ic,(x,y,w,h))
            smallText = pygame.font.SysFont("comicsansms",20)
            textSurf, textRect = text_objects(msg, smallText)
            textRect.center = ( (x+(w//2)), (y+(h//2)) )
            screen.blit(textSurf, textRect)
            # perform passed in function
            action()
                     
    else:
        #draw button with inactive color
        pygame.draw.rect(screen, ic,(x,y,w,h))

    # display text on button
    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w//2)), (y+(h//2)) )
    screen.blit(textSurf, textRect)

# first function called before main game loop is started
def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        button("Start",600,435,80,50,WHITE,RED,game_loop)
        pygame.display.update()




######### Highlight all the agents that are selected to get eaten ###########
# A fun, miscellaneous function that highlights on the screen the agents with the lowest fitness at the end of a generation
# Parameter:  pop: a population object representing a population of agents traversing the maze
def highlight_weak(pop):
    # Declare a variable that will capture the weakest agents from a generation of an agent population
    weakest = pop.kill_the_weak()
    # Let's paint them red to the screen
    color = RED
    for x in range(len(weakest)):
        pygame.draw.rect(screen, color, [maze_instance.CELL_SIZE * weakest[x].current_position[0], maze_instance.CELL_SIZE * weakest[x].current_position[1], maze_instance.CELL_SIZE, maze_instance.CELL_SIZE])
    # Update the screen with what has been drawn
    pygame.display.update()
    pygame.time.delay(3000)

######## Highlight all the selected parents #######
# Another miscellaneous function that highlights the fittest agents among a generation by painting them blue
# Parameter:  pop: a population object representing a population of agents traversing the maze
def highlight_parents(pop):
    # Capture selected parents
    selected = copy.deepcopy(pop.selection())
    # Paint them blue to the screen
    color = WHITE
    for x in range(len(selected)):
        pygame.draw.rect(screen, color, [maze_instance.CELL_SIZE * pop.Agent_quiver[selected[x]].current_position[0], maze_instance.CELL_SIZE * pop.Agent_quiver[selected[x]].current_position[1], maze_instance.CELL_SIZE, maze_instance.CELL_SIZE])
    # Update the screen with what has been drawn
    pygame.display.update()
    pygame.time.delay(3000)



#------------------ Main object declarations and implementation begin here -------------------------------




########################################################
# Basic Genetic Algorithm Pseudo Code:
# 1: Seed first generation
# 2: do while(TerminationCondition != True):
# 3:    population.move()
# 4:    population.calculate_fitness()
# 5:    population.select_parents()
# 6:    population.crossover&mutate()
# 7:    population.kill_the_weak()
# 8:    population.reset()
#########################################################

# ----------------- Start of Main Program Loop ----------------------------------------------------
# Instantiate a maze
maze_instance = Maze.Maze()
# Seed the first population to navigate the maze giving it (pop_size, maze object, DNA_length declaration)
test_population = Population.Population(30, maze_instance, 300)
# setup pygame display
pygame_setup(test_population.maze)
# display the maze to the pygame window
draw_maze(test_population.maze)

done_moving = False     # The flag that allows the maze to loop until the user clicks the close button
actionNumber = 0        # This is the DNA index for the agent to execute each loop
FPS = 1000               # defines game loop frames per second; lower numbers can be used to more closely observe agent movement
exited = False          # Flag holding the screen open

# main game loop where evolution of populations take place
def game_loop():
    
    global done_moving, actionNumber, FPS, exited

    # Begin a loop that runs for as many generations as you use as an argument for the range function
    for generation in range(100000):
        # While the user hasn't clicked the exit button and the generation is still navigating through their DNA sequences
        while ((not exited) and (not done_moving)):
            # Define how many frames per second the simulation runs at
            clock.tick(FPS) # should be called once per frame
            # Checks if exit is clicked on
            for event in pygame.event.get():  
                # First, if the user clicks the close button, we need to close the window down
                if event.type == pygame.QUIT:
                    # by changing the loop flag to True
                    exited = True

            #####################
            # Population movement
            #####################
            
            # move the entire population one step forward
            move_population_once(test_population,1,1)
            
        # Only continue with program, if window has not been exited
        if not exited:
            # RESET variables so next generation can be spawned into the maze
            done_moving = False
            actionNumber = 0
            # Clear the maze
            clear_screen(test_population)
            
            ######################
            ## Calculate Fitess
            ######################
            test_population.calculate_fitness()
            test_population.get_fitness_stats(screen)      
            # highlight_parents(test_population)
            #####################################################################
            ## Select Parents and Produce children through crossover and mutation
            #####################################################################
            children = test_population.crossover()
            

            ##########################
            ## Kill the weakest agents
            ##########################
            # highlight_weak(test_population)
            test_population.kill_the_weak()

            #############################
            ## Reset for next generation
            #############################
            
            test_population.add_children(children)
            # move all agents back to the start of the maze
            test_population.reset(screen)
            
            print("Current generation: " + str(test_population.global_gen_counter))
            print("Avg fitness: " + str(test_population.average_fitness) + "Top Fitness: " + str(test_population.top_score))
        
    # --------  End of Main Program Loop -----------

    # Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
    pygame.quit()
    quit()

# Start the program
game_intro()