"""Deterministic industrial line scenario simulator.

This is a transparent, parameter-based demonstrator, not a calibrated physics model
or live-connected factory twin. Inputs must be replaced with measured plant data
before operational decisions are made.
"""
from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(frozen=True)
class MachineLine:
    line_id: str
    shift_hours: float
    units_per_hour: float
    utilization: float
    planned_downtime_minutes: float
    unplanned_downtime_minutes: float
    changeover_minutes: float
    energy_kwh_per_hour: float
    quality_rate: float

    def __post_init__(self) -> None:
        if not self.line_id:
            raise ValueError("line_id is required")
        if self.shift_hours <= 0 or self.units_per_hour <= 0:
            raise ValueError("shift_hours and units_per_hour must be positive")
        if not 0 <= self.utilization <= 1 or not 0 <= self.quality_rate <= 1:
            raise ValueError("utilization and quality_rate must be in [0, 1]")
        for value in (self.planned_downtime_minutes, self.unplanned_downtime_minutes,
                      self.changeover_minutes, self.energy_kwh_per_hour):
            if value < 0:
                raise ValueError("downtime, changeover and energy values cannot be negative")


@dataclass(frozen=True)
class Scenario:
    name: str
    downtime_reduction: float = 0.0
    changeover_reduction: float = 0.0
    utilization_delta: float = 0.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("scenario name is required")
        for value in (self.downtime_reduction, self.changeover_reduction):
            if not 0 <= value <= 1:
                raise ValueError("reduction values must be in [0, 1]")
        if not -1 <= self.utilization_delta <= 1:
            raise ValueError("utilization_delta must be in [-1, 1]")


@dataclass(frozen=True)
class SimulationResult:
    line_id: str
    scenario: str
    available_minutes: float
    productive_minutes: float
    estimated_units: float
    estimated_good_units: float
    estimated_energy_kwh: float
    uptime_rate: float
    assumptions: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def simulate(line: MachineLine, scenario: Scenario) -> SimulationResult:
    shift_minutes = line.shift_hours * 60
    downtime = line.planned_downtime_minutes + line.unplanned_downtime_minutes
    adjusted_downtime = downtime * (1 - scenario.downtime_reduction)
    adjusted_changeover = line.changeover_minutes * (1 - scenario.changeover_reduction)
    available = max(0.0, shift_minutes - adjusted_downtime - adjusted_changeover)
    utilization = min(1.0, max(0.0, line.utilization + scenario.utilization_delta))
    productive = available * utilization
    units = line.units_per_hour * productive / 60
    good_units = units * line.quality_rate
    energy = line.energy_kwh_per_hour * line.shift_hours

    return SimulationResult(
        line_id=line.line_id,
        scenario=scenario.name,
        available_minutes=round(available, 2),
        productive_minutes=round(productive, 2),
        estimated_units=round(units, 2),
        estimated_good_units=round(good_units, 2),
        estimated_energy_kwh=round(energy, 2),
        uptime_rate=round(available / shift_minutes, 4),
        assumptions={
            "data_class": "synthetic_demo_parameters",
            "utilization": utilization,
            "quality_rate": line.quality_rate,
            "energy_model": "constant_kwh_per_hour_over_shift",
            "model_scope": "deterministic_first_order_scenario_estimator",
        },
    )
