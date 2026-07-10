# MiniSat-1 Mission Rules
**Document ID:** OPS-RULES-001 | **Rev:** A

Mission rules are standing constraints agreed before operations.
They remove deliberation from time-critical decisions. Rules are
mandatory; deviation requires Mission Director approval and a
documented rationale.

## Power and Thermal (EPS)
- **MR-01:** Battery voltage shall not be permitted below 7.2 V.
  At or below 7.2 V, all non-essential loads are shed immediately.
- **MR-02:** Battery temperature above 25 C is a caution condition;
  above 35 C is a critical condition requiring immediate action per
  OP-EPS-001.
- **MR-03:** A battery temperature RISE >= 1.0 C over 5 minutes
  during eclipse shall be treated as an anomaly indicator regardless
  of absolute temperature.
- **MR-04:** Battery preservation takes precedence over payload data
  return in all cases.

## Attitude Control (ADCS)
- **MR-05:** Pointing error above 5 deg is a caution condition;
  above 10 deg is critical.
- **MR-06:** Reaction wheel speed above 4000 rpm requires momentum
  management planning; above 5000 rpm is critical.

## Operations and Commanding
- **MR-07:** No commanding during anomaly characterization
  (procedure Section 4 activities) until verification steps are
  complete.
- **MR-08:** Payload is the first load shed under any power or
  thermal stress condition.
- **MR-09:** An uncommanded mode change shall be investigated before
  routine operations resume.
- **MR-10:** Every anomaly that reaches RED status shall be closed
  out with an Anomaly Response Report before the anomaly is
  considered resolved.

## Rationale Traceability
Limits in MR-01 through MR-06 derive from characterized nominal
behavior (commissioning baseline) plus margin: nominal eclipse
voltage floor 7.5 V, nominal eclipse discharge -0.45 A, nominal
battery temperature range 10-15 C, nominal pointing ~1.5 deg,
nominal wheel speed ~2000 rpm. Detection thresholds implemented in
the ground system (src/anomaly_detector.py) are identical to the
values stated here.
