# 12 · 指标、排期与验收

> v0.2：当前执行第14章10工作日原型；本章留存/商业化指标仅用于通过原型后的真实时间测试。旧W18/W22交付基线撤回，未批准自动扩展完整P0。

> Codex计划/美术、Claude实现、负责人组织实际测试与发行的任务分工见[执行总计划](../production/README.md)。后续20人多日研究、50～100人TestFlight及RC证据口径见[实际测试方案](../production/testing.md)，均是待执行计划。

## 12.1 核心验证问题与归因

原型12人样本使用第14章的具体人数阈值。本表为后续更大样本、真实时间版本的实验假设，不把原型压缩计时直接外推。

| ID | 问题 | 口径 | 后续测试目标/动作 |
|---|---|---|---|
| V1 | 主动第二/三次培育 | 首次会话内第二次、安装后24小时内第三次的开始比例，分母为所有新用户。排除FTUE/纠正、任务推荐、自动填槽、主持人帮助；另报教学完成者条件比例 | ≥70%/≥50%；分别统计缺钱、亲本忙、缺配方理解和无兴趣，先修阻断再解释意愿 |
| V2 | 能推理招牌 | 卡片解锁后48小时尝试率；无主持人帮助且无任何免费/付费答案揭示的独立解出率；成功者尝试中位数，同时报告未解出/退出人数 | 尝试≥50%、独立解出≥40%、成功者中位≤4；不能只挑成功者声称易懂 |
| V3 | 跨日个体偏好 | 对拥有时间相近（相差≤24小时）、可触摸曝光相近（比值≤2）的≥3只宠物，记录无奖励互动份额与跨日选择；排除引导、任务和产量差异影响 | 描述性结果，不沿用全部抚摸35%的旧门槛；需要玩家讲出行为/声音/互动理由，不能仅靠改名/收藏推断依恋 |
| V4 | 无奖励也愿意摸 | 单列金币/原料、亲密、任务均不增加的触摸次数、时长和发生比例。**包括奖励日上限后**的触摸；有奖励段另列。没有无奖励机会的会话记为不适用，不计0 | 后续目标：有无奖励机会的会话中≥30%产生主动触摸，且这些会话（含0）次数中位数≥5；均为待验证假设。原型用统一无奖励段避免只观察高频玩家 |

E1触感、E2a理解、E2b探索、E2c招牌是独立必要门槛，不能用“4项过3项”掩盖核心失败。原型E4偏好为探索项；任何装扮商业化仍需后续跨日偏好证据。

## 12.2 留存、付费与广告（实验假设）

| 指标 | 软启动 1（不含商业化） | 软启动 2（含商业化） | 说明 |
|---|---|---|---|
| FTUE 完成率 | ≥85% | ≥85% | 漏斗按 `ftue_step` |
| D1 留存 | ≥40% | ≥40% | 假设 |
| D7 留存 | ≥15% | ≥15% | 假设 |
| D30 留存 | 观察 | ≥5% | 在当前可用内容下观察；不得假定P1按时补齐 |
| 平均每日会话数（D1–D7 活跃者） | 3～5 | 3～5 | 观察真实分布，不以旧bot作为基线 |
| 付费转化（D7 累计） | — | ≥1.5% | 假设 |
| 首购商品分布 | — | Welcome Basket ≥50% | 验证低门槛首购 |
| 激励广告：DAU 中观看比例 | — | ≥30% | 假设 |
| 每观看者每日次数 | — | 3～5 | 上限 8 |
| 崩溃用户率 | <0.5% | <0.5% | — |

## 12.3 埋点表

| 事件 | 触发 | 关键属性 | 用途 |
|---|---|---|---|
| app_open | 进入前台 | session_id, minutes_since_last, level, offline_materials | 会话节奏 |
| ftue_step | 每个新手步骤完成 | step_id, duration_ms, retries | 新手漏斗 |
| touch_summary | 分段结束/进入后台时增量写入，带segment_id去重 | slime_uid, owned_minutes, visible_touchable_seconds, phase, reward_mode, taps_rewarded, taps_unrewarded, active_touch_ms, tutorial, task_prompt, host_help, position, segment_id | V3/V4；崩溃不丢掉整个会话，原型日志本地导出 |
| feed | 喂食 | slime_uid, food, count, method(drag/tap/fill_up/refill_all), cost | 喂食行为 |
| showing_changed | 表达风味切换 | slime_uid, from, to | 培育准备行为 |
| refill_all | 一键加满 | slimes, cost, partial, scope(pen/all) | 自动化使用 |
| offline_settle | 离线结算 | elapsed_min, materials, paused_by_cap | 饭碗/罐上限调参 |
| bake | 烘焙 | dessert, qty, method(bake/bake_deliver/treat) | 厨房使用 |
| order_deliver | 交付 | order_id, lines, coins, xp, ad_double | 经济 |
| order_skip / order_show_me | 取消/缺料跳转 | order_id, missing_material | 订单难度 |
| counter_sell | 柜台/原料出售 | item, qty, coins | 溢出监控 |
| breed_start | 开始培育 | nest_id, flavor_a, flavor_b, treat, k, fee, predicted_species, is_new, is_signature, tracked_sig, source(manual/breed_this/repeat/ftue/ftue_repair), task_prompt, host_help, profile, time_override, charm, breed_index | **V1、V2** |
| breed_hatch | 孵化 | species, is_new, sparkle, wait_after_ready_min | 发现节奏 |
| breed_cancel | 中止 | nest_id, elapsed_min | 误操作 |
| test_prediction / test_choice | 隐藏预览预测题/中性偏好选择 | test_id, participant_id, variant_order, question_id, answer, correct, help, reason_code | 第14章原型验证 |
| sig_track / sig_check / sig_hint / sig_solved | 招牌流程 | sig_id, attempt_no, body_ok, swirl_ok, treat_ok, hint_source, minutes_since_card | **V2** |
| codex_view / codex_cell_tap / breed_this | 图鉴 | tab, species, state | 线索使用 |
| visitor_spawn / visitor_complete | 访客 | target, minutes_to_complete, was_new | 探索订单效果 |
| detail_open / rename / favorite_lock / hat_equip | 宠物个体 | slime_uid, species | **V3** |
| friendship_level | 亲密升级 | slime_uid, level, days_owned | V3 |
| rehome | 放生 | species, was_duplicate, friendship_level | 偏好反证 |
| level_up / facility_buy | 进度 | level, minutes_since_install / facility_id | 经济节奏 |
| shop_view / iap_preview / try_on | 商店 | tab, source, product | 商品兴趣 |
| iap_purchase_start / success / fail / restore | 内购 | product, price_tier, error | 付费 |
| ad_offer_shown / ad_start / ad_reward / ad_fail | 广告 | placement, daily_index | 广告 |
| prompt_shown / prompt_dismissed | 情境推荐 | prompt_id | 打扰度 |
| notif_permission / att_result / age_band | 权限与合规 | result | 合规 |
| settings_change | 设置 | key, value | 偏好（如关震动比例） |

## 12.4 范围分级（P0 / P1 / P2）

| 优先级 | 内容 |
|---|---|
| **原型（当前范围）** | 第14章：1围栏、3风味、2招牌、无奖励触摸、短教学、最小经济链与本地日志；10工作日 |
| **P0（候选软启动1，验证后重新冻结范围）** | 牧场场景（3 围栏）、史莱姆渲染+形变 A+B、触摸状态机（点/长按/拖/晕眩/挤一挤/拥抱）、性格与情绪表现、喂食与表达风味、饭碗与生产、每种原料罐、离线结算、厨房即时烘焙、甜品架、订单与访客请求、培育（Body/Swirl/Treat、预览、招牌 4 个、追踪与提示）、闪光、图鉴、等级 1～12 与设施、每日任务、本地存档与备份、本地通知、FTUE、设置、埋点、远程配置（软启动 1 调参需要）、5 种风味（含 Cocoa）、帽子与 Wardrobe（金币/星星糖帽子） |
| **P0-M（软启动 2 前完成：商业化）** | StoreKit 2 商店与恢复购买、P0 商品 8 个、激励广告聚合与 4 个位置、中性年龄门、按实际追踪需求决定ATT接入 |
| **P1** | Matcha 风味+11 品种+Matcha Latte 招牌、环境→形态（Chilly/Toasty）、iCloud 云存档、固定位置装饰（金币消耗）、Rainy Day Hats、Playtime Pack、Picnic Pack、控制点网格形变（详情页）、L13+ |
| **P2** | 品种协作、成长阶段、赛季通行证、Game Center、资源包下载、Android |

## 12.5 完整P0参考工作量（非两周任务单）

保留v0.1模块估算用于后续取舍；原型内可复用工作应在下一轮估算中扣除，实际调参/修复/测试支持另计。

| 模块 | 程序 | 美术 | 策划 | 依赖 |
|---|---|---|---|---|
| 工程框架、配置加载、存档（原子写/备份/迁移） | 7–9 | — | 2 | — |
| 史莱姆渲染：调色/花纹/半透明着色器、分层、形变 A+B、弹簧 | 10–13 | 10–12 | 1 | M0 触感原型结论 |
| 触摸状态机、情绪、性格闲置、音高系统、震动 | 6–8 | 4–5（表情） | 4–5（音频采购与编辑） | 渲染 |
| 喂食/表达/饭碗/生产/罐/离线结算 | 8–10 | 3 | 2 | 存档 |
| 厨房、甜品架、出售 | 3–4 | 3 | 1 | 生产 |
| 订单、访客、顾客 | 5–6 | 5–6（头像） | 2 | 厨房 |
| 培育：窝、预览、招牌、追踪/提示、孵化演出、闪光、命名 | 8–10 | 6–8 | 3 | 渲染、生产 |
| 图鉴（矩阵/招牌/Breed This） | 4–5 | 2 | 1 | 培育 |
| 等级、解锁、设施、每日任务、目标面板、回归礼物 | 5–6 | 4 | 3 | 全部经济 |
| 牧场场景、围栏切换、昼夜调色、小屋列表 | 4–5 | 10–12 | 1 | 渲染 |
| UI 页面与 UI Kit | 8–10 | 8–10 | 2 | 各系统 |
| FTUE 脚本 | 4–5 | 1 | 3 | 全部核心系统 |
| 帽子/Wardrobe/Hat Stand | 2–3 | 6–8（12 顶+9 头饰） | 1 | 渲染锚点 |
| 埋点、本地通知、远程配置 | 4–6 | — | 2 | — |
| 性能、修复、TestFlight、商店素材 | 8–10 | 4–5 | 5 | — |
| **小计：软启动 1** | **86–110** | **66–79** | **33–34** | |
| 商业化：StoreKit 2、商店页、恢复、广告聚合、年龄门、ATT | 9–11 | 3（商店卡片、主题皮肤） | 3 | App Store Connect 协议、税务、广告账号（外部前置时间 1～3 周） |
| **合计 P0 + P0-M** | **95–121** | **69–82** | **36–37** | |

**产能说明**：原估算为P0 86～110程序人日、含商业化95～121人日。18周×5日=90日，已经小于执行第1档删减后的约92人日中值，还没有容纳会议、测试支持和迭代。因此撤回W18/W22基线。通过原型后用实际有效开发产能重新估算，不把5个工作日全部当成功能开发。

## 12.6 里程碑与进入条件

| 阶段 | 时间/范围 | 进入或退出条件 |
|---|---|---|
| M0 两周原型 | D1–D10；本次唯一计划阶段 | 按第14章四项必要门槛及经济检查决定继续/定向迭代/暂停 |
| M1 多日灰盒 | M0通过后另排；3风味小范围，真实计时，进行至少7天观察 | 实测回访、无奖励触摸、跨日宠物偏好、内容消耗；不依靠广告和任务维持指标 |
| M2 留存版本 | M1证据支持后冻结P0范围并重新估工 | 明确所需内容量，预算包含单程序的QA和修正；不同时承诺商业化/P1 |
| M3 软启动1 | 功能/性能/存档验收通过；时间另定 | 按真实版本与安装批次观察D1/D7；D30为观察项 |
| M4 商业化验证 | 留存与跨日偏好成立后单独安排P0-M | 再评估商品、广告与容量；原型结果不能证明付费意愿 |
| P1 内容扩展 | 单独排队、估工、验证；无固定第3～4周承诺 | 用现有内容测试结果确定优先级；与修复/商业化争用同一个程序时明确取舍 |

原型使用线下真机与本地日志，不以App Store审核为两周前置。商店协议、广告账号、隐私材料和外部TestFlight审核在决定相应阶段时安排。

## 12.7 可砍范围（按砍的顺序）

| 档 | 砍什么 | 节省（程序/美术人日） | 代价 |
|---|---|---|---|
| 1 | 每日任务 → P1；闪光+护符 → P1；回归礼物 → P1；Hat Stand 只留 2 顶 | 5–7 / 4–5 | 星星糖来源减少 → 招牌提示改为纯“3 次未命中免费” |
| 2 | Cocoa 风味及其 9 普通品种、Choco Lava、Neapolitan → P1；L5 改解锁 Lemon Cream Pie | 2 / 6–8 | 图鉴 16 种+2 招牌；长线内容更依赖 P1 |
| 3 | 访客请求改为“图鉴悬赏”（无访客角色，只有文字卡） | 3 / 4 | 失去外部角色驱动 |
| 4 | 第 3 个围栏与 Big Nap House → P1 | 1–2 / 3 | 后期容量紧张 |
| 不可砍 | 形变 A+B、表达风味、Body/Swirl 预览、Recipe check、离线结算、存档安全、FTUE | — | 核心假设无法验证 |

## 12.8 验收用例（47条；按阶段执行）

两周原型只执行第14章覆盖的功能与经济项；购买/广告/完整产品存档等用例留待相应阶段。

> 前置：Debug 构建提供时间加速、资源修改、存档查看面板。数值均为初始设计值。

| ID | 模块 | 前置条件 | 步骤 | 期望结果 |
|---|---|---|---|---|
| AC-01 | 触摸 | 真机应用内时间戳+高速摄像 | 点击史莱姆 | 输入事件→首次提交可见形变≤1渲染帧；物理触摸到屏幕显示延迟单独报告，不用16.7ms混代端到端延迟 |
| AC-02 | 触摸 | 同上 | 单击后观察 | 80～120ms 达到压扁峰值；≤500ms 回到静止（误差 ≤1 帧） |
| AC-03 | 触摸 | 亲密 0 | ① 1 秒内点击 7 次；② 以 5 次/秒连续点击 10 秒 | ① 第 7 次点击时进入 Dizzy 2.5s，Dizzy 期间点击不增加亲密与挤一挤，之后恢复；② 不进入 Dizzy |
| AC-04 | 触摸 | Sugar 表达的史莱姆，今日挤一挤 0 | 点击 80 次（节奏 ≤5 次/秒） | 获得 10 个 Sugar；第 81～88 次不再产出；次日 04:00 后恢复 |
| AC-05 | 亲密 | 新史莱姆 | 点击 25 次、拥抱 4 次 | 亲密点 = 20 + 9 = 29（Lv1） |
| AC-06 | 喂食 | Sugar Slime 表达 Sugar | 喂 Strawberry×2，再喂 Milk×1 | 表达仍为 Sugar；气泡 “Cream 1/3”；再喂 Milk×2 → 表达 Cream，Toast `FEED_SHOWING` |
| AC-07 | 喂食 | 金币 100 | 喂 Lemon 后 3 秒内点 Undo | 金币回到 100；饭碗与连喂进度恢复喂食前 |
| AC-08 | 生产 | Strawberry Cream Slime，饭碗空，Jam 罐 0/80 | 喂 Strawberry×8，时间加速 120 分钟 | Jam = 32；饭碗 0；打盹 |
| AC-09 | 生产 | Sugar 罐 38/40，Sugar Slime 饭碗有 Sugar Cube | 等待 10 分钟 | 不开始消化（空间 2 < 4），头顶罐图标；烘焙 1 个 Sugar Cookie（−3）后自动开始 |
| AC-10 | 离线 | 三只初始宠物；原料罐全空、40上限，各按正常120分钟加满（不是FTUE快照） | 杀进程，时间 +3 小时，重开 | 结算：Sugar +40、Cream +24、Jam +32；Mochi 碗里剩 2 份；弹窗显示 `AWAY_PAUSED` |
| AC-11 | 时间 | 正常游戏中 | 设备时间 −2 小时后返回游戏 | 显示 `ERR_CLOCK` 一次；所有计时冻结；时间恢复后继续，无重复发放 |
| AC-12 | 培育 | Puff表达Lemon、Berry表达Strawberry，L3，已完成至少3次培育 | 放入 Body=Puff、Swirl=Berry | 预览 “Lemon body · Berry Dots”，New!；`Start · 80`；40 分钟；孵化 Lemon Strawberry Slime；+40 XP、+1 星星糖 |
| AC-13 | 培育 | 同上 | 点 Swap | 预览 “Strawberry body · Lemon Zest” |
| AC-14 | 招牌 | L4，已完成至少3次培育；Body表达Strawberry，Swirl表达Cream，架上有Strawberry Shortcake | Treat 放 Shortcake，Start | 费用 60；窝金光+`NEST_SPECIAL_GLOW`；90 分钟；Shortcake Slime；首次 +100 XP、+5 星星糖；Treat 已扣除 |
| AC-15 | 招牌 | 追踪 Shortcake | Treat 放 Berry Jelly 培育 | 结果 Strawberry Cream Slime 戴 Berry Jelly 头饰；Recipe check：Body ✓ Swirl ✓ Treat ✗；未命中计数 1 |
| AC-16 | 提示 | 追踪卡片，Body/Swirl 已得过 ✓，未命中 2 | 再未命中 1 次 | `SIG_HINT_FREE`；揭示 Treat（而不是 Body） |
| AC-17 | 培育存档 | Debug 显示结果字段 | Start 后杀进程 10 次再孵化 | 品种、名字、性格、最爱、闪光与 Start 时记录一致 |
| AC-18 | 闪光 | Debug：sinceLastSparkle=39 | 培育 1 次 | 结果必为闪光；计数归零 |
| AC-19 | 培育异常 | 围栏与小屋全满，荚 Ready | 点 Hatch | `NEST_NO_ROOM`；荚保留；该窝 Start 不可用；放生 1 只后可孵化 |
| AC-20 | 培育异常 | 两个槽 | 把同一只拖进两个槽 | 第二次被拒，`NEST_SAME_SLIME` |
| AC-21 | 订单 | 原料足够 | 交付 Strawberry Shortcake ×2 | +53 金币、+10 XP；Jam −4、Cream −4、Sugar −2 |
| AC-22 | 订单 | 架上有 1 个 Shortcake | 对 Shortcake ×2 订单点 Bake & Deliver | 先用架上 1 个，再即时烘焙 1 个；只扣 1 份原料 |
| AC-23 | 订单 | L2 | 交付 1 单 | 槽位倒计时 1:00 后出现新订单（±1 秒） |
| AC-24 | 订单 | L2 | Skip 一单并确认 | 冷却 5:00；无其他扣除 |
| AC-25 | 订单 | 缺 2 个 Lemon Curd | 查看订单卡 → Show me | 显示 “Need 2 more Lemon Curd”；跳回牧场，Lemon 被选中，有 Lemon 加成的史莱姆高亮 |
| AC-26 | 访客 | 请求 “sunny yellow slime with pink dots”，Lemon Strawberry Slime 在小屋 | 点 Show | 完成；+120 金币、+20 XP、+2 星星糖；该史莱姆仍在小屋，属性不变 |
| AC-27 | 数值 | L2，经验 70/80 | 获得 10 XP | 升 L3：+80 金币、+1 星星糖、+1 加速勺；Lemon 出现在托盘；`UNLOCK_LEMON` |
| AC-28 | 数值回归 | 第03章正式结束快照：L2、90金币、30XP、4星星糖、1勺，三碗60分钟；Jam7/Cream9/Sugar0 | 按07章7.7操作 | t=66：L3、50/200XP、226金币、7星星糖、2勺；Sugar6/Cream9/Jam7/Lemon0；Puff碗55分钟；第5只进入小屋 |
| AC-29 | 防死锁 | 金币 3，所有饭碗空 | 进入牧场 | 弹出免费方糖（6 个）；领取后 4 小时内不再出现 |
| AC-30 | 设施 | L5，金币 2,000，星星糖 4 | 购买 Twin Nest | 按钮显示 `Needs 5 Star Sugar`，不可购买；星星糖 5 后可买，扣 2,000 金币+5 星星糖 |
| AC-31 | 存档 | 正常存档 | 篡改主存档 1 字节后启动 | 读 bak1，`ERR_LOAD_BACKUP`；进度为最近一次备份 |
| AC-32 | 存档 | 自动化脚本 | 写存档过程中强杀 50 次 | 50 次重启均能加载（主档或备份），无崩溃 |
| AC-33 | 购买 | Sandbox 账号 | 购买 Extra Nest | 立即出现第 3 个窝；重启后仍在 |
| AC-34 | 购买 | 已购 Extra Nest、Tea Party Hats、Welcome Basket；删除重装 | Restore Purchases | 恢复第 3 窝与 3 顶帽子、Bow Topper；**不**再发 300 金币与 5 勺；`SHOP_RESTORE_DONE` |
| AC-35 | 购买 | Sandbox | 支付成功后、发放前杀进程 | 重启后发放一次；transactionID 去重，二次重启不重复发放 |
| AC-36 | 购买 | 当日已购 Handful of Spoons 3 次 | 打开商店 | 该商品显示 0 left today 且不可购买；04:00 后恢复 |
| AC-37 | 购买 | Ask to Buy 子账号 | 购买 Tea Party Hats | `SHOP_PENDING`；家长批准后自动发放 |
| AC-38 | 广告 | 广告测试模式 | 订单翻倍广告中途关闭 | 不发奖，`AD_CLOSED_EARLY`，次数不消耗；看完则 ×2 且次数 −1；第 4 次入口隐藏 |
| AC-39 | 合规 | 年龄门选 2016 年 | 继续游戏至 L5 | 无情境购买横幅、无 ATT 弹窗；广告请求带儿童导向标记 |
| AC-40 | 文案 | iPhone SE 3，动态字体 Large | 遍历全部页面截图 | 所有玩家可见文本为英文（自动扫描无 CJK 字符）；“Strawberry Shortcake”等最长名称不截断；无按钮溢出 |
| AC-41 | 生产 | Sugar Slime 碗里依次为 Sugar Cube×1、Milk×2；Sugar 罐 38/40，Cream 罐 0/40 | 等待 30 分钟 | 跳过 Sugar Cube（空间 2 < 4），消化 2 份 Milk，Cream +6；Sugar Cube 仍在碗里；烘焙 Sugar Cookie 后自动消化该 Cube |
| AC-42 | FTUE资源 | 新档标准路径 | 完成Starter bowls，然后Puff+Mochi开始第二次培育 | Starter扣60后90金币，Start再扣40后50；计时2分钟；重开不再领Starter |
| AC-43 | 共享罐预留 | 两只Sugar Slime各一份方糖，Sugar36/40 | 同时推进10分钟 | 仅一份完成至40；另一份完整保留，不出现44或截半份 |
| AC-44 | 免费收藏 | 初始设施 | 查看容量并放入每个P0品种各一只 | 围栏4+小屋30=34≥29，无须付费或放生；小屋不生产 |
| AC-45 | 访客持有 | 图鉴已发现目标，但活体均放生 | 请求展示 | 不可交付；小屋中实际持有匹配个体则可交付；Showing不替代出生Body/Swirl |
| AC-46 | 退款 | 喂Milk×3，推进1分钟；另有免费方糖 | Swap Snack | 只退两份未开始Milk的12金币；正在消化那份14分钟和预留保留；免费份退款0；日计数不重置 |
| AC-47 | 父母与容量 | 空间全满，荚Ready | Hatch及重复借用亲本 | 不发首次发现奖、不自动放生；荚和亲本锁保留；腾位成功Hatch后才发一次奖励并解除锁 |

## 12.9 立项风险

| # | 风险 | 可能性 | 影响 | 缓解 | 触发止损 |
|---|---|---|---|---|---|
| R1 | 触感做不出差异（核心卖点失效） | 中 | 高 | M0 先验证；A+B 不达标则评估控制点网格方案 | 按14章最多一次5工作日定向迭代，复测不通过则暂停扩展 |
| R2 | 培育规则“太透明”导致无惊喜，或“太难”导致挫败 | 中 | 高 | 通过原型后做预览信息量A/B（12.10）；招牌提示可调 | V1/V2 低于阈值 |
| R3 | 理解矩阵后缺少持续探索动机 | 高 | 高 | 原型测主动第2/3次；后续真实计时多日测试；不以P1按时补充为前提 | 探索门槛未过则不扩展内容 |
| R4 | 单程序产能不足，完整P0+商业化95～121人日仅为参考 | 高 | 高 | 两周先测；下一阶段重新估工，QA/修复/商业化顺序排队 | 原型D4/D6失守按14章冻结新增 |
| R5 | 同题材竞争：Slime Rancher 已上 iOS；商店已有多款史莱姆放置游戏 | 高 | 中 | 竖屏触摸+可推理培育的差异化素材；避开竞品术语 | 商店页 A/B 点击率显著低于品类基线（以自有测试为准） |
| R6 | 名称/商标冲突 | 中 | 中 | 立项前检索；文案集中在 `APP_TITLE` | — |
| R7 | 外观付费意愿不足 | 中 | 中 | 先验证偏好（V3），再上商业化 | 软启动 2 付费转化低于假设 |
| R8 | 未成年人与隐私合规 | 中 | 高 | 年龄门、儿童导向广告、隐私清单、不进 Kids 分类 | Apple 审核反馈 |
| R9 | 后期金币囤积 | 高 | 低 | P1 装饰与 L13+ | L12 后留存下滑 |
| R10 | 无云存档导致换机流失 | 中 | 中 | P1 iCloud | 客服工单量 |

## 12.10 验证顺序

首轮E1/E2a/E2b/E2c与偏好观察E4统一执行[第14章](14-two-week-prototype.md)，不再保留冲突的另一套样本/门槛。

原型通过后：先用真实时间小范围灰盒观察至少7天，验证饭碗覆盖、金币缺口、矩阵耗尽与跨日偏好；再决定完整P0内容量。预览完整外观vs色块的A/B放到这一阶段，固定其他条件与版本，预先定义样本和比较窗口。没有足够样本时只报告方向，不宣称胜出。

后续软启动必须同时满足核心玩法指标与留存进入条件；不得以“V1–V4至少3项达标”跳过触感或探索失败。原型/加速夹具/主持人帮助记录不得混入生产留存报表。
