from lupa import LuaRuntime
import re

# Make sure to copy over the recipe.lua file from your Factorio install. It should be located at ...\Factorio\data\base\prototypes\recipe.lua

lua = LuaRuntime(unpack_returned_tuples=True)

def load_lua_table(filename : str):
    try:
        with open(filename, "r") as file:
            lua_code = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found!")

    # Select only the parts after the last data:extend
    lua_code = lua_code.split("data:extend")[-1]
    # Remove the first (
    lua_code = re.sub(".*\({","{", lua_code)
    # Remove the last )
    lua_code = re.sub("\)\s*$","",lua_code)



    # If the file does not start with "return", prepend it.
    if not lua_code.lstrip().startswith("return"):
        lua_code = "return " + lua_code

    # For debugging, print the first 100 characters
    #print(lua_code[0:100])

    try:
        lua_table = lua.execute(lua_code)
    except Exception as e:
        raise RuntimeError("Error executing Lua code: " + str(e))
        
    
    return lua_table

def lua_table_to_python(obj):
    if hasattr(obj, 'items'):
        keys = list(obj.keys())
        if keys and all(isinstance(k, int) for k in keys):
            max_index = max(keys)
            result = []
            for i in range(1, max_index + 1):
                result.append(lua_table_to_python(obj[i]))
            return result
        else:
            result = {}
            for key, value in obj.items():
                result[key] = lua_table_to_python(value)
            return result
    elif isinstance(obj, (list, tuple)):
        return [lua_table_to_python(item) for item in obj]
    else:
        return obj
'''
Given a recipe.lua file, extract all the factorio recipes.

The results are dictionaries, with each item and core features. 

recipe['name'] = {
    'ingredients' : { str => int },
    'result_count' : int,
    'energy_required' : float,
    'allow_productivity' : bool
    (if incl_secondary_params)
    'category' : str,
    'subgroup' : str,
    'recipe_name' : str
}
'''
def read_recipes(filename: str = 'recipe.lua', expensive : bool = False, incl_secondary_params : bool = False):
    try:
        lua_table = load_lua_table(filename)
    except Exception as e:
        print(e)
        return

    py_obj = lua_table_to_python(lua_table)

    #print(py_obj)

    # post process to convert the list into a dictionary with only certain fields.
    # 'type': 'recipe'
    # recipes['copper-cable'] = {'ingredients' : {'name1': num1, 'name2': num2}, 'energy_required' : ?}

    singular_recipes = {}
    
    for curr_recipe in py_obj:
        if(curr_recipe['type'] == 'recipe'):
            #if(('subgroup' in curr_recipe) and (curr_recipe['subgroup'] == 'fluid-recipes')):
            #    continue

            new_recipe_dict = {}

            #Values in the list 'results' have the form:
            #{type="???", name="???", amount=?}

            if('results' not in curr_recipe):
                # This means the recipe has zero output. Useless. 
                continue
            elif('results' in curr_recipe and len(curr_recipe['results']) == 1):
                only_result = curr_recipe['results'][0]
                new_recipe_dict['result_count'] = only_result['amount']

            # TODO: make a special case for recipes with *multiple* outputs, which are stored in 'results'. These will need to use the recipe name, annoyingly
            elif('results' in curr_recipe):
                continue


            # Choose the name for this recipe. This should be the result, or the singular in 'results', otherwise the recipe name. 
            if('results' in curr_recipe and len(curr_recipe['results']) == 1):
                new_name = curr_recipe['results'][0]['name']
            else:
                new_name = curr_recipe['name']

            
            if('energy_required' in curr_recipe):
                new_recipe_dict['energy_required'] = curr_recipe['energy_required']
            else:
                new_recipe_dict['energy_required'] = 0.5
            
            if('result_count' in curr_recipe):
                new_recipe_dict['result_count'] = curr_recipe['result_count']
            elif('result_count' not in curr_recipe):
                new_recipe_dict['result_count'] = 1

            # Ingredients and results can both contain: 'ignored_by_stats' and 'ignored_by_productivity'. These are only used by coal liquefaction and kovarex refinement. 

            if('ingredients' in curr_recipe):
                inputs_dict = {}

                for an_input in curr_recipe['ingredients']:
                        
                    #print("current ingredient:" + str(an_input))
                    # Here we handle dictionary inputs
                    # They are a dict of {'type': 'fluid', 'amount': ???, 'name': ???}
                    # Change to ingredients = {'name1' : 'num1', 'name2' : 'num2', ...}
                    inputs_dict[an_input['name']] = an_input['amount']

                    #raise Exception("ValueError: unknown recipe ingredient format encountered:" + str(an_input))

                new_recipe_dict['ingredients'] = inputs_dict

            if('allow_productivity' in curr_recipe):
                # copy over whether productivity is allowed. 
                # Currently, this only seems to exist when 'true'
                new_recipe_dict['allow_productivity'] = curr_recipe['allow_productivity'] # = True
            else:
                new_recipe_dict['allow_productivity'] = False

            # What if we want secondary properties like category, subgroup, etc?
            if(incl_secondary_params):
                if('category' in curr_recipe):
                    new_recipe_dict['category'] = curr_recipe['category']
                if('subgroup' in curr_recipe):
                    new_recipe_dict['subgroup'] = curr_recipe['subgroup']
                if('name' in curr_recipe):
                    new_recipe_dict['recipe_name'] = curr_recipe['name']

            singular_recipes[new_name] = new_recipe_dict
    return singular_recipes

def unique_fields(filename : str = 'recipe.lua'):
    try:
        lua_table = load_lua_table(filename)
    except Exception as e:
        print(e)
        return

    py_obj = lua_table_to_python(lua_table)
    result_set = set()
    for item in py_obj:
        #print(item)
        result_set |= set(item)

    return list(result_set)
    #print(result_set)
        

if __name__ == '__main__':
    recipes = read_recipes(filename = 'recipe.lua', expensive = False)
    #print(recipes)
    """     
    try:
        lua_table = load_lua_table('recipe.lua')
    except Exception as e:
        print(e)
        return

    py_obj = lua_table_to_python(lua_table)

    print("unique fields:")
    print(unique_fields())
    select_with_field = 'main_product'
    #dont_display = ['icon', 'icon_size', 'crafting_machine_tint', 'enabled']
    print("fields with", select_with_field)
    selected = list(x for x in py_obj if (select_with_field in x) or ('normal' in x and select_with_field in x['normal']))
    print(selected)
    """
    """     
    keyword = 'science'
    for x in recipes:
        if(keyword in x):
            print(x + str(recipes[x]))
    """