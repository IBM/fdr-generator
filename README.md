# FDR instance generation

The repository includes the code for generating planning tasks according to specified structure

## Citing
```
@InProceedings{katz-et-al-socs2023,
  title =        "Generating SAS+ Planning Tasks of Specified Causal Structure",
  author =       "Michael Katz and Junkyu Lee and Shirin Sohrabi",
  booktitle =    "Proceedings of the 16th Annual Symposium on
                  Combinatorial Search (SoCS 2023)",
  publisher =    "{AAAI} Press",
  year =         "2023"
}
```



## Example usage:

### Single task generation
```
./generate.py --task --num-atoms 100 --num-variables 10 --num-goal-variables 4 --max-num-prevails 2 --max-num-effects 3 --max-atoms-per-layer 10 --domain-file-name domain.pddl --problem-file-name problem.pddl --sas-file-name output.sas --polytree-cg --edge-probability 0.2
```

### Domain generation
```
./generate.py --domain --inverted-fork-cg --num-atoms 200
```
or, for a default set of possible number of atoms:
```
./generate.py --domain --inverted-fork-cg
```

### Single task generated from an input PDDL task
```
./generate.py --task --input-json-file-name examples/sas_task.json --seed 2023
```

The json input file with task parameters can be obtained from pddl files by 
building the code in [this Fast Downward Fork](https://github.com/ctpelok77/downward/tree/causal_graph), and
running the following (producing the file named `sas_task.json`):
 ```
./fast-downward.py domain.pddl problem.pddl --search 'lazy_greedy([cg(),const(infinity)])'
```

