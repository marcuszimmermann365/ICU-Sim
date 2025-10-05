from __future__ import annotations
from typing import List

def ashtanga_sequence(N: int) -> List[dict]:
    def seg(t, ks, val):
        return {"t": t, "gamma_pairs": [(e,k,val) for e in range(N) for k in ks]}
    return [seg(0.0,[0,1,2],0.04), seg(5.0,[3,4],0.05), seg(10.0,[5,6],0.06)]
