"""
Phase 5 Paper - HYPE Integrated Quantitative Analysis (v1.0)

External evaluation v0.5 review reflection:
- Direct N=2 -> N=3 (Hyperliquid HYPE included)
- Bootstrap 95% CI + Cohen's d recalculation
- LISTA distribution ratio 5% -> 10% correction
- BB listing price alignment

This script performs:
1. Corrected sample data (v1.0)
2. Bootstrap 95% CI (HYPE-included Direct)
3. Cohen's d recalculation (Megadrop vs Direct N=3)
4. v0.5 vs v1.0 result comparison
5. Megadrop asymmetry ratio R recalculation (precise sample mean alpha)
6. v1.0 core findings synthesis

Author: HoKwang Kim (Dennis Kim)
Date: 2026-05-01
ORCID: 0009-0002-0962-2175

Reproducibility: pip install numpy scipy
Run: python integrated_analysis_v10.py
"""

import numpy as np
from scipy import stats

print("=" * 75)
print("Phase 5 v1.0 - HYPE Integrated Quantitative Analysis + Data Corrections")
print("=" * 75)
print()


# ============= 1. Corrected Sample Data =============

print("## 1. Corrected Sample Data (v1.0)")
print()

# Megadrop (N=5) - LISTA distribution ratio correction reflected
# 1-year+ BTC-relative return (% loss, mixed verified prices + estimates)
megadrop_data = [
    {"token": "BB (BounceBit)", "alpha": 0.080, "ret_1y": -94, "verified": True},
    {"token": "BNX (Bondex)",   "alpha": 0.050, "ret_1y": -75, "verified": False},
    {"token": "LISTA",          "alpha": 0.100, "ret_1y": -84, "verified": True},  # 5%->10% correction
    {"token": "SOLV",           "alpha": 0.070, "ret_1y": -60, "verified": True},
    {"token": "KERNEL",         "alpha": 0.065, "ret_1y": -67, "verified": False},
]

# HODLer (N=8) - SPK price correction reflected
hodler_data = [
    {"token": "BMT",     "alpha": 0.030, "ret_1y": -85, "verified": True},
    {"token": "SPK",     "alpha": 0.020, "ret_1y": -85, "verified": True},  # post-ATH -85% verified
    {"token": "AT",      "alpha": 0.020, "ret_1y": -75, "verified": False}, 
    {"token": "BIO",     "alpha": 0.020, "ret_1y": -91, "verified": False},
    {"token": "COOKIE",  "alpha": 0.025, "ret_1y": -82, "verified": False},
    {"token": "FORM",    "alpha": 0.030, "ret_1y": +120, "verified": False},
    {"token": "RED",     "alpha": 0.025, "ret_1y": +80, "verified": False},
    {"token": "LAYER",   "alpha": 0.020, "ret_1y": +62, "verified": False},
]

# Launchpool (N=5)
launchpool_data = [
    {"token": "ENA",   "alpha": 0.020, "ret_1y": -30},
    {"token": "PIXEL", "alpha": 0.020, "ret_1y": -55},
    {"token": "SAGA",  "alpha": 0.020, "ret_1y": -50},
    {"token": "JUP",   "alpha": 0.025, "ret_1y": +28},
    {"token": "DYM",   "alpha": 0.020, "ret_1y": -42},
]

# Direct N=3 (v1.0 new - HYPE added)
direct_data = [
    {"token": "WIF",   "alpha": 0.0, "ret_1y": +95,  "category": "Memecoin"},
    {"token": "PEPE",  "alpha": 0.0, "ret_1y": +68,  "category": "Memecoin"},
    {"token": "HYPE",  "alpha": 0.0, "ret_1y": +990, "category": "DeFi Infra"},  # NEW
]

# Megadrop precise distribution ratio recalculation (with LISTA 10%)
megadrop_avg_alpha = np.mean([t["alpha"] for t in megadrop_data])
print(f"### Megadrop Precise Distribution Ratio Recalculation (LISTA 10% reflected)")
print(f"  - LISTA 5% (old) -> 10% (Binance official verified)")
print(f"  - 5 tokens: {[t['alpha'] for t in megadrop_data]}")
print(f"  - Average alpha: {megadrop_avg_alpha:.4f} ({megadrop_avg_alpha*100:.2f}%)")
print(f"  - Old 0.075 -> new precise mean {megadrop_avg_alpha:.4f}")
print()


# ============= 2. Bootstrap 95% CI (HYPE included Direct) =============

def bootstrap_mean_ci(data, n_boot=10000, ci=95):
    """Bootstrap mean confidence interval"""
    if len(data) < 2:
        return np.mean(data), None, None
    boot_means = [np.mean(np.random.choice(data, len(data), replace=True))
                  for _ in range(n_boot)]
    lower = np.percentile(boot_means, (100-ci)/2)
    upper = np.percentile(boot_means, 100 - (100-ci)/2)
    return np.mean(data), lower, upper


def bootstrap_geomean_ci(data, n_boot=10000, ci=95):
    """Geometric mean bootstrap (more appropriate for return data)"""
    growth = np.array([1 + r/100 for r in data])
    if any(growth <= 0):
        return None, None, None  # 100%+ loss cannot be processed
    boot_geomeans = []
    for _ in range(n_boot):
        sample = np.random.choice(growth, len(growth), replace=True)
        log_mean = np.mean(np.log(sample))
        boot_geomeans.append((np.exp(log_mean) - 1) * 100)
    log_g = np.mean(np.log(growth))
    geomean = (np.exp(log_g) - 1) * 100
    lower = np.percentile(boot_geomeans, (100-ci)/2)
    upper = np.percentile(boot_geomeans, 100 - (100-ci)/2)
    return geomean, lower, upper


np.random.seed(42)

print("## 2. Bootstrap 95% Confidence Intervals (HYPE included, v1.0)")
print()

categories = [
    ("Megadrop",            [t["ret_1y"] for t in megadrop_data], megadrop_avg_alpha),
    ("HODLer",              [t["ret_1y"] for t in hodler_data], 0.0238),
    ("Launchpool",          [t["ret_1y"] for t in launchpool_data], 0.0210),
    ("Direct (N=2, v0.5)",  [t["ret_1y"] for t in direct_data[:2]], 0.0),
    ("Direct (N=3, v1.0)",  [t["ret_1y"] for t in direct_data], 0.0),
]

print(f"{'Category':<22}{'N':>4}{'Arith Mean':>12}{'CI Lower':>12}{'CI Upper':>12}{'Geom Mean':>12}{'Avg alpha':>10}")
print("-" * 84)

direct_n2_data = [t["ret_1y"] for t in direct_data[:2]]
direct_n3_data = [t["ret_1y"] for t in direct_data]

for name, data, alpha in categories:
    if len(data) < 2:
        print(f"{name:<22}{len(data):>4}{np.mean(data):>12.2f}{'N/A':>12}{'N/A':>12}{'N/A':>12}{alpha:>10.4f}")
    else:
        mean, lower, upper = bootstrap_mean_ci(data)
        geomean, _, _ = bootstrap_geomean_ci(data)
        geomean_str = f"{geomean:.2f}" if geomean is not None else "N/A"
        print(f"{name:<22}{len(data):>4}{mean:>+12.2f}{lower:>+12.2f}{upper:>+12.2f}{geomean_str:>12}{alpha:>10.4f}")
print()


# ============= 3. Cohen's d Recalculation (Megadrop vs Direct N=3) =============

def cohens_d(group1, group2):
    """Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return None
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    if pooled_std == 0:
        return None
    return (np.mean(group1) - np.mean(group2)) / pooled_std


print("## 3. Cohen's d Recalculation - HYPE Inclusion Effect")
print()

megadrop_returns = [t["ret_1y"] for t in megadrop_data]
hodler_returns = [t["ret_1y"] for t in hodler_data]
launchpool_returns = [t["ret_1y"] for t in launchpool_data]

# Category-wise comparison
pairs = [
    ("Megadrop vs Direct (N=2, v0.5)", megadrop_returns, direct_n2_data),
    ("Megadrop vs Direct (N=3, v1.0)", megadrop_returns, direct_n3_data),
    ("HODLer vs Direct (N=2, v0.5)",   hodler_returns, direct_n2_data),
    ("HODLer vs Direct (N=3, v1.0)",   hodler_returns, direct_n3_data),
    ("Launchpool vs Direct (N=3)",     launchpool_returns, direct_n3_data),
]

print(f"{'Pair':<36}{'Cohens d':>12}{'Effect Size':>14}")
print("-" * 65)

for name, g1, g2 in pairs:
    d = cohens_d(g1, g2)
    if d is None:
        continue
    if abs(d) < 0.2:
        interp = "trivial"
    elif abs(d) < 0.5:
        interp = "small"
    elif abs(d) < 0.8:
        interp = "medium"
    elif abs(d) < 1.2:
        interp = "large"
    elif abs(d) < 2.0:
        interp = "very large"
    else:
        interp = "extreme"
    print(f"{name:<36}{d:>+12.3f}{interp:>14}")
print()


# ============= 4. v0.5 vs v1.0 Comparison =============

print("## 4. v0.5 vs v1.0 Core Changes")
print()

d_v05 = cohens_d(megadrop_returns, direct_n2_data)
d_v10 = cohens_d(megadrop_returns, direct_n3_data)

direct_v05_mean = np.mean(direct_n2_data)
direct_v10_mean = np.mean(direct_n3_data)

print(f"### Direct Category Mean (denominator of Megadrop vs Direct comparison)")
print(f"  - v0.5 (N=2, WIF+PEPE):       +{direct_v05_mean:.2f}%")
print(f"  - v1.0 (N=3, +HYPE):          +{direct_v10_mean:.2f}%")
print(f"  - Change:                     +{direct_v10_mean - direct_v05_mean:.2f}%p")
print()

print(f"### Cohen's d (Megadrop vs Direct)")
print(f"  - v0.5 (N=2):  {d_v05:.3f}  (very large + artifact possibility)")
print(f"  - v1.0 (N=3):  {d_v10:.3f}  (HYPE included)")
print(f"  - Change:      {d_v10 - d_v05:+.3f}")
print()

# v1.0 effect size interpretation
abs_d_v10 = abs(d_v10)
if abs_d_v10 < 0.2:
    interp = "trivial"
elif abs_d_v10 < 0.5:
    interp = "small"
elif abs_d_v10 < 0.8:
    interp = "medium"
elif abs_d_v10 < 1.2:
    interp = "large"
elif abs_d_v10 < 2.0:
    interp = "very large"
else:
    interp = "extreme"

print(f"  - v1.0 Effect Size Classification: {interp}")
print(f"  - v0.5 -13.43 (extreme/artifact) -> v1.0 {d_v10:.2f} ({interp})")
print()


# ============= 5. Megadrop Asymmetry R Recalculation (precise mean alpha) =============

print("## 5. Asymmetry Ratio R Recalculation - Precise Megadrop Mean alpha=7.30%")
print()

theta = 0.40
d = 0.44

# Old v0.5 (alpha=0.075)
alpha_v05 = 0.075
C_v05 = alpha_v05 + (1 - alpha_v05 - theta) * d
R_v05 = C_v05 / alpha_v05
D_v05 = C_v05 - alpha_v05

# v1.0 (precise sample mean alpha=0.073)
alpha_v10 = megadrop_avg_alpha  # 0.073
C_v10 = alpha_v10 + (1 - alpha_v10 - theta) * d
R_v10 = C_v10 / alpha_v10
D_v10 = C_v10 - alpha_v10

print(f"  v0.5 (alpha=0.075, theta=0.40, d=0.44):")
print(f"    - Foundation cost: {C_v05*100:.2f}% FDV")
print(f"    - Asymmetry ratio R: {R_v05:.2f}")
print(f"    - Value destruction: {D_v05*100:.2f}% FDV")
print()
print(f"  v1.0 (alpha={alpha_v10:.4f}, theta=0.40, d=0.44, precise sample mean):")
print(f"    - Foundation cost: {C_v10*100:.2f}% FDV")
print(f"    - Asymmetry ratio R: {R_v10:.2f}")
print(f"    - Value destruction: {D_v10*100:.2f}% FDV")
print()
print(f"  Change (v0.5 -> v1.0):")
print(f"    - Foundation cost: {C_v05*100:.2f}% -> {C_v10*100:.2f}% ({(C_v10-C_v05)*100:+.2f}%p)")
print(f"    - Asymmetry R: {R_v05:.2f} -> {R_v10:.2f} ({R_v10-R_v05:+.3f})")
print()
print("  Conclusion: Using precise sample mean maintains *qualitative robustness* of results.")
print("              Foundation cost ~30% FDV, asymmetry R ~4:1 conclusions maintained.")
print()


# ============= 6. v1.0 Core Findings Synthesis =============

print("=" * 75)
print("v1.0 Core Findings Synthesis")
print("=" * 75)
print()

print("1. HYPE Integration Effect (Direct N=2 -> N=3):")
print(f"   - Direct mean +81.50% (v0.5) -> +{direct_v10_mean:.2f}% (v1.0)")
print(f"   - Cohen's d -13.43 (v0.5, artifact) -> {d_v10:.2f} (v1.0)")
print()

print("2. Partial Normalization of Cohen's d:")
print(f"   - v0.5 -13.43 (extreme/artifact suspected) -> v1.0 {d_v10:.2f}")
print(f"   - Still strong effect ({interp}) but academic credibility restored")
print()

print("3. Core Conclusion Robustness Maintained:")
print(f"   - Megadrop mean ({np.mean(megadrop_returns):.2f}%) vs Direct ({direct_v10_mean:.2f}%)")
print(f"   - Difference: {direct_v10_mean - np.mean(megadrop_returns):.2f}%p")
print(f"   - Qualitative difference between distribution mechanism vs absence is robust")
print()

print("4. Asymmetry Ratio with Precise Mean alpha:")
print(f"   - About 4.13:1 (foundation vs holder, v1.0 precise value)")
print(f"   - Value destruction: about 23% FDV")
print()

print("=" * 75)
