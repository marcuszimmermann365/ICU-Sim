from lcu.config import LCUConfig
from lcu.controller import run
import numpy as np

def test_meanfield_runs_basic():
    cfg = LCUConfig(N_entities=10, use_qutip=False, t_max=5.0, n_steps=50, k_love=0.1)
    res = run(cfg, backend="meanfield")
    assert (res["phi"] > 0).all()

def test_phys_and_env_schedules():
    cfg = LCUConfig(N_entities=5, use_qutip=False, t_max=6.0, n_steps=120,
                    n_phys_modes=1, omega_phys=1.1, g_phys_cons=0.05,
                    always_on_env=True, kappa_local=0.02, t_yoga=0.0)
    cfg.gamma_phys_schedule = [{"t": 0.0, "gamma_phys": 0.0}, {"t": 3.0, "gamma_phys": 0.05}]
    cfg.kappa_local_schedule = [{"t": 0.0, "kappa_local": 0.02}, {"t": 3.0, "kappa_local": 0.005}]
    res = run(cfg, backend="meanfield")
    assert "X" in res and res["X"].shape[2] == 8  # 7 + 1
