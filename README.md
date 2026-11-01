# Non-Gastric-Cancer Death Risk Calculator for Early Gastric Cancer

**早期胃癌患者非胃癌死亡风险计算器**

**Online calculator / 在线计算器：** https://zhangruixizi.github.io/egc-risk-calculator/

An open-source web calculator for the clinical simplified score derived from a locked post-LASSO Cox model. It stratifies patients with early gastric cancer into low- and high-risk groups for non-gastric-cancer death before treatment.

The calculator is a single static HTML page. All calculations run locally in the user's browser; no data are uploaded or stored, and nothing needs to be installed.

## Scoring system

```
Total score = floor((age − 25) / 5)
            + 9 × metastatic solid tumour
            + 7 × haematological malignancy (lymphoma or leukaemia)
            + 7 × chronic obstructive pulmonary disease (COPD)
            + 6 × diabetes with end-organ damage
            + 5 × moderate-to-severe kidney disease
```

| Item | Points |
|---|---|
| Age | 1 point per 5 years above 25, i.e. floor((age − 25) / 5) |
| Metastatic solid tumour | 9 |
| Haematological malignancy (lymphoma or leukaemia) | 7 |
| COPD | 7 |
| Diabetes with end-organ damage | 6 |
| Moderate-to-severe kidney disease | 5 |

The cut-off of 12 points was chosen as the maximally selected standardized log-rank statistic in the development cohort. The same fixed cut-off was used in external validation.

| Risk group | Total score | 36-month risk* | 60-month risk* |
|---|---|---|---|
| Low | < 12 | 3.4% | 6.6% |
| High | ≥ 12 | 20.4% | 35.9% |

\* Kaplan–Meier estimates of non-gastric-cancer death for each risk group in the development cohort. These are group-level estimates, not individualised competing-risk cumulative incidences.

## Files

| File | Purpose |
|---|---|
| `index.html` | The web calculator (HTML, CSS and JavaScript in one file, no dependencies) |
| `egc_score.py` | Reference Python implementation of the same score (standard library only) |
| `LICENSE` | MIT License |

## Usage

**Web:** open the online link above. To use it offline, download `index.html` and open it in any modern browser.

**Python** (3.8+, no packages required):

```bash
python egc_score.py 66 --metastatic
```

```python
from egc_score import calculate_score

r = calculate_score(70, copd=True, kidney=True)
print(r.total_score, r.risk_group, r.risk_36_months, r.risk_60_months)
```

Condition keywords: `copd`, `kidney`, `metastatic`, `diabetes`, `hematologic`.

## Intended use

This tool supports pre-treatment communication of overall prognostic risk and risk stratification. It is intended for research and clinical decision support. It does not by itself determine the choice of treatment, such as ESD, surgery or watchful observation, and it is not a substitute for clinical judgement.

## Citation

If you use this calculator, please cite the associated article (citation to be added upon publication).

## License

Released under the [MIT License](LICENSE).

---

## 中文说明

**在线地址：** https://zhangruixizi.github.io/egc-risk-calculator/

本项目是基于锁定的 Post-LASSO Cox 模型的临床简易积分开源网页计算器，用于早期胃癌患者治疗前的非胃癌死亡风险分层。网页为单个静态 HTML 文件，所有计算均在浏览器本地完成，不上传、不存储任何数据，使用者无需安装任何软件。

**积分公式：** 总分 = floor［（年龄 − 25）/ 5］+ 9×转移性肿瘤 + 7×血液系统恶性肿瘤（淋巴瘤或白血病任一项）+ 7×慢性阻塞性肺疾病 + 6×伴终末器官损害的糖尿病 + 5×中重度肾病。

**风险分层：** 12 分为截断值，由开发队列最大标准化 log-rank 统计量确定。总分＜12 分为低风险组（36/60 个月风险 3.4%/6.6%），≥12 分为高风险组（20.4%/35.9%）。外部验证使用同一固定截断点。以上风险为开发队列中相应风险组的 Kaplan–Meier 非胃癌死亡风险估计，并非个体化的竞争风险累计发生率。

**适用范围：** 本工具用于治疗前综合预后风险沟通与风险分层，不单独决定 ESD、外科手术或保守观察等治疗方式。

**开源许可：** MIT 许可证。
