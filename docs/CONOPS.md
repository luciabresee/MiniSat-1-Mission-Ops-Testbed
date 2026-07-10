# MiniSat-1 Concept of Operations (CONOPS)
**Document ID:** OPS-CONOPS-001 | **Rev:** A

## 1. Mission Overview
MiniSat-1 is a simulated 1U CubeSat in a ~500 km sun-synchronous low
Earth orbit (orbital period 95 min: ~60 min sunlight, ~35 min
eclipse). The mission objective is to collect Earth-observation
payload data and downlink it during ground station passes while
demonstrating reliable autonomous operations between contacts.

The spacecraft is out of ground contact for the large majority of
each day. Onboard autonomy manages routine operations; the ground
team reviews recorded telemetry after each pass and responds to
anomalies using approved operator procedures.

## 2. Mission Phases
- **Launch and Early Operations (LEOP):** deployment, detumble,
  first contact, initial state-of-health verification.
- **Commissioning:** subsystem checkout, baseline telemetry
  characterization. Alarm limits are validated against observed
  nominal behavior during this phase.
- **Nominal Operations:** routine payload collection and downlink
  (current phase; the operations testbed simulates this phase).
- **Extended Operations / Disposal:** end-of-life operations per
  orbital debris requirements.

## 3. Spacecraft Segment
Six subsystems: EPS (2S li-ion battery, body-mounted solar arrays),
ADCS (reaction wheels, sun/magnetic sensing), passive TCS, COMM
(UHF transceiver), C&DH (onboard computer, mode management), and an
Earth-imaging payload.

Spacecraft modes: NOMINAL, ECLIPSE, COMM, and SAFE. Mode transitions
are telemetered; an uncommanded mode change is treated as an
anomaly indicator.

## 4. Ground Segment
Single ground station providing approximately five contacts per day
of ~9 minutes each (reference pass starts in the simulation:
t = 120, 400, 700, 1000, 1300 min). All commanding occurs during
these windows. The mission operations dashboard provides telemetry
replay, subsystem status (GREEN/YELLOW/RED), an event log, and
operator recommendations.

## 5. Nominal Operations
Each orbit follows the power/thermal cycle driven by eclipse:
solar charging in sunlight (battery current ~ +0.35 A), battery
discharge in eclipse (~ -0.45 A), battery temperature cycling
between ~15 C (sunlight) and ~10 C (eclipse exit). Operators verify
state-of-health each pass, review the event log since last contact,
and confirm subsystem status GREEN before routine payload tasking.

## 6. Off-Nominal Operations
Anomaly detection layers static limits with context-aware checks
(e.g., battery temperature rising during eclipse, when nominal
behavior is cooling). On YELLOW: increase monitoring, prepare the
applicable procedure. On RED: execute the applicable procedure
(e.g., OP-EPS-001 for battery temperature anomalies), shed loads in
priority order (payload first), command SAFE mode if required, and
escalate per procedure criteria. All anomalies conclude with an
Anomaly Response Report.

## 7. Command Authority
Routine commanding is executed by the on-console operator within
mission rules. Actions beyond mission rules, and all escalation
conditions defined in operator procedures, require Mission Director
approval. In loss-of-contact contingencies, onboard autonomy
(SAFE-mode fallback) preserves the spacecraft until the next pass.

## 8. Constraints and Assumptions
Payload operations are the lowest-priority load and are the first
shed under power or thermal stress. Battery preservation takes
precedence over mission data return. The simulation assumes fixed
eclipse geometry and pass schedule; a real mission would ingest
orbit-propagated event predictions.
