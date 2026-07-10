"""
MiniSat-1 Anomaly Detector
Reads telemetry CSV and assigns GREEN/YELLOW/RED status per subsystem
using static limits plus context-aware checks.
"""

import pandas as pd
import numpy as np

# ---- Static limits: (yellow, red) ----
BATT_TEMP_LIMITS = (25.0, 35.0)        # deg C, high side
BATT_VOLTAGE_LIMITS = (7.4, 7.2)       # volts, low side
BATT_CURRENT_LIMITS = (-0.6, -0.9)     # amps, discharge side
POINTING_LIMITS = (5.0, 10.0)          # degrees
WHEEL_LIMITS = (4000.0, 5000.0)        # rpm

# ---- Context check: temp rise during eclipse ----
TREND_WINDOW_MIN = 5                   # look-back window, minutes
ECLIPSE_RISE_YELLOW = 1.0              # deg C rise over window
ECLIPSE_RISE_RED = 3.0

STATUS_ORDER = {"GREEN": 0, "YELLOW": 1, "RED": 2}


def worst(a, b):
    """Return the more severe of two status strings."""
    return a if STATUS_ORDER[a] >= STATUS_ORDER[b] else b


def check_high(value, limits):
    """Status for a 'too high is bad' parameter."""
    yellow, red = limits
    if value > red:
        return "RED"
    if value > yellow:
        return "YELLOW"
    return "GREEN"


def check_low(value, limits):
    """Status for a 'too low is bad' parameter."""
    yellow, red = limits
    if value < red:
        return "RED"
    if value < yellow:
        return "YELLOW"
    return "GREEN"


def detect(df):
    """
    Run all checks on a telemetry DataFrame.
    Returns the DataFrame with added status columns, plus an event list.
    """
    n = len(df)
    eps_status = []
    adcs_status = []
    events = []
    prev_eps = "GREEN"
    prev_adcs = "GREEN"

    # Pre-compute battery temp change over the trend window
    temp_delta = df["batt_temp_C"].diff(TREND_WINDOW_MIN)

    for i in range(n):
        row = df.iloc[i]

        # ---- EPS checks ----
        s = check_high(row["batt_temp_C"], BATT_TEMP_LIMITS)
        s = worst(s, check_low(row["batt_voltage_V"], BATT_VOLTAGE_LIMITS))
        s = worst(s, check_low(row["batt_current_A"], BATT_CURRENT_LIMITS))

        # Context check: battery temp RISING during eclipse
        reason = None
        if row["in_eclipse"] and i >= TREND_WINDOW_MIN:
            rise = temp_delta.iloc[i]
            if rise >= ECLIPSE_RISE_RED:
                s = worst(s, "RED")
                reason = f"Batt temp rose {rise:.1f} C in {TREND_WINDOW_MIN} min DURING ECLIPSE"
            elif rise >= ECLIPSE_RISE_YELLOW:
                s = worst(s, "YELLOW")
                reason = f"Batt temp rising ({rise:.1f} C/{TREND_WINDOW_MIN} min) during eclipse"

        # ---- ADCS checks ----
        a = check_high(row["pointing_error_deg"], POINTING_LIMITS)
        a = worst(a, check_high(row["wheel_speed_rpm"], WHEEL_LIMITS))

        eps_status.append(s)
        adcs_status.append(a)

        # ---- Log status transitions as events ----
        if s != prev_eps:
            events.append({
                "time_min": int(row["time_min"]),
                "subsystem": "EPS",
                "new_status": s,
                "detail": reason or f"batt_temp={row['batt_temp_C']:.1f}C, "
                                    f"V={row['batt_voltage_V']:.2f}, "
                                    f"I={row['batt_current_A']:.2f}A",
            })
        if a != prev_adcs:
            events.append({
                "time_min": int(row["time_min"]),
                "subsystem": "ADCS",
                "new_status": a,
                "detail": f"pointing={row['pointing_error_deg']:.1f}deg, "
                          f"wheel={row['wheel_speed_rpm']:.0f}rpm",
            })
        prev_eps, prev_adcs = s, a

    df = df.copy()
    df["eps_status"] = eps_status
    df["adcs_status"] = adcs_status
    return df, events


if __name__ == "__main__":
    for name in ["nominal", "anomaly"]:
        df = pd.read_csv(f"data/{name}_telemetry.csv")
        checked, events = detect(df)
        print(f"\n=== {name.upper()} dataset: {len(events)} status events ===")
        for e in events:
            print(f"  t={e['time_min']:>5} min  {e['subsystem']:<5} -> "
                  f"{e['new_status']:<7} {e['detail']}")
