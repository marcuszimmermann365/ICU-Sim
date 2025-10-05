from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, Optional, Dict, Tuple
import numpy as np

@dataclass
class LCUConfig:
    # Core
    N_entities: int = 2
    d_trunc: int = 10
    use_qutip: bool = True
    t_max: float = 10.0
    n_steps: int = 200
    hbar: float = 1.0

    # Conscious (7 modes)
    omega_cons: Sequence[float] = field(default_factory=lambda: [1.0]*7)
    w_chakra: Sequence[float] = field(default_factory=lambda: [1.0]*7)
    g_cons_offdiag: float = 0.0
    active_chakras: Optional[Sequence[int]] = None

    # Physical
    n_phys_modes: int = 0
    omega_phys: float = 1.0
    g_phys_cons: float = 0.0

    # Love
    k_love: float = 0.1
    love_mode: str = "harmonic"  # or "inverse"

    # Yoga / interventions
    t_yoga: Optional[float] = None
    gamma_drive: float = 0.0
    gamma_map: Optional[Dict[Tuple[int,int], float]] = None
    gamma_schedule: Optional[Sequence[dict]] = None
    lindblad_scale_map: Optional[Dict[Tuple[int,int], float]] = None
    lindblad_schedule: Optional[Sequence[dict]] = None

    # Phys drives (MF)
    gamma_phys_drive: float = 0.0
    gamma_phys_schedule: Optional[Sequence[dict]] = None

    # Environment (open systems)
    kappa_relax: float = 0.0
    kappa_local: float = 0.0
    kappa_local_schedule: Optional[Sequence[dict]] = None
    kphi_dephase: float = 0.0
    always_on_env: bool = False

    # Entity-specific omegas (MF convenience)
    omega_cons_entity: Optional[np.ndarray] = None

    seed: Optional[int] = 123

    def validate(self) -> None:
        assert self.N_entities >= 1
        assert len(self.omega_cons) == 7
        assert len(self.w_chakra) == 7
        if self.active_chakras is None:
            self.active_chakras = list(range(7))
        else:
            for k in self.active_chakras:
                assert 0 <= k < 7

    def tlist(self) -> np.ndarray:
        return np.linspace(0.0, self.t_max, self.n_steps)

    def set_prana_gradient(self, base: float = 0.8, step: float = 0.1):
        self.omega_cons = [base + step*k for k in range(7)]
