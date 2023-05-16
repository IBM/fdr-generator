"""
The class holds an action, and allows for printing in STRIPS or FDR format
"""
import atom

class Action(object): 
    def __init__(self, preconditions, add_effects, delete_effects):
        self.preconditions = set(preconditions)
        self.add_effects = set(add_effects)
        self.delete_effects = set(delete_effects)
        self.id = None
        assert len(self.delete_effects - self.preconditions) == 0, (self.preconditions, self.delete_effects)
        assert len(self.delete_effects) == len(self.add_effects), (self.add_effects, self.delete_effects)


    def get_pddl(self, atoms_none_of_those):
        ## The idea is to ignore the none_of_those values. 
        ## Any value should be able to be chosen as none_of_those        
        pre = self.preconditions - atoms_none_of_those
        del_eff = self.delete_effects - atoms_none_of_those
        add_eff = self.add_effects - atoms_none_of_those
        pre_str = " ".join(atom.get_atoms_pddl(pre, False))
        del_effs_str = " ".join(atom.get_atoms_pddl(del_eff, True))
        add_effs_str = " ".join(atom.get_atoms_pddl(add_eff, False))
        return " (:action action_" + str(self.id) + "\n" + \
               "   :parameters () \n   :precondition (and " + pre_str + ") \n" + \
               "   :effect (and " + del_effs_str + " " +  add_effs_str  + ")) \n\n"


    def write_fdr(self, stream, get_var_val_fdr):
        prevail = [ get_var_val_fdr(fact) for fact in self.preconditions - self.delete_effects ]
        add_sorted = [ get_var_val_fdr(fact) for fact in self.add_effects]
        del_sorted = [ get_var_val_fdr(fact) for fact in self.delete_effects]
        add_sorted.sort()
        del_sorted.sort()    
        pre_post = []
        for a,b in zip(add_sorted,del_sorted):
            assert a[0] == b[0], (a, b)
            var = a[0]
            pre = b[1]
            post = a[1]
            pre_post.append((var, pre, post, []))            
        print("begin_operator", file=stream)
        print("action_" + str(self.id), file=stream)
        print(len(prevail), file=stream)
        
        for var, val in prevail:
            print(var, val, file=stream)
        print(len(pre_post), file=stream)
        for var, pre, post, cond in pre_post:
            print(len(cond), end=' ', file=stream)
            for cvar, cval in cond:
                print(cvar, cval, end=' ', file=stream)
            print(var, pre, post, file=stream)

        print("0", file=stream)   # Cost for no metric
        print("end_operator", file=stream)
        