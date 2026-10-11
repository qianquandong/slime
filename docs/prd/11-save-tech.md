# 11 · 存档与产品技术约束

## 11.1 时间与离线

| 规则 | 说明 |
|---|---|
| 时间源 | 墙钟 `now`（设备 UTC 时间）+ 单调时钟（进程内防跳变）。MVP 不依赖服务器时间 |
| 存档记录 | `lastSeenWall`（最后一次在前台的墙钟）、`maxWallSeen`（见过的最大墙钟） |
| 正常离线 | `elapsed = now − lastSeenWall`，上限 7 天；按 06 章 6.7 算法结算 |
| 时间回拨 | 若 `now < maxWallSeen − 5 分钟`：所有计时（饭碗、培育、订单到达、访客、每日重置）**冻结**，直到 `now ≥ maxWallSeen`；显示 `ERR_CLOCK` 一次；已获得的东西不回收 |
| 时间前拨 | 允许（单机、无排行榜）。影响：可提前完成培育与访客；饭碗上限天然限制产出（最多 6 小时）；不额外处罚。软启动监控“单次离线 >3 天且 24 小时内再次 >3 天”的比例 |
| 时区变化 | 计时全部用 UTC；“每日 04:00 重置”按当前时区计算，同一 UTC 日内最多重置 1 次 |
| 前台运行 | 用单调时钟推进，每 1 秒驱动一次生产与计时；进入后台时立即存档 |

## 11.2 培育完成与随机结果

| 规则 | 说明 |
|---|---|
| 写入时机 | Start 时：亲本快照、Treat、结果品种、名字、性格、最爱食物、闪光、结束时间全部写入存档后，才扣费与消耗 Treat（同一事务） |
| 防刷 | 重开游戏、杀进程不改变已决定的结果；随机数种子 = 存档内持久化的计数器，不使用“启动时随机” |
| 完成 | `now ≥ endTime` → Ready；需玩家点击孵化（不自动孵化） |
| 本地通知 | Start 时预约 `endTime` 的本地通知（已授权时）；中止或加速后重新预约 |

## 11.3 存档与崩溃恢复

| 项 | 规则 |
|---|---|
| 格式 | 二进制或 JSON + 版本号 `schemaVersion` + CRC32 校验 |
| 位置 | App 沙盒 Application Support（随 iCloud 设备备份/系统迁移） |
| 写入 | 先写临时文件 → fsync → 原子替换；保留 2 份轮换备份（`save.bak1/bak2`） |
| 触发 | 每次经济事务后（防抖 2 秒合并）；进入后台；FTUE 每步结束；内购发放后**立即**写 |
| 读取失败 | 校验失败 → 依次尝试 bak1、bak2 → 成功则提示 `ERR_LOAD_BACKUP`；全部失败 → 新档前先把损坏文件另存供客服 |
| 磁盘满 | 写入失败提示 `ERR_SAVE_FAIL`，继续游戏但每 30 秒重试 |
| 事务一致性 | 扣费与发放在同一次存档内提交（例如培育 Start、设施升级、内购发放） |

## 11.4 内购与恢复（StoreKit 2）

| 场景 | 规则 |
|---|---|
| 购买成功 | 校验 `Transaction`（StoreKit 2 本地 JWS 验证）→ 发放 → 存档 → `transaction.finish()`；顺序不可颠倒 |
| 发放前崩溃 | 下次启动监听 `Transaction.updates`/未完成交易，重新发放（以 transactionID 去重，已发放 ID 记录在存档） |
| 待批准（Ask to Buy） | 显示 `SHOP_PENDING`，批准后经 `Transaction.updates` 发放 |
| 恢复购买 | 设置页与商店页的 `Restore Purchases` 按钮（Apple 建议由用户主动触发，不在启动时自动恢复）：遍历 `Transaction.currentEntitlements`，恢复所有永久商品；Welcome Basket 只恢复 Bow Topper |
| 消耗品 | 不可恢复；购买确认页注明 |
| 退款 | 收到 revocation 时：永久商品移除（帽子从史莱姆身上取下；Extra Nest 中若有培育进行中则完成后不能再开第 3 窝）；消耗品已用部分不追回 |
| 换设备 | 无云存档时进度不迁移（除 iCloud 设备备份/迁移），但永久商品可恢复 |

## 11.5 版本更新

| 规则 | 说明 |
|---|---|
| 存档迁移 | `schemaVersion` 递增；启动时按顺序执行迁移函数；迁移前备份 |
| 新客户端读旧档 | 必须支持；P0 起所有字段带默认值 |
| 旧客户端读新档 | 拒绝并提示 `ERR_UPDATE_REQUIRED` |
| 内容 ID | 品种、甜品、食物、帽子、设施 ID **永不复用、永不删除**；下架内容加 `retired` 标记 |
| 配置 | 配置表随包；P0 支持远程配置（静态 JSON，签名校验，失败用包内值），仅覆盖数值类字段（价格、时长、倍率、上限），不能新增 ID |
| 强制更新 | 不做（单机）；仅当存档版本不兼容时提示 |

## 11.6 账号、云存档与服务端：是否进入 MVP

| 能力 | MVP 决定 | 理由 | 后续 |
|---|---|---|---|
| 账号系统 | **不做** | 单机内容；减少隐私合规与登录流失 | — |
| 云存档 | **不做（P1）** | 需要处理冲突合并；MVP 依赖系统备份即可；但“换机丢档”是留存风险 | P1：iCloud（CloudKit 私有库）+ 冲突时取“经验更高”的一份并提示 |
| Game Center | P2 | 成就非核心 | — |
| 自建服务端 | **不做** | 3 人团队；无多人、无交易 | 远程配置用静态 CDN 文件 |
| 服务器时间校验 | 不做 | 单机无公平问题；前拨影响有限 | 若加入限时活动/通行证（P2）再做 |
| 统计分析 | **做（P0）** | 核心假设验证依赖埋点（12 章） | 选择不使用 IDFA 也能工作的分析 SDK |
| 广告聚合 | **做（P0）** | 激励广告 | 年龄 <13 时设置儿童导向请求 |

## 11.7 合规与隐私（P0 必做项）

| 项 | 要求 |
|---|---|
| 中性年龄门 | 首次出现广告/商店前（L3 后首次进入商店或首次广告按钮）显示 `AGE_TITLE`，只问出生年份，不预选、不暗示 |
| ATT | 年龄 ≥13 时，第 1 天第 2 次打开后显示说明页再请求；`NSUserTrackingUsageDescription` 文案英文；拒绝不影响功能 |
| 隐私清单 | App 与第三方 SDK 的 Privacy Manifest 与 Required Reason API 声明齐全 |
| App 隐私标签 | 按实际 SDK 数据收集填写 |
| 年龄分级 | 按 Apple 新年龄分级问卷填写；**不选择** Kids Category |
| 屏蔽词 | 改名使用本地英文屏蔽词表 |

## 11.8 性能目标

| 指标 | 目标（iPhone XR/A12 为最低档；iPhone 12 为参考档） |
|---|---|
| 帧率 | 交互时 60fps；10 秒无输入降到 30fps；离线结算/后台 0fps |
| 触摸到视觉响应 | ≤1 帧（16.7ms） |
| 冷启动到可触摸 | 参考档 ≤3 秒；最低档 ≤5 秒 |
| 离线结算计算 | ≤50ms（后台线程） |
| 内存 | 峰值 ≤350MB（最低档） |
| 安装包 | ≤150MB（P0 全部资源随包） |
| 耗电 | 前台 10 分钟耗电不高于同机型静态 2D 休闲游戏基线（测试时测对照组） |
| 同屏 | 当前围栏 4 只全量动画 + 相邻围栏静帧（其余不渲染）；粒子池上限 200 |
| 崩溃率 | 软启动崩溃用户率 <0.5%（实验目标） |

## 11.9 内容配置表关键字段

> 初稿见 `config/`；以下为程序读取所需的关键字段，不含完整代码。

| 表 | 关键字段 | 说明 |
|---|---|---|
| flavors | id, flavor_name, tier, unlock_level, food_id, food_name, food_price, digest_min, material_id, material_name, material_value, body_color, pattern_style, scope | 风味=食物=原料一一对应 |
| species（规则生成+招牌覆盖） | id, name, kind(starter/basic/sugar-pattern/blend/pure/signature), body, pattern, treat, unlock_level, breed_min, fee, discovery_xp, art_parts, idle_anim, sfx_set, scope, retired | 普通品种由规则生成；招牌行覆盖外观与时间 |
| signatures | id, name, body_flavor, pattern_flavor, treat_dessert, card_unlock_level, signature_part, clue_string_id, required_env(P1), scope | 匹配键 = (body, pattern, treat[, env]) |
| desserts | id, name, unlock_level, recipe(material:qty 列表), sell_price, xp, topper_art, scope | 价格/经验由公式校验 |
| levels | level, xp_to_next, coin_reward, star_sugar_reward, spoon_reward, unlocks(id 列表) | — |
| facilities | id, name, group, level_req, cost_coins, cost_star_sugar, effect_key, effect_value, art_id | — |
| order_rules | level_min, level_max, refresh_min, lines_min, lines_max, qty_max, cancel_cooldown_min, dessert_weight_rule | — |
| visitors | id, name_string_id, portrait, scope | 访客与顾客共用（`config/visitors.csv`） |
| daily_tasks | id, string_id, target, reward_coins, reward_xp, unlock_level, group | `config/daily_tasks.csv`；选取规则见 06 章 6.10 |
| cosmetics | id, name, name_string_id, slot, price_type(coins/star_sugar/iap/reward), price, source, anchor_overrides, scope | `config/cosmetics.csv` |
| iap_products | product_id, type(consumable/non_consumable), name_string_id, desc_string_id, test_price_cny, grants(列表), daily_limit, restore_grants, scope | `config/iap_products.csv` |
| ad_placements | id, string_id, reward, daily_cap, shared_counter | `config/ad_placements.csv` |
| params | key, value, unit | 全局公式常数（`config/params.csv`） |
| strings | string_id, english, zh_note, location, max_chars | 文案（附录 A） |

## 11.10 存档关键字段

| 对象 | 字段 |
|---|---|
| player | schemaVersion, coins, xp, level, starSugar, spoons, flags(ftueStep, ageBand, attAsked, notifAsked), createdAt |
| time | lastSeenWall, maxWallSeen, lastDailyReset |
| slimes[] | uid, speciesId, name, personality, favoriteFood, showingFlavor, streakFood, streakCount, bowlQueue[{food, minutesLeft}], reservedJar, friendshipPoints, todayPets, todayHugs, todayFeeds, todaySqueeze, squeezeRing, topper, hat, sparkle, form(P1), location(pen/house), penSlot, favoriteLock, bornAt, inNestId |
| nests[] | id, startWall, endWall, parentA, parentB, flavorA, flavorB, treat, resultSpeciesId, resultName, resultPersonality, resultFavorite, resultSparkle, isSignature, charmUsed |
| pantry | {materialId: qty}, shelf {dessertId: qty} |
| orders[] | id, customer, lines[{dessertId, qty}], arriveAt |
| visitor | targetBody, targetPattern, customer, arriveAt |
| codex | discovered{speciesId: {firstAt, count, sparkleSeen}}, signatures{sigId: {tracked, attempts, misses, revealedSlots[]}} |
| facilities | {group: tierId} |
| dailyTasks | date, tasks[{id, progress, claimed}], allClaimed |
| ads | date, counters{placement: n} |
| iap | processedTransactionIds[], entitlements[] |
| rng | breedCounter, sinceLastSparkle |
