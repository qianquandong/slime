# 交接与证据模板

执行时复制相应模板到任务PR或 `docs/production/evidence/` 下，命名包含日期、任务ID和build。这里的空白项都不是已完成结果。公开仓库仅放脱敏结果；原始用户日志、录像、联系方式和签名凭据留在受限位置。

## 1. 单任务交接

```text
任务ID / 标题 / 主责 / 状态：
依赖 / 对应PRD章节及验收ID：
基准commit / 当前commit / PR：
本次改变的行为：
输出文件与可安装构建位置：
运行步骤与环境版本：
自动化命令 / 退出码 / 报告位置：
实际设备 / OS / build / 测试执行者：
PASS项 / FAIL项 / NOT RUN项及原因：
美术版本 / 占位项 / 所需Codex交付（尺寸、锚点、状态）：
已知缺陷 / 风险 / 未完成范围：
需要的具体决定（含可审查方案）：
下一任务 / 执行者：
```

## 2. 真机用例记录

```text
用例ID / 日期 / 执行者：
设备型号 / OS / 电池与热状态 / 开关条件：
App version(build) / commit / Unity / Xcode：
profile / config hash / asset manifest version：
前置状态与准备方式：
操作步骤：
预期结果：
实际结果与测量值（单位、样本量、误差）：
结论：PASS / FAIL / NOT RUN / BLOCKED
日志/截图/录像位置与时间点（脱敏）：
缺陷ID / 修复commit / 复测日期与结论：
```

## 3. M0逐人数据列

```text
participant_id, build, profile_hash, variant_order, signature_order,
E1_prefer, A_active_ms, B_active_ms,
first_hatch_seconds, ftue_help, ftue_exit,
autonomous_second_start, autonomous_third_start, E2b_blocker,
prediction_1_correct, prediction_2_correct, prediction_help,
signature_solved_unassisted, attempts, hint_used, explanation_correct,
favorite_reason_category, next_day_remembered,
crash, technical_failure, intervention_notes, evidence_id
```

汇总时另写每项分子/分母、退出/缺失、成功者中位数与未成功人数；active_ms按PRD14区间并集算法计算。记录参与同意与证据保留期限的受限位置，不把同意书或个人信息嵌入公开CSV。

## 4. 阶段决定

```text
阶段 / 冻结版本 / 日期 / 负责人：
原定范围与实际差异：
原定门槛（引用）及逐项结果：
样本/观察窗口/缺失/主持人干预/版本变更：
关键证据与反例：
未解决S0/S1/S2：
决定：继续 / 定向迭代 / 暂停扩展 / 验证待完成
理由与不支持的结论：
下一阶段范围 / 不做项 / 分工 / 估工 / 外部等待 / 缓冲：
需补的美术/设备/账号/招募输入：
决策人及实际确认时间：
```

## 5. 发行记录

```text
App / Bundle ID / marketing version / build / commit：
Unity / macOS / Xcode / iOS SDK / 最低iOS：
配置hash / 资产清单hash / Archive与dSYM受限存放位置：
QA报告 / 性能报告 / 原始安装与升级结果：
已知问题及接受人：
隐私/SDK清单 / 年龄/出口/地区材料核对人：
商店字段/截图版本 / 支持与隐私URL检查：
官方要求最后核对日期：
TestFlight处理/审核状态和时间：
App Review提交/反馈/修正/批准时间：
发布方式 / 确认地区与价格 / 负责人发行决定：
App Store链接 / 实际可下载时间 / 商店安装验证：
首日/24h/72h/第7天负责人和结果：
严重问题处置与修复build：
```

## 6. 需求/技术决定（ADR）

```text
决定ID / 日期 / 状态（提议或已确定）：
问题与可复现证据：
候选方案、成本、影响：
采用方案与理由：
需要同步的PRD/配置/代码/资产/测试：
受影响阶段与新增估工：
决定人 / 生效commit：
```
