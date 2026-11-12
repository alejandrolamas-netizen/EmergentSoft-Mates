# Digital South — Industrial Digital Twin foundation

## Role in the architecture

The Industrial Digital Twin is the first domain application of the EmergentSoft Intelligence Engine (EIE).

- The twin represents a production line through explicit operating parameters.
- The simulator evaluates alternative operating scenarios.
- EIE compares scenario outputs against weighted objectives and preserves evidence.
- A validated, read-only CSV adapter now converts authorized shift exports into simulator inputs. The bundled CSV remains synthetic.

## Current prototype scope

The current implementation is a deterministic, first-order scenario estimator. It models shift duration, utilization, planned/unplanned downtime, changeover time, nominal throughput, quality rate and energy consumption.

It is **not yet**:
- connected to PLC, SCADA, MES, ERP, sensors or IoT gateways;
- calibrated against a real factory;
- a discrete-event or physics-based simulator;
- a predictive-maintenance model;
- an operational recommendation system.

The example uses synthetic demonstration parameters and illustrative normalization thresholds. It must not be presented as measured factory performance or as a validated savings estimate.

## Data ingestion and run

The CSV schema is documented in [INDUSTRIAL-DATA-CONTRACT.md](INDUSTRIAL-DATA-CONTRACT.md). The adapter validates timestamps, required columns, numeric values and operating ranges.

```bash
python examples/digital_south_twin_eie.py
python examples/digital_south_twin_eie.py path/to/authorized_shift_export.csv
python -m unittest discover -s tests -v
```

Every CSV row is simulated for each candidate scenario. EIE scores the arithmetic mean of the normalized per-shift metrics and retains the individual shift results in its evidence trace. The bundled template is synthetic; provide only anonymized, authorized plant exports for a pilot. CSV imports are marked unverified until a plant data owner confirms their definitions and provenance.

## Path to a real pilot

1. Define one production line and obtain permission to use its data.
2. Agree on data dictionary, units, sampling intervals and ownership.
3. Capture baseline cycle time, throughput, quality, downtime, changeovers and energy.
4. Validate simulator assumptions with plant personnel.
5. Compare simulated outputs with held-out observed periods; report error and uncertainty.
6. Keep human approval mandatory before any operational intervention.

## Data integration boundary

A future adapter should ingest read-only, consented data from CSV exports or approved MES/SCADA interfaces. Do not connect to or control industrial equipment from this prototype.
