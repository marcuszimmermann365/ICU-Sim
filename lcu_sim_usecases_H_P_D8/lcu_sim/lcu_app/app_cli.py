import argparse, os
import matplotlib.pyplot as plt
from lcu.controller import run
from lcu.plotting import plot_phi, plot_sep_heatmap
from .scenarios import build_scenario
from .metrics import compute_all_metrics

def main():
    p = argparse.ArgumentParser(description="LCU App CLI — Run predefined use cases and get insights.")
    p.add_argument("--use-case", required=True)
    p.add_argument("--backend", choices=["auto","meanfield","exact"], default=None)
    p.add_argument("--outdir", default="outputs")
    p.add_argument("--no-plot", action="store_true")
    p.add_argument("--save-csv", action="store_true")
    args = p.parse_args()

    spec, cfg = build_scenario(args.use_case)
    backend = args.backend if args.backend else spec.backend
    os.makedirs(args.outdir, exist_ok=True)
    res = run(cfg, backend=backend)

    metrics = compute_all_metrics(res)
    print("=== LCU Use Case:", spec.name, "===")
    print(spec.description)
    for k, v in metrics.items():
        try: print(f"{k}: {v:.6g}")
        except Exception: print(f"{k}: {v}")

    if args.save_csv:
        import csv
        csv_path = os.path.join(args.outdir, f"{spec.name}_phi.csv")
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t","phi"])
            for t, ph in zip(res["t"], res["phi"]):
                w.writerow([float(t), float(ph)])
        print("Saved:", csv_path)

    if not args.no_plot:
        if "phi" in res: plot_phi(res["t"], res["phi"], label=f"Phi ({spec.name})")
        if "separations" in res:
            plot_sep_heatmap(res["t"], res["separations"], N=getattr(cfg, "N_entities", 2), K=7, pair=(0,1))
        png_path = os.path.join(args.outdir, f"{spec.name}_plots.png")
        plt.savefig(png_path, dpi=140, bbox_inches="tight"); print("Saved plot:", png_path)
        plt.show()
