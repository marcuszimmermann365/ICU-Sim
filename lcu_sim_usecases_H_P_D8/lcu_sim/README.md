# LCU-Sim (v0.3.0)

- Exact (QuTiP) Backend für kleine Systeme
- Mean-Field Backend für große N
- Yoga/Interventionen (`gamma_map`, `lindblad_scale_map`, `gamma_schedule`, `lindblad_schedule`)
- Love-Potential: harmonic / inverse (MF)
- Physische Modi + Kopplung (`n_phys_modes`, `omega_phys`, `g_phys_cons`)
- Generische Umwelt: `kappa_local`, `kphi_dephase`, `always_on_env`, `kappa_local_schedule`
- Phys-Drives: `gamma_phys_drive`, `gamma_phys_schedule`
- Samadhi-Detektor: `observables.samadhi_time(...)`

## CLIs
```bash
lcu-sim         # Low-level Simulation (exact/meanfield)
lcu-app         # Use-Case Runner (A..G..H..P..D8)
lcu-opt         # Optimierung (Samadhi-Zeit)
lcu-env-sweep   # H1 Sweep: min. k_love in Metropole
```
