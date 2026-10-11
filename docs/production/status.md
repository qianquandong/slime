# 执行状态与下一步

更新：2026-10-11。这是初始交接状态；计划文档完成不等于游戏完成。执行者每次交接更新此页，详细证据使用 [模板](templates.md)。

## 已有事实

- PRD v0.2、完整CSV配置、配置/经济回放工具与20项Python经济回归已存在。
- 代码实现前的设计基线在PR #1 / `codex/prd-two-week-prototype`；是否合并需Claude开工时检查。
- 本目录与CLAUDE.md提供全流程、角色分工、任务、测试和发布清单。
- 本次文档改动后重跑配置/经济检查及20项Python回归均通过；这不是Unity或真机测试结果。
- 无Unity工程，无已交付游戏资产，无iPhone实测/玩家研究，无TestFlight或App Store上线记录。

## 执行看板

| 任务 | 状态 | 主责 | 当前缺口 / 下一动作 |
|---|---|---|---|
| ENV-01 | READY（可开始调查） | Claude + 负责人 | 核实Unity/Mac/Xcode/实体机/签名；输出environment记录，安装空工程 |
| ART-01 | PLANNED | Codex | 制作代表样片、确定导入契约；需Claude给实际渲染预览反馈 |
| DEV-01～02 | PLANNED | Claude | 依赖ENV；创建最小工程与可触摸样片 |
| ART-02 / DEV-03～07 | PLANNED | Codex / Claude | 依赖首个样片；实现原型核心闭环、资产与记录 |
| DEV-08 / M0研究 | PLANNED | Claude / 负责人 / Codex | 12人预约、测试包与ART-02验收均未具备 |
| RET-01～03 / M1 | PLANNED，未开启 | Claude / Codex / 负责人 | 等M0证据和继续决定 |
| SCOPE-01 / FULL-01～06 / ART-03 | PLANNED，未开启 | Codex / Claude | 等M1与正式范围冻结 |
| QA-01 / BETA-01 | PLANNED，未开启 | Claude + 负责人 | 等完整免费版、设备覆盖与账号准备 |
| ART-04 / STORE-01 / RELEASE-01 | PLANNED，未开启 | Codex / Claude / 负责人 | 等RC、商店材料、审核与发布决定 |
| LIVE-01 / MON-01 | PLANNED，未开启 | 各角色 | 等真实上线与后续产品证据 |

## 待收集信息

以下“未知”不是已失败，也不能直接标通过。负责人在开始相关阶段前提供，Claude可以先做不依赖这些输入的工作。

| 输入 | 当前状态 | 需要时点 |
|---|---|---|
| Unity精确版本、Mac/Xcode、构建途径 | 未核实 | ENV-01 |
| Apple开发者身份/签名/Bundle ID | 未核实 | ENV-01设备安装；TestFlight前完整确认 |
| 两台实体iPhone型号/OS | 未核实 | M0 D1前 |
| 12名成年英语目标测试者与主持人 | 未预约 | M0 D1前预约，D8～10到场 |
| 商店名称/真实客服邮箱/政策网址 | 未确认 | STORE-01前 |
| 首发地区、素材授权/采购预算 | 未确认 | 对应采购前、STORE-01前 |

## 现在交给Claude的指令

> 阅读根目录CLAUDE.md及docs/production/。先确认计划分支是否已合并；未合并则从codex/prd-two-week-prototype创建任务分支。先做ENV-01与DEV-01，跑已有Python检查，建立可复现的Unity工程和真机安装路径，再做DEV-02触摸样片。具体代码、Shader、导入与构建由你实现；产品/数值与美术交Codex。每个任务交付PR、运行步骤和真实测试证据；没有真机或账号时明确列缺口并继续独立工程工作。不要跳过M0门槛直接做完整P0或商业化。
