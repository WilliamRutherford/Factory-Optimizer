import params
import RecipeParser

recipes = RecipeParser.read_recipes(filename = params.RECIPE_PATH)


# Given the different levels of Assemblers / Modules PLUS the addition of quality, we must define the 'maximum' tier our optimizer can use. 
# The optimal solution would be to define the quantity of each that is available, however deciding what each recipe should and shouldn't use would balloon the scope. 

# What is our heuristic for when productivity vs speed modules should be used?

# Speed Module: Unrestrained by input, restrained by speed of output + number of assemblers / space available. 
# Productivity Module: Lots of expensive items into a recipe with low quantity output. The more assemblers/recipes an intermediate item has gone through, the higher the value of productivity.  

# Productivity + Speed Module Beacon: High quantity items where large amounts are needed; speed modules almost entirely offset the downside of productivity modules. 
# This requires there to be a large number of assemblers; because a tiled setup will have 6+ assemblers per beacon. 


