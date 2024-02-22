# import utility functions
from utils import get_terms, get_function_symbols
# import pysmt functions for creating formulas and terms
from pysmt.shortcuts import Not, Equals, Function, And, Symbol, REAL
from pysmt.typing import FunctionType

class CongruenceClosure:
    def __init__(self):
        # Initalize list of lists
        self.parents = []
        # print("initialized an empty list")

    # def print_list_of_lists(self):
    #     print(self.parents)

    def hasChanged(self, last_state_parents):
        return self.parents != last_state_parents #returns True if there was a change, o.w returns False 
            
    def find_sublist(self, function_application):
        # print("looking for sublist")
        for sub_list in self.parents:
            if function_application in sub_list:
                # print("yes! we found the sub list of the function_application")
                index_of_sub_list = self.parents.index(sub_list)
                return sub_list, index_of_sub_list

    def add_equality(self, element1, element2, flag):
        # If its inequaliy, keep the elements of the literal separate
        if flag == "NOT_EQUALS":
            # print("inside not_equals in CC")
            # Each element gets a new list
            self.parents.append([element1])
            self.parents.append([element2])
        elif flag == "EQUALS":
            # Merge the elements based on the equality
            # print("inside equals in CC")
            self.merge_elements(element1, element2)

    def merge_elements(self, element1, element2):
        # print("inside merge_elements")
        # print("type of element1: ", type(element1))
        # print("type of element2: ", type(element2))
        # Create a new list and add both of the elements to this list
        self.parents.append([element1, element2])

    def merge_using_toplevel(self):
        new_parents = []

        for sublist in self.parents:
            merged = False

            for existing_sublist in new_parents:
                if any(var in existing_sublist for var in sublist):
                    existing_sublist.extend(var for var in sublist if var not in existing_sublist)
                    merged = True
                    break

            if not merged:
                new_parents.append(sublist)

        return new_parents
    
    # Iterates through the functions_suspected_for_merge_per_sub_list in order to check 
    # which sub list each one of them belongs, and to merge between all those sub lists
    def merge_all_sub_lists_of_elements(self, functions_suspected_for_merge_per_sub_list):
        new_parents = self.parents.copy()
        merged_sub_list = []
        for function_application in functions_suspected_for_merge_per_sub_list:
            sub_list, index_of_sub_list = self.find_sublist(function_application)
            # print("sub_list: ", sub_list, "index_of_sub_list: ", index_of_sub_list)
            # Adds to merged sub list, and delete duplicates
            merged_sub_list+=sub_list
            merged_sub_list = list(set(merged_sub_list))
            # print("merged_sub_list: ", merged_sub_list)
            # Removes the small sub lists we want to merge to a bigger sub list
            if sub_list in new_parents:
                new_parents.remove(sub_list)
                
        # Merge between all the sublist in new_parents, not inlcuding empty lists
        if merged_sub_list != []:
            new_parents.append(merged_sub_list)
        # print("new_parents (after each sub_list): ", new_parents)

        return new_parents


    def merge_using_congruence(self, all_elements_in_cube, all_function_symbols_in_cube):
        new_parents = self.parents.copy()
        all_elements_in_cube_str = [str(element) for element in all_elements_in_cube] # String list of all elements in cube
        # print("all_elements_in_cube_str: ", all_elements_in_cube_str)
        # print(type(all_elements_in_cube_str))
        # print("all_elements_in_cube: ", all_elements_in_cube)
        # print(type(all_elements_in_cube))
        for sub_list in self.parents: 
            functions_suspected_for_merge_per_sub_list = []
            for element in sub_list:
                # Iterates through all the function symbols in cube (f,g,h,etc.)
                for function_symbol in all_function_symbols_in_cube:
                    # Build an application (but string type) from the function symbol and element (from f and x1 -> f(x1))
                    function_application_str = str(function_symbol) + '(' + str(element) + ')'
                    
                    # Checks if the application exists in the cube (for example: if f(x3) is part of the cube elements)
                    if function_application_str in all_elements_in_cube_str:
                        # print(function_application_str, " added to suspected list")
                        # Find the index of function_application in the all_elements_in_cube list
                        i = all_elements_in_cube_str.index(function_application_str)
                        # print("and his index in all_elements_in_cube is: ", i)
                        # Append to suspected list the FNode function_application
                        functions_suspected_for_merge_per_sub_list.append(all_elements_in_cube[i])

            # print("functions_suspected_for_merge_per_sub_list: ", functions_suspected_for_merge_per_sub_list)

            # Iterates through the functions_suspected_for_merge_per_sub_list in order to check 
            # which sub list each one of them belongs, and to merge between all those sub lists
            merged_sub_list = []
            for function_application in functions_suspected_for_merge_per_sub_list:
                sub_list, index_of_sub_list = self.find_sublist(function_application)
                # print("sub_list: ", sub_list, "index_of_sub_list: ", index_of_sub_list)
                # Adds to merged sub list, and delete duplicates
                merged_sub_list+=sub_list
                merged_sub_list = list(set(merged_sub_list))
                # print("merged_sub_list: ", merged_sub_list)
                # Removes the small sub lists we want to merge to a bigger sub list
                if sub_list in new_parents:
                    new_parents.remove(sub_list)
                    
            # Merge between all the sublist in new_parents, not inlcuding empty lists
            if merged_sub_list != []:
                new_parents.append(merged_sub_list)
            # print("new_parents (after each sub_list): ", new_parents)

        # print("final new_parents after all iterations: ", new_parents)
        return new_parents

    # Checks if elements of tuples are in the same sub list in parents (list of lists)
    def are_elements_in_same_sublist(self, tpl):
        return all(any(elem in sublist for sublist in self.parents) for elem in tpl)


    def check_if_in_the_same_subset(self, zipped):
        for tup in zipped:
            set_of_the_index = set()
            for arg in tup:
                sub_list_of_arg, index_of_sub_list_of_arg = self.find_sublist(arg)
                # print(index_of_sub_list_of_arg)
                set_of_the_index.add(index_of_sub_list_of_arg)
            # print("this is set_of_the_index:", set_of_the_index)
            if len(set_of_the_index) > 1:
                return False
        return True
    
    def merge_function_with_many_args(self, all_elements_in_cube):
        # print("this are all elements in cube: ", all_elements_in_cube)
        list_of_tuples_of_args = []
        list_of_functions_with_lots_of_args = []
        list_of_symbols_applications = set()
        for element in all_elements_in_cube:
            if element.is_function_application() and len(element.args()) > 1:
                # print(element)
                list_of_symbols_applications.add(element.function_name())
                # print(list_of_symbols_applications)
                list_of_functions_with_lots_of_args.append(element)
                list_of_tuples_of_args.append(element.args())
                # print(list_of_tuples_of_args)

        if len(list_of_symbols_applications) > 1:
            return self.parents
        
        zipped = list(zip(*list_of_tuples_of_args))
        # print("this is zipped", zipped)

        result = self.check_if_in_the_same_subset(zipped)
        # print(result)

        if result:
            self.parents = self.merge_all_sub_lists_of_elements(list_of_functions_with_lots_of_args)

        return self.parents


    def build_core(self):
        # print("this are parentsssssss: ", self.parents)
        core = self.parents.copy()
        for sub_list in self.parents:
            if len(sub_list) == 1 or len(sub_list) == 2:
                core.remove(sub_list)
                # print("core now: ", core)
        return core