"""fogsim -- simulator for data-/bandwidth-aware DAG scheduling in
federated fog systems, matching the model and algorithms of the paper.

The four schedulers live in their own modules:

    milp      -- exact MILP via scipy.optimize.milp (HiGHS backend)
    rounding  -- LP relaxation + randomized rounding of the assignment
    greedy    -- Algorithm 1: bandwidth/data-aware greedy DAG scheduler
    ga        -- Algorithm 2: genetic algorithm

Entry point (run from the project root):

    python3 code/fogsim.py gen    --tasks 50 --nodes 5 --seed 0
    python3 code/fogsim.py sweep  slack --tasks 30 --nodes 4 --reps 5
    python3 code/fogsim.py plot
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
INST_DIR = os.path.join(ROOT, "data", "instances")
RES_DIR = os.path.join(ROOT, "data", "results")
FIG_DIR = os.path.join(RES_DIR, "figures")

from .instance import Instance, generate_instance, save_instance, load_instance
from .milp import run_milp
from .rounding import run_rounding
from .greedy import run_greedy
from .ga import run_ga
from .experiments import evaluate, sweep, plot
