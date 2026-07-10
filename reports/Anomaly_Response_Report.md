# Anomaly Response Report: Battery Over-Temperature During Eclipse
**Report ID:** ARR-2026-001 | **Spacecraft:** MiniSat-1
**Anomaly class:** EPS / Thermal | **Severity:** RED (critical)
**Status:** Closed - recovered, follow-up actions open

## 1. Summary
During the orbit-8 eclipse (mission time 820-855 min), MiniSat-1
experienced an off-nominal battery temperature rise with correlated
excess discharge current and accelerated voltage sag. The ground
system detected the condition at onset (t = 820 min) via the
eclipse thermal-trend monitor. Telemetry is consistent with an
unexpected parasitic load of approximately 0.55 A. The condition
self-cleared at eclipse exit (t = 855 min). No permanent battery
degradation is indicated. Follow-up actions remain open to identify
the offending load.

## 2. Detection
- t = 820 min: EPS status transitioned GREEN -> RED. Trigger:
  battery temperature rise of 1.7 C over 5 min during eclipse
  (limit: >= 1.0 C/5 min YELLOW, >= 3.0 C/5 min RED), with
  battery discharge current simultaneously exceeding the -0.9 A
  RED static limit.
- Detection latency was effectively zero: the trend monitor and the
  current limit flagged the first minutes of the event. The static
  temperature limit (25 C YELLOW) would not have tripped until
  approximately 15 minutes later - the context-aware check provided
  the early warning.

## 3. Telemetry Signature
- **Battery temperature:** rose from ~13 C at eclipse entry to
  ~30 C by eclipse exit, versus a nominal profile cooling to ~10 C.
- **Battery current:** stepped from the nominal -0.45 A eclipse
  discharge to approximately -1.0 A at onset - roughly double the
  design eclipse load. The step change was instantaneous, not
  gradual.
- **Battery voltage:** sagged approximately 0.28 V below the
  nominal eclipse discharge curve by eclipse exit.
- **All other channels nominal:** solar array current ~0 A
  (consistent with eclipse), ADCS within limits, no uncommanded
  mode change observed.

## 4. Cause Assessment
- **Proximate cause:** an unexpected electrical load of ~0.55 A
  active during eclipse. Joule heating from the elevated discharge
  current through battery internal resistance accounts for the
  temperature rise; the same load accounts for the accelerated
  voltage sag. A temperature-sensor artifact is ruled out by the
  multi-channel correlation, in particular the instantaneous
  current step.
- **Root cause:** not conclusively determined from telemetry alone.
  Candidate hypotheses, in order of assessed likelihood: (a) a
  payload or heater element failed-on due to a switching fault;
  (b) a flight software mode-management error enabling a
  sunlight-only load during eclipse; (c) partial short in the power
  distribution path. Discriminating among these requires the
  follow-up actions in Section 7.

## 5. Operator Response
Response followed OP-EPS-001. Characterization steps (Sections 4.1-
4.6 of the procedure) confirmed the multi-channel signature and
resolved the decision point to Branch B (confirmed excess load).
In the recorded scenario the condition cleared at eclipse exit
(t = 855 min) when temperatures and currents returned to nominal,
prior to load-shedding commands taking effect; recovery was
confirmed by nominal behavior through the subsequent eclipse per
procedure exit criteria.

## 6. Recovery and Current State
Battery temperature, current, and voltage returned to nominal
profiles at eclipse exit and remained nominal through the following
eclipse. Exit criteria of OP-EPS-001 Section 8 were satisfied. The
spacecraft resumed nominal operations.

## 7. Follow-Up Actions (Open)
- **FA-1:** Review load-switch telemetry and command history for
  the anomaly window to identify the parasitic load.
- **FA-2:** If software-related, audit mode-management logic for
  eclipse load-enable conditions.
- **FA-3:** Trend battery capacity over the next 30 eclipse cycles
  to verify no degradation from the thermal excursion.
- **FA-4:** Evaluate adding per-load current telemetry to reduce
  ambiguity in future load-fault isolation.

## 8. Lessons Learned
- Context-aware monitoring (expected-behavior checks) detected the
  anomaly ~15 minutes earlier than static limits alone would have.
  Early detection preserved the full response timeline.
- Multi-channel corroboration (thermal trend + current step +
  voltage sag) enabled a confident Branch B diagnosis and prevented
  a false "sensor glitch" dismissal.
- Event logging captured the trend-check trigger but not the
  concurrent current-limit violation; ground software should log
  all violated limits per frame (see dashboard "future
  improvements").
