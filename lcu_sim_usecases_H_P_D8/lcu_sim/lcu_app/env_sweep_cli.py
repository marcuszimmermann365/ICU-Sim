import argparse, numpy as np
from lcu.controller import run
from lcu.config import LCUConfig

def main():
    p = argparse.ArgumentParser(description="LCU Env-Sweep — match Monastery Phi in Metropolis by sweeping k_love")
    p.add_argument("--phi-target", type=float, default=None)
    p.add_argument("--k-min", type=float, default=0.0)
    p.add_argument("--k-max", type=float, default=0.5)
    p.add_argument("--k-steps", type=int, default=21)
    args = p.parse_args()

    if args.phi_target is None:
        cfgA = LCUConfig(N_entities=50, use_qutip=False, t_max=20.0, n_steps=400,
                         k_love=0.08, always_on_env=True, kappa_local=0.005)
        resA = run(cfgA, backend="meanfield")
        phi_target = float(resA["phi"][-1])
    else:
        phi_target = args.phi_target

    best_k = None
    ks = np.linspace(args.k_min, args.k_max, args.k_steps)
    for k in ks:
        cfgB = LCUConfig(N_entities=50, use_qutip=False, t_max=20.0, n_steps=400,
                         k_love=float(k), always_on_env=True, kappa_local=0.05)
        resB = run(cfgB, backend="meanfield")
        phi_end = float(resB["phi"][-1])
        print(f"k_love={k:.3f} -> Phi_end={phi_end:.4f}")
        if phi_end >= phi_target and best_k is None:
            best_k = float(k)
    if best_k is None:
        print("No k_love in sweep reached target Phi (increase k-max).")
    else:
        print(f"Minimal k_love to reach target Phi≈{phi_target:.4f}: {best_k:.3f}")
