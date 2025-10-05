import argparse, os, itertools, math, random
from lcu.controller import run
from lcu.config import LCUConfig
from lcu.observables import samadhi_time
from lcu_app.scenarios import build_scenario

def main():
    p = argparse.ArgumentParser(description="LCU Optimizer — minimize Samadhi time")
    p.add_argument("--use-case", default="GD6")
    p.add_argument("--E", type=float, default=0.6)
    p.add_argument("--fraction", type=float, nargs=3, default=[0.25, 0.5, 0.75])
    p.add_argument("--chakra", type=int, nargs=3, default=[3, 5, 6])
    p.add_argument("--seed", type=int, default=123)
    args = p.parse_args()

    spec, cfg = build_scenario(args.use_case)
    N = cfg.N_entities; random.seed(args.seed)
    best = (math.inf, None, None)

    for f in args.fraction:
        cnt = max(1, int(N * f)); targets = random.sample(range(N), cnt)
        for k in args.chakra:
            gamma_val = args.E / cnt
            cfg_iter = LCUConfig(**{**cfg.__dict__})
            cfg_iter.gamma_map = {(e,k): gamma_val for e in targets}
            res = run(cfg_iter, backend="meanfield")
            t0 = samadhi_time(res["phi"], res["t"], threshold=0.9, dwell=0.5)
            if t0 < best[0]: best = (t0, f, k)

    print("Best Samadhi time:", best[0])
    print("Best fraction:", best[1], "Best chakra:", best[2])
