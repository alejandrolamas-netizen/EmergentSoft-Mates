"""Read-only CSV ingestion for consented industrial shift records."""
import csv
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO

from .simulator import MachineLine

REQUIRED_COLUMNS = (
    "timestamp", "line_id", "shift_hours", "units_per_hour", "utilization",
    "planned_downtime_minutes", "unplanned_downtime_minutes",
    "changeover_minutes", "energy_kwh_per_hour", "quality_rate",
)


class CsvDataError(ValueError):
    """Raised when a CSV file violates the industrial data contract."""


@dataclass(frozen=True)
class ShiftRecord:
    timestamp: datetime
    line: MachineLine


def _parse_number(value: str, column: str, row_number: int) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise CsvDataError(f"row {row_number}: column '{column}' must be numeric") from exc
    if not math.isfinite(parsed):
        raise CsvDataError(f"row {row_number}: column '{column}' must be a finite number")
    return parsed


def load_shift_records(source: str | Path | TextIO) -> list[ShiftRecord]:
    """Load validated shift snapshots from a path or open text stream."""
    should_close = not hasattr(source, "read")
    handle = open(source, "r", encoding="utf-8-sig", newline="") if should_close else source
    try:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise CsvDataError("CSV contains duplicate column names")
        missing = [column for column in REQUIRED_COLUMNS if column not in headers]
        if missing:
            raise CsvDataError("CSV is missing required columns: " + ", ".join(missing))

        records: list[ShiftRecord] = []
        for row_number, row in enumerate(reader, start=2):
            if not row or all(value is None or not str(value).strip() for value in row.values()):
                continue
            if None in row:
                raise CsvDataError(f"row {row_number}: contains more values than the header")
            missing_values = [column for column in REQUIRED_COLUMNS if row.get(column) is None]
            if missing_values:
                raise CsvDataError(
                    f"row {row_number}: missing values for " + ", ".join(missing_values)
                )
            try:
                timestamp = datetime.fromisoformat((row["timestamp"] or "").strip())
            except ValueError as exc:
                raise CsvDataError(f"row {row_number}: timestamp must be ISO 8601") from exc
            line_id = (row["line_id"] or "").strip()
            if not line_id:
                raise CsvDataError(f"row {row_number}: line_id is required")

            numeric = {
                column: _parse_number(row[column], column, row_number)
                for column in REQUIRED_COLUMNS
                if column not in ("timestamp", "line_id")
            }
            try:
                line = MachineLine(line_id=line_id, data_class="csv_imported_unverified", **numeric)
            except (TypeError, ValueError) as exc:
                raise CsvDataError(f"row {row_number}: {exc}") from exc
            records.append(ShiftRecord(timestamp=timestamp, line=line))

        if not records:
            raise CsvDataError("CSV contains no shift records")
        return records
    except csv.Error as exc:
        raise CsvDataError(f"invalid CSV: {exc}") from exc
    finally:
        if should_close:
            handle.close()
