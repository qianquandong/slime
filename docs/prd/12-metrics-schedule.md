# 12 · 指标、排期与验收

## 12.1 核心验证问题

| # | 问题 | 判定指标（定义） | 实验假设阈值 | 低于阈值时的动作 |
|---|---|---|---|---|
| V1 | 玩家是否**主动**尝试第二、第三个培育配方 | ① 首次会话内开始第 2 次培育（非 FTUE 脚本）的新用户比例；② D1 结束前开始第 3 次培育的比例；③ D3 内尝试的不同 (Body, Swirl, Treat) 组合数中位数 | ① ≥70% ② ≥50% ③ ≥6 | 检查漏斗断点：费用？预览不清？图鉴未被打开？先改 UI 引导，再考虑降低第 2/3 次培育时间 |
| V2 | 推理是否成立（不靠攻略、不盲试） | ① 招牌卡片解锁后 48 小时内尝试比例；② 解出中位尝试次数；③ 未花星星糖提示就解出的比例 | ① ≥50% ② ≤4 次 ③ ≥40% | 线索文本改写；Recipe check 更醒目 |
| V3 | 是否对特定宠物形成偏好 | ① 拥有 ≥5 只的玩家中，抚摸次数第 1 名的史莱姆占总抚摸比例（均匀基线 = 1/N）；② 改名率；③ 收藏锁使用率；④ 详情页打开次数的个体集中度 | ① ≥35%（N=5 时基线 20%）② ≥30% ③ ≥20% | 加强性格差异（反应、音色）；把亲密升级反馈做得更明显 |
| V4 | 触摸是否被当作玩法而非任务 | L3 之后，每次会话自愿抚摸次数中位数（不含挤一挤日上限后） | ≥15 次/会话 | 回到触感原型调参 |

> 所有阈值均为**实验假设**，用于决定下一步，不是市场预测。

## 12.2 留存、付费与广告（实验假设）

| 指标 | 软启动 1（不含商业化） | 软启动 2（含商业化） | 说明 |
|---|---|---|---|
| FTUE 完成率 | ≥85% | ≥85% | 漏斗按 `ftue_step` |
| D1 留存 | ≥40% | ≥40% | 假设 |
| D7 留存 | ≥15% | ≥15% | 假设 |
| D30 留存 | 观察 | ≥5% | 依赖 P1 内容节奏 |
| 平均每日会话数（D1–D7 活跃者） | 3～5 | 3～5 | 与经济模拟假设比对 |
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
| touch_summary | 会话结束（聚合，避免高频上报） | slime_uid, taps, holds, hugs, dizzy_count, squeeze_drops | V3、V4 |
| feed | 喂食 | slime_uid, food, count, method(drag/tap/fill_up/refill_all), cost | 喂食行为 |
| showing_changed | 表达风味切换 | slime_uid, from, to | 培育准备行为 |
| refill_all | 一键加满 | slimes, cost, partial, scope(pen/all) | 自动化使用 |
| offline_settle | 离线结算 | elapsed_min, materials, paused_by_cap | 饭碗/罐上限调参 |
| bake | 烘焙 | dessert, qty, method(bake/bake_deliver/treat) | 厨房使用 |
| order_deliver | 交付 | order_id, lines, coins, xp, ad_double | 经济 |
| order_skip / order_show_me | 取消/缺料跳转 | order_id, missing_material | 订单难度 |
| counter_sell | 柜台/原料出售 | item, qty, coins | 溢出监控 |
| breed_start | 开始培育 | nest_id, flavor_a, flavor_b, treat, k, fee, predicted_species, is_new, is_signature, tracked_sig, source(manual/breed_this/repeat/ftue), charm, breed_index | **V1、V2** |
| breed_hatch | 孵化 | species, is_new, sparkle, wait_after_ready_min | 发现节奏 |
| breed_cancel | 中止 | nest_id, elapsed_min | 误操作 |
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
| **P0（软启动 1：留存验证）** | 牧场场景（3 围栏）、史莱姆渲染+形变 A+B、触摸状态机（点/长按/拖/晕眩/挤一挤/拥抱）、性格与情绪表现、喂食与表达风味、饭碗与生产、每种原料罐、离线结算、厨房即时烘焙、甜品架、订单与访客请求、培育（Body/Swirl/Treat、预览、招牌 4 个、追踪与提示）、闪光、图鉴、等级 1～12 与设施、每日任务、本地存档与备份、本地通知、FTUE、设置、埋点、远程配置（软启动 1 调参需要）、5 种风味（含 Cocoa）、帽子与 Wardrobe（金币/星星糖帽子） |
| **P0-M（软启动 2 前完成：商业化）** | StoreKit 2 商店与恢复购买、P0 商品 8 个、激励广告聚合与 4 个位置、中性年龄门、ATT 说明页 |
| **P1** | Matcha 风味+11 品种+Matcha Latte 招牌、环境→形态（Chilly/Toasty）、iCloud 云存档、固定位置装饰（金币消耗）、Rainy Day Hats、Playtime Pack、Picnic Pack、控制点网格形变（详情页）、L13+ |
| **P2** | 品种协作、成长阶段、赛季通行证、Game Center、资源包下载、Android |

## 12.5 工作量（人日，区间）与依赖

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

**校验结论**：单程序按每周 5 个有效人日计（16 周 = 80 人日），P0 需 86～110 人日，P0+P0-M 需 95～121 人日（**19～24 周**）。美术 P0 66～79 人日、含商业化 69～82 人日（约 13～17 周），不是瓶颈。

| 目标周数 | 能交付什么 | 条件 |
|---|---|---|
| 12 周 | **垂直切片**：3 种风味、核心循环、2 个招牌、无 Cocoa、无商业化 | 可行 |
| 16 周 | **软启动 1 版本**（留存验证，无内购无广告） | 必须执行 12.7 第 1、2 档可砍项（节省 7～9 程序人日），且实际耗时落在估算区间下半段；**风险高** |
| 18 周（计划基线） | 软启动 1 版本，P0 完整（含 Cocoa） | 执行第 1 档可砍项（估算中值约 92 人日） |
| 22 周（计划基线） | 软启动 2：P0 + 商业化 | 商业化在软启动 1 运行期间并行开发 |

**建议**：以“W18 软启动 1、W22 软启动 2”为计划基线；需求中的 12～16 周对应“垂直切片～留存验证版”，不对应完整商业化 MVP。

## 12.6 里程碑

| 里程碑 | 周 | 交付 | 通过标准 |
|---|---|---|---|
| M0 触感原型 | W0–2 | 1 只史莱姆：形变 A+B、音效、震动；对照组：仅缩放 | 实验 E1 达标（12.10） |
| M1 核心循环灰盒（= 12 周垂直切片的地基） | W3–5 | 喂食→表达→生产→烘焙→订单→培育（3 风味、预览）；存档 | 实验 E2 达标 |
| M2 Alpha | W6–10 | P0 系统全部灰盒可玩；FTUE v1；美术管线打通（拼装预览工具） | 内部连续 3 天游玩无阻断 bug |
| M3 Beta（内容完整） | W11–15 | 5 风味、29 品种、4 招牌、L1–12、正式美术与音频、埋点；TestFlight 外部 50～100 人 | 崩溃用户率 <1%；FTUE 完成率 ≥85% |
| M4 软启动 1 | W16–18 | 菲律宾/马来西亚上架（无内购无广告）；并行开发 P0-M | 12.1 V1–V4 与 12.2 留存数据可读 |
| M5 软启动 2 | W19–22 | 商业化 P0-M + 软启动 1 修正；加拿大/澳大利亚/新西兰 | 付费与广告数据可读 |

外部前置（策划负责，W8 前启动）：App Store Connect 付费协议与税务、广告平台账号、隐私政策与客服页面、商标检索、TestFlight 外部测试审核。

## 12.7 可砍范围（按砍的顺序）

| 档 | 砍什么 | 节省（程序/美术人日） | 代价 |
|---|---|---|---|
| 1 | 每日任务 → P1；闪光+护符 → P1；回归礼物 → P1；Hat Stand 只留 2 顶 | 5–7 / 4–5 | 星星糖来源减少 → 招牌提示改为纯“3 次未命中免费” |
| 2 | Cocoa 风味及其 9 普通品种、Choco Lava、Neapolitan → P1；L5 改解锁 Lemon Cream Pie | 2 / 6–8 | 图鉴 16 种+2 招牌；长线内容更依赖 P1 |
| 3 | 访客请求改为“图鉴悬赏”（无访客角色，只有文字卡） | 3 / 4 | 失去外部角色驱动 |
| 4 | 第 3 个围栏与 Big Nap House → P1 | 1–2 / 3 | 后期容量紧张 |
| 不可砍 | 形变 A+B、表达风味、Body/Swirl 预览、Recipe check、离线结算、存档安全、FTUE | — | 核心假设无法验证 |

## 12.8 验收用例（41 条）

> 前置：Debug 构建提供时间加速、资源修改、存档查看面板。数值均为初始设计值。

| ID | 模块 | 前置条件 | 步骤 | 期望结果 |
|---|---|---|---|---|
| AC-01 | 触摸 | iPhone XR，240fps 高速摄像 | 点击史莱姆 | 触点凹陷在同一渲染帧出现（≤16.7ms，即 ≤4 个 240fps 帧） |
| AC-02 | 触摸 | 同上 | 单击后观察 | 80～120ms 达到压扁峰值；≤500ms 回到静止（误差 ≤1 帧） |
| AC-03 | 触摸 | 亲密 0 | ① 1 秒内点击 7 次；② 以 5 次/秒连续点击 10 秒 | ① 第 7 次点击时进入 Dizzy 2.5s，Dizzy 期间点击不增加亲密与挤一挤，之后恢复；② 不进入 Dizzy |
| AC-04 | 触摸 | Sugar 表达的史莱姆，今日挤一挤 0 | 点击 80 次（节奏 ≤5 次/秒） | 获得 10 个 Sugar；第 81～88 次不再产出；次日 04:00 后恢复 |
| AC-05 | 亲密 | 新史莱姆 | 点击 25 次、拥抱 4 次 | 亲密点 = 20 + 9 = 29（Lv1） |
| AC-06 | 喂食 | Sugar Slime 表达 Sugar | 喂 Strawberry×2，再喂 Milk×1 | 表达仍为 Sugar；气泡 “Cream 1/3”；再喂 Milk×2 → 表达 Cream，Toast `FEED_SHOWING` |
| AC-07 | 喂食 | 金币 100 | 喂 Lemon 后 3 秒内点 Undo | 金币回到 100；饭碗与连喂进度恢复喂食前 |
| AC-08 | 生产 | Strawberry Cream Slime，饭碗空，Jam 罐 0/80 | 喂 Strawberry×8，时间加速 120 分钟 | Jam = 32；饭碗 0；打盹 |
| AC-09 | 生产 | Sugar 罐 38/40，Sugar Slime 饭碗有 Sugar Cube | 等待 10 分钟 | 不开始消化（空间 2 < 4），头顶罐图标；烘焙 1 个 Sugar Cookie（−3）后自动开始 |
| AC-10 | 离线 | 3 只按 7.7 第 1 轮加满 | 杀进程，时间 +3 小时，重开 | 结算：Sugar +40、Cream +24、Jam +32；Mochi 碗里剩 2 份；弹窗显示 `AWAY_PAUSED` |
| AC-11 | 时间 | 正常游戏中 | 设备时间 −2 小时后返回游戏 | 显示 `ERR_CLOCK` 一次；所有计时冻结；时间恢复后继续，无重复发放 |
| AC-12 | 培育 | Puff 表达 Lemon，Berry 表达 Strawberry，L3 | 放入 Body=Puff、Swirl=Berry | 预览 “Lemon body · Berry Dots”，New!；`Start · 80`；40 分钟；孵化 Lemon Strawberry Slime；+40 XP、+1 星星糖 |
| AC-13 | 培育 | 同上 | 点 Swap | 预览 “Strawberry body · Lemon Zest” |
| AC-14 | 招牌 | L4，Body 表达 Strawberry，Swirl 表达 Cream，架上有 Strawberry Shortcake | Treat 放 Shortcake，Start | 费用 60；窝金光+`NEST_SPECIAL_GLOW`；90 分钟；Shortcake Slime；首次 +100 XP、+5 星星糖；Treat 已扣除 |
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
| AC-28 | 数值回归 | FTUE 结束存档（L2、150 金币、30 XP、4 星星糖、1 勺；Jam 7、Cream 9、Sugar 0） | 按 07 章 7.7 操作 | 终点：L3、40/200 XP、163 金币、6 星星糖、2 勺；原料 Sugar 28、Cream 32、Jam 27（培育前） |
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

## 12.9 立项风险

| # | 风险 | 可能性 | 影响 | 缓解 | 触发止损 |
|---|---|---|---|---|---|
| R1 | 触感做不出差异（核心卖点失效） | 中 | 高 | M0 先验证；A+B 不达标则评估控制点网格方案 | E1 不达标且 2 周调参无改善 → 重新评估项目 |
| R2 | 培育规则“太透明”导致无惊喜，或“太难”导致挫败 | 中 | 高 | 预览信息量 A/B（E3）；招牌提示可调 | V1/V2 低于阈值 |
| R3 | 内容消耗快（参与型约 7 天集齐 P0 普通品种） | 高 | 中 | P1 Matcha+环境形态在软启动第 3～4 周上线；等级曲线远程可调 | D7→D30 衰减过快 |
| R4 | 单程序瓶颈，P0+商业化 19～24 周 | 高 | 高 | 两段式软启动（先留存后商业化）；可砍清单；外包音频 | M2 延期 >2 周 → 执行第 2 档可砍 |
| R5 | 同题材竞争：Slime Rancher 已上 iOS；商店已有多款史莱姆放置游戏 | 高 | 中 | 竖屏触摸+可推理培育的差异化素材；避开竞品术语 | 商店页 A/B 点击率显著低于品类基线（以自有测试为准） |
| R6 | 名称/商标冲突 | 中 | 中 | 立项前检索；文案集中在 `APP_TITLE` | — |
| R7 | 外观付费意愿不足 | 中 | 中 | 先验证偏好（V3），再上商业化 | 软启动 2 付费转化低于假设 |
| R8 | 未成年人与隐私合规 | 中 | 高 | 年龄门、儿童导向广告、隐私清单、不进 Kids 分类 | Apple 审核反馈 |
| R9 | 后期金币囤积 | 高 | 低 | P1 装饰与 L13+ | L12 后留存下滑 |
| R10 | 无云存档导致换机流失 | 中 | 中 | P1 iCloud | 客服工单量 |

## 12.10 待验证事项与下一步 3 个关键实验

**待验证事项**

| # | 事项 | 方法 |
|---|---|---|
| T1 | 弹簧参数（k=280、ζ=0.38）与凹陷强度是否“软”而不“黏” | E1 |
| T2 | 玩家能否在不看提示的情况下理解 Body/Swirl | E2 |
| T3 | 预览显示完整外观 vs 只显示色块，哪种带来更多第 2/3 次培育 | E3 A/B |
| T4 | 饭碗时长 2 小时是否匹配实际回访间隔 | 软启动 `app_open.minutes_since_last` |
| T5 | 订单刷新与等级曲线是否让 L4 在第 2 天到达 | 软启动 `level_up` |
| T6 | 英文文案自然度 | 母语测试者审读（每版 2 人） |
| T7 | 商标与 ASO 关键词 | 法务/工具检索 |
| T8 | 首测地区 CPI 与留存基线 | 软启动 1 |

**实验 E1：触感原型对照测试（W0–2）**

| 项 | 设计 |
|---|---|
| 样本 | 12～16 名目标用户（远程 TestFlight 或线下） |
| 版本 | A：缩放回弹（方案 A）；B：A + 局部凹陷着色器 + 性格音高 + 震动；随机顺序各玩 3 分钟自由摸 |
| 指标 | 自愿触摸时长；偏好选择；一句话描述（编码“软/弹/黏/假”） |
| 通过 | ≥70% 偏好 B；B 的自愿触摸时长中位数 ≥45 秒 |

**实验 E2：培育推理灰盒测试（W3–5）**

| 项 | 设计 |
|---|---|
| 样本 | 10～15 名未接触过本作的玩家 |
| 流程 | 灰盒版 FTUE + 30 分钟自由游玩（3 风味、2 招牌、时间加速 10×） |
| 指标 | ① FTUE 后“预测后代外观”正确率（只给槽位，不给预览）；② 未提示情况下开始第 2、3 次培育的比例；③ 招牌解出尝试次数与是否求助 |
| 通过 | ① ≥80% ② ≥70% / ≥50% ③ 中位 ≤4 次，求助（问主持人）≤20% |

**实验 E3：软启动 1 留存与偏好（W16–18）**

| 项 | 设计 |
|---|---|
| 地区 | 菲律宾、马来西亚；无内购、无广告 |
| A/B | 预览卡：A 显示完整外观+名称（未发现显示 ???）；B 只显示主体色块+花纹图标 |
| 指标 | 12.1 V1–V4、12.2 留存；A/B 比较 breed_index≥3 的比例与 D7 |
| 决策 | V1–V4 至少 3 项达标且 D1 达到假设 → 进入软启动 2；否则按 12.1 “动作”列迭代一轮再测 |
