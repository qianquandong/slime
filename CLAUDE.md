# Claude 开发入口 · Slime Sweets Farm

你负责本项目的具体代码实现、自动化检查、构建和缺陷修复。Codex 负责产品计划、数值规则、美术方向与美术交付审核；项目负责人负责设备、账号、测试招募和发行决定。先读本文件，再按 [开发总计划](docs/production/README.md) 执行。

## 当前状态与工作边界

- 仓库现在只有 PRD、配置和 Python 检查工具；**尚无 Unity 客户端、已交付游戏美术、真机测试结果或 App Store 构建**。查看 [状态表](docs/production/status.md)，不要把计划写成完成记录。
- 立即可执行范围是 ENV-01、ART-01 技术接入准备和 DEV-01～DEV-08 两周原型。原型范围以 [PRD 第14章](docs/prd/14-two-week-prototype.md) 为准。
- 后续 M1～M5 是有进入条件的计划。上一阶段通过并记录负责人决定后才继续，不直接把完整 PRD 全部做完。
- 不擅自改玩法、经济、测试人数/阈值或增加广告、IAP、账号、云服务。实现遇到矛盾时，给出可复现例子、最小方案和影响，交 Codex 更新规格；可以继续独立任务。
- 不因缺少正式美术停止工程：使用可替换占位资产，记录缺件；涉及 E1 手感与 E2c 剪影的正式测试必须等待相应美术达到验收标准。

## 开始顺序

1. 检查当前分支、未提交改动和 PR 状态。此计划最初位于 `codex/prd-two-week-prototype` / PR #1；若已合并则从最新 `main` 开工，否则从该计划分支创建任务分支并注明依赖。不要覆盖他人工作，也不要自动合并 PR。
2. 阅读 [分工与阶段](docs/production/README.md)、[开发任务](docs/production/development.md)、[美术交接](docs/production/art.md)、[实际测试](docs/production/testing.md)、[上架流程](docs/production/app-store.md)。按当前任务再读 PRD 03～08、11、14；数值从 `config/` 读取。
3. 先运行已有检查，记录结果与提交 SHA：

   ```bash
   python tools/balance_check.py --species-csv --strings-md
   python -m unittest discover -s tools -p "test_*.py"
   git diff --check
   ```

4. 做 ENV-01：记录 Unity 精确版本、包锁、Mac/Xcode、iPhone 与签名可用性。默认 Unity 6 LTS + URP 2D、C#、竖屏 iPhone，最低 iOS 16 / A12。版本需验证实际兼容后锁定，不写泛泛的“最新版”。Windows 可以做编辑器开发；签名 iOS 构建需要可用的 macOS/Xcode 构建环境。
5. 做 DEV-01，先交付能在真机启动的最小工程，再实现触摸。每次只推进一个明确任务单元，附运行方法、验证结果和下一项任务。

## 工程约束

- Unity 工程放在 `client/SlimeSweetsFarm/`。提交 Assets、Packages、ProjectSettings 及 `.meta`；不提交 Library、Temp、Obj、构建缓存、证书或密钥。工程路径是计划，首次创建前确认不存在冲突。
- 正式数值来源为根目录 `config/*.csv`。导入器生成运行时配置；生成结果不另设一套手写价格。原型使用独立 profile，记录覆盖项，不修改正式等级解锁表来方便演示。
- 把经济/培育/时间计算与 Unity 展示分开，允许注入时钟和随机种子。Python 检查工具是规格参照，不是完整生产实现，也不是客户端测试的替代品。
- 必须保持：教学基线90金币；免费小屋30位；整份消化与容量预留；只退未开吃食物实付金额；亲本到 Hatch/Cancel 才解锁；访客检查实际拥有；失败事务不产生部分扣费。细节读对应 PRD，不只照此摘要实现。
- UI 文案使用 String ID，英文来自 `config/strings.csv`。缺少文案先提交新增提案，禁止把测试调试文字留到正式包。
- 原型的 A/B、时间压缩、夹具入口与生产包隔离。发行构建不含可触发的调试菜单、免费资源按钮、测试清档入口或原型计时覆盖。
- 存档、事件日志、配置与构建均带版本。实际用户日志不能提交到公开 GitHub；仓库只保留脱敏汇总、人工确认过的截图和受限证据位置说明。

## 完成一项任务的标准

使用 [记录模板](docs/production/templates.md) 更新任务状态并提交 PR：写清实现行为、依赖、运行命令、机器/设备、测试结果、失败项、美术占位项、证据和未完成项。未执行的真机步骤写 `NOT RUN`，缺依赖写 `BLOCKED`；编译成功不等于已测试，截图不等于交互验收。

对于无法在当前环境完成的签名、真机、账户动作：先完成可做的代码、测试、构建脚本与操作步骤，准确列出剩余动作和执行者。不要伪造日志、用户结果或 App Store 状态。

每次交接给 Codex 时提供：任务 ID / commit / 可运行构建位置 / 缺陷 / 待决问题 / 美术需求（尺寸、锚点、状态、截图）/ 下一步。不要声称已经自动通知另一名助手；负责人会转交，或通过明确授权的协作渠道传递。
