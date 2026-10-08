# Awesome LLM Agents

### LLM 与 Agent 前沿研究：发展脉络、方法比较与研究机会

**从 2000 余篇论文看清 LLM 与 Agent 前沿：哪些方向受到关注，大家在解决什么问题，不同工作之间有什么联系。**

本仓库围绕 LLM 与 Agent 的核心研究问题，连接经典工作与前沿进展，提供 **16 个研究专题、综述导读、Hot Words 和 2050 条文献记录**。各专题从问题背景出发，解释方法的来路、不同路线的联系与取舍，并讨论仍待解决的研究问题。

**从研究问题进入，沿方法脉络深入。** 可以先用综述建立全貌，再进入专题比较具体工作；遇到不熟悉的概念时，按需查阅前置知识、经典论文和[基础学习资源](#foundations)。

**综述与研究路线图 · 16 个研究专题 · Hot Words · 2050 条可检索文献记录**

[先读哪篇综述](#surveys) · [快速了解前沿](#start) · [专题索引](#topics) · [近期阅读](#updates) · [基础补充](#foundations) · [实践资源](docs/resources.md) · [参与贡献](#contributing)

**[17｜Hot Words：概念的来源与研究脉络](chapters/17_hot_words.md)**：从 JEV 的决策模型出发，连接 harness、Agent Skills、记忆、OPD、自演化与 long-horizon，区分名称、机制和能力目标。

> **从哪里开始？** [综述导读](chapters/00_surveys.md)帮助选择研究方向，[Agent 全局总览](docs/overview.md)介绍系统组成与核心问题；已有方向的读者可以直接进入[专题索引](#topics)。

<a id="surveys"></a>

## 第一次读论文：先选一篇综述

**[00｜综述导读：长程任务、自演化与递归自改进](chapters/00_surveys.md)** 提供各方向的研究入口：先理解问题背景与分类框架，再沿专题比较代表方法、证据与开放问题。综述与研究路线图分别注明定位，便于按研究目标选择阅读顺序。

| 想先了解的方向 | 推荐起点 | 接下来读 |
| --- | --- | --- |
| **Agent 系统与执行框架** | [Agent System and Harness Design](https://arxiv.org/abs/2606.20683v1) | [基础与工具](chapters/01_basics.md) |
| **Long-horizon：长程任务** | [Towards Long-Horizon Agents: A Survey](https://long-horizon-agents.github.io/) | [记忆](chapters/02_memory.md) · [评测](chapters/06_evaluation.md) |
| **Self-evolving：自演化** | [Self-Improvements in Modern Agentic Systems](https://arxiv.org/abs/2607.13104v1) | [技能与自改进](chapters/03_skills_and_self_improvement.md) |
| **RSI：递归自改进** | [Recursive Self-Improvement in AI](https://arxiv.org/abs/2607.07663v2) · [The Last AI Built by Humans](https://arxiv.org/abs/2609.11873v3) | [综述章的概念区分](chapters/00_surveys.md) · [自改进方法](chapters/03_skills_and_self_improvement.md) |
| **编码 Agent 的持续改进** | [Self-Evolving Coding Agents](https://arxiv.org/abs/2608.03392v4) | [训练数据](chapters/04_training_data.md) · [评测](chapters/06_evaluation.md) |

更多技能、协作、安全、GUI、世界模型与具身方向综述，见[完整导读](chapters/00_surveys.md)。先认清问题和路线，再读单篇方法，比从热榜上随机挑论文更有方向。

<a id="start"></a>

## 快速了解前沿

先看研究问题，再看方法分支，最后选择论文深入阅读。不必按章节顺序通读，也不必先读完所有经典论文。

| 你的目标 | 推荐路线 |
| --- | --- |
| **快速知道大家在做什么** | [综述导读](chapters/00_surveys.md) → [专题索引](#topics) → 感兴趣章节的研究分支与近期论文导读 |
| **深入一个方向，比较不同路线** | 选择专题 → 读发展脉络与方法比较 → 沿章节引用查原文 → 在[全量目录](catalog/README.md)继续查找相关工作 |
| **寻找值得研究的问题** | 专题中的局限与开放问题 → [八个跨方向研究问题](docs/research_questions.md) → [跨专题研究进展](docs/after_snapshot.md) |
| **阅读时发现基础不够** | 按需查[前置知识](docs/llm_primer.md)与[术语表](docs/glossary.md)；需要系统学习时转到[基础补充资源](#foundations)，再回到专题 |

串联这些论文的主线是：**如何让模型从生成回答，走向持续、可靠地完成任务？** 工具、记忆和协作改变系统的执行方式；数据、强化学习和蒸馏改变能力的获得方式；GUI、机器人与科研任务引入不同环境中的约束。评测、安全和效率则贯穿这些方向。

```text
                        用户目标
                           ↓
                 观察 → 决策 → 执行动作
                   ↑               │
                   └─── 环境反馈 ──┘
                           ↓
                    验证结果与交付

系统能力    工具使用 · 记忆 · 技能 · 协作
学习方法    交互数据 · 强化学习 · 蒸馏
任务环境    网页与桌面 · 机器人 · 科研
贯穿各层    评测 · 安全 · 计算效率
```

<a id="topics"></a>

## 专题索引

各专题采用“**方向背景 → 基础概念 → 经典发展脉络 → 前沿研究方向 → 比较与研究机会**”的结构。综述解释问题与方法，配套目录提供完整的文献检索入口。

### Agent 系统：从工具调用到可靠执行

| 方向 | 主要内容 | 阅读入口 |
| --- | --- | --- |
| **01 · 基础、规划与工具使用** | Agent 工作循环、任务分解、工具接口、观察与证据选择 | [综述](chapters/01_basics.md) · [论文](catalog/01_basics.md) |
| **02 · 记忆与上下文** | 工作记忆、长期记忆、检索、压缩、写入与遗忘 | [综述](chapters/02_memory.md) · [论文](catalog/02_memory.md) |
| **03 · 技能库与自改进** | 经验复用、技能发现、反馈学习、自动修改与能力积累 | [综述](chapters/03_skills_and_self_improvement.md) · [论文](catalog/03_skills_and_self_improvement.md) |
| **06 · 评测与能力基准** | 更长的任务链、更复杂的能力组合，以及跨领域场景覆盖 | [综述](chapters/06_evaluation.md) · [论文](catalog/06_evaluation.md) |
| **07 · 安全与对齐** | 提示注入、工具权限、欺骗、奖励漏洞与人工监督 | [综述](chapters/07_safety.md) · [论文](catalog/07_safety.md) |
| **08 · 多智能体与人机协作** | 角色分工、通信与协调、协作成本、人工接管 | [综述](chapters/08_collaboration.md) · [论文](catalog/08_collaboration.md) |

### 训练与底层能力：Agent 如何学会做事

| 方向 | 主要内容 | 阅读入口 |
| --- | --- | --- |
| **04 · 训练数据与交互环境** | 行动轨迹、合成数据、数据筛选、环境与任务课程 | [综述](chapters/04_training_data.md) · [论文](catalog/04_training_data.md) |
| **05 · 强化学习与蒸馏** | 结果反馈、信用分配、策略优化、教师与学生训练 | [综述](chapters/05_rl_and_distillation.md) · [论文](catalog/05_rl_and_distillation.md) |
| **13 · 推理效率与模型架构** | 推理预算、缓存与压缩、循环计算、延迟与计算成本 | [综述](chapters/13_efficiency.md) · [论文](catalog/13_efficiency.md) |
| **14 · 模型科学与可解释性** | 表征、优化、能力来源、机制解释与实验验证 | [综述](chapters/14_model_science.md) · [论文](catalog/14_model_science.md) |

### 交互与应用：从数字环境走向物理世界

| 方向 | 主要内容 | 阅读入口 |
| --- | --- | --- |
| **09 · 多模态理解与 GUI Agent** | 视觉理解、屏幕定位、网页与桌面操作、交互反馈 | [综述](chapters/09_multimodal_gui.md) · [论文](catalog/09_multimodal_gui.md) |
| **10 · 世界模型与规划** | 状态表征、动态预测、行动后果、基于模型的规划 | [综述](chapters/10_world_models.md) · [论文](catalog/10_world_models.md) |
| **11 · 具身智能与 VLA** | 视觉—语言—动作模型、机器人操作、迁移与真实执行 | [综述](chapters/11_embodied.md) · [论文](catalog/11_embodied.md) |
| **12 · 科研与数学 Agent** | 科学假设、实验设计、程序与证明、可检验的研究产出 | [综述](chapters/12_science.md) · [论文](catalog/12_science.md) |

### 延伸阅读：理解相关能力与证据边界

| 方向 | 主要内容 | 阅读入口 |
| --- | --- | --- |
| **15 · 前沿模型技术报告** | 训练披露、评测条件、开放程度、能力声明与证据 | [综述](chapters/15_frontier_reports.md) · [论文](catalog/15_frontier_reports.md) |
| **16 · 多模态生成** | 图像与视频生成、可控性、交互生成与 Agent 的区别 | [综述](chapters/16_generation.md) · [论文](catalog/16_generation.md) |

世界模型、模型科学和多模态生成分别连接环境预测、能力解释与内容合成，为理解 Agent 的技术基础及其与其他系统的组合方式提供背景。

**其他记录：** [相邻方向](catalog/90_adjacent.md) · [待复核条目](catalog/99_review.md) · [分类说明](docs/adjacent_topics.md)

<a id="updates"></a>

## 近期阅读与项目更新

- 综述入口连接长程任务、自演化与 RSI，并补充作者项目页及研究路线图。
- 16 个专题按“方向背景 → 基础概念 → 经典发展脉络 → 前沿研究方向 → 比较与研究机会”组织；经典不限发表时间，前沿围绕趋势论文展开。
- Hot Words 追溯概念来源，并通过相关论文解释机制、应用与相邻概念的区别。
- 文献目录支持按主题与关联方向检索，机器可读数据保留来源和分类依据。
- [跨专题研究进展](docs/after_snapshot.md)串联证据组织、交互训练、科研验证与机器人执行。

版本变更见[更新记录](CHANGELOG.md)，内容规范见[章节组织说明](docs/chapter_expansion.md)。

如果你已经掌握基础，可以从这些问题切入近期内容：

| 研究问题 | 从哪里继续 |
| --- | --- |
| 长任务中，如何组织信息、保存证据并避免遗忘要求？ | [记忆与上下文](chapters/02_memory.md) · [补充研究](docs/after_snapshot.md) |
| 成功轨迹换一个执行框架，是否仍是有效的训练数据？ | [训练数据](chapters/04_training_data.md) · [强化学习与蒸馏](chapters/05_rl_and_distillation.md) |
| 自动改进和多智能体协作，怎样证明收益不是来自更多预算？ | [自改进](chapters/03_skills_and_self_improvement.md) · [协作](chapters/08_collaboration.md) · [评测](chapters/06_evaluation.md) |
| 预测环境变化，何时真正有助于规划和机器人执行？ | [世界模型](chapters/10_world_models.md) · [具身智能](chapters/11_embodied.md) |
| 科研 Agent 的产出，怎样从“看似合理”变成可验证的知识？ | [科研与数学](chapters/12_science.md) · [跨方向研究问题](docs/research_questions.md) |

<a id="foundations"></a>

## 基础补充：推荐从这些仓库开始

以下资源分别覆盖模型基础、Agent 研究体系与提示方法，可与专题中的经典工作配合阅读。

| 仓库 | 适合补充什么 | 如何与本仓库配合 |
| --- | --- | --- |
| **[Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM)** | LLM 里程碑论文、基础文献、课程及训练与推理资源 | 不熟悉模型背景时先查这里，再回来看近期方法改变了哪些环节 |
| **[LLM-Agent-Paper-List](https://github.com/WooooDyy/LLM-Agent-Paper-List)** | LLM Agent 综述及其分类论文，建立 Agent 组成、能力与应用的知识框架 | 用它建立历史脉络，再用本仓库追踪各分支的近期工作 |
| **[Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)** | 提示方法、上下文使用与相关学习材料；属于教学资源，不是纯论文列表 | 不熟悉提示与模型交互时按需补课，辅助理解 Agent 方法与实验设置 |

更多入口见[资源导航](docs/resources.md)。阅读中可按需查阅[大模型前置知识](docs/llm_primer.md)、[术语表](docs/glossary.md)和[研究机会](docs/learning_path.md)。



<a id="scope"></a>

## 文献与维护

文献目录以 AlphaXiv 趋势文献为基础，结合专题检索、经典论文及作者发布材料。每条记录按主要研究问题归类，并通过关联方向连接跨领域工作。正文保留原始引用，方法比较注明影响结论的任务设置与实验条件。

[收录与分类](docs/methodology.md) · [覆盖统计](docs/coverage.md) · [分类方法](docs/classification_audit.md) · [质量检查](docs/quality_review.md) · [来源记录](sources/README.md) · [题名与版本](docs/version_notes.md)

<a id="contributing"></a>

## 参与贡献

欢迎补充重要论文、纠正分类与引用，也欢迎指出哪段解释缺少前置知识、哪组方法比较不够清楚。具体格式见[贡献指南](CONTRIBUTING.md)。

推荐提供：**题名与原文链接 + 所属方向 + 研究问题 + 核心贡献 + 与已有工作的联系**。欢迎同时补充影响方法比较的实验设置和适用条件。

<details>
<summary><strong>仓库结构与本地检查</strong></summary>

```text
README.md       阅读入口与专题索引
chapters/       综述导读、16 个研究专题与 Hot Words
catalog/        全量分类论文目录
docs/           前置知识、研究机会、补充阅读与方法说明
data/           语料、分类规则与覆盖统计
sources/        来源核验与版本记录
scripts/        目录生成、覆盖审计与链接检查
```

阅读不需要安装依赖或申请模型 API。在仓库根目录运行以下命令可检查内容，维护脚本仅使用 Python 3 标准库：

```bash
python3 scripts/validate_guide.py
python3 scripts/audit_coverage.py --check
python3 scripts/build_catalog.py --source data/papers.jsonl --check
```

第三方论文、摘要与代码的使用请遵循各自授权；本仓库不对这些材料作统一再授权。

</details>
