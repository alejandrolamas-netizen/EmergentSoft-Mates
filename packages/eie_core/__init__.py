"""EmergentSoft Intelligence Engine — deterministic, provider-agnostic core."""
from .engine import (
    Candidate, Criterion, Evaluation, CampaignResult,
    run_campaign, weighted_reward,
)

__all__ = [
    "Candidate", "Criterion", "Evaluation", "CampaignResult",
    "run_campaign", "weighted_reward",
]
