# Stephen Haugland and Shane Snediker
# Artificial Intelligence Spring 2020
# This file creates a population of agents 
# and defines the DNA crossover of successive populations as well as mutations

# An import that I will probably only need to data testing
import Maze
import Agent        # Import user defined class that defines individual agents
import random       # Import Python random library for generating random numbers
import copy         # Import Python copy library for making deep copies
from operator import itemgetter, attrgetter # used in sorting agents by fitness score

# Population class
# Class for organinizing the agent population and reproduction
class Population:

    #########################################
    #### Class Attributes 
    #########################################

    pop_size = 50             # The size of each generation of agents
    Agent_quiver = [None]       # An array containing pop_size Agent objects
    number_of_survivors = pop_size // 2    # A constant value representing the top 20 agents of each generation
    global_gen_counter = 0      # A counter that tracks how many generations throughout the simulation
    agent_DNA_length = None     # Store how long the agents DNA strands are
    # Should we include a maze that the population is bound to for ease of access?
    maze = Maze.Maze()

    #########################################
    #### Class Methods 
    #########################################

    # Population constructor to initiate a population of agents to traverse the maze
    def __init__(self, size, maze, dna_length):
        self.pop_size = size
        self.number_of_survivors = size // 2
        self.agent_DNA_length = dna_length
        self.maze = maze
        agents = []
        for _ in range(size):
            Agent007 = copy.deepcopy(Agent.Agent(self.maze, dna_length))
            agents.append(Agent007)
        self.Agent_quiver = agents

    # Calculates the fitness for every agent in the population
    # Should be called after after each round of movement
    def calculate_fitness(self):
        # Calculate fitness for each individual agent
        for x in range(len(self.Agent_quiver)):
            self.Agent_quiver[x].calculate_fitness(self.maze)
        # Sort the agent quiver by fitness scores
        self.Agent_quiver = sorted(self.Agent_quiver, key = attrgetter('fitness_score'), reverse = False)

    # print to console the top and average fitness score to monitor evolution progress
    def get_fitness_stats(self):
        sum = 0
        for x in range(self.pop_size):
            sum += self.Agent_quiver[x].fitness_score
        avg = sum // self.pop_size
        print('Top fitness score: {}\nAverage fitness score: {}' .format(self.Agent_quiver[self.pop_size - 1].fitness_score, avg))

    # Once an population has completed a round of movement, reset them to the beginning of the maze
    def reset(self):
        for x in range(self.pop_size):
            self.Agent_quiver[x].current_position = self.maze.MAZE_START
            self.Agent_quiver[x].current_orientation = self.maze.MAZE_START_ORIENTATION
            self.Agent_quiver[x].fitness_score = 0

    # Move every agent in the population one step based on DNA index
    def move(self, DNA_index):
        for x in self.pop_size:
            self.Agent_quiver[x].move(DNA_index,self.maze)

    # This method selects the parents for the next generation using Roulette Wheel Selection
    # Implementation details referenced from: https://www.tutorialspoint.com/genetic_algorithms/genetic_algorithms_parent_selection.htm
    # In this method there is selection pressure towards fitter individuals but there is a chance for any agent to become a parent
    def selection(self):
        # sum of all fitness values
        sum = 0
        # add up all fitness scores
        for x in range(len(self.Agent_quiver)):
             sum += self.Agent_quiver[x].fitness_score

        # Recursively generate boundaries between 0 and 1 that split up the number space into probabilites for each agent
        # This way each agent will have certain probability to reproduce with those who have a higher fitness getting a larger chance to mate
        selection_boundaries = [0]
        for i in range(len(self.Agent_quiver) - 1):
            # add the previous fitness proportion to the current fitness proportion to get a new boundary
            selection_boundaries.append(selection_boundaries[i] + ((self.Agent_quiver[i].fitness_score)/sum))
        selection_boundaries.append(1)

        # Now we have n boundaries (dividing lines) between 0 and 1 where n = the number of agents
        # The number line between 0 and 1 is split into n different sections in between boundaries corresponding to the probability of selection
        # Now a random number is chosen between 0 and 1 to see which parents get selected
       
        # This holds the indices that point to selected parents from the original populations quiver
        parent_indices = []
        previously_selected_parent = None
        for x in range(self.pop_size):
            # This random selection will occur n times where n = population size
            r = random.random()
            # find the index of the parent that got randomly selected
            selected_parent_index = findClosest(selection_boundaries, len(selection_boundaries), r)

            # prevent self-mating
            # if same parent is selcted two times in a row, go through loop again to select a new parent
            if (selected_parent_index == previously_selected_parent):
                # decrement loop counter to ensure N parents are selected
                x -= 1
                print("Parent cannot mate with itself")
            # else if the selected parent is a different agent then the previously selected agent, add to selection list
            else:
                # add this index to the list of indices it was not just added
                parent_indices.append(selected_parent_index)
                # update previous selection for next round
                previously_selected_parent = copy.deepcopy(selected_parent_index)
        # return a list of indices pointing to parents in Agent_quiver that should be sequentially iterated through to produce children
        return parent_indices
  

    # This method removes the least fit agents from the population based on number of survivors defined in Population class
    # This method is called each time new children have been created
    def kill_the_weak(self):
        # Begin by aligning the population of agents from the fittest to the weakest (Fitter agents have higher scores)
        ordered_agents = sorted(self.Agent_quiver, key = attrgetter('fitness_score'), reverse = False)
        # Now we kill a portion of the population
        # Let's initialize an array to hold the survivors
        Fittest = []
        # Now we iterate through the list of fitness sorted agents saving the fittest portion
        for agent in range((self.number_of_survivors)):
            Fittest.append(ordered_agents[agent])
        # Copy over the fittest agents into the new quiver 
        self.Agent_quiver = copy.deepcopy(Fittest)

        # most likely comment this out later
        #return Fittest

    def add_children(self, children):
        for x in range(self.pop_size // 2):
            self.Agent_quiver.append(children[x])

    
    # Function to define DNA crossover reproduction
    # Because the directional order of an agent's movements will lead to
    # increased fitness within individual agents, we adopt a version
    # of reproduction called ordered crossover.  In ordered crossover,
    # large segments of DNA get chunked together and passed on to successive generations.
    # Throughout this method, we often refer to the first parent in a genetic 
    # combination as p1, and the second parent as p2.
    # Ultimately, in this version of crossover we want to take a DNA strand
    # of random size from p1 plucked from a random location within p1's DNA sequence.
    # We then place that random strand at a random location within the child's DNA sequence.
    # At that point we begin filling in the rest of the child's DNA structure with 
    # p2's DNA
    def crossover(self):
        # We begin by killing the weakest half of the population
        selected_parents = self.selection()

        # Initialize an array to hold our new crossover generation of children
        new_pop = []

        # The self.kill_the_weak() funciton call provides us with the surviving
        # parents that we've selected and in an array in randomized order.
        
        # Now we can start the reproductive process.  This will be a pretty detailed
        # for loop that will iterate through the shuffled parent list 
        # combining specific DNA segments and genes to create children.
        # Each iteration of the first nested loop combines 2 agents from 
        # the parent array and creates a child.
        # variable i will be tied to p1 and j will be tied to p2
        j = 1
        for i in range(0, len(selected_parents), 2):
            # print("This iteration of the mating loop i is: " + str(i))
            # print("This iteration of j is: " + str(j))
            # Initialize a dynamic array that will hold the specific sequence of DNA
            # from p1 that will be passed to the child
            DNA_holder = []

            # Create a random integer from 50 to the size of an agent's DNA strand
            # We will pull a strand of DNA of this random size from p1
            # TODO This current implementation allows a randomization of the length of 
            # the DNA strand we're going to pull from p1 from 50 - full size of 
            # an agent's DNA structure.  We may want to consider putting a limit on 
            # how large of a strand is pulled from p1?  Having too large of a chunk of  
            # p1's DNA may really limit p2's influence in the DNA of the children.  
            # But my initial thoughts are that using randomly generated values during every             
            # reproduction should generate enough variety that a few reproductions resulting 
            # from p1-dominated genes shouldn't have too much of an effect on the overall generation
            p1_strand_length = random.randint(50, self.Agent_quiver[selected_parents[i]].DNA_length)            
            #print("This iteration the p1 strand length is " + str(p1_strand_length))

            # Create a random integer from 0 up to the size of p1's DNA genes 
            # that are not getting pulled to represent the index 
            # where we will place the DNA strand from p1
            # In other words, we're going to pluck the random sized DNA
            # segment from p1 beginning at a random location in p1's DNA
            # structure, and the following variable will help us place that same 
            # DNA segment beginning at the same index in the child
            p1_DNA_start_index = random.randint(0, (self.Agent_quiver[selected_parents[i]].DNA_length - p1_strand_length))
            #print("This iteration the p1 start index is " + str(p1_DNA_start_index))
            # We need to preserve this starting index despite needing to iterate across it
            # in an upcoming loop, so we establish a deep copy
            p1_DNA_start_index_deepCopy = copy.deepcopy(p1_DNA_start_index)

            # Next we create an array that will hold the DNA structure of this new child
            new_child_DNA = []

            # Iterate through the p1 DNA structure capturing a chunk of size p1_strand_length
            # beginning at the random index number catpured in p1_DNA_start_index
            while p1_DNA_start_index_deepCopy < (p1_strand_length + p1_DNA_start_index):
                # Hold the DNA segment of p1. p1 is represented by Agent_quiver[i]
                DNA_holder.append(self.Agent_quiver[selected_parents[i]].DNA[p1_DNA_start_index_deepCopy])
                p1_DNA_start_index_deepCopy += 1

            # Now we need to begin building the child's DNA structure
            # We begin by adding to it the DNA strand from p1 that we've
            # just captured in DNA_holder beginning at the same index as p1
            
            # Recalibrate the index iterating variable
            p1_DNA_start_index_deepCopy = copy.deepcopy(p1_DNA_start_index)
    
            # Declare a counter variable
            k = 0
            # Start a loop that runs as many iterations as the randomized
            # size of p1's DNA strand that we pulled
            while p1_DNA_start_index_deepCopy < (p1_DNA_start_index + p1_strand_length):
                # Add to the child's DNA structure the strand from p1 by inserting it 
                # starting at the same index that the strand began in p1 
                new_child_DNA.insert(p1_DNA_start_index_deepCopy, DNA_holder[k])
                # Increment your index iterator and counter variables
                p1_DNA_start_index_deepCopy += 1
                k += 1
            
            # Now that the child has received the DNA it will take from p1, 
            # we need to fill in the remaining DNA elements with genes
            # from the DNA structure of p2
            # If by chance the p1 strand fit perfectly at the end of the child's
            # DNA structure, then we need to start from the beginning filling
            # in the blanks.  Otherwise, we start at the first index past where
            # the DNA from p1 ended.
            # Declare x to represent the last index of the strand we pulled from p1  
            x = p1_DNA_start_index + p1_strand_length
            #print("First index after end of strip = " + str(x))
            # WHILE WE'RE INBETWEEN THE END OF THE P1 STRAND AND THE 500TH GENE
            while (x < self.Agent_quiver[selected_parents[i]].DNA_length):
                #print("Latter end filling")
                # keep loading indices from p2 into the corresponding indices in the child DNA array
                new_child_DNA.insert(x, self.Agent_quiver[selected_parents[j]].DNA[x])
                x += 1
                #if (x == self.Agent_quiver[j].DNA_length - 1):
                 #   print("The last index filled is " + str(x))

            if (p1_DNA_start_index > 0):
                y = 0
                while(y < p1_DNA_start_index):
                    #print("Front half filling")
                    new_child_DNA.insert(y, self.Agent_quiver[selected_parents[j]].DNA[y])
                    y += 1

                # Begin a loop to fill the latter indices of the child array from
                # corresponding indices of p2 beginning 1 index past the p1 strand
                #x = p1_DNA_start_index + p1_strand_length - 1
                # While we haven't reached the end of p2's DNA structure
                # TESTING: z = 1
                #while x < self.Agent_quiver[j].DNA_length:
                # TESTING: print("After filling up the latter indices, child DNA is this big: " + str(len(new_child_DNA)))
                # Now that we've filled up the end of the child DNA structure,
                # we come back around to the front end and fill each index up to
                # the index that lands directly before the p1 strand begins

            # Now that we've filled up the latter end of the new child DNA with corresponding
            # genes from p2, we need to wrap around and fill in the front end of the DNA structure
            # Declare a counter variable
            y = 0
            while(y < p1_DNA_start_index):
                new_child_DNA.insert(y, self.Agent_quiver[j].DNA[y])
                y += 1

            # Now we create a new child infusing them with the DNA resulting
            # from the above reproduction process
            new_child = Agent.Agent(self.maze, self.agent_DNA_length, new_child_DNA)

            # The last part of the reproductive process is to introduce mutation
            # We want to only introduce mutation a small percentage of the time.
            # Also, we want the percentage of time that a child's genes get mutated 
            # to be highest in the beginning generations and decrease with successive generations.

            # We begin by capturing a random float between 0 and 1 which will be our probability
            mutate_rate = random.random()
            # Now we determine if this regeneration iteration is within the first
            # 10 generations.  If so, we'll mutate new children at a rate of 15%
            if self.global_gen_counter < 11:
                # If the randomly generated float is less than .15, that represents 
                # a 15% chance of happening, so in this case we initiate mutation
                if mutate_rate < .15:
                    # Mutate this child
                    new_child.mutate()

            # This elif loop will catch generations 10 - 20 and initiate mutation 10% of the time
            elif self.global_gen_counter > 10 and self.global_gen_counter < 21:
                # If this randomly generated float is less than .10, that represents 
                # a 10% chance of happening, so in this case we initiate mutation
                if mutate_rate < .10:
                    # Mutate this child
                    new_child.mutate()

            # This else loop will catch all generations past 20 and initiate mutation 5% of the time
            else:
                # If this randomly generated float is less than .05, that represents 
                # a 5% chance of happening, so in this case we initiate mutation
                if mutate_rate < .05:
                    # Mutate this child
                    new_child.mutate()

            # Now that we've successfully crossed DNA from 2 parent agents to produce 
            # a child whose DNA is a combination of both of its parents, as well as
            # implemented DNA mutation based on a predetermined probability, now we 
            # need to add the child from this iteration to our new population
            new_pop.append(new_child)

            # We need to increment our i and j variables an extra digit so that they jump 2 indices every loop
            j += 2

        # Let's increment the generation counter before we return from this method
        self.global_gen_counter += 1

        # return a new generation of agents
        return new_pop

##########################################################
# This code below is contributed by Smitha Dinesh Semwal 
##########################################################
# This code uses binary search to locate the closet element in a list to a target value
# These two function defined below were found at: https://www.geeksforgeeks.org/find-closest-number-array/
# All credit belongs to Smitha Dinesh Semwal
#### Modification made to code to return the single index value that the target lies in
# Returns the index corresponding to the selected parent based on the random value passed into target 
def findClosest(arr, n, target): 
  
    # Corner cases 
    if (target <= arr[0]): 
        return 0 
    if (target >= arr[n - 1]): 
        return (n - 2)
  
    # Doing binary search 
    i = 0; j = n; mid = 0
    while (i < j):  
        mid = (i + j) // 2
  
        if (arr[mid] == target): 
            return mid
  
        # If target is less than array  
        # element, then search in left 
        if (target < arr[mid]) : 
  
            # If target is greater than previous 
            # to mid, return closest of two 
            if (mid > 0 and target > arr[mid - 1]): 
                return getClosest(arr[mid - 1], arr[mid], (mid-1), mid, target) 
  
            # Repeat for left half  
            j = mid 
          
        # If target is greater than mid 
        else : 
            if (mid < n - 1 and target < arr[mid + 1]): 
                return getClosest(arr[mid], arr[mid + 1], mid, (mid + 1), target) 
                  
            # update i 
            i = mid + 1
          
    # Only single element left after search 
    return mid 
  
  
# Method to compare which proportional value is closest to the target. 
# We find the closest by taking the difference 
# between the target and both values. It assumes 
# that val2 is greater than val1 and target lies 
# between these two. 
def getClosest(val1, val2, index1, index2, target): 
  
    # if (target - val1 >= val2 - target): 
    #     return index2
    # else: 
    #     return index1

    # modified to return what index boundary the target lies in
    return index1
  
# Driver code 
# arr = [0, 0.1, 0.25, 0.4, 0.6, 0.99, 1]  
# n = len(arr) 
# target = 1

# print(findClosest(arr, n, target)) 

##################################################################################
# The code above is contributed by Smitha Dinesh Semwal, with slight modification 
##################################################################################


# ------------------------ TEST AREA ------------------------------------------

agent_holder_arr = []
test_agent_pop = 50
for x in range(test_agent_pop):
    test_bot = Agent.Agent(Maze.Maze(), 500) 
    agent_holder_arr.append(test_bot)
    
Test_pop = Population(test_agent_pop, Maze.Maze(),500)
Test_pop.Agent_quiver = agent_holder_arr

Test_pop.crossover()

    
