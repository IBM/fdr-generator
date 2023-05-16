class Atom(object):
    def __init__(self, _id):
        self.id = _id

    def get_pddl(self, is_negated):
        ret = "(atom_" + str(self.id) +")"
        if is_negated:
            return "(not %s)" % ret
        return ret

    def get_fdr(self, is_negated):
        ret = "Atom atom_" + str(self.id) +"()"
        if is_negated:
            return "Negated%s" % ret
        return ret

def get_atoms_pddl(atoms, is_negated):
    atoms = [ x if isinstance(x, Atom) else Atom(x) for x in atoms ]
    return [x.get_pddl(is_negated) for x in atoms]

def get_atoms_fdr(atoms, is_negated):
    atoms = [ x if isinstance(x, Atom) else Atom(x) for x in atoms ]
    return [x.get_fdr(is_negated) for x in atoms]

def get_atoms_to_string_pddl(atoms, is_negated):
    return " ".join(get_atoms_pddl(atoms, is_negated))
