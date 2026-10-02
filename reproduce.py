"""Three falls on one ideal elastic rope model, solved and checked against the frozen reference.

    python reproduce.py

Exits nonzero, naming the quantity, if anything disagrees with reference/result.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

from scipy.integrate import solve_ivp

R = json.loads((Path(__file__).parent / "reference" / "result.json").read_text())
TOL = R["tolerance_relative"]


def close(label, actual, expected, tol=TOL):
    if not math.isfinite(actual) or abs(actual - expected) > tol * max(1.0, abs(expected)):
        raise AssertionError("%s: %r != %r" % (label, actual, expected))


def ea_from_rating(rated_kN, m, g, f):
    """The rope's effective EA, fitted so the standard drop gives the rated peak."""
    w, F = m * g, 1e3 * rated_kN
    return ((F - w) ** 2 - w ** 2) / (2 * w * f)


def peak_closed(h, k, m, g):
    """Energy at the lowest point: m g (h + x) = k x^2 / 2."""
    w = m * g
    return w + math.sqrt(w * w + 2 * w * k * h)


def fall(h, k, m, g):
    """Free fall of h, then a linear spring, integrated to the FIRST turnaround only."""
    def engage(_t, y):
        return y[0] - h
    engage.terminal, engage.direction = True, 1
    a = solve_ivp(lambda _t, y: (y[1], g), (0, 30), (0.0, 0.0), events=engage,
                  method="DOP853", rtol=1e-12, atol=1e-12)
    t0, (z0, v0) = float(a.t_events[0][0]), a.y_events[0][0]

    def turn(_t, y):
        return y[1]
    turn.terminal, turn.direction = True, -1
    b = solve_ivp(lambda _t, y: (y[1], g - k * (y[0] - h) / m), (t0, t0 + 30), (z0, v0),
                  events=turn, method="DOP853", rtol=1e-12, atol=1e-12)
    if len(a.t_events[0]) != 1 or len(b.t_events[0]) != 1:
        raise AssertionError("engagement or turnaround not found")
    x = float(b.y_events[0][0][0]) - h
    return k * x, x, float(b.t_events[0][0])


def run():
    m, g = R["mass_kg"], R["gravity_m_s2"]
    ea = ea_from_rating(R["rated_impact_kN"], m, g, R["standard_fall_factor"])
    close("EA_eff_N", ea, R["EA_eff_N"])
    close("calibration round trip", peak_closed(R["standard_fall_factor"], ea, m, g) / 1e3,
          R["rated_impact_kN"])
    peaks = {}
    for name, c in R["cases"].items():
        h, L = c["fall_m"], c["rope_m"]
        k = ea / L
        F, x, t = fall(h, k, m, g)
        close("%s closed form vs ODE" % name, F, peak_closed(h, k, m, g))
        close("%s energy at lowest point" % name, m * g * (h + x), 0.5 * k * x * x)
        close("%s peak_force_kN" % name, F / 1e3, c["peak_force_kN"])
        close("%s max_stretch_m" % name, x, c["max_stretch_m"])
        close("%s turnaround_s" % name, t, c["turnaround_s"])
        peaks[name] = F / 1e3
        print("%s  %4.1f m fall on %4.1f m of rope  fall factor %.1f  peak %.3f kN  stretch %.3f m"
              % (name, h, L, h / L, F / 1e3, x))
    lower = 100 * (1 - peaks["C"] / peaks["A"])
    close("C_lower_peak_than_A_percent", lower, R["C_lower_peak_than_A_percent"])
    if not peaks["A"] > peaks["B"] > peaks["C"]:
        raise AssertionError("order A > B > C not reproduced")
    # deliberately artificial counterfactual: ONE fixed stiffness for all lengths (case B's)
    kB = ea / R["cases"]["B"]["rope_m"]
    fixed = {n: peak_closed(c["fall_m"], kB, m, g) / 1e3 for n, c in R["cases"].items()}
    for n, v in fixed.items():
        close("%s fixed_stiffness_counterfactual_kN" % n, v, R["fixed_stiffness_counterfactual_kN"][n])
    if not fixed["C"] > fixed["B"] > fixed["A"]:
        raise AssertionError("the counterfactual should reverse the order")
    print("12 m fall: peak rope force %.2f %% lower than the 2 m fall "
          "(conditional on the 8.8 kN fit; the order is not)" % lower)
    print("negative control (one fixed spring, artificial) reverses the order:",
          {n: round(v, 3) for n, v in fixed.items()})
    print("EVERYTHING REPRODUCES")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print("MISMATCH: %s" % e, file=sys.stderr)
        sys.exit(1)
