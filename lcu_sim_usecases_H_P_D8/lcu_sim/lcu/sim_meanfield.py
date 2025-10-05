from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List
from .config import LCUConfig

@dataclass
class MFState:
    x: np.ndarray  # (N, Kc+Kp)
    p: np.ndarray

def _pairs_to_matrix(pairs, N, Kc):
    M = np.zeros((N,Kc))
    for e,k,v in pairs:
        if 0 <= e < N and 0 <= k < Kc:
            M[e,k] = v
    return M

def _current_maps(cfg: LCUConfig, tnow: float, N: int, Kc: int):
    G = np.zeros((N,Kc))
    if cfg.gamma_drive != 0.0:
        G[:, cfg.active_chakras] += cfg.gamma_drive
    if cfg.gamma_map:
        for (e,k), v in cfg.gamma_map.items():
            if 0 <= e < N and 0 <= k < Kc:
                G[e,k] += v
    if cfg.gamma_schedule:
        eligible = [seg for seg in cfg.gamma_schedule if seg.get("t", 0.0) <= tnow]
        if eligible:
            seg = sorted(eligible, key=lambda s: s.get("t",0.0))[-1]
            pairs = seg.get("gamma_pairs", [])
            G = _pairs_to_matrix(pairs, N, Kc)

    KAP = np.full((N,Kc), cfg.kappa_relax)
    if cfg.lindblad_scale_map:
        for (e,k), v in cfg.lindblad_scale_map.items():
            if 0 <= e < N and 0 <= k < Kc:
                KAP[e,k] = v
    if cfg.lindblad_schedule:
        eligible = [seg for seg in cfg.lindblad_schedule if seg.get("t", 0.0) <= tnow]
        if eligible:
            seg = sorted(eligible, key=lambda s: s.get("t",0.0))[-1]
            pairs = seg.get("kappa_pairs", [])
            KAP = _pairs_to_matrix(pairs, N, Kc)
    return G, KAP

def _get_kappa_local_at(cfg: LCUConfig, tnow: float) -> float:
    val = float(getattr(cfg, "kappa_local", 0.0))
    sch = getattr(cfg, "kappa_local_schedule", None)
    if sch:
        eligible = [seg for seg in sch if seg.get("t", 0.0) <= tnow]
        if eligible:
            seg = sorted(eligible, key=lambda s: s.get("t",0.0))[-1]
            val = float(seg.get("kappa_local", val))
    return val

def _get_gamma_phys_at(cfg: LCUConfig, tnow: float) -> float:
    val = float(getattr(cfg, "gamma_phys_drive", 0.0))
    sch = getattr(cfg, "gamma_phys_schedule", None)
    if sch:
        eligible = [seg for seg in sch if seg.get("t", 0.0) <= tnow]
        if eligible:
            seg = sorted(eligible, key=lambda s: s.get("t",0.0))[-1]
            val = float(seg.get("gamma_phys", val))
    return val

def run_meanfield(cfg: LCUConfig, x0: Optional[np.ndarray]=None, p0: Optional[np.ndarray]=None):
    cfg.validate()
    N = cfg.N_entities
    Kc = 7
    Kp = int(getattr(cfg, "n_phys_modes", 0))
    Ktot = Kc + Kp
    h = cfg.t_max / (cfg.n_steps - 1)
    t = np.linspace(0.0, cfg.t_max, cfg.n_steps)

    if x0 is None:
        x0 = np.zeros((N,Ktot)); 
        if N > 0: x0[0,:Kc] = 1.0
    if p0 is None:
        p0 = np.zeros((N,Ktot))
    x = x0.copy(); p = p0.copy()

    def grad_potential(x, tnow):
        g = np.zeros_like(x)
        # Chakra harmonic
        for k in range(Kc):
            if cfg.omega_cons_entity is not None:
                g[:,k] += (np.array(cfg.omega_cons_entity)[:,k]**2) * x[:,k]
            else:
                g[:,k] += (cfg.omega_cons[k]**2) * x[:,k]
        # Physical harmonic
        if Kp > 0:
            for pidx in range(Kp):
                kp = Kc + pidx
                g[:,kp] += (cfg.omega_phys**2) * x[:,kp]
        # Cross-coupling (chakras among themselves)
        if cfg.g_cons_offdiag != 0.0:
            for k in range(Kc):
                for l in range(Kc):
                    if l == k: continue
                    g[:,k] += cfg.g_cons_offdiag * x[:,l]
        # Phys <-> Chakra symmetric coupling
        if cfg.g_phys_cons != 0.0 and Kp > 0:
            phys_mean = np.mean(x[:, Kc:Kc+Kp], axis=1, keepdims=True)
            chak_mean = np.mean(x[:, cfg.active_chakras], axis=1, keepdims=True)
            for k in cfg.active_chakras:
                g[:,k] += cfg.g_phys_cons * (x[:,k] - phys_mean[:,0])
            for pidx in range(Kp):
                kp = Kc + pidx
                g[:,kp] += cfg.g_phys_cons * (x[:,kp] - chak_mean[:,0])
        # Love
        if getattr(cfg, "love_mode", "harmonic") == "harmonic":
            for k in cfg.active_chakras:
                w = cfg.w_chakra[k]
                mean_k = np.mean(x[:,k])
                g[:,k] += cfg.k_love * w * (x[:,k] - mean_k) * (2*(N-1)/N)
        else:
            eps = 1e-3
            for k in cfg.active_chakras:
                for n in range(N):
                    diff = x[n,k] - x[:,k]
                    denom = (np.abs(diff)**3 + eps)
                    g[n,k] += cfg.k_love * np.sum(diff/denom)
        # Drives
        if cfg.t_yoga is not None and tnow >= cfg.t_yoga:
            G, _ = _current_maps(cfg, tnow, N, Kc)
            g[:, :Kc] -= G
        # Physical drive (global scalar, active when yoga on or always_on_env)
        if Kp > 0 and (cfg.always_on_env or (cfg.t_yoga is not None and tnow >= cfg.t_yoga)):
            g[:, Kc:Kc+Kp] -= _get_gamma_phys_at(cfg, tnow)
        return g

    X = np.zeros((len(t), N, Ktot)); P = np.zeros_like(X)
    for i, ti in enumerate(t):
        X[i] = x; P[i] = p
        p_half = p - 0.5*h*grad_potential(x, ti)
        x_new = x + h * p_half
        p_new = p_half - 0.5*h*grad_potential(x_new, ti+h)
        x, p = x_new, p_new
        # Relative damping on chakras
        if (cfg.t_yoga is not None and ti >= cfg.t_yoga) or cfg.always_on_env:
            if (cfg.kappa_relax > 0.0) or cfg.lindblad_scale_map or cfg.lindblad_schedule:
                Gtmp, KAP = _current_maps(cfg, ti, N, Kc)
                mean_x_chak = np.mean(x[:, :Kc], axis=0, keepdims=True)
                p[:, :Kc] -= KAP * (x[:, :Kc] - mean_x_chak)
        # Local damping (all DOF) with schedule
        k_loc_now = _get_kappa_local_at(cfg, ti)
        if k_loc_now > 0.0 and (cfg.always_on_env or (cfg.t_yoga is not None and ti >= cfg.t_yoga)):
            p -= k_loc_now * x

    # Build separations (chakras only) and Phi
    sep = {}
    for i in range(len(t)):
        for n in range(N):
            for m in range(n+1, N):
                for k in range(Kc):
                    sep[(i,n,m,k)] = float(abs(X[i,n,k] - X[i,m,k]))
    phi = []
    for i in range(len(t)):
        num = float(np.sum(X[i,:,:]**2))
        denom = 1.0
        for n in range(N):
            for m in range(n+1, N):
                for k in range(Kc):
                    denom += (X[i,n,k] - X[i,m,k])**2
        phi.append(num/denom)
    return {"t": t, "X": X, "P": P, "separations": sep, "phi": np.array(phi)}
