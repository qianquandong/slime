# 03 · 前 10 分钟体验脚本

## 3.1 目标与约束

| 目标 | 量化要求 |
|---|---|
| 第一次触摸 | 进入牧场后 ≤15 秒发生 |
| 第一次喂食并看到变色 | ≤2 分钟 |
| 第一次甜品交付 | ≤4 分钟 |
| 第一次配方推理 | ≤6 分钟（Body/Swirl 放置决策） |
| 第一次培育完成 | ≤7:30（培育计时 30 秒，等待期间有事可做） |
| 最长被动等待 | 任意时刻 ≤30 秒 |
| 结束状态 | L2，经验 30/80，金币 150，星星糖 4，加速勺 1，原料 Berry Jam 7 / Fresh Cream 9，3 只史莱姆（2 只 Sugar Slime + 1 只 Strawberry Cream Slime），图鉴 2/29 |

> 结束状态与 07 章可复算路径的起点完全一致，并被 `tools/balance_check.py` 的模拟作为初始状态使用。

**新手期专用覆盖规则（仅 FTUE，脚本步骤结束即失效）：**

| 参数 | 正常值 | FTUE 值 | 原因 |
|---|---|---|---|
| 食物价格 | Strawberry/Milk 6 金币 | 前 3 个 Strawberry、前 3 个 Milk 免费（标 “On the house”） | 不让玩家在理解前花钱 |
| 消化时间 | Strawberry 15 分钟/份 | 前 6 份食物各 10 秒 | 2 分钟内看到产出 |
| 培育时间 | 10×(1+1+1)=30 分钟 | 第 1 次 30 秒；第 2 次 ≤2 分钟；第 3 次 ≤5 分钟 | 第一天连续获得发现 |
| 培育费用 | 60 金币 | 第 1 次免费 | 同上 |
| 新手订单奖励 | 按公式 14 金币 / 3 经验 | 固定 20 金币 / 10 经验 | 让第一单就推进等级 |
| 新手访客奖励 | 公式 90 金币 / 20 经验 / 2 星星糖 | 固定 30 金币 / 10 经验 / 2 星星糖 | 控制起点金币为 150 |
| 初始金币 | — | 50 | 结束时正好 150 |

## 3.2 逐时间段脚本

> 文案均为玩家可见英文，引用 `config/strings.csv` 的 String ID；中文仅为说明。引导角色 **Nana Bun**（`GUIDE_NAME`）以对话框出现在屏幕下 1/3，单手拇指可点任意处继续。

| 时间 | 画面 | 玩家操作 | 反馈 | 奖励 | 引导文案（String ID / English） | 解锁 |
|---|---|---|---|---|---|---|
| 0:00–0:05 | 标题画面：Logo “Slime Sweets Farm”，背景一只史莱姆在轻轻呼吸 | 点任意处 | 史莱姆被点到也会形变（标题画面即可触摸） | — | `TITLE_TAP` “Tap to start” | — |
| 0:05–0:15 | 镜头推近 Meadow Pen，只有 **Mochi**（Sugar Slime，透明淡蓝）在睡觉，头顶 “Zzz” 气泡；手指图标在 Mochi 上脉动 | 点 Mochi | 醒来动画 0.6s，惊讶→开心表情 | — | `TUT_01` “Psst… someone's napping. Give them a poke!” | 触摸 |
| 0:15–0:45 | Mochi 近景；身体下方出现挤一挤环（8 格） | 连续点击 8 次 | 每次点击：凹陷+压扁+回弹、音阶逐次升高；第 8 次弹出 1 个 **Sugar**，飞入左上角储藏罐 | Sugar ×1 | `TUT_02` “That's Mochi! Mochi loves pokes.” → `TUT_03` “Keep squishing! 8 squishes pop out a Sugar drop.” | 挤一挤 |
| 0:45–1:00 | 同上 | 长按 Mochi ≥1s | 拉伸+爱心粒子+柔和震动；亲密条 +3 | 亲密 +3 | `TUT_04` “Now press and hold Mochi for a hug.” | 拥抱 |
| 1:00–1:40 | 底部食物托盘（Snacks）滑出，只有 Strawberry（标 “On the house” ×3） | 把 Strawberry 拖到 Mochi（或先点食物再点 Mochi） | 吃东西咀嚼动画 0.6s；身体染上 1/3 粉色；头顶气泡 “Strawberry 1/3” | — | `TUT_05` “Mochi looks hungry. Drag a Strawberry over!” → `TUT_06` “Feed the same snack 3 times in a row to change Mochi's color.” | 喂食 |
| 1:40–2:00 | 同上 | 再喂 2 个 Strawberry | 2/3 粉 → 3/3 全粉，闪光转场 0.4s，Toast `FEED_SHOWING` | — | `TUT_07` “Mochi is showing Strawberry! Slimes make goodies while they digest.” | 表达风味 |
| 2:00–2:30 | Mochi 消化中（饭碗图标转圈，FTUE 每份 10 秒）；每 10 秒弹出 3 个 **Berry Jam** 飞入储藏罐 | 观看/继续抚摸 | 原料飞入动画 0.6s | Berry Jam ×3（到 2:30 时累计 9） | — | 生产 |
| 2:30–3:30 | 订单板入口在底部导航 Orders 上出现红点；切到订单页，顾客 **Bella** 的订单：Berry Jelly ×1（需 2 Berry Jam + 1 Sugar） | 点 `ORDER_BAKE_DELIVER` | 烘焙动画 1s → 甜品飞向 Bella → 收银铃声 | 20 金币，10 经验（经验条 10/20） | `TUT_08` “Bella wants a Berry Jelly. Tap Bake & Deliver!” | 订单、厨房 |
| 3:30–4:00 | 回到牧场；一只害羞的史莱姆从草丛探头，蹦到围栏里 | 命名或点 “Continue” 使用默认名 **Puff** | 害羞表情，躲到 Mochi 身后 | 第 2 只史莱姆 | `TUT_09` “A shy slime wandered in! Want to name them?” | 改名 |
| 4:00–4:40 | 食物托盘出现 Milk（“On the house” ×3） | 喂 Puff 3 个 Milk | 逐次染成奶油白；Toast “Puff is showing Cream!” | — | `TUT_10` “Give Puff 3 Milks to make them creamy.” | — |
| 4:40–5:10 | Bella 以访客身份回到牧场门口，头顶气泡显示一只粉色带奶油漩涡的史莱姆剪影 | 点 Bella | 访客卡片：`VISITOR_LINE` → “I'd love a pink slime with creamy swirls!” | — | `TUT_11` “Bella's back with a wish: a pink slime with creamy swirls!” | 访客请求（仅新手；常规 L4 解锁） |
| 5:10–6:10 | **培育窝（Nest）**页：两个大槽位 **Body**（“Sets the main color”）与 **Swirl**（“Sets the pattern”），Treat 槽灰色锁定 | 把 Mochi、Puff 拖进槽位 | 每放一只，预览卡实时更新。**放错**（Puff 在 Body）时预览显示 “Cream body · Berry Dots”，Nana 提示 `TUT_13`，`NEST_SWAP` 按钮闪烁；**放对**时预览 “Strawberry body · Cream Swirl” 并出现对勾 | — | `TUT_12` “In the Nest, Body sets the main color and Swirl sets the pattern. Who goes where?” / `TUT_13` “That makes a creamy slime with pink dots. Try swapping!” / `TUT_14` “That's exactly Bella's wish. Tap Start — this one's free!” | 培育、预览 |
| 6:10–6:40 | 点 `NEST_START_FREE` 后荚在窝里摇晃，30 秒倒计时 | 可去点图鉴或继续抚摸 | 图鉴页显示 1 个已发现（Sugar Slime），Strawberry Cream 格显示“孵化中”剪影；其余为矩阵剪影 | — | `TUT_15` “While it wobbles, peek at your Slime Book.” | 图鉴 |
| 6:40–7:30 | 荚剧烈摇晃 | 点荚 | 揭晓演出 2.5s（0.8s 后可跳过）：Strawberry Cream Slime 出生 → `HATCH_NEW` → 命名（默认随机名，示例 **Berry**） | 发现经验 30、星星糖 1 → **升到 L2**：+50 金币、+1 星星糖、+1 加速勺；解锁 Strawberry Shortcake 配方 | `TUT_16` “Something's wobbling! Tap the pod.” | 等级 2 |
| 7:30–8:30 | Bella 的访客卡片出现 `VISITOR_SHOW` “Show Berry” | 点 Show | Berry 蹦到 Bella 面前，Bella 开心转圈；史莱姆**不被消耗**，返回围栏 | 30 金币、10 经验（30/80）、2 星星糖 | `TUT_17` “You cracked your first recipe! Show Bella?” | — |
| 8:30–9:20 | 回到牧场；脚本把 Mochi 的当前零食设为 Sugar Cube（`TUT_18B` “Mochi will make Sugar for your desserts.”）；`HUD_REFILL_COST` 按钮发光，显示总价 120 | 点 Refill All | 三只的饭碗按各自当前零食依次装满（Mochi: Sugar Cube×12；Puff: Milk×8；Berry: Strawberry×8）；FTUE 消化覆盖结束，恢复正常时长 | 金币 150→30 | `TUT_18` “Bowls run out while you're away. Tap Refill All before you go!” | 一键加满 |
| 9:20–9:40 | 通知说明页（仅说明，不强制） | Sure / Not now | 选 Sure 后弹出 iOS 系统通知授权 | — | `NOTIF_PRE_TITLE` / `NOTIF_PRE_BODY` | 本地通知 |
| 9:40–10:00 | 目标面板（Next Goal）+ 订单板出现 3 个普通订单 | 自由游玩 | — | — | `TUT_19` “Next goal: reach Level 3 to unlock Lemons.” | 普通订单 |

**FTUE 结束时数值核对：**

| 项 | 计算 | 结果 |
|---|---|---|
| 金币 | 初始 50 + 新手订单 20 + L2 奖励 50 + 访客 30 | 150（Refill All 前） |
| 经验 | 订单 10 + 发现 30 = 40 → 升 L2 消耗 20，余 20；+ 访客 10 | L2，30/80 |
| 星星糖 | 发现 1 + L2 奖励 1 + 访客 2 | 4 |
| 加速勺 | L2 奖励 1 | 1 |
| 原料 | Jam：3 份 Strawberry×3 = 9，Berry Jelly 用 2 → 7；Cream：3 份 Milk×3 = 9；Sugar：挤一挤 1，Berry Jelly 用 1 → 0 | Jam 7、Cream 9、Sugar 0 |

> 注意：07 章的可复算路径从“Refill All 之前、金币 150”开始计算。

## 3.3 新手异常与断点续玩

| 情况 | 处理 |
|---|---|
| 玩家 10 秒内不点 Mochi | 手指图标放大，Mochi 打呼噜并翻身；20 秒后播放轻微震动+提示音（仅一次） |
| 玩家在喂食步骤点其他地方 | 非关键 UI 置灰但可见；点灰色区域时 Nana 重复当前提示，不弹错误 |
| 拖食物失败（松手位置不在史莱姆上） | 食物弹回托盘；第二次失败后出现“先点食物再点史莱姆”的替代提示 |
| Body/Swirl 放反 | 不阻止；预览即时显示错误结果并提示 Swap；**若玩家坚持用错误组合开始**：允许（得到 Cream Strawberry Slime），Bella 说 “Close! But I wanted pink with creamy swirls.”，FTUE 免费再培育一次（同样 30 秒） |
| FTUE 中途杀进程 | 每个步骤结束写入存档（步骤号）；重开后从最近完成的步骤继续，已获奖励不重复发放 |
| FTUE 中途来电/切后台 | 计时按真实时间继续；回来时若孵化已完成，直接进入孵化步骤 |
| 跳过引导 | 主线步骤不可跳过（总时长短）；可选提示（拥抱、图鉴）提供 `TUT_SKIP` |
| 无网络 | FTUE 全程离线可完成；商店与广告入口在 FTUE 中隐藏 |

## 3.4 FTUE 之后的 10～30 分钟（第一天剩余部分）

| 时机 | 内容 | 目的 |
|---|---|---|
| 首次打开内继续游玩 | 普通订单 3 个（L1–3：1～2 行，每行 1～2 个）；第 2 次培育 ≤2 分钟（推荐 Cream Slime：Puff 作 Body、Mochi 作 Swirl） | 第一天内有第 2 个发现 |
| 第 2 次打开 | 若到 L3：Lemon 解锁（`UNLOCK_LEMON`），图鉴新增 Lemon 行/列剪影；玩家可自行尝试 Lemon 组合（07 章 7.7 即此情形） | 把规则迁移到新风味 |
| 第 2 天（L4） | 访客请求解锁，第一位访客描述 “sunny yellow slime with pink dots” | 外观描述驱动推理（发现路径 2，见 05 章） |
| 第一天结束 | 模拟：参与型 L3、发现 4 种；轻度 L3、发现 3 种 | — |
