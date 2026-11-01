"""Clinical simplified score for non-gastric-cancer death in early gastric cancer.

Reference implementation of the scoring system used by ``index.html``.
Pure Python standard library; no dependencies.

    total score = floor((age - 25) / 5)
                  + 7 * COPD
                  + 5 * moderate-to-severe kidney disease
                  + 9 * metastatic tumour
                  + 6 * diabetes with end-organ damage
                  + 7 * haematological malignancy (lymphoma or leukaemia)

A total score >= 12 defines the high-risk group. The 36- and 60-month risks
reported are Kaplan-Meier estimates of non-gastric-cancer death for each risk
group in the development cohort; they are group-level estimates, not
individualised competing-risk cumulative incidences.

Command-line example::

    python egc_score.py 66 --copd --kidney
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import floor

AGE_MIN = 25
AGE_MAX = 120
AGE_ORIGIN = 25
AGE_STEP = 5
RISK_CUTOFF = 12

# key -> (label, points)
FACTORS: dict[str, tuple[str, int]] = {
    "copd": ("Chronic obstructive pulmonary disease (COPD)", 7),
    "kidney": ("Moderate-to-severe kidney disease", 5),
    "metastatic": ("Metastatic solid tumour", 9),
    "diabetes": ("Diabetes with end-organ damage", 6),
    "hematologic": ("Haematological malignancy (lymphoma or leukaemia)", 7),
}

# Kaplan-Meier non-gastric-cancer death risk by group (development cohort)
GROUP_RISK = {
    "low": {"risk_36_months": 0.034, "risk_60_months": 0.066},
    "high": {"risk_36_months": 0.204, "risk_60_months": 0.359},
}


@dataclass(frozen=True)
class ScoreResult:
    age_points: int
    condition_points: int
    total_score: int
    risk_group: str  # "low" or "high"
    risk_36_months: float
    risk_60_months: float
    item_points: dict[str, int]


def calculate_score(age: float, **conditions: bool) -> ScoreResult:
    """Return the simplified score, risk group and group-level KM risks.

    ``age`` is age in years at diagnosis (25-120). Each keyword in ``FACTORS``
    is True/False (or 1/0); omitted conditions are treated as absent.
    """
    unknown = set(conditions) - set(FACTORS)
    if unknown:
        raise ValueError(f"Unknown condition(s): {', '.join(sorted(unknown))}")
    age = float(age)
    if not AGE_MIN <= age <= AGE_MAX:
        raise ValueError(f"Age must be between {AGE_MIN} and {AGE_MAX} years.")

    age_points = floor((age - AGE_ORIGIN) / AGE_STEP)
    item_points = {
        key: points if bool(conditions.get(key, False)) else 0
        for key, (_, points) in FACTORS.items()
    }
    condition_points = sum(item_points.values())
    total = age_points + condition_points
    group = "high" if total >= RISK_CUTOFF else "low"
    return ScoreResult(
        age_points=age_points,
        condition_points=condition_points,
        total_score=total,
        risk_group=group,
        risk_36_months=GROUP_RISK[group]["risk_36_months"],
        risk_60_months=GROUP_RISK[group]["risk_60_months"],
        item_points=item_points,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("age", type=float, help="age in years (25-120)")
    for key, (label, points) in FACTORS.items():
        parser.add_argument(f"--{key}", action="store_true", help=f"{label} ({points} points)")
    args = parser.parse_args()

    r = calculate_score(args.age, **{k: getattr(args, k) for k in FACTORS})
    print(f"Age points:        {r.age_points}")
    print(f"Comorbidity points: {r.condition_points}")
    print(f"Total score:       {r.total_score}")
    print(f"Risk group:        {r.risk_group} (cut-off >= {RISK_CUTOFF})")
    print(f"36-month group risk: {r.risk_36_months:.1%}")
    print(f"60-month group risk: {r.risk_60_months:.1%}")


if __name__ == "__main__":
    main()
