from __future__ import annotations
from typing import Dict, Any
import numpy as np

def avg_separation(res, pair=(0,1), K=7) -> float:
    tlen = len(res["t"])
    vals = [res["separations"][(ti, pair[0], pair[1], k)] for ti in range(tlen) for k in range(K) if (ti, pair[0], pair[1], k) in res["separations"]]
    return float(np.mean(vals)) if len(vals)>0 else float('nan')

def phi_gain(res) -> float:
    phi = res["phi"]; return float(phi[-1]-phi[0])

def compute_all_metrics(res, **kwargs) -> Dict[str, Any]:
    return {
        "phi_start": float(res["phi"][0]),
        "phi_end": float(res["phi"][-1]),
        "phi_gain": phi_gain(res),
        "avg_sep_pair01": avg_separation(res),
    }
