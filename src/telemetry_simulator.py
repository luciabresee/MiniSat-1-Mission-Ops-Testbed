"""
MiniSat-1 Telemetry Simulator
Generates simulated 1U CubeSat telemetry for a 24-hour mission period,
plus a version with an injected battery over-temperature anomaly.
"""

import numpy as np
import pandas as pd

# ---- Mission constants ----
ORBIT_PERIOD_MIN = 95        # minutes per orbit
ECLIPSE_DURATION_MIN = 35    # minutes of each orbit in Earth's shadow
SIM_DURATION_MIN = 1440      # 24 hours of telemetry
SAMPLE_RATE_MIN = 1          # one telemetry frame per minute

# ---- EPS constants ----
BATT_VOLTAGE_FULL = 8.3          # volts, fully charged 2S li-ion pack
BATT_VOLTAGE_NOMINAL_LOW = 7.5   # typical voltage after eclipse discharge
SOLAR_CURRENT_PEAK = 0.9         # amps in full sun
BATT_TEMP_SUNLIGHT = 15.0        # deg C, typical battery temp in sun
BATT_TEMP_ECLIPSE_DROP = 5.0     # deg C it cools during eclipse

RNG_SEED = 7                     # reproducible "random" noise

# ---- Anomaly injection constants ----
ANOMALY_ORBIT = 8            # inject during the 8th orbit's eclipse
ANOMALY_EXTRA_CURRENT = 0.55 # amps of unexpected extra load
ANOMALY_HEAT_RATE = 0.45     # deg C per minute of temperature rise


def build_timeline():
    """Create the time base and eclipse flag for the whole simulation."""
    minutes = np.arange(0, SIM_DURATION_MIN, SAMPLE_RATE_MIN)
    orbit_phase = minutes % ORBIT_PERIOD_MIN
    in_eclipse = orbit_phase >= (ORBIT_PERIOD_MIN - ECLIPSE_DURATION_MIN)
    return minutes, orbit_phase, in_eclipse


def simulate_power(minutes, orbit_phase, in_eclipse, rng):
    """Simulate EPS telemetry: solar current, battery current, voltage."""
    n = len(minutes)

    solar_current = np.where(in_eclipse, 0.0, SOLAR_CURRENT_PEAK)
    solar_current += rng.normal(0, 0.02, n)
    solar_current = np.clip(solar_current, 0, None)

    batt_current = np.where(in_eclipse, -0.45, 0.35)
    batt_current += rng.normal(0, 0.02, n)

    minutes_into_eclipse = np.where(
        in_eclipse,
        orbit_phase - (ORBIT_PERIOD_MIN - ECLIPSE_DURATION_MIN),
        0.0
    )
    discharge_fraction = minutes_into_eclipse / ECLIPSE_DURATION_MIN
    batt_voltage = (
        BATT_VOLTAGE_FULL
        - discharge_fraction * (BATT_VOLTAGE_FULL - BATT_VOLTAGE_NOMINAL_LOW)
    )
    batt_voltage += rng.normal(0, 0.01, n)

    return solar_current, batt_current, batt_voltage


def simulate_thermal(orbit_phase, in_eclipse, rng):
    """Battery and spacecraft temperatures follow the sun/shadow cycle."""
    n = len(orbit_phase)

    minutes_into_eclipse = np.where(
        in_eclipse,
        orbit_phase - (ORBIT_PERIOD_MIN - ECLIPSE_DURATION_MIN),
        0.0
    )
    cooling = (minutes_into_eclipse / ECLIPSE_DURATION_MIN) * BATT_TEMP_ECLIPSE_DROP

    batt_temp = BATT_TEMP_SUNLIGHT - cooling + rng.normal(0, 0.15, n)
    craft_temp = (BATT_TEMP_SUNLIGHT + 5.0) - cooling * 1.6 + rng.normal(0, 0.3, n)

    return batt_temp, craft_temp


def simulate_adcs(minutes, rng):
    """Reaction wheel speed and pointing error under nominal control."""
    n = len(minutes)
    wheel_speed = 2000 + 150 * np.sin(minutes / 40.0) + rng.normal(0, 20, n)
    pointing_error = np.abs(rng.normal(1.5, 0.5, n))
    return wheel_speed, pointing_error


def simulate_comms_and_mode(minutes, in_eclipse):
    """Ground contact windows and spacecraft mode string."""
    n = len(minutes)

    pass_starts = [120, 400, 700, 1000, 1300]
    comm_link = np.zeros(n, dtype=bool)
    for start in pass_starts:
        comm_link[(minutes >= start) & (minutes < start + 9)] = True

    mode = np.full(n, "NOMINAL", dtype=object)
    mode[in_eclipse] = "ECLIPSE"
    mode[comm_link] = "COMM"

    return comm_link, mode


def generate_nominal_telemetry():
    """Build the full nominal telemetry DataFrame and save to CSV."""
    rng = np.random.default_rng(RNG_SEED)

    minutes, orbit_phase, in_eclipse = build_timeline()
    solar_current, batt_current, batt_voltage = simulate_power(
        minutes, orbit_phase, in_eclipse, rng
    )
    batt_temp, craft_temp = simulate_thermal(orbit_phase, in_eclipse, rng)
    wheel_speed, pointing_error = simulate_adcs(minutes, rng)
    comm_link, mode = simulate_comms_and_mode(minutes, in_eclipse)

    df = pd.DataFrame({
        "time_min": minutes,
        "in_eclipse": in_eclipse,
        "mode": mode,
        "batt_voltage_V": batt_voltage.round(3),
        "batt_current_A": batt_current.round(3),
        "batt_temp_C": batt_temp.round(2),
        "craft_temp_C": craft_temp.round(2),
        "solar_current_A": solar_current.round(3),
        "wheel_speed_rpm": wheel_speed.round(1),
        "pointing_error_deg": pointing_error.round(2),
        "comm_link": comm_link,
    })

    df.to_csv("data/nominal_telemetry.csv", index=False)
    print(f"Generated {len(df)} telemetry frames -> data/nominal_telemetry.csv")
    return df


def generate_anomaly_telemetry():
    """
    Generate telemetry with a battery over-temperature anomaly injected
    during one eclipse: a hidden load causes excess discharge current,
    which drives battery heating and faster voltage sag.
    """
    df = generate_nominal_telemetry()

    orbit_number = df["time_min"] // ORBIT_PERIOD_MIN
    anomaly_mask = (orbit_number == ANOMALY_ORBIT) & df["in_eclipse"]
    idx = df.index[anomaly_mask]
    n_anom = len(idx)

    t_anom = np.arange(n_anom)

    # Root cause: extra discharge current (more negative = heavier drain)
    df.loc[idx, "batt_current_A"] -= ANOMALY_EXTRA_CURRENT

    # Symptom 1: battery temperature RISES instead of falling
    df.loc[idx, "batt_temp_C"] += ANOMALY_HEAT_RATE * t_anom + 2.0

    # Symptom 2: voltage sags faster under the heavier load
    df.loc[idx, "batt_voltage_V"] -= 0.008 * t_anom

    df.to_csv("data/anomaly_telemetry.csv", index=False)
    print(f"Injected battery anomaly in orbit {ANOMALY_ORBIT} "
          f"({n_anom} frames) -> data/anomaly_telemetry.csv")
    return df


if __name__ == "__main__":
    generate_nominal_telemetry()
    generate_anomaly_telemetry()
