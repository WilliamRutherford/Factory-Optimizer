import json
import math
import numpy as np
from collections import defaultdict
from scipy.spatial.distance import cdist

'''
For each recipe:
name: the name of the recipe
ingredients: {name="", amount = #}*
result_count: the number of items produced. default of 1
result: name of the item produced (should be same as name)
results: If the process has multiple outputs, this is a list of them and their amounts. 
energy_required: a number, representing the number of seconds at crafting speed of 1. default of 0.5

examples:
  {
    type = "recipe",
    name = "iron-plate",
    category = "smelting",
    energy_required = 3.5,
    ingredients = {{"iron-ore", 1}},
    result = "iron-plate"
  }
  
  {
    type = "recipe",
    name = "iron-gear-wheel",
    normal =
    {
      ingredients = {{"iron-plate", 2}},
      result = "iron-gear-wheel"
    },
    expensive =
    {
      ingredients = {{"iron-plate", 4}},
      result = "iron-gear-wheel"
    }
  }
'''
recipes = {
    "iron-gear-wheel": {
        "ingredients": [("iron-plate", 2)],
        "energy_required": 0.5,
        "result": "iron-gear-wheel"
    },
    "iron-plate": {
        "category": "smelting",
        "ingredients": [("iron-ore", 1)],
        "energy_required": 3.2,
        "result": "iron-plate",
        "result_count": 1
    },
    "copper-plate": {
        "category": "smelting",
        "ingredients": [("copper-ore", 1)],
        "energy_required": 3.2,
        "result": "copper-plate",
        "result_count": 1
    },    
    "copper-cable": {
        "ingredients": [("copper-plate", 1)],
        "energy_required": 0.5,
        "result_count": 2
    },
    "transport-belt": {
        "ingredients": [("iron-plate",1),("iron-gear-wheel",1)],
        "energy_required": 0.5,
        "result_count": 2
    },
    "electronic-circuit": {
        "ingredients": [("iron-plate",1),("copper-cable",3)],
        "energy_required": 0.5
    }
}

def read_game_json(filepath='data.json'):
    f = open(filepath)
    gamedata = json.dump(f)
    f.close()
    return gamedata

'''
Given some desired output rate of particular item(s), generate all the intermediate steps and total raw resources required. 
'''
def generate_recipe_tree(requirements):
    # First, we should go through and identify every recipe, ignoring speed and number. 
    
    in_items = list(map((lambda x: x[0]), requirements))
    steps = defaultdict({"in":[], "out":[]})
    next_step = {}
    for in_item in in_items:
        recipe_inputs = list(map((lambda x: x[0]), recipes[in_item]["ingredients"]))
        steps[in_item]["in"] += recipe_inputs
        next_step = next_step.union(set(recipe_inputs))
    
    # Next, go through and for each step, calculate the amount out and amount in. This tells us the amount of every proceeding recipe. 

'''
From a list of all production steps, generate a weighted directional graph matrix representing the flow/s between steps. 
We want the items to be in descending order of input/output belts. 

The question is, should the matrix be symmetric or not? Do we want to consider directionality? Does that make a difference? 
'''
def generate_graph_matrix(recipe_tree):
    # Get the names of all items. Each of these represents a row/col in our matrix. 
    all_items = list(recipe_tree.keys())
    #item_flow = list(map((lambda x: ), recipe_tree))
    n = len(all_items)
    for an_item in recipe_tree.keys():
        pass
    # Currently, we make sure it is sorted in order at the end. Technically we could just sort the items at the beginning. 
    matrix = sort_by_sum(matrix, ascending = False)

'''
Once we have the matrix representing all the recipes and flow, we optimize a mapping between recipes and points.
'''
def optimize_mapping(requirements):
    recipe_mtx = generate_graph_matrix(generate_recipe_tree(requirements))
    num_recipes = np.shape(recipe_mtx)[0]
    start_pts = generate_num_lattice(num_recipes)
    (pts, dsts) = generate_distance_matrix(start_pts)

'''
Given the locations and the weight of edges, calculate our loss function. 

The result can be represented as item-distance, where 10 items moving 1 block is identical to 1 item moving 10 blocks. 
'''
def loss_fn(dsts, connections):
    if(np.shape(dsts) != np.shape(connections)):
        print("loss_fn: mismatch in matrix shapes! dsts:",np.shape(dsts),"connections:", np.shape(connections))
    return np.sum(np.multiply(np.flatten(dsts), np.flatten(connections)))

'''
Given a matrix, permute both the rows and cols so they are in descending or ascending order of sum. Return the permuted matrix, as well as the permutation we used to get there. 
'''
def sort_by_sum(matrix, ascending = True):
    result = matrix
    sums = np.sum(matrix, 0)
    order = np.argsort(sums)
    if(not ascending):
        order = order[::-1]
    result = result[order, :]
    result = result[:, order]    
    return (result, order)
    
'''
Given a radius, calculate the points where abs(x) + abs(y) <= r
'''
def generate_lattice(radius):
    points = np.zeros((1+2*radius*(radius+1),2))
    points[0:] = [0,0]
    indx = 1
    for i in range(1, radius+1):
        # First, add the points on either axis.
        points[indx:]   = [ i, 0]
        points[indx+1:] = [-i, 0]
        points[indx+2:] = [0,  i]
        points[indx+3:] = [0, -i]
        # This is because 0 = -0, so [0,i] = [-0,i] which would be double counted. 
        indx += 4
        ''' 
        For each smaller radius, find all points where abs(x)+abs(y) = m
        abs(y) = m - abs(x)
        y = +- (m - abs(x))
        so y = m - abs(x) and y = abs(x) - m
        '''
        for x in range(1, i):
            y = i - x
            points[indx:]   = [ x,  y]
            points[indx+1:] = [-x,  y]
            points[indx+2:] = [ x, -y]
            points[indx+3:] = [-x, -y]
            indx += 4

    return points
'''
Given a number of points, generate a diamond shaped lattice of the tightest packing around the origin. 
If the number does not perfectly match a lattice, we cut off some values from the outer shell. This means it will prefer lower x values. 
'''
def generate_num_lattice(n):
    radius = (math.sqrt(2*n-1)-1)/2
    min_radius = math.floor(radius)
    max_radius = math.ceil(radius)
    lattice = generate_lattice(max_radius)
    return lattice[0:n,]

'''
Given an array of n points, generate the n x n matrix representing the distances between them. This will be a symmetric matrix. 
Therefore, A_i,j = the distance between the ith point and the jth point. 

The dst_metric is a string representing the distance metric to use. Usually, this will be the usual L2 Norm, or the L1 Norm for cityblock (manhattan) distances. 

The points are also re-ordered to be in ascending order of total distance to all other points. 
'''
def generate_distance_matrix(pts, dst_metric='cityblock'):
    dsts = np.zeros((np.shape(pts)[0], np.shape(pts)[0]))
    dsts = cdist(pts, pts, metric=dst_metric)
    og_sum = np.sum(dsts)
    '''
    Now, sort in ascending order of total distance to all other points. 
    '''    
    (dsts, asc_order) = sort_by_sum(dsts)
    
    '''
    Use this to reorder our points.
    '''
    pts = pts[asc_order]
    new_sum = np.sum(dsts)
    if(og_sum != new_sum):
        print("There is a mismatch after permuting, the sum of all distances has changed.")
    return (pts, dsts)