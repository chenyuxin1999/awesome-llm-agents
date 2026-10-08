# 学习与实践资源

[返回首页](../README.md) · [研究机会](learning_path.md)

研究资源可以分为三类：论文库帮助建立问题地图，教程补充概念与实现背景，实验环境则把方法放进可重复的任务中。下面按用途组织入口，便于与各专题配合使用。

## 1. 论文库、教程与项目目录

| 资源 | 内容 | 适合的用途 |
| --- | --- | --- |
| [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM) | LLM 论文、课程与工具 | 补充模型基础，查找训练和推理相关研究 |
| [LLM-Agent-Paper-List](https://github.com/WooooDyy/LLM-Agent-Paper-List) | Agent 综述配套论文库 | 建立系统组成、能力与应用的分类框架 |
| [Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | 提示方法与学习材料 | 理解模型交互、上下文组织及常见实现方式 |
| [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 应用与代码示例 | 了解不同任务如何组合模型、工具与数据 |
| [awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | Agent 项目目录 | 比较系统形态，寻找相关工程项目 |

## 2. 理解 Agent 的经典入口

| 资源 | 适合什么时候读 | 先抓住什么 |
|---|---|---|
| [ReAct](https://arxiv.org/abs/2210.03629) | 看完基础章之后 | 推理与环境动作如何交替 |
| [Toolformer](https://arxiv.org/abs/2302.04761) | 想区分训练与工具包装时 | 工具使用可以成为学习目标 |
| [Reflexion](https://arxiv.org/abs/2303.11366) | 想理解失败反馈时 | 语言反馈如何影响下一次尝试 |
| [Voyager](https://arxiv.org/abs/2305.16291) | 想理解技能积累时 | 可执行技能与探索任务如何连接 |
| [The Rise and Potential of LLM Based Agents](https://arxiv.org/abs/2309.07864) | 有基础后建立文献地图 | 早期 Agent 研究的问题分解 |
| [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 开始做小系统时 | 工作流与动态 Agent 的工程取舍 |

这些工作分别回答行动如何组织、工具如何学习、反馈如何利用以及经验如何复用。可先按关心的问题选择，再沿对应专题深入。

## 3. 把能力放进可执行环境

| 一手资源 | 对应问题 | 使用前检查 |
|---|---|---|
| [WebArena](https://github.com/web-arena-x/webarena) | 浏览器里的多步任务 | 网站版本、环境状态、成功检查器 |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | 真实仓库问题修复 | 数据分割、测试环境、模型是否接触过题目 |
| [OSWorld](https://github.com/xlang-ai/OSWorld) | 桌面电脑操作 | 系统环境、权限、重置方式、动作接口 |
| [τ-bench](https://github.com/sierra-research/tau-bench) | 用户、工具和规则同时存在的任务 | 用户模拟、约束遵守、重复试验 |
| [AgentBench](https://github.com/THUDM/AgentBench) | 不同交互环境的综合评测 | 每种环境到底测了什么，避免混用总分 |

按项目说明准备依赖与数据，固定实验版本，并从隔离环境中的最小任务开始。涉及账户、文件修改和外部操作时，使用测试数据与受限权限。

## 4. 从资源选择到研究设计

论文和代码应围绕同一个研究问题选择：先确定要改变的能力或系统组件，再寻找能观察其效果的任务。实现前检查许可证、运行要求和评测配置；比较时统一模型、工具权限与预算，分别记录完成质量、资源开销和失败原因。

执行框架的选择同样取决于任务需求。状态记录、模型替换、工具权限、失败恢复和预算统计各自解决不同问题；简单流程可以从脚本开始，复杂任务再引入相应组件。跨方向的问题设计见[研究机会](learning_path.md)，文献入口见[专题索引](../README.md#topics)。
