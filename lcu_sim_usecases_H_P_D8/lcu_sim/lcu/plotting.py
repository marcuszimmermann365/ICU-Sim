import numpy as np
import matplotlib.pyplot as plt

def plot_phi(t, phi, ax=None, label="Phi"):
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(t, phi, label=label)
    ax.set_xlabel("t"); ax.set_ylabel("Phi"); ax.legend()
    return ax

def plot_sep_heatmap(t, sep_dict, N, K, pair=(0,1)):
    import numpy as np, matplotlib.pyplot as plt
    s_mat = np.zeros((K, len(t)))
    for ti in range(len(t)):
        for k in range(K):
            s_mat[k, ti] = sep_dict.get((ti, pair[0], pair[1], k), np.nan)
    plt.imshow(s_mat, aspect='auto', origin='lower', extent=[t[0], t[-1], 0, K-1])
    plt.colorbar(label="Separation s")
    plt.ylabel("Chakra k"); plt.xlabel("t")
