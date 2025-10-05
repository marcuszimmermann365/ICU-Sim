from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
from lcu.config import LCUConfig
from .schedules import ashtanga_sequence

@dataclass
class ScenarioSpec:
    name: str
    description: str
    backend: str = "meanfield"
    config: Dict[str, Any] = None

def build_scenario(name: str, overrides: Optional[Dict[str, Any]] = None) -> Tuple[ScenarioSpec, LCUConfig]:
    s = name.lower().strip()
    desc = ""; backend = "meanfield"

    # Base examples (subset)
    if s in ["a1","resonanz","empathie"]:
        desc = "A1: Resonanz & Empathie"
        cfg = LCUConfig(N_entities=2, use_qutip=False, t_max=20.0, n_steps=400,
                        k_love=0.15, g_cons_offdiag=0.02)
    elif s in ["gd7","ashtanga-sequence","digitale-ashtanga"]:
        desc = "GD7: Digitale Ashtanga-Sequenz"
        N=1
        cfg = LCUConfig(N_entities=N, use_qutip=False, t_max=15.0, n_steps=300,
                        k_love=0.0, t_yoga=0.0)
        cfg.gamma_schedule = ashtanga_sequence(N)

    # GA/GB/GC/GD6 from earlier (shortcuts)
    elif s in ["gd6","fastest-samadhi","schnellste-erleuchtung"]:
        desc = "GD6: Optimierung der Samadhi-Zeit"
        cfg = LCUConfig(N_entities=20, use_qutip=False, t_max=20.0, n_steps=400,
                        k_love=0.12, t_yoga=6.0, kappa_relax=0.03)

    # --- New Category H ---
    elif s in ["h1","kloster-vs-metropole"]:
        desc = "H1: Kloster vs. Metropole"
        cfg = LCUConfig(N_entities=50, use_qutip=False, t_max=20.0, n_steps=400,
                        k_love=0.08, always_on_env=True, kappa_local=0.005)
    elif s in ["h2","burnout-sabbatical"]:
        desc = "H2: Burnout & Sabbatical"
        cfg = LCUConfig(N_entities=100, use_qutip=False, t_max=30.0, n_steps=600,
                        k_love=0.06, always_on_env=True, t_yoga=0.0)
        cfg.gamma_schedule = [
            {"t": 0.0, "gamma_pairs": [(e,k,0.05) for e in range(cfg.N_entities) for k in range(7)]},
            {"t": 20.0, "gamma_pairs": [(e,k,0.0)  for e in range(cfg.N_entities) for k in range(7)]},
        ]
        cfg.kappa_local_schedule = [
            {"t": 0.0, "kappa_local": 0.05},
            {"t": 20.0, "kappa_local": 0.005},
        ]

    # --- New Category P ---
    elif s in ["p1","psychosomatik-loop","psychosomatische-schleife"]:
        desc = "P1: Psychosomatische Schleife"
        cfg = LCUConfig(N_entities=1, use_qutip=False, t_max=25.0, n_steps=500,
                        n_phys_modes=2, omega_phys=1.0, g_phys_cons=0.06,
                        k_love=0.0, always_on_env=True, t_yoga=0.0)
        cfg.omega_cons = [0.6,0.7,0.5,0.8,0.7,0.6,0.5]
        cfg.gamma_phys_schedule = [
            {"t": 0.0, "gamma_phys": 0.0},
            {"t": 12.0, "gamma_phys": 0.05},
        ]
    elif s in ["p2","embodiment-vs-intellekt"]:
        desc = "P2: Embodiment vs. Intellekt"
        cfg = LCUConfig(N_entities=50, use_qutip=False, t_max=25.0, n_steps=500,
                        n_phys_modes=1, omega_phys=1.1, g_phys_cons=0.05,
                        k_love=0.08, always_on_env=True, t_yoga=5.0)
        # Default: Embodiment -> phys drive
        cfg.gamma_phys_drive = 0.04
        cfg.gamma_map = {(e,k): 0.0 for e in range(cfg.N_entities) for k in [5,6]}

    # --- New Category D8 ---
    elif s in ["d8","curriculum-optimal"]:
        desc = "D8: Curriculum Design"
        cfg = LCUConfig(N_entities=30, use_qutip=False, t_max=30.0, n_steps=600,
                        k_love=0.08, always_on_env=True, t_yoga=0.0, kappa_relax=0.02)
        def seg(t, ks, val):
            return {"t": t, "gamma_pairs": [(e,k,val) for e in range(cfg.N_entities) for k in ks]}
        cfg.gamma_schedule = [seg(0.0,[0,1,2],0.03), seg(10.0,[3,4],0.04), seg(20.0,[5,6],0.05)]

    else:
        raise ValueError(f"Unbekanntes Szenario: {name}")

    if overrides:
        for k,v in overrides.items():
            if hasattr(cfg,k): setattr(cfg,k,v)
    spec = ScenarioSpec(name=s.upper(), description=desc, backend=backend, config={})
    return spec, cfg
