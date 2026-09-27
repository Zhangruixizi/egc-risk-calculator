"""早期胃癌患者非胃癌死亡风险模型。

本模块实现锁定的线性 Survival-SVM 连续风险评分、36/60个月绝对风险
换算，以及用于临床展示的整数积分和风险分层。

整数积分仅用于高低风险分层；绝对风险必须由连续 Survival-SVM 评分计算。
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, floor
from typing import Mapping


RISK_CUTOFF = 9
CALIBRATION_COEFFICIENT = 2.148962
BASELINE_SURVIVAL_36 = 0.955523128
BASELINE_SURVIVAL_60 = 0.909956429


@dataclass(frozen=True)
class Predictor:
    """模型变量的锁定参数。"""

    key: str
    label: str
    points: int
    beta: float
    mean: float
    sd: float


AGE = Predictor(
    key="age",
    label="年龄",
    points=0,
    beta=0.166632905,
    mean=66.064165844,
    sd=8.501717451,
)

PREDICTORS: tuple[Predictor, ...] = (
    Predictor("copd", "慢性阻塞性肺疾病（COPD）", 7, 0.156021618, 0.058242843, 0.234202080),
    Predictor("myocardial_infarction", "心肌梗死", 4, 0.098045484, 0.083909181, 0.277251565),
    Predictor("moderate_to_severe_kidney_disease", "中重度肾脏疾病", 4, 0.093176281, 0.051332675, 0.220675399),
    Predictor("metastatic_tumor", "转移性实体肿瘤", 7, 0.104440442, 0.023692004, 0.152087780),
    Predictor("diabetes_with_end_organ_damage", "伴终末器官损害的糖尿病", 3, 0.051327715, 0.030602172, 0.172237275),
    Predictor("lymphoma", "淋巴瘤", 5, 0.039493245, 0.005923001, 0.076732777),
    Predictor("leukemia", "白血病", 5, 0.024594699, 0.002961500, 0.054339028),
)


@dataclass(frozen=True)
class Prediction:
    """单名患者的计算结果。"""

    age_points: int
    comorbidity_points: int
    total_score: int
    risk_group: str
    continuous_risk_score: float
    risk_36_months: float
    risk_60_months: float
    item_scores: dict[str, int]


def _binary(value: object, name: str) -> int:
    """将布尔值或0/1标准化为模型所需的0或1。"""
    if isinstance(value, bool):
        return int(value)
    if value in (0, 1):
        return int(value)
    raise ValueError(f"{name} 必须为0/1或True/False。")


def calculate_prediction(age: float, conditions: Mapping[str, object]) -> Prediction:
    """计算临床整数积分、风险分层和36/60个月绝对风险。

    Parameters
    ----------
    age:
        患者初次确诊时的年龄（岁）。模型开发队列的观察范围为50–89岁；
        范围外仍可返回计算值，但应在临床解释时保持谨慎。
    conditions:
        7项合并症的字典，键必须使用 ``PREDICTORS`` 中的英文key，值为0/1
        或False/True。

    Returns
    -------
    Prediction
        包含临床简化积分、风险分层、连续SVM评分及36/60个月绝对风险。
    """
    try:
        age = float(age)
    except (TypeError, ValueError) as exc:
        raise ValueError("年龄必须是有效数字。") from exc
    if not 0 < age < 120:
        raise ValueError("年龄应为0至120岁之间的数值。")

    unknown = set(conditions) - {predictor.key for predictor in PREDICTORS}
    if unknown:
        raise ValueError(f"存在未知的合并症变量：{', '.join(sorted(unknown))}")

    values = {predictor.key: _binary(conditions.get(predictor.key, 0), predictor.label) for predictor in PREDICTORS}

    # 临床简化积分：仅用于高、低风险分层。
    age_points = floor((age - 50) / 5)
    item_scores = {predictor.key: values[predictor.key] * predictor.points for predictor in PREDICTORS}
    comorbidity_points = sum(item_scores.values())
    total_score = age_points + comorbidity_points
    risk_group = "高风险组" if total_score >= RISK_CUTOFF else "低风险组"

    # 连续线性 Survival-SVM 评分：RS = Σ beta_j * (x_j - mean_j) / SD_j。
    continuous_risk_score = AGE.beta * ((age - AGE.mean) / AGE.sd)
    continuous_risk_score += sum(
        predictor.beta * ((values[predictor.key] - predictor.mean) / predictor.sd)
        for predictor in PREDICTORS
    )

    # 锁定的OOF Cox校准关系：Risk(t) = 1 - S0(t) ^ exp(2.148962 * RS)。
    calibrated_multiplier = exp(CALIBRATION_COEFFICIENT * continuous_risk_score)
    risk_36_months = 1 - BASELINE_SURVIVAL_36**calibrated_multiplier
    risk_60_months = 1 - BASELINE_SURVIVAL_60**calibrated_multiplier

    return Prediction(
        age_points=age_points,
        comorbidity_points=comorbidity_points,
        total_score=total_score,
        risk_group=risk_group,
        continuous_risk_score=continuous_risk_score,
        risk_36_months=risk_36_months,
        risk_60_months=risk_60_months,
        item_scores=item_scores,
    )
