# Digital South — Industrial shift CSV contract

## Purpose

One CSV row represents one production-line shift snapshot. The integrated example evaluates every row in the file and reports per-shift evidence plus arithmetic-mean normalized metrics. Its energy-efficiency score is a normalized good-units-per-kWh productivity proxy, not a claim that total energy consumption falls in the scenario. This is a read-only interchange format for authorized, anonymized exports, not a live telemetry protocol.

## Required columns

| Column | Type / unit | Meaning |
|---|---|---|
| timestamp | ISO 8601 datetime | Shift reference time; include timezone where known |
| line_id | text | Stable pseudonymous production-line identifier |
| shift_hours | hours | Scheduled shift duration |
| units_per_hour | units/hour | Nominal throughput under the agreed reference condition |
| utilization | ratio [0, 1] | Measured utilization for the shift |
| planned_downtime_minutes | minutes | Planned downtime during the shift |
| unplanned_downtime_minutes | minutes | Unplanned downtime during the shift |
| changeover_minutes | minutes | Total changeover time during the shift |
| energy_kwh_per_hour | kWh/hour | Average energy rate used by the current first-order model |
| quality_rate | ratio [0, 1] | Good units divided by total units |

## Validation rules

- All columns are required; numeric values must be finite.
- Shift duration and nominal throughput must be positive.
- Utilization and quality rate must be between 0 and 1.
- Downtime, changeover and energy values cannot be negative.
- Timestamps must use ISO 8601.
- Empty files and files with no records are rejected.
- Invalid rows fail with a row number and a specific validation message; records are not silently repaired.

## Example

The repository includes data/industrial_shift_template.csv. Its records are synthetic and must never be described as factory measurements.

## Run the adapter

```python
from packages.industrial_twin.csv_adapter import load_shift_records

records = load_shift_records("data/industrial_shift_template.csv")
for record in records:
    print(record.timestamp, record.line.line_id)
```

## Data governance for a pilot

Obtain written permission from the data owner. Remove personal data, customer names, order identifiers, proprietary product details and other unnecessary identifiers. Agree on timezone, measurement definitions, sampling interval, retention period and permitted use.

Do not upload confidential factory data to a public repository. Do not connect this adapter to PLC/SCADA/MES systems or use its output to control equipment.

## Model limitation

CSV-imported records are labeled `csv_imported_unverified` in simulation evidence. The bundled template is synthetic even though it enters through the CSV adapter. The adapter does not make the simulator calibrated, predictive or live-connected. Energy estimation and throughput assumptions must be validated against observed plant data before any operational or financial claim is made.
