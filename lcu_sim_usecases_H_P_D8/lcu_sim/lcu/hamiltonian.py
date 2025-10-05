from __future__ import annotations
from typing import Tuple, Dict
import numpy as np
from .config import LCUConfig
try:
    import qutip as qt
except Exception:
    qt = None

def build_dims(cfg: LCUConfig) -> int:
    return cfg.N_entities * (7 + cfg.n_phys_modes)

def mode_index(entity: int, chakra_or_phys_idx: int, cfg: LCUConfig) -> int:
    return entity * (7 + cfg.n_phys_modes) + chakra_or_phys_idx

def build_exact_h(cfg: LCUConfig) -> Tuple:
    assert qt is not None, "QuTiP benötigt (pip install .[exact])."
    cfg.validate()
    d = cfg.d_trunc
    total_modes = build_dims(cfg)
    h_terms = []
    x_ops: Dict[tuple, 'qt.Qobj'] = {}

    def lift(op, idx):
        fac = [qt.qeye(d) for _ in range(total_modes)]
        fac[idx] = op
        return qt.tensor(fac)

    # Chakra modes
    a = qt.destroy(d); adag = a.dag()
    xloc = (a + adag)/np.sqrt(2.0); nloc = adag*a

    for e in range(cfg.N_entities):
        for k in range(7):
            idx = mode_index(e, k, cfg)
            xk = lift(xloc, idx); nk = lift(nloc, idx)
            x_ops[(e,k)] = xk
            h_terms.append(cfg.omega_cons[k] * nk)

    # Cross-coupling within entity (chakras)
    if cfg.g_cons_offdiag != 0.0:
        for e in range(cfg.N_entities):
            for k in range(7):
                for l in range(k+1,7):
                    h_terms.append(cfg.g_cons_offdiag * x_ops[(e,k)] * x_ops[(e,l)])

    # Physical modes + coupling
    if cfg.n_phys_modes > 0:
        for e in range(cfg.N_entities):
            for p in range(cfg.n_phys_modes):
                idxp = mode_index(e, 7+p, cfg)
                xp = lift(xloc, idxp); npop = lift(nloc, idxp)
                h_terms.append(cfg.omega_phys * npop)
                if cfg.g_phys_cons != 0.0:
                    for k in range(7):
                        h_terms.append(cfg.g_phys_cons * xp * x_ops[(e,k)])

    # Love harmonic
    for n in range(cfg.N_entities):
        for m in range(n+1, cfg.N_entities):
            for k in cfg.active_chakras:
                dx = x_ops[(n,k)] - x_ops[(m,k)]
                h_terms.append(0.5 * cfg.k_love * (dx*dx))

    H = sum(h_terms)
    return H, x_ops

def build_yoga_drive(cfg: LCUConfig, x_ops):
    if ((cfg.gamma_drive == 0.0) and not cfg.gamma_map) or (cfg.t_yoga is None):
        return None
    def H_t(t, args):
        zero = 0 * next(iter(x_ops.values()))
        if t < cfg.t_yoga:
            return zero
        term = zero
        if cfg.gamma_map:
            for (e,k), xop in x_ops.items():
                if k in cfg.active_chakras:
                    g = cfg.gamma_map.get((e,k), 0.0)
                    if g != 0.0:
                        term = term + g * xop
        else:
            for (e,k), xop in x_ops.items():
                if k in cfg.active_chakras:
                    term = term + cfg.gamma_drive * xop
        return term
    return H_t

def build_lindblad_ops(cfg: LCUConfig, x_ops):
    if qt is None:
        return []
    c_ops = []
    # relative damping (x_n - x_m)
    if cfg.kappa_relax > 0.0 and (cfg.always_on_env or cfg.t_yoga is not None):
        for k in cfg.active_chakras:
            for n in range(cfg.N_entities):
                for m in range(n+1, cfg.N_entities):
                    scale_n = cfg.lindblad_scale_map.get((n,k), cfg.kappa_relax) if cfg.lindblad_scale_map else cfg.kappa_relax
                    scale_m = cfg.lindblad_scale_map.get((m,k), cfg.kappa_relax) if cfg.lindblad_scale_map else cfg.kappa_relax
                    scale = 0.5*(scale_n + scale_m)
                    c_ops.append(np.sqrt(scale) * (x_ops[(n,k)] - x_ops[(m,k)]))
    # local amplitude damping (a-op) and dephasing (x-op)
    if cfg.kappa_local > 0.0 or cfg.kphi_dephase > 0.0:
        d = cfg.d_trunc
        a = qt.destroy(d)
        total = build_dims(cfg)
        for e in range(cfg.N_entities):
            for k in cfg.active_chakras:
                idx = mode_index(e, k, cfg)
                fac = [qt.qeye(d) for _ in range(total)]
                fac[idx] = a
                ag = qt.tensor(fac)
                if cfg.kappa_local > 0.0:
                    c_ops.append(np.sqrt(cfg.kappa_local) * ag)
                if cfg.kphi_dephase > 0.0:
                    c_ops.append(np.sqrt(cfg.kphi_dephase) * x_ops[(e,k)])
    return c_ops
