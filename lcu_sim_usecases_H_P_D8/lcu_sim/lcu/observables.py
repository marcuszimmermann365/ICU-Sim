from __future__ import annotations
from typing import Dict, Tuple, List
import numpy as np
try:
    import qutip as qt
except Exception:
    qt = None

def separations(states: List, x_ops: Dict[Tuple[int,int], 'qt.Qobj']):
    out = {}
    for ti, state in enumerate(states):
        mu = {key: float(qt.expect(x, state)) for key, x in x_ops.items()}
        keys = list(x_ops.keys())
        for i, (n,k) in enumerate(keys):
            for j in range(i+1, len(keys)):
                (m,kk) = keys[j]
                if kk == k and m > n:
                    out[(ti,n,m,k)] = abs(mu[(n,k)] - mu[(m,k)])
    return out

def phi_metric(states: List, x_ops: Dict[Tuple[int,int], 'qt.Qobj']):
    phi = []
    for state in states:
        num = 0.0
        mu = {key: float(qt.expect(x, state)) for key, x in x_ops.items()}
        for _, x in x_ops.items():
            num += float(qt.expect(x*x, state))
        denom = 1.0
        keys = list(x_ops.keys())
        for i, (n,k) in enumerate(keys):
            for j in range(i+1, len(keys)):
                (m,kk) = keys[j]
                if kk == k and m > n:
                    denom += (mu[(n,k)] - mu[(m,k)])**2
        phi.append(num / denom)
    return np.array(phi, dtype=float)

def samadhi_time(phi_array, t_array, threshold: float = 0.8, dwell: float = 0.5):
    T = float(t_array[-1] - t_array[0]) if t_array[-1] > t_array[0] else 0.0
    window = dwell * T
    for i, t0 in enumerate(t_array):
        if phi_array[i] >= threshold:
            t_end = t0 + window
            mask = (t_array >= t0) & (t_array <= t_end)
            if getattr(mask, 'any', lambda: False)():
                frac = float((phi_array[mask] >= threshold).mean())
                if frac >= 0.9:
                    return float(t0)
    return float('inf')
