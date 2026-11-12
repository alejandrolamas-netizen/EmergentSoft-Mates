# Digital South — Industrial Digital Twin foundation

## Role in the architecture

The Industrial Digital Twin is the first domain application of the EmergentSoft Intelligence Engine (EIE).

- The twin represents a production line through explicit operating parameters.
- The simulator evaluates alternative operating scenarios.
- EIE compares scenario outputs against weighted objectives and preserves evidence.
- A future data adapter can replace synthetic inputs with validated plant telemetry.

## Current prototype scope

The current implementation is a deterministic, first-order scenario estimator. It models shift duration, utilization, planned/unplanned downtime, changeover time, nominal throughput, quality rate and energy consumption.

It is **not yet**:
- connected to PLC, SCADA, MES, ERP, sensors or IoT gateways;
- calibrated against a real factory;
- a discrete-event or physics-based simulator;
- a predictive-maintenance model;
- an operational recommendation system.

The example uses synthetic demonstration parameters and illustrative normalization thresholds. It must not be presented as measured factory performance or as a validated savings estimate.

## Run

```bash
python examples/digital_south_twin_eie.py
python -m unittest discover -s tests -v
```

## Path to a real pilot

1. Define one production line and obtain permission to use its data.
2. Agree on data dictionary, units, sampling intervals and ownership.
3. Capture baseline cycle time, throughput, quality, downtime, changeovers and energy.
4. Validate simulator assumptions with plant personnel.
5. Compare simulated outputs with held-out observed periods; report error and uncertainty.
6. Keep human approval mandatory before any operational intervention.

## Data integration boundary

A future adapter should ingest read-only, consented data from CSV exports or approved MES/SCADA interfaces. Do not connect to or control industrial equipment from this prototype.
