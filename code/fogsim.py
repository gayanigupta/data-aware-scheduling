#!/usr/bin/env python3
"""fogsim -- command-line entry point.

The implementation lives in the fogsim package (code/fogsim/); this file
only parses arguments.  Run from the project root:

  python3 code/fogsim.py gen    --tasks 50 --nodes 5 --seed 0
  python3 code/fogsim.py sweep  slack --tasks 30 --nodes 4 --reps 5
  python3 code/fogsim.py plot
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fogsim import (INST_DIR, generate_instance, save_instance,
                    sweep, plot)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen", help="generate an instance JSON")
    g.add_argument("--tasks", type=int, default=50)
    g.add_argument("--nodes", type=int, default=5)
    g.add_argument("--alpha", type=float, default=1.5)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--out", default=None)

    s = sub.add_parser("sweep", help="run an experiment sweep -> CSV")
    s.add_argument("kind", choices=["slack", "nodes", "size", "failure"])
    s.add_argument("--tasks", type=int, default=50)
    s.add_argument("--nodes", type=int, default=5)
    s.add_argument("--reps", type=int, default=5)
    s.add_argument("--seed", type=int, default=0)

    sub.add_parser("plot", help="render sweep CSVs to PNG figures")

    args = ap.parse_args()

    if args.cmd == "gen":
        inst = generate_instance(n_tasks=args.tasks, n_nodes=args.nodes,
                                 alpha=args.alpha, seed=args.seed)
        os.makedirs(INST_DIR, exist_ok=True)
        out = args.out or os.path.join(
            INST_DIR, f"dag{args.tasks}_nodes{args.nodes}"
                      f"_a{args.alpha}_s{args.seed}.json")
        save_instance(inst, out)
        print("wrote", out)
    elif args.cmd == "sweep":
        sweep(args.kind, tasks=args.tasks, nodes=args.nodes,
              reps=args.reps, seed=args.seed)
    else:
        plot()


if __name__ == "__main__":
    main()
