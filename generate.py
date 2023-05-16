#! /usr/bin/env python3

import os
import sys
from math import floor, ceil
import timers

import logging
import utils
import options
from causal_graph import CausalGraphGenerator, CausalGraphCollectionGenerator
from planning_task import PlanningTask
from planning_task_custom import PlanningTaskCustom
import random

def print_usage():
    print("Usage: " + sys.argv[0] + " <num_atoms> <num_variables> <size_goal_state> <max_prevail_size> <max_effect_size> <max_atoms_per_layer> <prob_edge> <domain_file> <problem_file>")
    print("  num_atoms (min 4)")
    print("  num_variables (min 2  max num_atoms and num_atoms/num_variables is an integer)")
    print("  size_goal_state (min 1 max num_atoms)")
    print("  max_prevail_size (min 0 max num_variables) and max_prevail_size + max_effect_size <= num_variables")
    print("  max_effect_size (min 1 max num_variables) and max_prevail_size + max_effect_size <= num_variables")
    print("  max_atoms_per_layer (min 1)")
    print("  prob_edge")


def create_task_custom(max_atoms_per_layer, domain_file, problem_file, sas_file, opts):
    with timers.timing("Creating task" , False):
        task = PlanningTaskCustom(max_atoms_per_layer, opts)
    if not opts.sas_only:
        with timers.timing("Writing PDDL files: %s" % problem_file , False):
            task.write_pddl(None, None)
    if not opts.pddl_only:
        with timers.timing("Writing FDR file: %s" % sas_file , False):
            task.write_fdr(None)

def create_task(num_atoms, num_variables, num_goal_variables, max_num_prevails, max_num_effects, max_atoms_per_layer, causal_graph, domain_file, problem_file, sas_file, opts):
    with timers.timing("Creating task" , False):
        task = PlanningTask(num_atoms, num_variables, num_goal_variables, max_num_prevails, max_num_effects, max_atoms_per_layer, causal_graph, opts)
    if not opts.sas_only:
        with timers.timing("Writing PDDL files: %s" % problem_file , False):
            task.write_pddl(domain_file, problem_file)
    if not opts.pddl_only:
        with timers.timing("Writing FDR file: %s" % sas_file , False):
            task.write_fdr(sas_file)            

def get_uniform_sample(min_val, max_val, sample_size):
    ret = random.sample(range(min_val, max_val), sample_size)
    ret.sort()
    return ret

def get_possible_num_variables(atoms, sample_size=4):
    ## We choose the values between 10 (minimal) and  int(floor(atoms / 2))
    min_val = 10
    max_val = int(floor(atoms / 2)) 
    return get_uniform_sample(min_val, max_val, sample_size)
    

def get_possible_num_goals(vars, sample_size=4):
    min_val = 1
    max_val = int(ceil(vars / 2)) + 1
    return get_uniform_sample(min_val, max_val, sample_size)


def get_possible_num_prevails(sample_size=2):
    min_val = 1
    max_val = 10
    return get_uniform_sample(min_val, max_val, sample_size)

def get_possible_num_effects(sample_size=2):
    min_val = 1
    max_val = 10
    return get_uniform_sample(min_val, max_val, sample_size)

def get_possible_num_atoms_per_layer(atoms, sample_size=2):
    min_val = 5
    max_val = int(ceil(atoms/10))
    return get_uniform_sample(min_val, max_val, sample_size)

    
def generate_domain(domain_name, cggen, edge_probability, args):
    ATOMS = range(200, 1001, 200)
    #ATOMS.extend(range(1000, 5001, 200))

    folder_name = domain_name
    logging.info("Generating domain %s" % folder_name) 
    utils.create_missing_folder(folder_name)
    for num_atoms in ATOMS:
        generate_domain_instances(domain_name, num_atoms, cggen, edge_probability, args)


def generate_domain_instances(domain_name, num_atoms, cggen, edge_probability, args, number_of_variables=None, number_of_goals=None):
    ### The domain is defined by the causal graph structure, with different numbers of variables
    
    folder_name = domain_name
    logging.info("Generating domain %s, number of atoms: %s" % (folder_name, num_atoms))
    utils.create_missing_folder(folder_name)
    if number_of_variables:
        vars_list = [number_of_variables]
    else:
        vars_list = get_possible_num_variables(num_atoms)
    atoms_per_layer = get_possible_num_atoms_per_layer(num_atoms)
    prevails_list = get_possible_num_prevails()
    effects_list = get_possible_num_effects()
    for num_variables in vars_list:
        if number_of_goals:
            goals_list = [number_of_goals]
        else:
            goals_list = get_possible_num_goals(num_variables)
        for num_goals in goals_list:
            for max_num_prevails in prevails_list:
                for max_num_effects in effects_list:
                    for max_atoms_per_layer in atoms_per_layer:
                        problem_file_name = "prob-%04d-%04d-%04d-%02d-%02d-%02d.pddl" % (num_atoms, num_variables, num_goals, max_num_prevails, max_num_effects, max_atoms_per_layer)
                        sas_file_name = "output-%04d-%04d-%04d-%02d-%02d-%02d.sas" % (num_atoms, num_variables, num_goals, max_num_prevails, max_num_effects, max_atoms_per_layer)

                        domain_file = os.path.join(folder_name, "domain-%s" % problem_file_name)
                        problem_file = os.path.join(folder_name, problem_file_name)
                        sas_file = os.path.join(folder_name, sas_file_name)
                        cg = cggen.generate_causal_graph(num_variables, edge_probability)
                        create_task(num_atoms, num_variables, num_goals, max_num_prevails, max_num_effects, max_atoms_per_layer, cg, domain_file, problem_file, sas_file, args)

 
# NEEDS UPDATE
def generate_collection(args):
    cgcolgen = CausalGraphCollectionGenerator(args)
    for prob in [0.01, 0.1, 0.25, 0.5, 0.75]:
        for name, cggen in cgcolgen.get_prob_dependent_pairs():
            generate_domain(name+ "_%s" % prob, cggen, prob, args)

    for name, cggen in cgcolgen.get_prob_independent_pairs():
        generate_domain(name, cggen, 1, args)

    
if __name__ == "__main__":    
    args = options.parse_args()

    random.seed(args.seed)
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)-8s %(message)s",
                        stream=sys.stdout)

    if int(args.task) + int(args.domain) + int(args.collection) != 1:
        logging.error("Exactly one of --task, --domain, and --collection should be used!")
        exit(1)
    
    if args.task:
        if args.input_json_file_name:
            create_task_custom(args.max_atoms_per_layer,args.domain_file_name, args.problem_file_name, args.sas_file_name, args)
            exit(0)
        if not args.num_variables or args.num_goal_variables is None or args.max_num_prevails is None or args.max_num_effects is None or not args.max_atoms_per_layer:
            logging.error("All task options should be used!")
            logging.error("--num-variables --num-goal-variables --max-num-prevails --max-num-effects --max-atoms-per-layer")
            exit(1)

        if (not args.num_atoms and not args.average_domain_size) or (args.num_atoms and args.average_domain_size):
            logging.error("Exactly one of --num-atoms or --average-domain-size should be used")
            exit(1)

         
        if (not args.domain_file_name or not args.problem_file_name) and not args.sas_file_name:
            logging.error("At least one of PDDL or FDR task names should be specified")
            logging.error("--domain-file-name --problem-file-name --sas-file-name")
            exit(1)

        if args.average_domain_size:
            args.num_atoms = args.average_domain_size * args.num_variables

        cggen = CausalGraphGenerator(args)
        cg = cggen.generate_causal_graph()
        #logging.info(cg.graph)
        create_task(args.num_atoms, args.num_variables, args.num_goal_variables, args.max_num_prevails, args.max_num_effects, args.max_atoms_per_layer, cg, args.domain_file_name, args.problem_file_name, args.sas_file_name, args)

    if args.domain:
        cggen = CausalGraphGenerator(args)
        domain_name = cggen.get_causal_graph_method_name()
        if cggen.is_problem_dependent():
            domain_name = "%s_%s" % (domain_name, args.edge_probability)
        if args.num_atoms:
            num_vars = None
            if args.num_variables:
                num_vars = args.num_variables
            num_goals = None
            if args.num_goal_variables:
                num_goals = args.num_goal_variables
            generate_domain_instances(domain_name, args.num_atoms, cggen, args.edge_probability, args, number_of_variables=num_vars, number_of_goals=num_goals)
        else:
            generate_domain(domain_name, cggen, args.edge_probability, args)

    if args.collection:
        generate_collection(args)
    
    #print_usage()

    

