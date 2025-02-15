import math

import params
import RecipeParser

recipes : dict = RecipeParser.read_recipes(filename = params.RECIPE_PATH)

class ProductionUnit:

    # Assembler_type is one of ["productivity", "speed", "beacons"]
    assembler_type : str = ""
    num_assemblers : int = 0
    output_count : float = 0
    ingredients : dict = {}
    assembler_recipe : dict = {}
    '''
    Create a "Production Unit" all using the same recipe.
    '''
    def __init__(self, recipe_name: str, desired_output: float = 0):
        self.assembler_recipe = recipes[recipe_name]
        self.output_count = desired_output
        # Determine the type
        if(self.assembler_recipe['allow_productivity']):
            self.assembler_type = "productivity"
        # TODO: We will add some condition for when we will allow beacons
        elif(False):
            self.assembler_type = "beacons"
        else:
            self.assembler_type = "speed"

    def calc_production(self, desired_output : float):
        #self.output_count = desired_output
        self.num_assemblers = 0
        self.ingredients = self.assembler_recipe['ingredients']

        output_mult = 1
        speed_mult = 1
        if(self.assembler_type == "productivity"):
            output_mult = 1 + params.ASSEMBLER_SLOTS * params.PRODUCTIVITY_MODULE_BONUS
            speed_mult  = 1 - params.ASSEMBLER_SLOTS * params.PRODUCTIVITY_MODULE_PENALTY
        elif(self.assembler_type == "speed"):
            speed_mult = 1 + params.ASSEMBLER_SLOTS * params.SPEED_MODULE_BONUS
        elif(self.assembler_type == "beacons"):
            pass

        # items = recipe.output * output_mult
        # time = recipe.energy_required / (assembler_energy(per sec) * speed_mult)
        # 1 / time = assembler_energy * speed_mult / recipe.energy_required
        recipe_items = self.recipe['result_count'] * output_mult
        recipe_per_time = speed_mult * params.ASSEMBLER_CRAFTING / self.recipe['energy_required']
        items_per_sec = recipe_items * recipe_per_time

        # Set the number of assemblers. The ceiling makes this a one-way operation, invalidating the desired_output
        self.num_assemblers = math.ceil(desired_output / items_per_sec)
        self.output_count = self.num_assemblers * items_per_sec

        # How many of each ingredient do we need per second? 
        # This is the input times recipe_per_time
        for curr_input in self.ingredients:
            self.ingredients[curr_input] *= recipe_per_time


# Given the different levels of Assemblers / Modules PLUS the addition of quality, we must define the 'maximum' tier our optimizer can use. 
# The optimal solution would be to define the quantity of each that is available, however deciding what each recipe should and shouldn't use would balloon the scope. 

# What is our heuristic for when productivity vs speed modules should be used?

# Speed Module: Unrestrained by input, restrained by speed of output + number of assemblers / space available. 
# Productivity Module: Lots of expensive items into a recipe with low quantity output. The more assemblers/recipes an intermediate item has gone through, the higher the value of productivity.  

# Productivity + Speed Module Beacon: High quantity items where large amounts are needed; speed modules almost entirely offset the downside of productivity modules. 
# This requires there to be a large number of assemblers; because a tiled setup will have 6+ assemblers per beacon. 

'''
Given an output or list of output items, calculate all the intermediate steps. 
desired_outputs: dictionary[str -> int]
(the keys of desired_outputs must be a subset from the keys of recipes)
'''
def decompose(desired_outputs : dict):
    # Do a tree search, and find all the recipes our factory will use. 
    # Store these as some "AssemblerUnit" class, storing the recipe, output/s, and inputs/s. These values will be calculated later. 

    # Our core issue will be multiple recipes (at different levels) requiring the same ingredient from another recipe. 
    pass
