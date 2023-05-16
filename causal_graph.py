#!/usr/bin/python

import random
import numpy as np

import options 

class CausalGraph:
    def __init__(self, num_variables, edge_probability, seed):
        self.graph = {}
        self.method = "unknown_cg"
        self.num_variables = num_variables
        # self.edge_probability = None
        self.edge_probability = edge_probability
        self.max_precondition = None
        self.max_effect = None
        self.seed = seed

        random.seed(seed)
        np.random.seed(seed)

    """    
    def print_causal_graph(graph):
        dot = Digraph(format='png')
        nodes = set()
        for var in graph:
            nodes.add(var)
            for to_var in graph[var]:
                nodes.add(to_var)
        for node in nodes:
            dot.node(str(node), str(node))
        for var in graph:
            for to_var in graph[var]:
                dot.edge(str(var), str(to_var))
        dot.render('tmp.gv', view=True)
    """ 

    # def get_max_precondition(self):
    #     return self.max_precondition

    # def get_max_effect(self):
    #     return self.max_effect

    def is_leaf(self, var):
        return var not in self.graph or len(self.graph[var]) == 0

    def get_causal_graph_method_name(self):
        return self.method
    
    ##########################################################################################################
    def is_edge_to_be_added(self):
        assert(self.edge_probability)
        return np.random.choice([0,1], p=[1-self.edge_probability, self.edge_probability]) == 1

    def add_edge(self, from_var, to_var):
        if from_var not in self.graph:
            self.graph[from_var] = set()
        self.graph[from_var].add(to_var)
        
##########################################################################################################
class CausalGraphCustom(CausalGraph):
    def __init__(self, task_info, seed):
        CausalGraph.__init__(self, len(task_info["variables"]), 1, seed)

        self.method = "custom_cg"
        for edge in task_info["causal_graph_edges"]:
            self.add_edge(edge["from"], edge["to"])


class CausalGraphRandom(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method = "random_cg"

        ### TODO: Need to fix to make sure all are connected
        ## We can start with a tree and then add edges
        for var in range(0, self.num_variables):
            for to_var in range(0, self.num_variables):
                if (var != to_var):
                    if self.is_edge_to_be_added():
                        self.add_edge(var, to_var)


class CausalGraphChain(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "chain_cg"
        self.max_precondition = 2
        self.max_effect = 1

        ## For each pair of adjacent nodes we add at least one edge
        for var in range(0, self.num_variables-1):
            must_add = True
            if self.is_edge_to_be_added():
                must_add = False
                self.add_edge(var, var+1)
            if must_add or self.is_edge_to_be_added():
                self.add_edge(var+1, var)
                if not must_add:
                    self.max_effect = 2

class CausalGraphDirectedChain(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "directed_chain_cg"
        self.max_precondition = 2
        self.max_effect = 1

        for var in range(0, self.num_variables-1):
            self.add_edge(var, var+1)

class CausalGraphBipartite(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "bi_partite_cg"
        self.max_effect = 1

        ## Directed full bi-partite graph: all edges go from left to right
        num_vars_left = random.randint(1, self.num_variables-1)
        for var in range(0, num_vars_left):
            for to_var in range(num_vars_left, self.num_variables):
                self.add_edge(var, to_var)

class CausalGraphBidirectionalBipartite(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "bidirectional_bi_partite_cg"
        self.max_effect = 2

        ## Undirected full bi-partite graph
        num_vars_left = random.randint(1, self.num_variables-1)
        for var in range(0, num_vars_left):
            for to_var in range(num_vars_left, self.num_variables):
                self.add_edge(var, to_var)
                self.add_edge(to_var, var)

class CausalGraphFork(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "fork_cg"
        self.max_precondition = 2
        self.max_effect = 1

        for var in range(1, self.num_variables):
            self.add_edge(0, var)

class CausalGraphInvertedFork(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "inverted_fork_cg"
        self.max_effect = 1

        for var in range(1, self.num_variables):
            self.add_edge(var, 0)

class CausalGraphStar(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "star_cg"
        self.max_effect = 1

        ## For each non-center node, we add at least one edge to the center
        for var in range(1, self.num_variables):
            must_add = True
            if self.is_edge_to_be_added():
                must_add = False
                self.add_edge(0, var)
            if must_add or self.is_edge_to_be_added():
                self.add_edge(var, 0)
                if not must_add:
                    self.max_effect = 2

class CausalGraphTree(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)
        self.method =  "tree_cg"
        self.max_precondition = 2
        self.max_effect = 1

        ## For each node i, we choose a parent out of 0..i-1 
        ## This should result in a (weakly) connected graph, since 0..i-1 is a weakly connected component at step i 
        for var in range(1, self.num_variables):
            
            parent = random.randint(0, var-1)
            self.add_edge(parent, var)

class CausalGraphPolytree(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)
        self.method =  "polytree_cg"
        self.max_effect = 1

        ## For each node i, we choose a neighbour out of 0..i-1 and choose the direction
        ## This should result in a (weakly) connected graph, since 0..i-1 is a weakly connected component at step i 
        for var in range(1, self.num_variables):
            
            neigh = random.randint(0, var-1)
            if self.is_edge_to_be_added():
                self.add_edge(neigh, var)
            else:
                self.add_edge(var, neigh)

class CausalGraphDAG(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)
        self.method =  "dag_cg"
        self.max_effect = 1

        ## For each node i, we choose at least one parent out of 0..i-1 
        ## This should result in a (weakly) connected graph, since 0..i-1 is a weakly connected component at step i 
        for var in range(1, self.num_variables):
            parent_chosen = False
            while not parent_chosen:
                for parent in range(0, var):
                    if self.is_edge_to_be_added():
                        self.add_edge(parent, var)
                        parent_chosen = True


class CausalGraphComplete(CausalGraph):
    def __init__(self, num_variables, edge_probability, seed):
        CausalGraph.__init__(self, num_variables, edge_probability, seed)

        self.method =  "complete_cg"

        for var in range(0, self.num_variables-1):
            for to_var in range(var+1, self.num_variables):
                self.add_edge(var, to_var)
                self.add_edge(to_var, var)

class CausalGraphGenerator(object):
    def __init__(self, args, causal_graph_method=None):
        self.args = args
        self.seed = args.causal_graph_generator_seed
        if causal_graph_method:
            self.causal_graph_method = causal_graph_method
        else:
            ## All info taken from args 
            self.causal_graph_method = self.get_causal_graph_method_name_from_args()
            self.check_options()        

    def is_problem_dependent(self):
        return (self.causal_graph_method in ["random_cg", "chain_cg", "star_cg", "polytree_cg", "dag_cg"])

    def check_options(self):
        if int(self.args.random_cg) + int(self.args.chain_cg) + int(self.args.directed_chain_cg) \
            + int(self.args.bi_partite_cg) + int(self.args.fork_cg) + int(self.args.inverted_fork_cg) \
            + int(self.args.star_cg) + int(self.args.tree_cg) + int(self.args.polytree_cg) \
            + int(self.args.dag_cg) + int(self.args.complete_cg)  + int(self.args.bidirectional_bi_partite_cg) != 1:
            print("Exactly one of --random-cg --chain-cg --directed-chain-cg --bi-partite-cg --fork-cg --inverted-fork-cg --star-cg --tree-cg --polytree-cg --dag-cg --complete-cg --bidirectional-bi-partite-cg should be used!")
            exit(1)
                    
        if not self.args.edge_probability and self.is_problem_dependent():
            print("The option --edge-probability should be specified!")
            exit(1)

    def generate_causal_graph(self, num_variables=None, edge_probability=None):
        if not num_variables:
            num_variables = self.args.num_variables
        if not edge_probability:
            edge_probability = self.args.edge_probability

        if self.causal_graph_method == "random_cg":
            return CausalGraphRandom(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "chain_cg":
            return CausalGraphChain(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "directed_chain_cg":
            return CausalGraphDirectedChain(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "bi_partite_cg":
            return CausalGraphBipartite(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "fork_cg":
            return CausalGraphFork(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "inverted_fork_cg":
            return CausalGraphInvertedFork(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "star_cg":
            return CausalGraphStar(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "tree_cg":
            return CausalGraphTree(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "polytree_cg":
            return CausalGraphPolytree(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "dag_cg":
            return CausalGraphDAG(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "complete_cg":
            return CausalGraphComplete(num_variables, edge_probability, self.seed)
        if self.causal_graph_method == "bidirectional_bi_partite_cg":
            return CausalGraphBidirectionalBipartite(num_variables, edge_probability, self.seed)
        return None

    def get_causal_graph_method_name(self):
        return self.causal_graph_method

    def get_causal_graph_method_name_from_args(self):
        if self.args.random_cg:
            return "random_cg"
        if self.args.chain_cg:
            return "chain_cg"
        if self.args.directed_chain_cg:
            return "directed_chain_cg"
        if self.args.bi_partite_cg:
            return "bi_partite_cg"
        if self.args.fork_cg:
            return "fork_cg"
        if self.args.inverted_fork_cg:
            return "inverted_fork_cg"
        if self.args.star_cg:
            return "star_cg"
        if self.args.tree_cg:
            return "tree_cg"
        if self.args.polytree_cg:
            return "polytree_cg"
        if self.args.dag_cg:
            return "dag_cg"
        if self.args.complete_cg:
            return "complete_cg"
        if self.args.bidirectional_bi_partite_cg:
            return "bidirectional_bi_partite_cg"
        return "unknown_cg"


class CausalGraphCollectionGenerator(object):
    def __init__(self, args):
        self.args = args

    def get_prob_dependent_pairs(self):
        return [("random_cg", CausalGraphGenerator(self.args, "random_cg")), 
                ("chain_cg", CausalGraphGenerator(self.args, "chain_cg")), 
                ("star_cg", CausalGraphGenerator(self.args, "star_cg")), 
                ("polytree_cg", CausalGraphGenerator(self.args, "polytree_cg")), 
                ("dag_cg", CausalGraphGenerator(self.args, "dag_cg"))]
        
    def get_prob_independent_pairs(self):
        return [("directed_chain_cg", CausalGraphGenerator(self.args, "directed_chain_cg")), 
                ("fork_cg", CausalGraphGenerator(self.args, "fork_cg")), 
                ("inverted_fork_cg", CausalGraphGenerator(self.args, "inverted_fork_cg")), 
                ("tree_cg", CausalGraphGenerator(self.args, "tree_cg")),
                ("bi_partite_cg", CausalGraphGenerator(self.args, "bi_partite_cg")), 
                ("bidirectional_bi_partite_cg", CausalGraphGenerator(self.args, "bidirectional_bi_partite_cg")), 
                ("complete_cg", CausalGraphGenerator(self.args, "complete_cg"))]


        
if __name__ == "__main__":    
    args = options.parse_args()
    cggen = CausalGraphGenerator(args)
    cg = cggen.generate_causal_graph()
    print(cg.graph)
    

