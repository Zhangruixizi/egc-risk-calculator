"""Streamlit本地计算器入口。

启动：streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from risk_model import PREDICTORS, calculate_prediction


st.set_page_config(page_title="早期胃癌非胃癌死亡风险计算器", page_icon="📊", layout="wide")

st.title("早期胃癌患者非胃癌死亡风险计算器")
st.caption("基于锁定的线性 Survival-SVM 模型与临床简化积分系统")

with st.sidebar:
    st.header("患者信息")
    age = st.number_input("年龄（岁）", min_value=18, max_value=110, value=66, step=1)
    conditions: dict[str, bool] = {}
    st.subheader("合并症指标")
    for predictor in PREDICTORS:
        conditions[predictor.key] = st.toggle(f"{predictor.label}（{predictor.points}分）", value=False)

result = calculate_prediction(age, conditions)

if age < 50 or age > 89:
    st.warning("当前年龄超出模型开发队列的观察范围，结果应谨慎解释。")

left, right = st.columns([1, 1])
with left:
    st.subheader("临床简化积分")
    a, b, c = st.columns(3)
    a.metric("年龄积分", f"{result.age_points}分")
    b.metric("合并症积分", f"{result.comorbidity_points}分")
    c.metric("总分", f"{result.total_score}分")

    st.subheader("各项积分")
    rows = [{"项目": f"年龄（{age}岁）", "分值": result.age_points}]
    rows.extend(
        {"项目": f"{predictor.label}（{'是' if conditions[predictor.key] else '否'}）", "分值": result.item_scores[predictor.key]}
        for predictor in PREDICTORS
    )
    st.dataframe(rows, hide_index=True, use_container_width=True)

with right:
    st.subheader("预测结果")
    if result.risk_group == "高风险组":
        st.error(result.risk_group)
    else:
        st.success(result.risk_group)
    x, y = st.columns(2)
    x.metric("36个月预测风险", f"{result.risk_36_months:.1%}")
    y.metric("60个月预测风险", f"{result.risk_60_months:.1%}")

with st.expander("模型计算说明"):
    st.markdown(
        """
        - 临床简化积分：`floor((年龄 - 50) / 5) + 各合并症分值`；总分≥9分为高风险组。
        - 绝对风险不由整数总分直接换算，而是由锁定的线性 Survival-SVM 连续风险评分及其OOF Cox校准关系计算。
        - 本工具仅用于研究、风险沟通和临床辅助评估，不构成单独的诊断或治疗建议。
        """
    )
