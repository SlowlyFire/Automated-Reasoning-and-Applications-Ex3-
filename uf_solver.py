# importing system module for reading files
import sys

# import utility functions
from utils import get_terms, get_function_symbols

# import classses for parsing smt2 files
from pysmt.smtlib.parser import SmtLibParser
from six.moves import cStringIO

# import pysmt functions for creating formulas and terms
from pysmt.shortcuts import Not, Equals, Function, And

# import the CongruenceClosure class
from congruence_closure import CongruenceClosure

# In order to solve and return sat/unsat
def uf_solver(cube):
    # Step1 - Initialize an empty list (will be list of lists)
    cc = CongruenceClosure()
    # print("Initial Cube:", cube)
    all_elements_in_cube = get_terms(cube)
    all_function_symbols_in_cube = get_function_symbols(cube)
    # print("this are all the elements: ", all_elements_in_cube)

    # Step2 - Iterate through the cube (all the literals), and build list of lists from them
    for literal in cube:
        # print("Processing Literal:", literal)
        if literal.is_not(): # If literal is inequality
            flag = "NOT_EQUALS"
            # Negation: add the inequality to the list of lists (each one of the members will its own list)
            inequality = literal.args()[0]
            x, y = inequality.args()
            # print("This is x (member of inequality): ", x)
            # print("This is y (member of inequality): ", y)
            cc.add_equality(x, y, flag)
        elif literal.is_equals(): # If literal is equality
            flag = "EQUALS"
            # Equality: add the equality to dictionary (members will have the same representative)
            x, y = literal.args()
            cc.add_equality(x, y, flag)
        else:
            # print("inside else, the format of the literal is unvalid")
            raise ValueError("Unexpected literal format: {}".format(literal))

    # print("\n")
    # print("the cube again is: ", cube)
    # print("Initial configuration: ")
    # cc.print_list_of_lists()
    # print("\n")

    # Step3 - Use Top-Level and Congruence, untill there is no change in parents (at the list of lists)
    last_state_parents = cc.parents.copy()
    # Use of Top Level
    while(True):
        cc.parents = cc.merge_using_toplevel()
        # print("###new merged parents toplevel:")
        # cc.print_list_of_lists()

        # If there is no change in parents (list of lists), then break (finished)
        if not cc.hasChanged(last_state_parents):
            break

        # Keep a copy of the current state of parents
        last_state_parents = cc.parents.copy() 

    # Use of Congruence - (maybe i need to insert it inside the while loop)
    cc.parents = cc.merge_using_congruence(all_elements_in_cube, all_function_symbols_in_cube)

    # Checks functions with more than 1 arg - (maybe i need to insert it inside the while loop)
    cc.parents = cc.merge_function_with_many_args(all_elements_in_cube)
    
    # Step4 - Check for a contradiction in the congruence closure structure
    for literal in cube:
        if literal.is_not(): # If literal is inequality
            inequality = literal.args()[0]
            x, y = inequality.args()
            # print("This is x (member of inequality): ", x)
            # print("This is y (member of inequality): ", y)

            # Check if they are in the same list
            for sub_list in cc.parents:
                if x in sub_list and y in sub_list:
                    # print("Found a contradiction, unsat!")
                    core = cc.build_core()
                    return False, core

    # If no contradiction            
    return True, None

# main function
def main():
    # read path from input
    path = sys.argv[1]
    with open(path, "r") as f:
        smtlib = f.read()

    # parse the smtlib file and get a formula
    parser = SmtLibParser()
    script = parser.get_script(cStringIO(smtlib))
    formula = script.get_last_formula()

    # we are assuming `formula` is a flat cube.
    # `cube` represents `formula` as a list of literals
    cube = formula.args()

    # check if sat or unsat and print result
    sat, core = uf_solver(cube)
    if sat:
        print("sat")
    else:
        print("unsat")
        print("-----")
        print("\n".join([str(x) for x in core]))

if __name__ == "__main__":
    main()










