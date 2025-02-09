A program to optimize Factorio Factories.

RecipeParser.py: Takes the internal Factorio recipe.lua, and converts to a more suitable Python dictionary. 

(TODO) AssemblerProduction.py: Calculate the inputs and outputs per second for various recipes, after defining the level of their Assembler machines, and any Productivity and Speed Modules of various levels.

(TODO) Optimize.py: Create a weighted graph for each Assembler, and use Simulated Annealing to arrange them onto discrete gridpoints. It's goal is to locally minimize the number and lengths of belts. A preprocessing step partitioning different sub-assemblies may be used, to reduce the size of the space. 
