# 史莱姆甜品牧场 · Slime Sweets Farm（工作名）

竖屏、单手操作的 iPhone 宠物养成游戏：揉捏有名字和性格的史莱姆，喂不同食物让它显色，用 **Body / Swirl / Treat** 三个槽位按看得见的规则培育新品种，再把史莱姆产出的原料做成甜品、交订单、扩建牧场。

本仓库目前包含 **MVP 产品需求文档（v0.1 评审稿，2026-10-11）**、初始配置表，以及可复算全部数值的检查脚本。

## 文档

| 章节 | 内容 |
|---|---|
| [00 总览、假设与术语](docs/prd/00-overview.md) | 关键决策、假设清单、术语对照 |
| [01 产品定位与竞品分析](docs/prd/01-positioning.md) | 目标用户、支柱、商业假设、竞品（官方来源，检索日期 2026-10-11）、首测地区 |
| [02 核心循环与目标](docs/prd/02-core-loop.md) | 10 秒 / 3 分钟 / 1 天 / 30 天循环，自动化后点击的意义 |
| [03 前 10 分钟体验脚本](docs/prd/03-ftue.md) | 逐时间段脚本、新手覆盖规则、异常处理 |
| [04 宠物状态与互动规则](docs/prd/04-pet-state.md) | 属性取舍、状态变化、情绪状态机、输入判定 |
| [05 培育与发现系统](docs/prd/05-breeding.md) | 确定性/随机规则、29 个品种、4 个招牌配方、4 条发现路径、线索与提示 |
| [06 生产、甜品和订单](docs/prd/06-production-orders.md) | 产出公式、储藏、厨房、订单与访客请求、离线结算、防死锁 |
| [07 数值与经济](docs/prd/07-economy.md) | 货币来源/消耗、升级表、设施成本、离线收益、可复算路径、经济检查 |
| [08 UI 与互动表现](docs/prd/08-ui.md) | 6 个页面线框图、触摸反馈分层、动画/声音/震动、误触保护 |
| [09 商业化](docs/prd/09-monetization.md) | 12 个商品、激励广告上限、内容节奏与团队负荷、付费随机的立场 |
| [10 美术、音效与内容生产](docs/prd/10-art-audio.md) | 资产清单、模块化方案、2D 形变成本评估、质量标准 |
| [11 存档与产品技术约束](docs/prd/11-save-tech.md) | 时间/离线、崩溃恢复、StoreKit 2 恢复购买、版本更新、配置与存档字段、性能目标 |
| [12 指标、排期与验收](docs/prd/12-metrics-schedule.md) | 核心验证指标、埋点、P0/P1/P2、工作量、里程碑、41 条验收用例、风险与 3 个关键实验 |
| [13 闭合检查与修正记录](docs/prd/13-closure-check.md) | 配方—资源—解锁链检查、设计中修正的矛盾 |
| [附录 A 文案表](docs/prd/appendix-a-strings.md) | 全部玩家可见英文文案（String ID / English / 中文用途 / 位置 / 长度上限） |

## 配置与检查

`config/*.csv` 是全部初始设计值的唯一来源；PRD 中的表格与算例都由它推出。

```bash
python tools/balance_check.py --species-csv --strings-md
```

该命令只使用 Python 标准库（3.10+），会做这些事：
- 闭合检查：解锁键、配方原料、招牌可达性、星星糖与设施、文案长度、PRD 中引用的 String ID。
- 用断言复算 07 章的“喂养→生产→交付→升级→培育”路径。
- 对两类玩家（每天 5 次 / 3 次打开）做 30 天节奏模拟。
- 重新生成 `config/species.generated.csv` 和附录 A 的文案表。

任一检查失败时退出码非 0。

```
config/   flavors, desserts, signatures, levels, facilities, order_rules, params, cosmetics, strings (+ species.generated)
docs/prd/ PRD 各章
tools/    balance_check.py
```

## 状态

- 所有数值均为**初始设计值**，留存、付费和广告目标都是**实验假设**。
- 计划基线：W0–2 做触感原型，W18 软启动 1（验证留存，不含商业化），W22 软启动 2（加入商业化）。详见第 12 章。
