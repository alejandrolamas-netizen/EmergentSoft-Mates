import io
import unittest
from datetime import datetime

from packages.industrial_twin.csv_adapter import CsvDataError, load_shift_records

HEADER = (
    "timestamp,line_id,shift_hours,units_per_hour,utilization,"
    "planned_downtime_minutes,unplanned_downtime_minutes,changeover_minutes,"
    "energy_kwh_per_hour,quality_rate\n"
)
VALID_ROW = "2026-11-01T06:00:00-03:00,line-01,8,12,0.82,20,35,45,18,0.96\n"


class CsvAdapterTests(unittest.TestCase):
    def test_loads_valid_shift_record(self):
        records = load_shift_records(io.StringIO(HEADER + VALID_ROW))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].line.line_id, "line-01")
        self.assertEqual(records[0].line.shift_hours, 8)
        self.assertIsInstance(records[0].timestamp, datetime)
        self.assertEqual(records[0].line.data_class, "csv_imported_unverified")

    def test_rejects_missing_columns(self):
        with self.assertRaisesRegex(CsvDataError, "missing required columns"):
            load_shift_records(io.StringIO("timestamp,line_id\n"))

    def test_rejects_invalid_utilization(self):
        invalid = VALID_ROW.replace(",0.82,", ",1.82,")
        with self.assertRaisesRegex(CsvDataError, "row 2"):
            load_shift_records(io.StringIO(HEADER + invalid))

    def test_rejects_non_finite_measurements(self):
        invalid = VALID_ROW.replace(",0.82,", ",nan,")
        with self.assertRaisesRegex(CsvDataError, "finite number"):
            load_shift_records(io.StringIO(HEADER + invalid))

    def test_rejects_extra_csv_values(self):
        invalid = VALID_ROW.rstrip("\\n") + ",unexpected\\n"
        with self.assertRaisesRegex(CsvDataError, "more values than the header"):
            load_shift_records(io.StringIO(HEADER + invalid))

    def test_rejects_invalid_timestamp(self):
        invalid = VALID_ROW.replace("2026-11-01T06:00:00-03:00", "yesterday")
        with self.assertRaisesRegex(CsvDataError, "ISO 8601"):
            load_shift_records(io.StringIO(HEADER + invalid))


if __name__ == "__main__":
    unittest.main()
