import argparse
import matplotlib.pyplot as plt
from .config import LCUConfig
from .controller import run
from .plotting import plot_phi, plot_sep_heatmap

def main():
    p = argparse.ArgumentParser(description="LCU Simulation CLI")
    p.add_argument("--backend", choices=["auto","meanfield","exact"], default="auto")
    p.add_argument("--n", type=int, default=2)
    p.add_argument("--d", type=int, default=10)
    p.add_argument("--t-max", type=float, default=10.0)
    p.add_argument("--n-steps", type=int, default=200)
    p.add_argument("--k-love", type=float, default=0.1)
    p.add_argument("--g-cons", type=float, default=0.0)
    p.add_argument("--t-yoga", type=float, default=None)
    p.add_argument("--gamma", type=float, default=0.0)
    p.add_argument("--kappa-relax", type=float, default=0.0)
    p.add_argument("--kappa-local", type=float, default=0.0)
    p.add_argument("--omega-cons", type=float, nargs=7, default=[1,1,1,1,1,1,1])
    p.add_argument("--weights", type=float, nargs=7, default=[1,1,1,1,1,1,1])
    p.add_argument("--love-mode", choices=["harmonic","inverse"], default="harmonic")
    p.add_argument("--n-phys", type=int, default=0)
    p.add_argument("--omega-phys", type=float, default=1.0)
    p.add_argument("--g-phys-cons", type=float, default=0.0)
    p.add_argument("--always-on-env", action="store_true")
    p.add_argument("--no-plot", action="store_true")
    args = p.parse_args()

    cfg = LCUConfig(
        N_entities=args.n, d_trunc=args.d, t_max=args.t_max, n_steps=args.n_steps,
        k_love=args.k_love, g_cons_offdiag=args.g_cons, t_yoga=args.t_yoga,
        gamma_drive=args.gamma, kappa_relax=args.kappa_relax,
        kappa_local=args.kappa_local, omega_cons=args.omega_cons, w_chakra=args.weights,
        use_qutip=(args.backend in ["auto","exact"]), love_mode=args.love_mode,
        n_phys_modes=args.n_phys, omega_phys=args.omega_phys, g_phys_cons=args.g_phys_cons,
        always_on_env=args.always_on_env
    )
    res = run(cfg, backend=args.backend)

    if not args.no_plot:
        if "phi" in res: plot_phi(res["t"], res["phi"])
        if "separations" in res:
            pair = (0,1) if cfg.N_entities >= 2 else (0,0)
            plot_sep_heatmap(res["t"], res["separations"], N=cfg.N_entities, K=7, pair=pair)
        plt.show()
    else:
        print("Done. Keys:", list(res.keys()))
