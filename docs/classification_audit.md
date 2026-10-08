# 分类方法与数据说明

[文献目录](../catalog/README.md) · [贡献指南](../CONTRIBUTING.md) · [收录标准](methodology.md)

## 分类原则

以文献主要解决的研究问题确定主归属，以关联标签连接方法、对象和应用。每条记录只有一个主类，跨方向阅读不重复计数。
分类由来源类别、题名与简述规则以及显式校正共同确定。规则负责建立一致的检索入口，校正配置记录跨领域工作中需要单独判断的归属。

## 生成规则

1. 应用显式校正配置，并核对记录标识、来源类别、题名和证据片段，避免配置错用。
2. 匹配题名规则，再匹配简述规则；同一证据层内按规则优先级决定归属。自动规则不扫描完整摘要。
3. 同层同优先级的不同目标发生冲突时转入待复核，其他有效关联保留为副标签。
4. 未命中规则的记录使用来源分类转换；对证据要求较高的类别另行设置保护条件。
5. 证据不足的条目进入待复核目录，相邻学科单独保留。二者均不表示负面质量判断。

配置文件：[分类体系与规则](../data/taxonomy.json) · [显式校正](../data/classification_overrides.json)。

## 主题边界

- 评测按任务跨度、场景与能力组合组织；评分、验证、诊断及校准作为支撑方法。
- 循环架构与推理计算组织以效率为主要入口；模型表征、优化机制与可解释性以模型科学为主要入口。
- 多模态生成与世界模型分别关注内容构造与决策预测，不因使用相同生成结构而合并。
- 技术报告按所披露的研究对象阅读；发布形式本身不是能力或可靠性的证明。

## 数据完整性

| 检查项 | 数量 |
| --- | ---: |
| 文献记录 | 2050 |
| 唯一标识 | 2050 |
| 主分类 | 18 |
| 重复主归属 | 0 |

生成器检查标识唯一性、主类与关联标签合法性、元数据保留及证据片段一致性。完整记录保存在 JSONL 中，网页目录仅展示阅读所需信息。

## 分类状态

以下状态记录每条文献的分类路径，便于定位规则覆盖与人工校正。

| 状态字段 | 记录数 |
| --- | ---: |
| `local_override_reviewed` | 54 |
| `rule_assigned_unreviewed` | 882 |
| `legacy_mapped_unreviewed` | 916 |
| `needs_review` | 198 |

## 数据字段

| 字段 | 含义 |
| --- | --- |
| `id/title/url/abstract/one_line` | 来源标识、题名、链接、摘要与简述；缺失值保留为 null |
| `source_dates/likes` | 来源日期与平台关注信号 |
| `new/secondary_tags` | 主分类与关联主题 |
| `old/legacy_mapped_primary` | 导入时的来源分类及转换结果，用于追踪数据来源 |
| `reason/evidence_basis` | 分类依据与可匹配的来源片段 |
| `classification_status/classification_rule_ids` | 分类状态与所用规则 |

## 本地重建

在项目根目录执行，仅需 Python 3 标准库：

```bash
python3 scripts/build_catalog.py --source data/papers.jsonl
python3 scripts/build_catalog.py --source data/papers.jsonl --check
```

重建从保存的来源字段重新应用分类配置，不直接复用已计算的主归属。`--check` 仅在内存重建并逐字节比较，不改写文件。
导入外部文献数据时可使用 `--source /path/corpus.jsonl --assign /path/assign.json`；`--output-dir` 支持在临时目录验证输出。
生成范围包括语料 JSONL、分类目录和本说明，不改写研究章节。
