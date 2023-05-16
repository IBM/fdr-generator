#!/usr/bin/python

import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", help="Generate a single task", action="store_true")
    parser.add_argument("--domain", help="Generate a domain", action="store_true")
    parser.add_argument("--collection", help="Generate a collection of domains", action="store_true")

    parser.add_argument("--input-json-file-name", help="The name of the sas file to read from")

    parser.add_argument("--num-atoms", type=int, help="The number of atoms, min 4")
    parser.add_argument("--average-domain-size", type=int, help="The average domain size per variable, to be used with the number of variables instead of num_atoms")
    parser.add_argument("--num-variables", type=int, help="The number of variables, no more than half of the atoms")
    parser.add_argument("--num-goal-variables", type=int, help="The number of non-leaf goal variables, min 0, no more than --num-variables")
    parser.add_argument("--max-num-prevails", type=int, help="The upper bound on the number of prevails, no more than --num-variables")
    parser.add_argument("--max-num-effects", type=int, help="The upper bound on the number of effects, min 1, no more than --num-variables")
    parser.add_argument("--max-atoms-per-layer", type=int, help="The upper bound on the number of new atoms added per layer, min 1, no more than --num-atoms")
    parser.add_argument("--edge-probability", type=float, help="The probability of generating an edge in the causal graph, number in (0,1]")

    ## probabilities for variables
    parser.add_argument("--exactly-one-of-mutex-probability", type=float, help="The probability of a mutex to be exactly one of instead of at most one of, number in (0,1]", default=0.1)

    ## probabilities for action generation
    parser.add_argument("--unconditioned-eff-probability", type=float, help="The probability of an effect to not have a precondition specified, number in (0,1]", default=0.1)
    parser.add_argument("--non-contributing-actions-add-probability", type=float, help="The probability of an effect to not have a precondition specified, number in (0,1]", default=0.1)
    parser.add_argument("--enforce-new-atom-probability", type=float, help="The probability of enforcing an action to add a new atom, number in (0,1]", default=0.1)
    parser.add_argument("--enforce-new-atom-no-edge-probability", type=float, help="The probability of enforcing an action to add a new atom, without contributing an edge to the causal graph (always possible) number in (0,1]", default=0.01)

    parser.add_argument("--domain-file-name", help="The name of the domain file to write to", default="domain.pddl")
    parser.add_argument("--problem-file-name", help="The name of the problem file to write to", default="problem.pddl")
    parser.add_argument("--sas-file-name", help="The name of the sas file to write to", default="output.sas")

    parser.add_argument("--random-cg", help="A random causal graph", action="store_true")
    parser.add_argument("--chain-cg", help="A chain causal graph", action="store_true")
    parser.add_argument("--directed-chain-cg", help="A chain causal graph", action="store_true")
    parser.add_argument("--bi-partite-cg", help="A bi-partite causal graph", action="store_true")
    parser.add_argument("--fork-cg", help="A fork causal graph", action="store_true")
    parser.add_argument("--inverted-fork-cg", help="An inverted fork causal graph", action="store_true")
    parser.add_argument("--star-cg", help="A star causal graph", action="store_true")
    parser.add_argument("--tree-cg", help="A tree causal graph", action="store_true")
    parser.add_argument("--polytree-cg", help="A polytree causal graph", action="store_true")
    parser.add_argument("--dag-cg", help="A DAG causal graph", action="store_true")
    parser.add_argument("--complete-cg", help="A complete graph causal graph", action="store_true")
    parser.add_argument("--bidirectional-bi-partite-cg", help="An undirected complete bipartite causal graph", action="store_true")
  
    parser.add_argument("--seed", type=int, help="Random seed", default=0)
    parser.add_argument("--causal-graph-generator-seed", type=int, help="Random seed for the causal graph generator", default=2020)
    parser.add_argument("--pddl-only", help="Dump PDDL only", action="store_true")
    parser.add_argument("--sas-only", help="Dump SAS+ only", action="store_true")

    return parser.parse_args()
        
def copy_args_to_module(args):
    module_dict = sys.modules[__name__].__dict__
    for key, value in vars(args).items():
        module_dict[key] = value


def setup():
    args = parse_args()
    copy_args_to_module(args)


setup()