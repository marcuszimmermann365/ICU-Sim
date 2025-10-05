from __future__ import annotations
from .config import LCUConfig
from .sim_exact import run_exact
from .sim_meanfield import run_meanfield

def run(cfg: LCUConfig, backend: str = "auto"):
    if backend == "meanfield":
        return run_meanfield(cfg)
    if backend == "exact":
        return run_exact(cfg)
    if cfg.use_qutip:
        try:
            import qutip  # noqa
            return run_exact(cfg)
        except Exception:
            return run_meanfield(cfg)
    else:
        return run_meanfield(cfg)
