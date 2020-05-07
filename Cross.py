# Stephen Haugland and Shane Snediker
# Artificial Intelligence Spring 2020
# This file creates a population of agents 
# and defines the DNA crossover of successive populations as well as mutations

import Agent        # Import user defined class that defines individual agents
import Controller   # Import user defined class that instantiates our maze object
import random       # Import Python random library for generating random numbers
import copy         # Import Python copy library for making deep copies

# Population class
# Class for organinizing the agent population and reproduction
class Population:

    #########################################
    #### Class Attributes 
    #########################################

    pop_size = None             # The size of each generation of agents
    Agent_quiver = [None]       # An array containing pop_size Agent objects
    number_of_survivors = 20    # A constant value representing the top 20 agents of each generation
    global_gen_counter = 0      # A counter that tracks how many generations throughout the simulation

    #########################################
    #### Class Methods 
    #########################################

    # Population constructor to initiate a population of agents to traverse the maze
    def __init__(self, agents, size):
        self.pop_size = size
        self.Agent_quiver = agents

    # This method selects the parents for the next generation using Roulette Wheel Selection
    # Implementation details referenced from: https://www.tutorialspoint.com/genetic_algorithms/genetic_algorithms_parent_selection.htm
    # In this method there is selection pressure towards fitter individuals but there is a chance for any agent to become a parent
    def selection(self):
        sum = 0
        for x in range(len(self.Agent_quiver)):
            sum += self.Agent_quiver[x].fitness_score
            
        Rand = random.randint(0,sum)

    # This method takes in a generation of agents,
    # orders them from fittest to weakest and returns 
    # a randomized order of the surviving parents 
    def kill_the_weak(self):
        # First we have to kill off the weakest from the previous generation
        # Survival of the fittest is gruesome
        # Begin by aligning the population of agents from the fittest to the weakest (Fitter agents have lower scores)
        Ordered_agents = sorted(self.Agent_quiver, key = self.Agent_quiver.fitness, reverse = True)
        # Now we kill half of the population
        # Let's initialize an array half the size of our population
        # to hold the survivors
        Fittest = [self.number_of_survivors]
        # Now we iterate through the list of ordered agents saving the top half
        for agent in range((self.number_of_survivors)):
            Fittest.append(Ordered_agents[agent])
        # We want this reproductive process to be random between the surviving parents
        # Therefore we need to randomize the order or the parent array
        Fittest.shuffle()

        return Fittest



        # TODO NUMBER OF PARENTS TO BE SELECTED AND PARENTS TO LIVE ON INTO NEXT GEN!!
        # TODO RUN SOME TESTS TO MAKE SURE THAT THESE FUNCTIONS ARE DOING WHAT YOU'RE INTENDING FOR THEM TO DO!!            
    
    
    
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
    def  crossover(self):
        # We begin by killing the weakest half of the population
        self.kill_the_weak()
        
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
        for i, j in range(self.len()):
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
            p1_strand_length = random.randint(50, self.Agent_quiver.DNA_length)

            # Create a random integer from 0 up to the size of p1's DNA genes 
            # that are not getting pulled to represent the index 
            # where we will place the DNA strand from p1
            # In other words, we're going to pluck the random sized DNA
            # segment from p1 beginning at a random location in p1's DNA
            # structure, and the following variable will help us place that same 
            # DNA segment beginning at the same index in the child
            p1_DNA_start_index = random.randint(0, (self.Agent_quiver[i].DNA_length - p1_strand_length))
            # We need to preserve this starting index despite needing to iterate across it
            # in an upcoming loop, so we will establish a deep copy
            p1_DNA_start_index_deepCopy = copy.deepcopy(p1_DNA_start_index)

            # Next we create an array that will hold the DNA structure of this new child
            new_child_DNA = []

            # Iterate through the p1 DNA structure capturing a chunk of size p1_strand_length
            # beginning at the random index number catpured in p1_DNA_start_index
            for p1_DNA_start_index_deepCopy in range(p1_strand_length):
                # Hold the DNA segment of p1. p1 is represented by Agent_quiver[i]
                DNA_holder.append(self.Agent_quiver[i].DNA[p1_DNA_start_index_deepCopy])

            # Now we need to begin building the child's DNA structure
            # We begin by adding to it the DNA strand from p1 that we've
            # just captured in DNA_holder beginning at the same index as p1
            
            k = 0
            # Start a loop that runs as many iterations as the randomized
            # size of p1's DNA strand that we pulled
            while k < p1_strand_length:
                # Append to the child's DNA structure the strand from p1 
                # starting at the same index that the strand began in p1 
                new_child_DNA[p1_DNA_start_index].append(DNA_holder[i])

            # Now that the child has received the DNA it will take from p1, 
            # we need to fill in the remaining DNA elements with genes
            # from the DNA structure of p2

            # If by chance the p1 strand fit perfectly at the end of the child's
            # DNA structure, then we need to start from the beginning filling
            # in the blanks.  Otherwise, we start at the first index past where
            # the DNA from p1 ended.  So we begin by filtering out the rare case
            # where the DNA strand from p1 fit at the very end of the child DNA structure
            if (self.Agent_quiver[i].DNA_length - p1_DNA_start_index) != p1_strand_length:
                # Begin a loop to fill the latter indices of the child array from
                # corresponding indices of p2 beginning 1 index past the p1 strand
                x = p1_DNA_start_index + p1_strand_length + 1
                # While we haven't reached the end of p2's DNA structure
                while x < self.Agent_quiver[j].DNA_length:
                    # keep loading indices from p2 into the corresponding indices in the child DNA array
                    new_child_DNA[x] = self.Agent_quiver[j].DNA[x]

                # Now that we've filled up the end of the child DNA structure,
                # we come back around to the front end  and fill each index up to
                # the index that lands directly before the p1 strand begins
                y = 0
                while y < p1_DNA_start_index:
                    new_child_DNA[y] = self.Agent_quiver[j].DNA[y]

            # This is the case where the p1 strand fits precisely at the end of the child array
            else:
                x = 0
                while x < p1_DNA_start_index:
                    new_child_DNA[x] = self.Agent_quiver[j].DNA[x]

            # Now we create a new child infusing them with the DNA resulting
            # from the above reproduction process
            # TODO I need to confirm that this is the correct way to tie new agents to our maze
            new_child = Agent.Agent(new_child_DNA, Controller.Maze)

            # The last part of the reproductive process is to introduce mutation
            # We want to only introduce mutation a small percentage of the time.
            # Also, we want the percentage of time that a child's genes get mutated 
            # to be highest in the beginning generations and decrease with successive generations
            # First we determine if this regeneration iteration is within the first
            # 10 generations.  If so, we'll mutate new children at a rate of 15%
            if self.global_gen_counter < 11:
                # Randomly generate a float between 0 and 1
                mutate_rate = random.random()
                # If this randomly generated float is less than .15, that represents 
                # a 15% chance of happening, so in this case we initiate mutation
                if mutate_rate < .15:
                    # Mutate this child
                    new_child.mutate()
                    # TODO DO I NEED TO END ON AN ELIF OR ELSE OR IS IT OKAY TO NOT DO SO?

            # This elif loop will catch generations 10 - 20 and initiate mutation 10% of the time
            elif self.global_gen_counter > 10 and self.global_gen_counter < 21:
                # Randomly generate a float between 0 and 1
                mutate_rate = random.random()
                # If this randomly generated float is less than .10, that represents 
                # a 10% chance of happening, so in this case we initiate mutation
                if mutate_rate < .10:
                    # Mutate this child
                    new_child.mutate()

            # This elif loop will catch all generations past 20 and initiate mutation 5% of the time
            elif self.global_gen_counter > 20:
                # Randomly generate a float between 0 and 1
                mutate_rate = random.random()
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

        # Let's increment the generation counter before we return from this method
        self.global_gen_counter += 1

        # return a new generation of agents
        return new_pop