# 早期胃癌患者非胃癌死亡风险计算器（本地 Python 版）

本目录包含与公开网页一致的锁定模型公式：

- 8项预测因子：年龄、COPD、心肌梗死、中重度肾脏疾病、转移性实体肿瘤、伴终末器官损害的糖尿病、淋巴瘤、白血病；
- 临床简化积分用于高低风险分层（总分≥9分为高风险组）；
- 36个月和60个月绝对风险由连续线性 Survival-SVM 评分及锁定的OOF Cox校准关系计算，**不是**由整数总分直接换算。

## 本地启动

在本目录打开终端后执行：

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

终端会显示本地访问地址，通常为 `http://localhost:8501`。

## 算法调用示例

```python
from risk_model import calculate_prediction

patient = {
    "copd": False,
    "myocardial_infarction": True,
    "moderate_to_severe_kidney_disease": False,
    "metastatic_tumor": False,
    "diabetes_with_end_organ_damage": False,
    "lymphoma": False,
    "leukemia": False,
}

result = calculate_prediction(age=70, conditions=patient)
print(result.total_score, result.risk_group)
print(result.risk_36_months, result.risk_60_months)
```

## 重要说明

该模型来自回顾性队列的开发与外部验证，适用于初次确诊时临床判断为早期胃癌的患者。开发队列年龄观察范围为50–89岁；范围外输入仍可完成数学计算，但临床解释应谨慎。本工具用于研究、风险沟通和临床辅助评估，不构成独立的诊断或治疗建议。
