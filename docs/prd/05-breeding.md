# 05 · 培育与发现系统

## 5.1 设计目标与候选系统评估

**目标**：培育结果可观察（看得见输入）、可推理（每个输入对应一个属性）、可验证（开始前预览、结束后逐槽对错），把“惊喜”留给命名、性格、闪光与招牌造型，而不是留给不透明的随机。

| 候选输入 | 决定的属性 | 复杂度评估 | 对美术的放大倍数 | 结论 |
|---|---|---|---|---|
| 食材（连喂 3 次 → 表达风味） | 亲本的表达风味 → 后代主体色/花纹；同时决定产出原料 | 低：一个计数器+一个状态 | 每种风味 1 套色板+1 种花纹 | **P0** |
| 亲本槽位（Body / Swirl） | Body 槽 → 主体；Swirl 槽 → 花纹 | 低：两个槽位读取表达风味 | 无额外 | **P0** |
| Treat 槽（放入 1 个甜品，可选） | 后代头饰；特定组合触发招牌品种 | 中：配方匹配表 | 头饰复用甜品图标；招牌品种每个需专属部件 | **P0（4 个招牌）** |
| 环境（窝的温度：Chilly / Toasty） | 质感/形态：Jelly（果冻透明、回弹更快）/ Puffy（棉花糖、回弹更慢） | 中：需要形态着色器与物理参数，且所有品种都要适配 | 形态×品种全组合需检查；不扩图鉴 | **P1** |
| 品种生产协作 | 同栏相邻特定品种产量 +x% | 中高：布局策略、UI 说明、平衡 | 少 | **P2** |
| 多代遗传（祖代隐性基因） | — | 高：不可见状态，违背可推理目标 | — | **不做** |

## 5.2 确定性规则（P0）

### 5.2.1 输入、处理、输出

| 环节 | 规则 |
|---|---|
| **输入** | ① Body 槽：史莱姆 A；② Swirl 槽：史莱姆 B（A≠B，均不在其他窝中）；③ Treat 槽（L4 解锁，可空）：甜品架上的 1 个甜品 T；④ 金币费用 |
| **快照** | 点 Start 时记录 `flavorA = A.showing`、`flavorB = B.showing`、`T`；之后亲本再被喂食不影响本次结果 |
| **品种判定** | 若 T 非空且 (flavorA, flavorB, T) 命中招牌配方表 → 结果为该招牌品种；否则结果为普通品种：Body = flavorA，Swirl = flavorB（flavorB 为 Sugar 时“无花纹”） |
| **头饰判定** | 普通品种且 T 非空 → 头饰 = T 的迷你造型（如 Berry Jelly 头饰）；招牌品种不带头饰（专属部件代替）；T 为空 → 无头饰 |
| **等级系数** | k = 1 + tier(flavorA) + tier(flavorB)；tier：Sugar 0、Strawberry 1、Cream 1、Lemon 2、Cocoa 3（P1 Matcha 3） |
| **培育时间** | 普通：10 × k 分钟；招牌：10 × k × 3 分钟 |
| **费用** | 20 × k 金币；**招牌与普通相同**（费用在开始前显示，若按结果收费会泄露答案） |
| **首次发现奖励** | 普通：经验 10 × k，星星糖 +1；招牌：经验 100，星星糖 +5 |
| **输出** | 1 只新史莱姆：品种、头饰、名字、性格、最爱食物、闪光；初始表达风味 = Body 风味；亲密 0 |
| **亲本** | 不消耗；培育期间留在原处继续产出；带“In Nest”角标，不可放生、不可进入其他窝 |
| **Treat** | Start 时消耗 |

**算例**：Body = Puff（表达 Lemon），Swirl = Berry（表达 Strawberry），无 Treat。k = 1 + 2 + 1 = 4；时间 40 分钟；费用 80 金币；结果 Lemon Strawberry Slime（黄色主体、粉色点点）；首次发现 +40 经验、+1 星星糖。

**招牌算例**：Body 表达 Strawberry、Swirl 表达 Cream、Treat = Strawberry Shortcake。k = 3；时间 10×3×3 = 90 分钟；费用 60 金币；结果 Shortcake Slime；+100 经验、+5 星星糖。

### 5.2.2 开始后的“特别”提示

招牌品种在 Start 后立即让窝发出金光并显示 `NEST_SPECIAL_GLOW`（且时间为普通的 3 倍）。这是**承诺之后**的信息：玩家已经付了费用并消耗了 Treat，不能用“看一眼再取消”来零成本试探（中止不退费、不退 Treat）。

### 5.2.3 产量加成（品种的经济意义）

每份食物产出 = 3（基础）+ 1（食物风味 = 主体风味）+ 1（食物风味 = 花纹风味，Sugar 花纹不计）+ 1（亲密 5 级）。

| 品种类型 | 示例 | 吃对应食物的产出/份 | 意义 |
|---|---|---|---|
| Sugar Slime | 起始品种 | Sugar Cube：4 | 稳定糖源 |
| Basic | Strawberry Slime | Strawberry：4 | 单一原料 |
| Sugar-pattern | Sugar Cream Slime | Sugar Cube：4；Milk：4 | 糖+一种原料两用 |
| Blend | Strawberry Cream Slime | Strawberry：4；Milk：4 | 两种原料都高效 → 适合 Shortcake |
| Pure | Pure Lemon Slime | Lemon：5 | 单一原料最高效 |
| Signature | Shortcake Slime | Strawberry：4；Milk：4（同其 Body/Swirl） | 价值在外观与收集，不做数值碾压 |

## 5.3 随机性规则（P0）

| 随机项 | 规则 | 何时掷骰 | 为什么存在 | 为什么不影响公平 |
|---|---|---|---|---|
| 名字 | 从 200 个名字池等概率抽取（排除牧场中已有的名字） | Start 时 | 让每只有初始身份 | 可改名 |
| 性格 | 6 种等概率（各 1/6） | Start 时 | 同品种不同个体，形成偏好 | 只影响动画、音高 |
| 最爱食物 | 从 Start 时已解锁食物中等概率选 1 | Start 时 | 发现个体差异 | 只影响亲密 +1 |
| 闪光 | p = min(7%, 2% + 0.5% × (亲本A亲密等级 + 亲本B亲密等级))；距上次闪光第 40 次培育必出 | Start 时 | 长尾收集；把“亲密”与培育连起来 | 纯外观；不可交易；有保底 |
| 品种 | **不随机** | — | — | — |

所有随机结果在 Start 时决定并写入存档，杀进程重开不能刷结果（11 章）。

**闪光算例**：两亲本亲密分别 3 级与 2 级 → p = 2% + 0.5%×5 = 4.5%。两只都 5 级 → 2% + 5% = 7%（达上限）。

## 5.4 品种表（P0 共 29 种；首版范围已标注）

> 由规则生成，见 `config/species.generated.csv`；“最早可达”指风味与 Treat 全部解锁的等级。招牌卡片（含线索）在“卡片解锁”等级出现，但在此之前若玩家碰巧做对组合，也会得到该品种（`SIG_SURPRISE`）。

| ID | 品种名（英文，玩家可见） | Body | Swirl | Treat | 类型 | 最早可达 | 时间(分) | 费用 | 首发经验 | 加成食物 | 范围 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sp_plain_plain | Sugar Slime | Sugar | — | — | 起始 | L1 | 10 | 20 | 10 | Sugar Cube | P0 |
| sp_plain_strawberry | Sugar Strawberry Slime | Sugar | Strawberry | — | 原味底花纹 | L1 | 20 | 40 | 20 | Sugar Cube, Strawberry | P0 |
| sp_plain_cream | Sugar Cream Slime | Sugar | Cream | — | 原味底花纹 | L1 | 20 | 40 | 20 | Sugar Cube, Milk | P0 |
| sp_plain_lemon | Sugar Lemon Slime | Sugar | Lemon | — | 原味底花纹 | L3 | 30 | 60 | 30 | Sugar Cube, Lemon | P0 |
| sp_plain_cocoa | Sugar Cocoa Slime | Sugar | Cocoa | — | 原味底花纹 | L5 | 40 | 80 | 40 | Sugar Cube, Cocoa Bean | P0 |
| sp_strawberry_plain | Strawberry Slime | Strawberry | — | — | 基础 | L1 | 20 | 40 | 20 | Strawberry | P0 |
| sp_cream_plain | Cream Slime | Cream | — | — | 基础 | L1 | 20 | 40 | 20 | Milk | P0 |
| sp_lemon_plain | Lemon Slime | Lemon | — | — | 基础 | L3 | 30 | 60 | 30 | Lemon | P0 |
| sp_cocoa_plain | Cocoa Slime | Cocoa | — | — | 基础 | L5 | 40 | 80 | 40 | Cocoa Bean | P0 |
| sp_strawberry_strawberry | Pure Strawberry Slime | Strawberry | Strawberry | — | 纯种 | L1 | 30 | 60 | 30 | Strawberry(5) | P0 |
| sp_cream_cream | Pure Cream Slime | Cream | Cream | — | 纯种 | L1 | 30 | 60 | 30 | Milk(5) | P0 |
| sp_lemon_lemon | Pure Lemon Slime | Lemon | Lemon | — | 纯种 | L3 | 50 | 100 | 50 | Lemon(5) | P0 |
| sp_cocoa_cocoa | Pure Cocoa Slime | Cocoa | Cocoa | — | 纯种 | L5 | 70 | 140 | 70 | Cocoa Bean(5) | P0 |
| sp_strawberry_cream | **Strawberry Cream Slime** | Strawberry | Cream | — | 混合（新手目标） | L1 | 30 | 60 | 30 | Strawberry, Milk | P0 |
| sp_cream_strawberry | Cream Strawberry Slime | Cream | Strawberry | — | 混合 | L1 | 30 | 60 | 30 | Milk, Strawberry | P0 |
| sp_strawberry_lemon | Strawberry Lemon Slime | Strawberry | Lemon | — | 混合 | L3 | 40 | 80 | 40 | Strawberry, Lemon | P0 |
| sp_lemon_strawberry | Lemon Strawberry Slime | Lemon | Strawberry | — | 混合 | L3 | 40 | 80 | 40 | Lemon, Strawberry | P0 |
| sp_cream_lemon | Cream Lemon Slime | Cream | Lemon | — | 混合 | L3 | 40 | 80 | 40 | Milk, Lemon | P0 |
| sp_lemon_cream | Lemon Cream Slime | Lemon | Cream | — | 混合 | L3 | 40 | 80 | 40 | Lemon, Milk | P0 |
| sp_strawberry_cocoa | Strawberry Cocoa Slime | Strawberry | Cocoa | — | 混合 | L5 | 50 | 100 | 50 | Strawberry, Cocoa Bean | P0 |
| sp_cocoa_strawberry | Cocoa Strawberry Slime | Cocoa | Strawberry | — | 混合 | L5 | 50 | 100 | 50 | Cocoa Bean, Strawberry | P0 |
| sp_cream_cocoa | Cream Cocoa Slime | Cream | Cocoa | — | 混合 | L5 | 50 | 100 | 50 | Milk, Cocoa Bean | P0 |
| sp_cocoa_cream | Cocoa Cream Slime | Cocoa | Cream | — | 混合 | L5 | 50 | 100 | 50 | Cocoa Bean, Milk | P0 |
| sp_lemon_cocoa | Lemon Cocoa Slime | Lemon | Cocoa | — | 混合 | L5 | 60 | 120 | 60 | Lemon, Cocoa Bean | P0 |
| sp_cocoa_lemon | Cocoa Lemon Slime | Cocoa | Lemon | — | 混合 | L5 | 60 | 120 | 60 | Cocoa Bean, Lemon | P0 |
| sig_shortcake | **Shortcake Slime** | Strawberry | Cream | Strawberry Shortcake | 招牌 | L4（卡片 L4） | 90 | 60 | 100 | Strawberry, Milk | P0 |
| sig_cloud | **Cloud Puff Slime** | Sugar | Cream | Cream Puff | 招牌 | L4（卡片 L6） | 60 | 40 | 100 | Sugar Cube, Milk | P0 |
| sig_lava | **Choco Lava Slime** | Cocoa | Strawberry | Berry Jelly | 招牌 | L5（卡片 L7） | 150 | 100 | 100 | Cocoa Bean, Strawberry | P0 |
| sig_neapolitan | **Neapolitan Slime** | Strawberry | Cocoa | Cream Puff | 招牌 | L5（卡片 L9） | 150 | 100 | 100 | Strawberry, Cocoa Bean | P0 |

**P1 预留（Matcha 风味，L10 解锁）**：Sugar Matcha、Strawberry Matcha、Cream Matcha、Lemon Matcha、Cocoa Matcha、Matcha、Matcha Strawberry、Matcha Cream、Matcha Lemon、Matcha Cocoa、Pure Matcha（11 种）+ 招牌 Matcha Latte Slime（Body Matcha + Swirl Cream + Treat Matcha Roll）。P1 合计 41 种。

**首版范围建议**：上表 29 种全部为 P0（规则生成，额外成本主要是色板与花纹）。若排期紧张，可砍顺序：① Cocoa 相关 9 个普通品种+2 个招牌（风味整体顺延到 P1，等级表 L5 改解锁 Lemon Cream Pie）；② 招牌从 4 个减为 2 个（保留 Shortcake、Cloud Puff）。只执行①：16 个普通品种 + 2 个招牌（Shortcake、Cloud Puff 不依赖 Cocoa）= 18 种，②已自动满足；只执行②：25 + 2 = 27 种。两种情况都满足“至少 12 种”。

## 5.5 招牌配方与线索分级

| 招牌 | 线索（Tier 0，卡片解锁即显示，玩家可见英文） | Body 提示 | Swirl 提示 | Treat 提示 | 专属部件 |
|---|---|---|---|---|---|
| Shortcake Slime | “Pink on the outside, a creamy swirl inside, and a slice of cake for luck.” | Body: Strawberry | Swirl: Cream | Treat: Strawberry Shortcake | 海绵蛋糕夹层底座+顶部草莓 |
| Cloud Puff Slime | “Clear as the sky, swirled with cream, and dreaming of something puffy.” | Body: Sugar | Swirl: Cream | Treat: Cream Puff | 云朵轮廓（独立身体遮罩） |
| Choco Lava Slime | “Dark and gooey, freckled with pink. It only settles down with something wobbly.” | Body: Cocoa | Swirl: Strawberry | Treat: Berry Jelly | 底部熔岩滴落裙边+慢速流动闲置 |
| Neapolitan Slime | “Pink on top, chocolate below, and something creamy tucked in between.” | Body: Strawberry | Swirl: Cocoa | Treat: Cream Puff | 三色横条身体覆盖层 |

**提示获取规则：**

| 方式 | 规则 | 成本 |
|---|---|---|
| 追踪 Track | 同一时间追踪 1 张已解锁卡片；追踪后每次带 Treat 的培育结束，在揭晓后显示 `SIG_CHECK_TITLE`：Body ✓/✗、Swirl ✓/✗、Treat ✓/✗（相对被追踪的配方） | 免费 |
| 花星星糖 | 揭示 1 个槽位答案；**优先揭示尚未得到过 ✓ 的槽位**（同为未确认时按 Body→Swirl→Treat） | 每次 2 星星糖，每张卡最多 3 次 |
| 失败自动送 | 对追踪中的卡片每累计 3 次未命中，免费揭示 1 个槽位（规则同上，`SIG_HINT_FREE`） | 免费 |
| 访客请求（P1） | P0 访客只请求普通品种；P1 起卡片解锁后访客可用颜色词描述招牌外观 | — |

**为什么逐槽对错不会让解谜失去意义**：每次验证都需要真实的一次培育（费用+Treat+等待）。配方空间：Body 5 × Swirl 5 × Treat 9 = 225 种。线索中的颜色词让 Body/Swirl 通常在第 1 次就得到 ✓，剩下的是 Treat（P0 最多 9 个候选）。
- 不用任何提示的最坏情况：Body/Swirl 第 1 次 ✓ 后，Treat 逐个试，最坏 9 次。
- 有免费提示时的最坏情况：第 3 次未命中后免费揭示“尚未 ✓ 的槽位”= Treat → **第 4 次必中**。
- Body/Swirl 也猜错时：每次反馈都会告诉玩家哪个槽错了，免费提示每 3 次补 1 个槽，最坏第 10 次必中（3 个槽各需 3 次未命中换 1 次提示）。实际预期远低于此，作为首测指标验证（12 章 V2：招牌解出尝试次数中位数）。

## 5.6 完整发现路径（4 条）

### 路径 1：Strawberry Cream Slime（新手，第 4～7 分钟）

| 步 | 观察 | 推理 | 行动 | 验证 |
|---|---|---|---|---|
| 1 | Mochi 吃 3 个草莓后变粉；Puff 吃 3 个牛奶后变奶白 | “喂什么，就显什么色” | — | 气泡 3/3 |
| 2 | Bella：“a pink slime with creamy swirls” | 粉色=主体，奶油=花纹 | — | — |
| 3 | Nest 两个槽标注 Body “Sets the main color”、Swirl “Sets the pattern” | Mochi→Body、Puff→Swirl | 拖入 | 预览显示 “Strawberry body · Cream Swirl” |
| 4 | — | — | Start（免费，30 秒） | 孵化得到 Strawberry Cream Slime；Show Bella 成功 |

### 路径 2：规则迁移——Lemon Strawberry Slime（L4，约第 2 天；Lemon 于 L3 解锁，访客请求于 L4 解锁）

| 步 | 观察 | 推理 | 行动 | 验证 |
|---|---|---|---|---|
| 1 | L3：`UNLOCK_LEMON`；图鉴矩阵新增 Lemon 行/列（剪影带颜色点）。L4：`UNLOCK_VISITOR` | 新风味可以做新组合 | — | — |
| 2 | 第一位访客：“I'd love a sunny yellow slime with pink dots!” | 黄=Lemon 主体；粉点=Strawberry 花纹 | 买 3 个 Lemon 喂给任一只（如 Puff），使其表达 Lemon | Puff 变黄，`FEED_SHOWING` |
| 3 | — | Body=Puff(Lemon)，Swirl=Berry(Strawberry) | 预览 “Lemon body · Berry Dots”；费用 80，40 分钟 | 孵化→Lemon Strawberry Slime→Show 给访客 |

### 路径 3：招牌——Shortcake Slime（L4）

| 步 | 观察 | 推理 | 行动 | 验证 |
|---|---|---|---|---|
| 1 | L4 解锁 Treat 槽与 Shortcake 卡片：“Pink on the outside, a creamy swirl inside, and a slice of cake for luck.” | 粉=Strawberry Body；奶油漩涡=Cream Swirl；“a slice of cake”=某种蛋糕 Treat | 点 Track | — |
| 2 | 甜品架上只有 Berry Jelly（粉色，误以为相关） | 试 Strawberry/Cream + Berry Jelly | 培育（60 金币，30 分钟，消耗 1 个 Berry Jelly） | 结果：Strawberry Cream Slime + Berry Jelly 头饰；Recipe check：Body ✓ Swirl ✓ Treat ✗ |
| 3 | Treat 错了；已解锁甜品里唯一的“cake”是 Strawberry Shortcake | — | 烘焙 1 个 Shortcake，再次培育 | 窝发金光（90 分钟）→ Shortcake Slime；`SIG_SOLVED` |

### 路径 4：带误导的招牌——Choco Lava Slime（L7）

| 步 | 观察 | 推理 | 行动 | 验证 |
|---|---|---|---|---|
| 1 | 卡片：“Dark and gooey, freckled with pink. It only settles down with something wobbly.” | 深色=Cocoa Body；粉色斑点=Strawberry Swirl；“gooey”→猜 Choco Brownie | Track；Body Cocoa、Swirl Strawberry、Treat Choco Brownie | Recipe check：✓ ✓ ✗；得到 Cocoa Strawberry Slime（若首次也算新发现）+ Brownie 头饰 |
| 2 | Treat 不对；重读线索“settles down with something wobbly” | “wobbly”=果冻 | Treat 换 Berry Jelly | 窝发金光（150 分钟）→ Choco Lava Slime |
| 2'（卡住时） | 累计 3 次未命中 | — | 自动免费揭示尚未 ✓ 的槽位（此例为 Treat: Berry Jelly）；或提前花 2 星星糖揭示 | 不需要查攻略 |

## 5.7 线索展示：防止“只能查攻略”或“盲目试错”

| 线索载体 | 显示什么 | 何时 | 解决的问题 |
|---|---|---|---|
| 身体染色+连喂气泡 | 当前表达风味与进度 n/3 | 每次喂食 | 让“食物→颜色”可观察 |
| 槽位标签 | Body “Sets the main color” / Swirl “Sets the pattern” / Treat “Adds a topper. Some treats are special…” | 一直 | 让“槽位→属性”可推理 |
| 预览卡 | 普通结果：主体色块+花纹图标+头饰图标+名称（未发现显示 ???+New!） | 放入槽位即时 | 开始前验证普通品种 |
| 图鉴矩阵 | 行=Body、列=Swirl；未发现格子显示带两色点的剪影，点开显示 `BOOK_TRY`；未解锁风味显示 `BOOK_LOCKED` | 一直 | 告诉玩家“还有什么能做”，给出可执行配方 |
| 图鉴 Breed This | 一键跳到 Nest 并预填两只表达对应风味的亲本（没有时提示需喂哪种食物） | 图鉴详情 | 减少操作负担 |
| 访客请求 | 用颜色词+花纹词描述（英文）：如 “sunny yellow … pink dots” | 每 6 小时 | 外部目标驱动推理 |
| 招牌卡片 | Tier 0 线索文本+剪影；逐级提示 | 卡片解锁 | 深层推理；逐槽反馈保证可收敛 |
| Recipe check | Body/Swirl/Treat 各 ✓/✗ | 追踪中、带 Treat 的培育揭晓后 | 验证假设，避免盲试 |

## 5.8 失败与重复结果的用途

“失败”定义：结果不是玩家想要的（例如招牌未命中、放反槽位）。系统层面培育**永远成功产出 1 只史莱姆**。

| 结果 | 用途 |
|---|---|
| 招牌未命中 | 得到普通品种（可能是新发现）+ Treat 头饰；累计未命中次数推进免费提示 |
| 重复品种 | ① 留下作为产出者（同品种多只=该原料产能翻倍）；② 作为亲本（表达风味可通过喂食改变）；③ 放生：获得 10×k 金币，且若该品种仍有≥1只在牧场则 +1 星星糖（每日上限 3） |
| 闪光重复 | 同上，外观不同；图鉴记录 “Sparkle seen” |
| 放反槽位 | 得到对称品种（如 Cream Strawberry），本身也是图鉴中的一个格子 |

## 5.9 控制组合爆炸：可复用的外观方案

| 层 | 规则 | 资产复用方式 | P0 数量 |
|---|---|---|---|
| 主体色 Body | 每种风味 1 套 4 色（底色、暗部、高光、描边） | 所有身体共用同一灰度底图+调色（色板贴图/着色器参数）；Sugar 用半透明折射着色器变体 | 5 套 |
| 花纹 Swirl | 每种风味 1 种花纹形状：Berry Dots（点点）、Cream Swirl（漩涡）、Lemon Zest（星点碎屑）、Cocoa Drizzle（淋酱条纹） | 灰度遮罩贴图按 Swirl 风味着色；花纹在身体 UV 上，随形变一起变形 | 4 张遮罩 |
| 纯种 Pure | 无花纹，颜色加深 15%、高光更强，并带 1 个风味配件 | 配件：草莓叶冠 / 奶油尖顶 / 柠檬片发夹 / 可可豆小冠 | 4 个配件 |
| 头饰 Topper | Treat 甜品的 Q 版缩小造型 | 由甜品图标重绘为头饰（同一构图，加阴影与锚点） | 9 个 |
| 招牌部件 | 改变**轮廓**而不只是颜色 | 每个招牌 1 套专属部件或身体遮罩+1 段专属闲置动画 | 4 套 |
| 形态 Form（P1） | Chilly → Jelly、Toasty → Puffy；不进图鉴格子，记录为形态印章 | 1 个着色器参数集+物理参数（回弹速度） | 0（P1：2） |
| 闪光 Sparkle | 粒子层+描边高光 | 通用 | 1 |
| 表情 | 全品种通用 12 组眼+嘴 | 通用 | 12 |

**图鉴规模公式**：普通品种 = N²（N=风味数，含 Sugar）；招牌另计。P0：5²=25 + 4 = 29；P1（N=6）：36 + 5 = 41。形态、头饰、闪光**不增加格子**。新增 1 种风味的美术成本 ≈ 1 色板 + 1 花纹遮罩 + 1 纯种配件 + 食物/原料/1～2 个甜品图标 ≈ 2.5 个美术工作日，自动带来 2N+1 个新品种。

**如何让新品种不只是换颜色**：① 花纹形状各不相同（点/漩涡/碎屑/条纹）；② 纯种有专属配件；③ 招牌改变轮廓与闲置动画；④ 每种 Body 风味有不同的触摸音色（Sugar 玻璃感、Cream 闷软、Strawberry 清脆、Lemon 轻快、Cocoa 低沉）；⑤ 每种 Body 风味的形变参数略不同（Cocoa 更“稠”、回弹慢 15%；Lemon 更“弹”、回弹快 10%）。

## 5.10 P1 规格预留：环境 → 形态

| 项 | 规则 |
|---|---|
| 输入 | 窝的环境开关：Normal / Chilly（Chill Pad 设施）/ Toasty（Warm Lamp 设施），在 Start 前选择 |
| 输出 | 后代形态 Form：Round（默认）/ Jelly（透明度+40%、回弹快 20%）/ Puffy（外描边绒毛、回弹慢 25%） |
| 与招牌关系 | P1 新增招牌可要求特定环境（如 Matcha Latte 需 Toasty），线索中出现温度词 |
| 存档预留 | 个体字段 `form`（P0 固定 Round）；配方表字段 `required_env`（P0 为空） |

## 5.11 P2 规格预留：品种生产协作

同一围栏内，相邻（格位距离 1）的两只史莱姆，若 A 的 Swirl 风味 = B 的 Body 风味，则 B 每份食物产出 +1（每只最多 +1）。P0 存档预留 `pen_slot_index`。

## 5.12 培育异常

| 情况 | 处理 |
|---|---|
| 两个槽选同一只 | 拒绝，`NEST_SAME_SLIME` |
| 金币不足 | Start 按钮置灰，显示缺口；`ERR_NOT_ENOUGH_COINS` |
| 甜品架无甜品时点 Treat 槽 | 显示可烘焙的甜品列表，可直接 Bake 后放入 |
| 窝全忙 | 显示最近完成时间；不弹付费推荐，除非满足 09 章的情境推荐条件 |
| 孵化时围栏与小屋都满 | 荚保持 Ready（`NEST_NO_ROOM`），窝不可开新培育，直到腾出空位 |
| 培育中亲本被选为放生 | 不允许（In Nest 角标），提示需等待或中止 |
| 中止培育 | 二次确认；费用与 Treat 不退；亲本立即解除锁定 |
| 培育中杀进程/断电 | 结束时间与全部随机结果已在 Start 时写入存档，恢复后按时间结算 |
| 结果对应的风味后续被下架（版本更新） | 品种 ID 永不复用、永不删除；下架内容转“绝版”标记仍可展示 |
