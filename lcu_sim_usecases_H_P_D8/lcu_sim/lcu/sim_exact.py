from __future__ import annotations
from typing import Optional
import numpy as np
from .config import LCUConfig
from .hamiltonian import build_exact_h, build_yoga_drive, build_lindblad_ops
from .observables import separations, phi_metric

try:
    import qutip as qt
except Exception:
    qt = None

def initial_state_coherent(cfg: LCUConfig, alpha_entity: Optional[list] = None):
    assert qt is not None, "QuTiP benötigt."
    if alpha_entity is None:
        alpha_entity = [1.0] + [0.0]*(cfg.N_entities-1)
    d = cfg.d_trunc
    states = []
    for e in range(cfg.N_entities):
        a_e = alpha_entity[e] if e < len(alpha_entity) else 0.0
        for k in range(7):
            states.append(qt.coherent(d, a_e))
        for _ in range(cfg.n_phys_modes):
            states.append(qt.basis(d, 0))
    return qt.tensor(states)

def run_exact(cfg: LCUConfig, psi0=None):
    assert qt is not None, "QuTiP benötigt (pip install .[exact])."
    cfg.validate()
    H0, x_ops = build_exact_h(cfg)
    tlist = cfg.tlist(); args = {}
    H = H0
    H_t = build_yoga_drive(cfg, x_ops)
    if H_t is not None:
        H = [H0, [H_t, args]]
    if psi0 is None:
        psi0 = initial_state_coherent(cfg)
    c_ops = build_lindblad_ops(cfg, x_ops)

    if (not cfg.always_on_env) and (cfg.kappa_relax > 0.0) and (cfg.t_yoga is not None):
        t1 = tlist[tlist < cfg.t_yoga]; t2 = tlist[tlist >= cfg.t_yoga]
        states_all = []
        if len(t1) > 0:
            res1 = qt.mesolve(H, psi0, t1, c_ops=[], args=args); states_all.extend(res1.states); psi_mid = res1.states[-1]
        else:
            psi_mid = psi0
        if len(t2) > 0:
            res2 = qt.mesolve(H, psi_mid, t2, c_ops=c_ops, args=args); states_all.extend(res2.states)
        states = states_all
    else:
        res = qt.mesolve(H, psi0, tlist, c_ops=c_ops, args=args); states = res.states

    sep = separations(states, x_ops); phi = phi_metric(states, x_ops)
    return {"t": tlist, "states": states, "separations": sep, "phi": phi}
