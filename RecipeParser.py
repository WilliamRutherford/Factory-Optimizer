from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

def load_lua_table(filename : str):
    try:
        with open(filename, "r") as file:
            lua_code = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found!")

    # TODO: Remove the first line with 'data-extend: {' and the last line with a bracket '}'

    # If the file does not start with "return", prepend it.
    if not lua_code.lstrip().startswith("return"):
        lua_code = "return " + lua_code

    try:
        lua_table = lua.execute(lua_code)
    except Exception as e:
        raise RuntimeError("Error executing Lua code: " + str(e))
    
    return lua_table

# The rest of the code remains the same...
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
def convert_ingredients_field(data):
    if isinstance(data, dict):
        if "ingredients" in data and isinstance(data["ingredients"], list):
            ing_list = data["ingredients"]
            new_ing = {}
            for item in ing_list:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    ingredient, amount = item
                    new_ing[ingredient] = amount
                else:
                    new_ing[item] = None
            data["ingredients"] = new_ing

        for key, value in data.items():
            convert_ingredients_field(value)
    elif isinstance(data, list):
        for item in data:
            convert_ingredients_field(item)
    return data
'''
def read_recipes(filename: str = 'recipe.lua', expensive : bool = False, secondary_params : bool = False):
    try:
        lua_table = load_lua_table(filename)
    except Exception as e:
        print(e)
        return

    py_obj = lua_table_to_python(lua_table)

    # post process to convert the list into a dictionary with only certain fields.
    # 'type': 'recipe'
    # recipes['result'] = {'ingredients' : {'name1': num1, 'name2': num2}, 'energy_required' : ?}
    # Some recipes (like fluids) have multiple results, which is a field 'results'. For now, we ignore. 
    recipes = {}
    
    for a_recipe in py_obj:
        if(a_recipe['type'] == 'recipe'):
            if(('subgroup' in a_recipe) and (a_recipe['subgroup'] == 'fluid-recipes')):
                continue
            # What if the recipe has a "normal" and "expensive" version?
            # This means it will not have a 'result' value, it will contain a 'normal' and 'expensive' field
            # these fields contain 'result', 'ingredients'
            curr_recipe = {}
            if('normal' in a_recipe):
                if(expensive):
                    curr_recipe = a_recipe['expensive']
                else:
                    curr_recipe = a_recipe['normal']
            else:
                curr_recipe = a_recipe
            
            # From now on, we use curr_recipe instead of a_recipe
            # TODO: make a special case for recipes with multiple outputs, which is stored in 'results'. These will need to use the recipe name, annoyingly
            if('results' in curr_recipe):
                continue
            if('result' not in curr_recipe):
                continue
            new_recipe_dict = {}
            new_name = curr_recipe['result']

            

            if('energy_required' in curr_recipe):
                new_recipe_dict['energy_required'] = curr_recipe['energy_required']
            else:
                new_recipe_dict['energy_required'] = 1
            
            if('result_count' in curr_recipe):
                new_recipe_dict['result_count'] = curr_recipe['result_count']
            else:
                new_recipe_dict['result_count'] = 1

            if('ingredients' in curr_recipe):
                inputs_dict = {}

                for an_input in curr_recipe['ingredients']:
                        if(isinstance(an_input, list)):
                            inputs_dict[an_input[0]] = an_input[1]
                        elif(isinstance(an_input, dict)):
                            # Here we handle fluid inputs
                            # They are a dict of {'type': 'fluid', 'amount': ???, 'name': ???}
                            inputs_dict[an_input['name']] = an_input['amount']
                        else:
                            raise Exception("ValueError: unknown recipe ingredient format encountered:" + str(an_input))

    
                new_recipe_dict['ingredients'] = inputs_dict

            # What if we want secondary properties like category, subgroup, etc?
            if(secondary_params):
                if('category' in curr_recipe):
                    new_recipe_dict['category'] = curr_recipe['category']
                if('subgroup' in curr_recipe):
                    new_recipe_dict['subgroup'] = curr_recipe['subgroup']
                if('name' in curr_recipe):
                    new_recipe_dict['recipe_name'] = curr_recipe['name']

            recipes[new_name] = new_recipe_dict
    return recipes

def all_fields(filename : str = 'recipe.lua'):
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
        

def main():
    recipes = read_recipes(filename = 'recipe.lua', expensive = False)
    #print(recipes)
    
    try:
        lua_table = load_lua_table('recipe.lua')
    except Exception as e:
        print(e)
        return

    py_obj = lua_table_to_python(lua_table)

    print("all fields:")
    print(all_fields())
    select_with_field = 'main_product'
    #dont_display = ['icon', 'icon_size', 'crafting_machine_tint', 'enabled']
    print("fields with", select_with_field)
    selected = list(x for x in py_obj if (select_with_field in x) or ('normal' in x and select_with_field in x['normal']))
    print(selected)

if __name__ == '__main__':
    main()