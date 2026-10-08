# 11｜具身智能与 VLA：把语言、视觉和控制接成闭环

[首页](../README.md) · [专题索引](../README.md#topics) · [文献目录](../catalog/11_embodied.md)

## 方向背景：为什么具身智能必须连接语义与控制

具身智能研究具有身体的系统怎样感知环境、理解目标并通过行动改变物理世界。语言与视觉模型提供了通用语义知识，但物理执行还受到几何、动力学、传感误差和时间延迟约束。这个方向的关键，是让高层目标与低层控制在持续反馈中协调，而不是把语言计划直接当作可执行动作。

视觉—语言—动作模型（VLA）尝试把视觉观察与语言条件映射为机器人动作，为跨任务学习提供统一接口。然而，身体结构、控制频率和接触特性决定了动作的实际含义；训练数据中的相似外观也未必意味着相似动力学。因此泛化既涉及新目标与新场景，也涉及新的身体和交互条件。

本章从示范数据、动作表示与实时推理讲起，进入空间泛化、长期记忆、触觉接触、强化学习和系统组织。评价需要同时观察任务成功、恢复能力与安全停止，并明确哪些能力由策略模型承担，哪些依赖规划器、传感器、控制器和人工干预。

## 必要前置：VLA 是策略模型，不是整个 agent 系统

**VLA（Vision-Language-Action）**将视觉、语言及可能的机器人状态映射为动作；**策略**是根据当前信息选择动作的规则或概率分布。动作可以是关节目标、末端位移，也可以是未来一段控制序列。**具身 agent 系统**还包括任务规划、传感器、工具接口、记忆、执行器、验收与安全回退。VLA 可以是其中的低层技能，也可以承担部分推理，但不等于通用 LLM agent；一个编程 agent 能调用机器人，也不意味着它内部就是 VLA。

视觉编码器把图像转换为数值向量，这种向量表示称为 **embedding**；**latent（潜表示）**强调它是模型内部学习到的变量，不一定对应可直接读出的真实物理量。动作专家或动作头负责把表示变成机器人命令。扩散策略通过逐步去噪产生动作，流匹配策略学习从噪声到动作的连续变换；两者的输出对象可以是控制序列，不必是图像。基础概念可先查[大模型入门](../docs/llm_primer.md)。

机器人必须区分任务层、技能层和控制层：任务层选择“抓杯子”，技能层预测抓取动作，控制层跟踪位置、速度或力。策略可能一次预测多个动作，即动作分块；只执行其中一部分后重新观察，称为重规划。控制器每秒更新很多次，不代表大模型每秒看了同样多次新画面，报告实时性能时必须区分这两个频率。

## 经典发展：从示范动作到语义迁移，再到可部署系统

机器人完成语言任务，需要把语义目标一路连接到可执行运动。只从示范模仿动作，难以覆盖开放指令；只靠语言推理，又不能保证动作适合身体与环境。因此经典研究围绕三个连接点展开：高层目标怎样选择可行技能，多任务经验怎样进入统一策略，连续动作怎样稳定生成与部署。它们分别处理语义、数据与控制的缺口。

行为克隆从人类或已有控制器示范中学习动作，避免随机探索，但模型犯错后容易进入示范没覆盖的状态。语言模型能分解任务，却可能选择机器人没有的技能。[SayCan](https://arxiv.org/abs/2204.01691) 将语言适合程度与技能可执行性结合，解决高层计划与实际能力脱节；它并不替代底层控制学习。

逐任务训练难以共享多种操作经验，[RT-1](https://arxiv.org/abs/2212.06817) 探索用统一策略承接多任务机器人数据；[RT-2](https://arxiv.org/abs/2307.15818) 将动作编码到视觉语言模型可处理的输出空间，使网络语义与机器人示范联合训练。迁移的是语义和表示能力，动作可行性仍依赖身体与交互经验，不能把语言预训练当成接触控制数据。

单步动作回归还会遇到多解问题：从杯子左侧和右侧抓都可能合理，平均轨迹却可能撞向杯身。[ACT](https://arxiv.org/abs/2304.13705) 通过动作分块学习连续操作，[Diffusion Policy](https://arxiv.org/abs/2303.04137) 用生成分布表达多种可能动作。这两条路线分别处理时间结构和动作分布，可以组合，也引出了开环时间过长、动作块交接不连续的问题。

[OpenVLA](https://arxiv.org/abs/2406.09246) 提供开放模型与适配路线，[π0](https://arxiv.org/abs/2410.24164) 将视觉语言骨干与流式动作生成结合；[UMI](https://arxiv.org/abs/2402.10329) 则改变数据采集接口，让机器人之外的人类操作更容易进入训练。这些进展没有自动填平部署差距，反而使数据质量、实时性、跨身体接口和评价口径成为更重要的研究变量。

## 前沿研究方向

前沿具身研究需要同时改进学到的动作与运行这些动作的系统。下面先讨论示范数据、动作表示和实时推理，再进入跨身体泛化、长期记忆与接触感知，随后比较强化学习、高层技能组织以及全身控制和评价。这个顺序从策略输入延伸到持续执行。各方向不应被压成一个 VLA 成功率：模型是否理解目标、动作是否及时、接触是否稳定和失败能否恢复，可能分别受不同环节限制。

### 1. 数据与人类示范：数量、保真度和任务覆盖不能互换

示范数量只是数据规模的一维。重复采集同一种抓取，可能提高局部稳定性，却不能覆盖接近、接触、移动和释放之间的组合变化。人类视频、遥操作和自动采集又有不同的动作可见性与噪声。选择数据前应明确缺少的是基本动作、转移接口还是组合覆盖，再比较数据量，避免用更多相似轨迹掩盖结构性空缺。

**[SIEVE](https://arxiv.org/abs/2607.06442)**把示范视为可复用运动基元与转移接口的组合，先发现结构，再按组合覆盖分配选择预算，最后在每组保留有代表性的轨迹。与只按整段轨迹质量或单步动作筛选相比，它关注长任务可复用的连接结构。有效性仍取决于分段与结构识别是否可靠，不应把抽取出的基元直接视为唯一正确的任务分解。

遥操作数据能精确对应机器人动作，但采集昂贵；人类视频易扩展，却缺少直接可执行的机器人控制。用视频生成模型初始化策略，可以借用视觉先验，但原本服务内容创作的表示未必保留动作所需细节。数据路线应区分观察、动作、同步与任务标签分别从哪里来。

[2607.08639 · Native Video-Action Pretraining for Generalizable Robot Control](https://arxiv.org/abs/2607.08639) 从具身需求出发设计语义—动作 tokenizer、因果预训练、稀疏专家骨干和异步控制，避免只把双向视频生成器改成策略。它把表示、时间因果性与部署节拍一起设计。限制是训练配方和模型结构同时变化，不能把收益单独归于视频规模；需要按 tokenizer、预训练方向和执行机制分别消融，观察新任务能力来自哪里。

[2607.25895 · HiFi-UMI: Learning Deployable Manipulation Policies from High-Fidelity UMI Data Alone](https://arxiv.org/abs/2607.25895) 则主要提升采集保真度：轨迹精度、双夹爪相对位姿、同步与视野共同设计，研究高质量手持采集能否减少目标机器人后训练数据。它挑战“必须再加一点真机锚点”的惯常做法，但不能把在所测装置上的部署成功推广到任意身体。硬件标定、重建验证和采集覆盖本身仍是成本，不应被零机器人后训练的措辞隐藏。

二者分别改善模型吸收经验的方式和经验本身的质量。实际比较应固定任务范围，报告失败示范、传感同步、目标身体曝光程度与人工复位，而不只按小时数排序数据集。

示范扩展的不同路线，需要分别检查数据来源、动作对应关系和实际任务覆盖。 [Xiaomi-Robotics-1: Scaling Vision-Language-Action Models with over 100K Hours of Real-World Trajectories](https://arxiv.org/abs/2607.15330) 用多样真实轨迹研究数据规模与新任务适配，关注独立任务覆盖而非把相近轨迹重复计为多样性。 [Open-AoE: An Open Egocentric Manipulation Dataset and Toolchain for Embodied Learning](https://arxiv.org/abs/2607.14183) 从日常第一视角视频构建手部运动、相机轨迹与动作标签工具链，降低数据处理门槛。

[Ego2Robot: Scalable Robot Data Synthesis from Egocentric Human Data](https://arxiv.org/abs/2608.02580) 将人类第一视角经验转换为机器人训练样本，研究视觉、任务和身体变化下的迁移。 [HIL-UMI: Bringing Human-in-the-Loop Post-Training of Vision-Language-Action Models to Universal Manipulation Interface](https://arxiv.org/abs/2609.20659) 针对策略盲点采集人类纠正示范，把数据选择与部署失败连接起来，减少无目标地增加演示。

### 2. 动作表示与周期：分块为什么有效，何时又妨碍反应

动作分块让模型一次规划一段平滑行为，减少逐步调用成本，但环境在这段时间内仍可能变化。块长因此同时影响计算、平滑性与纠错机会。比较方法要标出模型重新观察、重新规划和底层控制各自的频率，不能将执行器高频输出当作模型每次都进行了新的闭环决策。

其中，预测长度与实际执行长度尤其需要分开：一次预测十步，并不要求十步全部不看反馈地执行。重新观察后，系统可以保留仍适用的动作，也可以重新规划，因此分块表示的收益未必依赖长时间开环执行。

[2608.02547 · Why Does Action Chunking Improve Behavioral Cloning Performance in Robotic Control?](https://arxiv.org/abs/2608.02547) 用对照实验检验时间平滑、有效任务长度和表示学习等解释，强调非马尔可夫表达与跨时间偏移的隐式集成。非马尔可夫在这里指当前观察不足以解释示范动作，需要历史；集成指学习当前动作与多种过去观察之间的关系。限制是不同任务上的主导机制不同，不能由一种设置中的解释推出所有策略都应使用同样块长。

[2608.15938 · Revisiting Open-Loop Execution in Robotics: Toward Reactive, Higher-Performing Policies](https://arxiv.org/abs/2608.15938) 发现较长开环执行主要帮助短历史策略模仿依赖历史的示范；给足上下文后，长开环不再有同样收益，更及时的闭环可能更好。它把“动作分块有效”拆成表示容量与执行反馈两个问题。其证据依赖所测专家行为和任务，部署时仍要考虑推理延迟；长历史策略如果算得太慢，也可能失去反应优势。

两篇研究共同要求比较历史长度、预测长度、实际执行前缀和总算力。对于递杯子任务，模型需要记住曾经抓空的历史，却也需要在人的手移动后立即调整，这两种需求不能用单一块长解决。

动作建模还涉及表示与时间组织的共同选择，评价应同时观察连贯性和反馈反应。 [ChunkFlow: Towards Continuity-Consistent Chunked Policy Learning](https://arxiv.org/abs/2607.12992) 用接缝感知训练、重叠融合等机制处理动作块边界抖动，解决连续性而非所有历史依赖。 [B-spline Policy: Accelerating Manipulation Policies via B-spline Action Representations](https://arxiv.org/abs/2607.09648) 用 B 样条表达连续动作，减少逐点输出负担，需检查平滑轨迹是否仍保留急需的快速反应。

[Ordered Action Tokens for Visuomotor Policy Learning](https://arxiv.org/abs/2607.21670) 将连续动作编码为有序、可解码的离散 token，为不同预算下的生成提供结构。 [Continue or Replan? Bernoulli-Continuation Policy Learning for Adaptive Horizon Execution](https://arxiv.org/abs/2608.03483) 学习继续执行还是重新规划的决策，让执行周期随状态变化，而非固定信任整段动作。

### 3. 实时推理：不要把旧计划的高频播放当成新决策

实时要求是从感知到动作的整条时延满足环境需要，而不是只让某个网络前向更快。缓存、异步执行和提前预测都能节省时间，但会引入状态过时。研究应同时记录缓存命中、错误复用与重新计算条件，尤其检查突发变化下系统是否仍能及时纠正。

**[ActionCache](https://arxiv.org/abs/2607.06370)**用多模态键保存中间动作，在相似上下文中检索并作为流式动作生成的初始位置，再继续细化。它复用的是过去计算，而不是简单重复上一段最终动作。摘要的加速主要针对动作头，不能直接当作整机加速倍数；真正部署仍要计算视觉编码、检索、通信与控制开销，并检查相似状态下是否真的需要相似动作。

等待期间环境不会暂停。异步推理能够让机器人不必停下来计算，但已经承诺执行的动作会改变状态，普通学习算法若忽略它们，就会错误理解动作与后果的对应。降低延迟既是架构问题，也是学习状态和调度问题。

[2609.18207 · Reinforcement Learning for Real-Time Vision-Language-Action Policies](https://arxiv.org/abs/2609.18207) 让大 VLA 提出动作块，小编辑策略根据最新观察快速修改，并用强化学习优化编辑行为。它保留大策略先验，同时给反应路径较小计算预算。原文讨论明确实验由人复位，并使用任务专用成功检测器；因此部署成本包括训练反馈与环境维护，不能把报告中的无人工干预理解成全流程无人参与。

[2608.23831 · Learning to Act While Waiting: RL Finetuning of Generalist Robot Policies Under Inference Latency](https://arxiv.org/abs/2608.23831) 将已承诺执行的动作和推理中途观察加入学习状态，恢复更接近马尔可夫的决策条件。它不是单纯把网络变快，而是让强化学习知道等待期间哪些控制仍在发生。利用中途观察的完整机制依赖视觉语言骨干与动作专家的可分离结构；换一个模型时应先核对输入噪声、缓存和时间对齐条件，而非直接套用延迟收益。

一个重要对照是相同真实时间内完成多少可靠操作，而不仅是相同动作步数下得分多少。还应测试延迟抖动、相机掉帧和通信排队，因为稳定实验室时延未必代表部署情况。

实时执行中的加速只有减少有效观测到新决策的等待，才可能改善闭环表现。 [TurboVLA: Real-Time Vision-Language-Action Model at 32 Hz on an RTX 4090 with <1 GB VRAM](https://arxiv.org/abs/2607.27205) 绕开大型语言模型作为所有动作的必经路径，探索更轻的视觉语言编码与动作生成组合。 [FlashVLA: Streaming Action Decoding for Fast and Asynchronous VLA Inference](https://arxiv.org/abs/2608.27384) 持续解码动作而非孤立生成整块，为异步执行提供更平滑的更新接口。

[Reflex: Enabling Fast and Predictive Vision-Language-Action Models for Reaction-Critical Manipulation](https://arxiv.org/abs/2608.14379) 将预测能力与快速控制结合，并用对时延敏感的任务测试动态反应。 [What Makes an Efficient VLA? Navigating Action-Head Design, Scaling, and Latency](https://arxiv.org/abs/2609.13984) 固定骨干比较动作头设计，指出初始化与表示对齐可能比新增生成结构更重要。

### 4. 空间、语言与跨身体泛化：究竟换了什么

泛化可以指换背景、物体、语言表达、任务组合或身体结构，这些变化需要不同能力。只在新场景中操作熟悉物体，不等于适应新机器人。评测应一次明确哪些因素变化、哪些保持固定，再观察感知注意、动作映射与任务语义分别承担什么作用。

**[Pelican-VLA 0.5](https://arxiv.org/abs/2607.06655)**联合视觉语言理解、未来帧生成和动作预测，并在感知与动作之间设置可学习瓶颈 token。报告将操作相关对象与接触区域的注意变化与这一接口联系起来，并考察新场景和新身体。注意图可以提供机制线索，但不应仅凭热图宣称获得完整因果解释；应结合接口替换和任务结果理解作者的归因。

[2609.02546 · ZETA: A Controlled Study of Zero-Shot Cross-Embodiment VLA Transfer for Tabletop Manipulation](https://arxiv.org/abs/2609.02546) 区分严格零样本迁移与预训练中见过目标身体的零样本迁移，并在受控目标身体上比较动作表示、源身体多样性和辅助训练。它表明少量目标身体预训练曝光也会明显改变结论，因此必须拆分报告。局限是所测设置主要围绕固定桌面与两指夹爪，移动底盘、灵巧手和长期任务仍需单独评价。

[2608.18433 · The Embodiment Gap in Robot Foundation Models](https://arxiv.org/abs/2608.18433) 将部署前仍要完成的工作定义为身体适配差距，按可共享结构和适配阶段整理研究，而不是只看成功率。这是一篇概念与综述性工作，贡献是评价框架，不是训练出一个统一控制器。它要求列出坐标标定、动作映射、数据采集和硬件接口等隐性投入，使“可迁移”与“无需工程”不再被混为一谈。

这组问题表明，泛化实验应一次只改变一类因素，再组合变化。对递杯任务可依次改变指令、杯子位置、相机姿态和夹爪；若全部同时改变，即使失败也无法知道要修哪里。

泛化条件应按语义、空间与身体变化拆开，避免把不同迁移问题混成同一个总分。 [Lift3D-VLA: Lifting VLA Models to 3D Geometry and Dynamics-Aware Manipulation](https://arxiv.org/abs/2607.06564) 给 VLA 增加显式三维几何与动态信息，减少仅凭二维外观选择动作的脆弱性。 [See like a Robot: Robot-Centric Pointmaps for VLA Models](https://arxiv.org/abs/2607.11498) 用相对机器人夹爪的点图表达深度，让表示更贴近执行坐标而非固定相机坐标。

[VistaVLA: Geometry- and Semantic-Aware 3D Gaussian-Grounded VLA for Robotic Manipulation](https://arxiv.org/abs/2607.12356) 以带语义的紧凑三维高斯表示组织场景，连接物体含义、位置与操作。 [Grounded Semantic Re-Binding for Robust Instruction Generalization in Vision-Language-Action Models](https://arxiv.org/abs/2608.02497) 针对指令改写后的视觉语言绑定不稳重新建立落地关系，区分语义知识缺失与联合编码失效。

### 5. 记忆与长期任务：记住事实之外，还要记住交接条件

长任务的关键常在子技能之间：上一阶段是否真的完成、物体当前在哪里、下一阶段所需姿态是否满足。保存一句“已经抓取”可能掩盖抓取不稳或姿态不合适。记忆应与可检测状态和技能前置条件对应，比较时需要观察中断恢复、局部重试与任务重排，而不只是增加历史帧数。

当前画面中的杯子可能已经清洗，也可能还没清洗；这类任务状态并不总能从单帧读出。把历史堆进上下文会增加成本，而只存文字又可能丢掉接触细节。长期操作还需要知道上一项技能留下的状态能否被下一项使用。

[2607.15275 · RoboTTT: Context Scaling for Robot Policies](https://arxiv.org/abs/2607.15275) 用测试时训练的快速权重保存历史，训练和推理期间都通过梯度更新递归状态，并配合长序列训练。这里的测试时训练不是重新训练整个机器人，而是把记忆写入模型内部可更新状态。它提供长上下文与有限部署开销的路线；风险是记忆更新可能混入错误经验，长上下文收益也必须与训练时序列预算分开计算。

[2608.09410 · Skills in Weights, Memory in Code: Hybrid Learning for Memory-Dependent Robot Manipulation](https://arxiv.org/abs/2608.09410) 将低层技能留在权重里，高层记忆管理交给可执行代码，通过执行反馈改进管理策略，并用本体信号与多帧视觉判断更新阶段状态。它减少为每种历史依赖任务重新采集完整示范的需要。限制是阶段完成验证器可能误判，代码中的状态也可能与真实环境脱节；应保留可追溯证据和重新观测机制。

两种方法是内部状态压缩与外部显式记忆的对照。前者更紧密地融入策略，后者更便于检查和修订，但谁更好取决于需要保存的是连续传感细节，还是离散任务事实。

长期任务中的记忆需要连接状态保持与行动条件，而不只是增加历史输入。 [NativeMEM: Native Memory Compression for Long-Horizon Robotic Manipulation](https://arxiv.org/abs/2607.06678) 将历史帧压成动作相关 token，用策略自身视觉编码器保留长时信息，检查压缩是否遗失罕见线索。 [Dual Latent Memory in Vision-Language-Action Models for Robotic Manipulation](https://arxiv.org/abs/2607.07608) 通过双潜记忆组织操作历史，缓解只依赖短时间观察的偏差。

[Don't Drop the BATON: Long-Horizon Robot Manipulation via Agentic Subtask Exploration and Transition-aware Memory](https://arxiv.org/abs/2608.16889) 为技能交接显式建模入口与出口条件，防止上一子任务成功却留下下一步无法使用的状态。 [MessyMem: Learning-from-Doing Memory for Mobile Manipulation](https://arxiv.org/abs/2609.15976) 记录跨房间交互结果和细粒度视觉证据，避免移动操作反复探索已知失败。

### 6. 接触、触觉与灵巧手：增加传感器还不够

接触控制要求把感觉变化与可执行动作联系起来。传感器更丰富不自动改善策略，因为不同身体的关节、接触位置和力学响应不同。需要区分感知标定、人体到机器人映射与闭环修正，检查方法依赖多少人工指导，以及在新物体或手型上哪些假设仍成立。

**[AnyDexRT](https://arxiv.org/abs/2607.08341)**结合自监督指尖对应、少量人类指导和接触相关的姿态修正，改善灵巧手遥操作重定向。它解决的是示范与执行身体之间的接口问题，而不是直接训练一个通用任务规划器。报告中的免标定不等于没有任何适配信息，仍需注意少样本人类指导与接触分类器所承担的条件。

看见夹爪碰到物体，不等于知道物体是否滑动、压力是否合适。灵巧手的多点接触和自由度使问题更复杂：同样姿态在不同摩擦下会产生不同后果。触觉不仅要进入输入，还要在接触变化后及时影响动作。

[2608.01402 · Demystifying When and Why VLAs Fail in Contact-Rich Tasks and How to Fix Them](https://arxiv.org/abs/2608.01402) 将接触失败拆成精度问题和力信号问题，分别追溯到生成策略训练匹配与力信号结构，再用针对性机制组合修复。它的价值在于先区分病因，而不只给原架构多接一组传感器。局限是所测接触任务与力传感条件有限，迁移时要检验新材料、工具和接触模式是否仍符合诊断。

[2608.25798 · TacForcing: Streaming Action Generation with Execution-Time Tactile Feedback](https://arxiv.org/abs/2608.25798) 把动作专家改为流式生成，保留未完成块的中间状态；每块执行后用新触觉继续生成，并限制触觉更新直接作用于下一待执行块。这样解决动作块内部触觉过时，而不另外拼接一套高频控制器。代价是生成缓存、触觉时间戳与执行调度必须严格匹配；传感噪声和缺测仍需要单独处理。

触觉与接触的价值取决于信息怎样进入控制，传感器变化与策略学习应分别比较。 [TouchWorld: A Predictive and Reactive Tactile Foundation Model for Dexterous Manipulation](https://arxiv.org/abs/2607.07287) 分离触觉预测与快速修正，比较未来接触先验和实时反馈怎样共同支持灵巧任务。 [FM-VLA: Force-based Memory for Vision-Language-Action Models in Contact-Rich Manipulation](https://arxiv.org/abs/2607.18231) 用力觉历史作为记忆，保存图像难以辨认的接触阶段和交互变化。

[ReTouch: Empowering Contact-Rich Dexterous Manipulation with Online-Refined Tactile Prediction](https://arxiv.org/abs/2608.01824) 以结构化触觉 patch 保留手指身份及局部接触，并用执行反馈在线修正预测。 [DeCAL: Towards Physically-Grounded Dexterous Vision-Language-Action Models via Contact-Aware Latent Co-Imagination](https://arxiv.org/abs/2609.09119) 将指尖触觉、视觉和语言的潜在接触想象结合，研究精细动作与陌生物体适配。

接触失败诊断研究从精度与力信号入手修改学习机制，TacForcing 则改变触觉反馈接入动作生成的时机。评测应报告滑落、过力、卡住和插入偏差等具体错误，以及传感频率、校准方式和恢复动作，而不是只展示一次精巧成功。

### 7. 强化学习与奖励：失败的整段轨迹不应否定所有动作

机器人任务的最终失败可能来自一次滑落，但此前的接近、识别与路径选择仍然正确。稀疏结果难以区分局部贡献，密集奖励又可能让策略优化错误的代理目标。比较奖励与学习方法时，应明确哪些信号来自真实传感器、人工规则或学习模型，并记录安全约束是否在探索中始终生效。

示范学习难以覆盖所有恢复状态，在线反馈因此很重要。但“最后成功给一分”的奖励太稀疏，而且把同一个优势值分给整段轨迹，会把前面正确完成的步骤与最后失败一起惩罚。奖励质量、信用分配与真实采样安全必须一起考虑。

[2608.13026 · Temporal GRPO: Beyond Trajectory-Level Credit in Vision-Language-Action Reinforcement Learning](https://arxiv.org/abs/2608.13026) 将轨迹对齐到可检测的任务阶段，只比较进入同一阶段的轨迹，并把阶段优势用于对应动作区间。它针对的是轨迹级信用混淆，而不是简单增加奖励频率。局限是阶段必须能被可靠检测；若阶段边界来自错误视觉判断，局部奖励反而可能更自信地奖励错误动作，应独立评价检测质量。

[2607.13033 · DenseReward: Dense Reward Learning via Failure Synthesis for Robotic Manipulation](https://arxiv.org/abs/2607.13033) 用模拟中的碰撞、抓空、掉落和恢复合成失败数据，训练视觉语言条件下的逐帧奖励模型。它回应了真实失败采集贵、成功轨迹重标注缺乏真实失败形态的问题。限制是模拟失败与真实材料、传感和接触可能不一致；逐帧评分更细并不意味着更真实，需要检查是否能正确排序真实恢复轨迹。

奖励与数据利用的改进应放回真实交互预算和恢复能力中评价。 [RynnValue: Scaling Robotic Value Foundation Models with Temporal Distance](https://arxiv.org/abs/2608.09853) 用到语言目标的有向时间距离组织价值监督，探索异构数据间更可比较的任务进度信号。 [Beyond Imitation: Self-Improving Robot Policies via Off-Policy Q-Planning](https://arxiv.org/abs/2608.21204) 在已有模仿策略之外通过离策略价值与规划利用自我成功、失败经验，减少直接改坏基础策略的风险。

[VLA-Precision: Asymmetric Co-Bootstrapping for Efficient Real-World Online RL of Vision-Language-Action Models](https://arxiv.org/abs/2609.04355) 通过不对称协同更新提升精细操作，同时约束在线交互中的策略漂移。 [Scaling Bimanual Household Manipulation from 1,500 hours of Demonstrations to On-Policy Corrections](https://arxiv.org/abs/2609.03591) 联合家庭双臂示范与策略失败时的人类纠正，研究规模数据和针对性纠错的不同作用。

Temporal GRPO 与 DenseReward 分别处理奖励的时间归属和奖励信号的来源，因而可以作为互补方向比较。但如果训练策略利用奖励器的视觉捷径，就需要真实任务终点和独立检查，不能只用同一个奖励网络宣布系统进步。

### 8. VLA 之外的 agent：规划、程序与技能如何协作

VLA 通常提供从观察与指令到动作的策略，但任务选择、工具切换、异常处理与长期经验管理可以由外部系统承担。程序技能增强可检查性，也引入接口和版本维护成本。研究应标明高层系统控制哪些决策、低层策略负责哪些反馈，避免将整套系统成功全部归因于一个动作模型。

低层策略擅长局部接触，却可能不善于重新解释目标；编程 agent 善于组合与状态管理，但解析几何规则未必足够完成不规则抓取。真正的系统问题是把各自擅长的任务分开，并设计重试与验证接口。

[2607.08448 · Harness VLA: Steering Frozen VLAs into Reliable Manipulation Primitives via Memory-Guided Agents](https://arxiv.org/abs/2607.08448) 把冻结 VLA 暴露为可重试的接触技能，与少量解析技能组合，利用执行轨迹、成功规则和失败模型学习各技能的适用范围。高层负责语义重定位和接触前准备，低层保留精细接触能力。限制是“冻结模型”并不表示系统没有学习成本，记忆构建、任务反馈和技能边界仍然需要适配。

[2609.12541 · Agent as Policy for Robotic Manipulation](https://arxiv.org/abs/2609.12541) 让通用 agent 根据视觉证据编写程序、发出动作并随物理结果修订，还通过保存流程缩短重复任务时间。它展示了运行时推理与编程可以构成一种策略接口，但不是证明任意 LLM 直接输出关节角都安全。机器人提供的接口、可用程序原语和执行时延是能力的一部分，应与训练型 VLA 的感知和动作条件对齐后比较。

这组研究让“agent 与 VLA 谁取代谁”的问题失去意义。更实际的选择是哪些状态由代码维护，哪些技能由学习策略实现，哪些动作必须被几何或安全控制器拒绝。跨层日志应能解释失败从计划、感知还是执行开始。

规划、程序和技能可以承担不同层次的职责，模块之间的交接决定了组合能否可靠执行。 [RoboHarness: Memory-Driven Orchestration of Heterogeneous Robot Policies for Long-Horizon Planning](https://arxiv.org/abs/2607.18060) 用记忆驱动的编排协调异构策略，让长期任务可以调用不同技能，而不要求所有能力塞进一个模型。 [ABot-AgentOS: A General Robotic Agent OS with Lifelong Multi-modal Memory](https://arxiv.org/abs/2607.10350) 保存可追溯的多模态交互知识，连接对话、图像与机器人过去任务，强调证据复用。

[Show-Harness: Just a VLM Agent Can Play Robots](https://arxiv.org/abs/2609.10522) 用共享语义动作接口让视觉语言 agent 控制不同机器人，关注接口设计对跨身体使用的影响。 [EmbodiedSWE: Coding Agents for Long Horizon Dexterous Robotics](https://arxiv.org/abs/2609.27308) 让编程 agent 产生已验证的复杂机器人解法，再转成示范，连接运行时编程与离线策略学习。

### 9. 全身控制与评测：语言遵循和安全停止都需独立检验

全身行为需要同时满足任务目标、平衡、接触和空间限制。执行了语言要求却造成危险，或者保持稳定却没有完成任务，都不能用单一成功率概括。评测应分别观察指令理解、动作可行性、失败恢复和停止机制，尤其避免只展示连续成功的片段而省略接管与重置成本。

机械臂固定在桌边时可以忽略的平衡、碰撞和机身通过性，在人形机器人上成为核心约束。任务成功也可能来自场景只有一个可做动作：桌上只有一个物体时，不看语言都可能拿对。高成功率因而需要与真实指令使用分开。

[2609.25636 · RoboFollow: Unveiling the Instruction Following Mirage in Embodied Agents](https://arxiv.org/abs/2609.25636) 提出高场景熵的诊断，即同一场景容纳多个不同动作分支，使语言真正影响选择；再逐层扰动布局和语义，分别看意图理解与执行。它发现强基线在简单层级表现好，不代表更深指令条件可靠。局限是为了隔离因素而简化对象和动作，复杂真实场景仍需补测；但它有效暴露了视觉捷径。

[2609.02358 · Humanoid Safe Stop via Learned Stoppability Value](https://arxiv.org/abs/2609.02358) 将紧急停止写成可达且避险的问题，联合学习停止策略和可停止性估计，只有不同估计都认为可行时才执行停止，否则进入回退。它说明“立即停下”并非总是同一个安全动作，身体当前状态决定能否稳定停住。估计器仍可能错，因此不能用学习模块取代独立硬件防护和部署责任。

全身任务应同时检查语言意图、局部接触、平衡、碰撞与停止恢复。只报告平均成功率会掩盖罕见高代价失败，也无法体现不同机器人上额外需要的控制适配。

全身任务扩大了动作与约束范围，也要求更加细分的控制和验收条件。 [HAF: Adapting Generalist VLAs to Humanoid Whole-Body Loco-manipulation via Hierarchical Action Flow and Spectral Latent RL](https://arxiv.org/abs/2608.16837) 用分层动作流和潜空间强化学习把通用 VLA 适配到全身移动操作，区分共享语义和专用身体控制。 [TANGO: Humanoid Navigation in Cluttered Environments with a Whole-Body Vision-Language-Action Model](https://arxiv.org/abs/2609.09158) 将拥挤环境导航从二维路径提升为手臂、躯干与步态协同，检验机器人能否真正穿过空间。

[X-WBC: A Cross-Embodiment Foundation Model for Humanoid Whole-Body Control](https://arxiv.org/abs/2609.15213) 跨多种人形身体联合训练全身控制，研究经验共享与硬件差异的兼容。 [RoboTwin-Phys: Do WAMs and VLAs Understand the Physical World?](https://arxiv.org/abs/2609.26292) 改变质量、摩擦和关节动态测试策略，揭示仅改变视觉场景无法发现的物理脆弱性。

## 方法比较：不要用一个成功率替代部署说明

具身方法分别改变示范学习、动作接口、实时反馈与高层组织。它们能否组合，取决于身体、传感器和控制频率是否匹配；比较成功率之前，需要先说明各层实际承担的职责与适配成本。

| 路线 | 学习或改动对象 | 擅长解决 | 关键代价与验证 |
|---|---|---|---|
| 行为克隆与动作分块 | 示范动作分布 | 多任务基本技能与时间结构 | 分布偏移、历史长度、开环比例 |
| 视觉语言预训练加动作头 | 语义与控制接口 | 指令、物体知识迁移 | 身体曝光、动作坐标、部署延迟 |
| 实时编辑与状态增强 | 快速反应或延迟状态 | 动态任务 | 时间戳、缓存、实际闭环频率 |
| 触觉与力觉策略 | 接触表示和执行反馈 | 滑动、插入、灵巧操作 | 传感校准、同步、硬件差异 |
| 外部记忆与程序 agent | 技能编排、状态管理 | 长期任务与恢复 | 验证器错误、程序副作用 |
| 在线强化学习 | 奖励、价值和策略 | 超越示范、修补失败 | 复位、奖励可信度、风险预算 |

一份可复查报告应写明训练中见过哪些身体、每种任务多少独立场景、失败后谁复位、动作频率与新观测频率、是否有人临时调整物体。系统成本还包括设备、标定、人员和故障停机，不只是模型参数和 GPU 显存。

## 负面结果与未解问题

动作分块不只是让轨迹平滑，长开环收益可能在长历史条件下消失；模型泛化不等于身体接口无需适配；高任务成功可能绕开语言；高频指令可能只是播放旧计划。这些发现要求机制对照，而不是把更大模型、更长动作块和更多数据叠加后统一归因为“智能增强”。

仍未解决的是长期历史、高频反馈和复杂语义能否以合理成本同时满足，以及奖励器能否覆盖真实失败而不诱发捷径。另一个难题是安全边界怎样跨层传递：高层 agent 认为任务合理，不意味着底层动作可执行；低层技能自报成功，也不意味着后续阶段入口条件满足。可靠系统应允许暂停、补充观测与人工接管。

## 研究机会

具身能力的进一步扩展受经验覆盖、决策时序和真实试错成本共同限制。下面分别讨论如何获得有价值的数据、连接不同层次的控制，以及在长期运行中安全地适应环境。

**1. 如何获得覆盖真实交互差异的具身经验，而不只增加示范数量？**

物体、身体、接触与场景组合使真实数据空间迅速扩大，人类视频、仿真与机器人轨迹又提供不同监督。研究机会是建立能够选择和对齐这些来源的数据机制，把稀有失败、恢复与接触变化纳入学习。关键是识别哪些经验真正提高未见环境的执行能力，并计算获得它们的实际成本。

**2. 如何连接语言目标、长期计划与实时控制的不同时间尺度？**

高层推理需要较长计算，低层控制却必须及时响应新观察。可以研究分层策略、动作分块和异步更新的联合设计，使高频执行不会长期沿用过时计划。评价应改变环境动态、时延和任务阶段，检查语义遵循、接触稳定和恢复能力能否同时保持。

**3. 如何让机器人在长期运行中自主适应，同时限制试错损失？**

部署环境变化使离线策略无法覆盖所有情况，真实试错又具有物理成本。研究机会是将记忆、可调用技能和在线学习结合，在明确安全边界内获取反馈并更新行为。需要评价跨任务收益、人工接管、旧技能保持与紧急停止，而不只展示少量成功动作。

**实验资源：** [OpenVLA 官方项目页](https://openvla.github.io/)。使用前核对任务、版本、数据与运行条件。
