import math
from statistics import median

import numpy as np


def _norm_ppf_975() -> float:
    return 1.959963984540054


def _wilson_interval(successes: int, n: int, z: float = None) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    if z is None:
        z = _norm_ppf_975()
    phat = successes / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z**2 / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def compute_metrics(scores: np.ndarray) -> dict:
    if len(scores) == 0:
        raise ValueError("Scores array is empty.")

    mean_v = float(np.mean(scores))
    median_v = float(median(scores.tolist()))
    var_v = float(np.var(scores, ddof=0))
    sd_v = float(np.std(scores, ddof=0))
    mode_v = float(np.bincount(scores.astype(int)).argmax())

    n = len(scores)
    dist = {str(i): float((scores == i).sum() / n) for i in range(1, 6)}
    top2 = dist["4"] + dist["5"]
    btm2 = dist["1"] + dist["2"]
    top = dist["5"]
    net = top - dist["1"]

    z = _norm_ppf_975()
    ci_mean_delta = z * sd_v / math.sqrt(n)
    ci_mean_low = mean_v - ci_mean_delta
    ci_mean_high = mean_v + ci_mean_delta
    ci_t2b_low, ci_t2b_high = _wilson_interval(int((scores >= 4).sum()), n, z=z)

    return {
        "mean": mean_v,
        "median": median_v,
        "sd": sd_v,
        "variance": var_v,
        "mode": mode_v,
        "top2box": float(top2),
        "bottom2box": float(btm2),
        "topbox": float(top),
        "net_score": float(net),
        "distribution": dist,
        "ci_mean_low": float(ci_mean_low),
        "ci_mean_high": float(ci_mean_high),
        "ci_t2b_low": float(ci_t2b_low),
        "ci_t2b_high": float(ci_t2b_high),
    }

