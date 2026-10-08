# 文献覆盖

[首页](../README.md) · [文献目录](../catalog/README.md) · [机器可读报告](../data/coverage_report.json)

本页汇总文献目录与正文引用的对应关系，提供专题覆盖、跨章引用与内容维护的统计入口。

## 总览

| 指标 | 数量 |
| --- | ---: |
| 文献记录 | 2050 |
| 研究专题 | 16 |
| 跨专题章节 | 2 |
| 专题引用的文献记录（去重） | 651 |
| 专题引用占文献库比例 | 31.8% |
| 专题正文汉字 | 144554 |
| 跨专题正文汉字 | 12164 |

## 各专题覆盖

引用记录按章去重，包含本专题主类和关联方向。主类覆盖率表示该类文献在所属专题中的引用比例。

| 专题 | 正文汉字 | 引用记录 | 其中主类 | 其中跨类 | 主类文献数 | 主类覆盖率 | 检查 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [01_basics](../chapters/01_basics.md) | 9094 | 40 | 12 | 28 | 12 | 100.0% | PASS |
| [02_memory](../chapters/02_memory.md) | 8906 | 39 | 39 | 0 | 147 | 26.5% | PASS |
| [03_skills_and_self_improvement](../chapters/03_skills_and_self_improvement.md) | 9439 | 44 | 41 | 3 | 191 | 21.5% | PASS |
| [04_training_data](../chapters/04_training_data.md) | 7832 | 35 | 25 | 10 | 25 | 100.0% | PASS |
| [05_rl_and_distillation](../chapters/05_rl_and_distillation.md) | 9186 | 48 | 41 | 7 | 159 | 25.8% | PASS |
| [06_evaluation](../chapters/06_evaluation.md) | 10418 | 56 | 56 | 0 | 249 | 22.5% | PASS |
| [07_safety](../chapters/07_safety.md) | 9011 | 41 | 25 | 16 | 58 | 43.1% | PASS |
| [08_collaboration](../chapters/08_collaboration.md) | 8990 | 31 | 22 | 9 | 22 | 100.0% | PASS |
| [09_multimodal_gui](../chapters/09_multimodal_gui.md) | 8544 | 44 | 33 | 11 | 38 | 86.8% | PASS |
| [10_world_models](../chapters/10_world_models.md) | 8884 | 44 | 44 | 0 | 205 | 21.5% | PASS |
| [11_embodied](../chapters/11_embodied.md) | 9336 | 58 | 58 | 0 | 303 | 19.1% | PASS |
| [12_science](../chapters/12_science.md) | 7795 | 30 | 15 | 15 | 15 | 100.0% | PASS |
| [13_efficiency](../chapters/13_efficiency.md) | 7856 | 42 | 42 | 0 | 96 | 43.8% | PASS |
| [14_model_science](../chapters/14_model_science.md) | 8312 | 42 | 42 | 0 | 75 | 56.0% | PASS |
| [15_frontier_reports](../chapters/15_frontier_reports.md) | 12397 | 48 | 43 | 5 | 43 | 100.0% | PASS |
| [16_generation](../chapters/16_generation.md) | 8554 | 44 | 44 | 0 | 120 | 36.7% | PASS |

## 跨专题章节

[综述导读](../chapters/00_surveys.md)与[Hot Words](../chapters/17_hot_words.md)连接多个方向，单独统计论文和一手网页引用。

| 章节 | 正文汉字 | 引用数 | 检查 |
| --- | ---: | ---: | --- |
| 00_surveys | 6429 | 23 | PASS |
| 17_hot_words | 5735 | 25 | PASS |

## 统计方法

- 以文献标识匹配正文引用，并按章和全库分别去重。
- 正文汉字统计排除注释、代码块、链接目标和未使用的链接定义。
- 文献库外的经典工作、补充论文和网页单独记录；目录本身不计入正文引用。
- 逐条引用位置、元数据完整性、未引记录和输入校验值保存在机器可读报告中。

## 检查结果

专题与跨专题章节的数量检查通过。

## 更新统计

在项目根目录运行：

```bash
python3 scripts/audit_coverage.py
python3 scripts/audit_coverage.py --check
```

生成命令更新本页及 `data/coverage_report.json`；`--check` 检查内容阈值与报告一致性，不修改文件。
复杂链接和自定义 Markdown 扩展需要结合[质量检查](quality_review.md)复核。
