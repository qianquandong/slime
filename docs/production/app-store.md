# App Store 从准备到上线

官方资料核对日期：**2026-10-11**。本页是未来执行清单，当前没有Apple账号状态、签名、上传或审核通过的证据。Claude在ENV-01和STORE-01各复核一次官方要求，在发行记录写下核对日期；规则变化时更新本页再构建。

## 1. 发行路线

内部真机原型 → M1真实时间测试 → 完整免费留存版 → TestFlight外测 → 发布候选RC → App Review → 人工发布到选定地区 → 商店实际安装 → 首日/首周修复与观察。

公开首发是可独立游玩的完整免费版本，不是两周原型。原型的加速时间、实验开关、未完成界面和占位内容不作为商店成品提交。Apple要求未完成的演示/测试版本通过TestFlight测试，商店信息与实际功能保持一致。[App Review Guidelines，2.1～2.3](https://developer.apple.com/app-store/review/guidelines/)

商业化不阻塞首个免费版本。要加入IAP/广告时走MON-01及独立隐私/购买测试，重新送审；不能在首发包放入尚未说明的隐藏商店。

## 2. 账号与工程准备

| 项目 | 执行者与操作 | 证据 / 完成标准 |
|---|---|---|
| Apple开发者身份 | 负责人选择个人/组织并完成Developer Program、身份验证和所需合同 | 仅记可用状态与负责人，不上传身份证、密码、2FA或证书私钥 |
| 团队权限 | 负责人提供所需App Store Connect角色及构建环境授权 | Claude能完成被授权的构建/上传；合同、身份和最终声明由有权限的真人处理 |
| 应用身份 | 确认工作名可用、Bundle ID、SKU、主语言English、应用记录 | Unity、Xcode、Provisioning与App Store Connect一致；名称需最终确认 |
| 构建环境 | Claude锁Unity/Xcode/macOS/包版本；设备开发安装与发行签名分别验证 | 能从干净checkout导出Xcode工程、Archive、Validate；保存命令/日志 |
| 版本与符号 | 设marketing version及每次上传递增build号，保存Archive/dSYM和构建清单 | 崩溃可符号化；commit与App Store Connect build对应 |
| 分发范围 | 负责人确定首发国家/地区、设备平台与免费价格 | 延续PRD建议先评估菲律宾/马来西亚；最终选择记入发行记录，不默认全世界开放 |

用于TestFlight/App Store分发需加入Apple Developer Program。Unity可在Windows编辑，但本地iOS最终编译与签名依赖macOS/Xcode；若用构建服务，要先配置授权环境与预算。[Apple分发说明](https://developer.apple.com/documentation/Xcode/distributing-your-app-for-beta-testing-and-releases)、[Unity iOS环境](https://docs.unity.com/en-us/engine/6000.3/manual/platform-specific/iphone/getting-started/ios-environment-setup)

截至核对日，Apple要求上传App Store Connect的应用使用 **Xcode 26或更高及iOS 26 SDK或更高**构建（2026-04-28起）；2026-09-09起iOS部署目标至少iOS 13。本项目部署目标仍为iOS 16，编译SDK与最低运行版本是两回事。发送构建前再次查官网，不仅检查本地Unity能否编译。[Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)

## 3. 隐私、权限、地区与审核材料

Claude先交一份实际技术清单：所有Unity包/原生插件/SDK及版本、初始化时机、联网域名、收集字段、用途、是否关联身份、是否跨应用追踪、存储/删除方式、系统权限、Required Reason API使用。Codex据此整理政策和商店回答，负责人核对真实业务身份后提交。

| 检查 | 执行要求 | 阻断条件 |
|---|---|---|
| 隐私政策与支持 | 真实可公开访问的HTTPS页面、有效联系渠道；App内设置能打开 | 空白页面、占位邮箱、描述与实际SDK不符 |
| App Privacy | 按应用及第三方代码的实际收集填写；无账号不等于无收集 | 未审查分析/崩溃SDK就选择“No data collected” |
| Privacy Manifest | 检查应用与嵌入SDK的声明、适用的Required Reason API理由，以及Apple所列SDK要求；检查最终Archive | 缺失/不匹配声明或校验错误未处理 |
| ATT | 只有存在Apple定义的追踪才按规则请求；无追踪的原型/免费版不因“第2次打开”自动弹窗 | SDK在授权前追踪、拒绝后仍追踪，或把ATT同意作为游戏条件 |
| 年龄与类别 | 负责人按实际内容/能力回答当前年龄问卷；不猜固定4+；本项目不选Kids Category | 文案宣称儿童适用而内容/数据处理未对应；新增广告/UGC后未重评 |
| 加密出口合规 | Claude列出系统HTTPS/加密库及用途，负责人据实际实现完成问卷与所需材料 | 直接复制“无加密”或随意设豁免字段 |
| 地区义务 | 只选择已确认可发行的地区；如扩EU/中国大陆等，另查App Store Connect当前要求并补齐 | 没有地区材料却全区勾选；不要把年龄门等同于所有地区合规 |
| 无障碍声明 | 只填写已实际验证的能力，并给出设备证据 | 未测就宣称支持VoiceOver/Larger Text等 |

隐私政策URL和数据处理回答是上架材料，需覆盖第三方SDK；应随实际行为更新。[App Privacy说明](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/) 隐私清单是技术声明，不能代替商店隐私回答。[Privacy Manifest文档](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files) ATT依据实际追踪用途决定。[User Privacy and Data Use](https://developer.apple.com/app-store/user-privacy-and-data-use/)

年龄与出口合规分别按当前官方流程填写：[年龄分级](https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating/)、[出口合规](https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance/)。新增地区、收费、广告或数据收集都要复核，而不是沿用旧问卷截图。

## 4. TestFlight执行步骤

1. Claude生成已通过内部QA的签名Archive，保存commit、构建版本、配置/资产哈希与dSYM；运行Xcode Validate并处理错误，上传App Store Connect。
2. 等待Apple处理完成，核对Bundle ID、version/build、加密问卷和构建状态；上传成功不等于可测试。[上传构建](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds)
3. 先让有适当权限的内部测试者安装，验证新档、更新、核心流程、崩溃反馈；不能把所有玩家加入团队来绕开外部审核。
4. 填写Beta描述、What to Test、反馈邮箱和审核联系人；创建外部测试组，提交所需Beta审核，通过后邀请已招募目标用户。首次提交的外部测试build需完整审核，同版本后续build是否免审由Apple决定。[邀请外部测试者](https://developer.apple.com/help/app-store-connect/test-a-beta-version/invite-external-testers/)
5. 按 [测试方案](testing.md)收数据、排缺陷和冻结RC。构建最多测试90天，记录到期日并安排替换；不能让研究中途因包过期丢失观察窗口。[TestFlight概览](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/)

不保证Beta审核时间。招募和构建分发需遵守TestFlight当前规则；Beta可用、App Review通过和商店上线是不同状态。研究中的原始录像与联系方式不进入公开仓库。

## 5. 商店素材与字段包

Codex负责文案、图标设计与截图排版；Claude提供同一RC的实际游戏截图、构建图标与版本信息；负责人提供身份/联系/地区等真实信息。执行STORE-01时创建 `docs/production/store-listing.md`，逐字段记录最终值、来源和确认状态。

| 字段/素材 | 初始准备方向 | 完成标准 |
|---|---|---|
| 名称 | Slime Sweets Farm（工作名） | 负责人完成名称确认；全包与商店一致 |
| 副标题/描述/关键词 | 围绕触摸、喂养、可推理培育和甜品牧场；不写竞品名或未实现功能 | 英文人工校对，符合App Store Connect当前字段长度；链接无占位 |
| 图标 | Codex提供1024×1024设计母版与源；Claude按当前Xcode资产目录/Icon Composer支持方式集成 | 真机主屏及商店预览清晰；按实际图标流程验证尺寸/透明度，不直接上传角色透明精灵图 |
| 截图6张 | ①触摸宠物 ②喂食显色 ③Body/Swirl组合 ④Treat招牌 ⑤甜品订单 ⑥个人牧场/收藏 | 每张对应可复现RC状态，标题与功能相符，无遮挡安全区，无调试/真实个人数据 |
| 支持/隐私/版权 | 负责人真实可访问的信息 | 手机浏览器打开测试并记录；不要虚构法人或客服承诺 |
| 分类/年龄/地区/价格 | 实际游戏分类、问卷结果、确认地区、免费首发 | 负责人核对；付费/IAP另行需要相应协议、税务/银行资料 |
| 审核说明 | 无账号的实际进入方式、核心路径、等待时长、特殊配置、联系方式 | 审核员可重复完整流程；如未来需账号，提供有效审核访问，不泄露私人账号 |

图标制作按 [Apple图标说明](https://developer.apple.com/help/app-store-connect/manage-app-information/add-an-app-icon/) 验证。截图尺寸/必需设备组可能变化，交付前以 [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/) 和应用实际设备支持为准，不能固定照抄旧“6.9/6.5英寸各一套”。商店截图应展示应用实际使用；可以做标题排版，但不能用生成图伪造玩法。[审核指南2.3.3](https://developer.apple.com/app-store/review/guidelines/)

审核说明草稿（Claude用实际RC核对后才能提交）：

```text
This is a single-player pet and dessert-farm game. [Confirm actual network needs.]
Account requirement: [Confirm: no account / provide review access if changed.]
Core path: new game -> feed a slime -> choose Body and Swirl -> start breeding
-> hatch -> use ingredients to make a dessert and complete an order.
First hatch time: [Measured RC value, not prototype override.]
In-app purchases / ads: [Confirm absent in this release.]
Permissions and online services: [List only what this build actually uses.]
Review contact: [Owner-provided contact.]
```

## 6. RC到发布的逐项检查

- [ ] STORE-01的RC与QA报告commit/build一致；无S0/S1，受影响经济/存档回归通过。
- [ ] 冷启动、离线、拒绝权限、干净安装、带进度更新、最小档性能均有实际结果。
- [ ] 正式资产来源/授权记录完整；图标/截图/英文文案无占位。
- [ ] 隐私清单、数据回答、年龄/出口/地区材料匹配该Archive。
- [ ] 测试夹具、测试URL、研究日志导出入口、免费资源按钮已按发行方案剥离；诊断日志不包含个人数据。
- [ ] 支持网址、隐私网址和联系渠道真实可用；定价/可用地区已确认。
- [ ] 选择已处理好的build，补齐审核信息，负责人确认材料后提交App Review；记录提交时间与Apple状态。
- [ ] 选择人工发布，审核通过后再核对地区/价格/build/已知问题，由负责人完成发布决定与操作。Apple也提供自动/定时等选项，本项目首发选人工以便完成最后检查。[版本发布选项](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/select-an-app-store-version-release-option/)
- [ ] 从实际App Store页面干净安装并体验教学、培育、重启恢复；保存商店链接、时间、版本与检查结果后才能标记LIVE。

若审核拒绝：保存Apple原文、定位对应规则/页面、Claude修代码或Codex修材料、验证实际build，再按实际情况重新提交；不只把版本号加一。PRD/商店承诺与实际不符时同时修正。

## 7. 上线后与故障处理

负责人安排首日、24小时、72小时、第7天人工检查，Codex分析反馈，Claude定位修复；此文档不代表已设置自动监控。记录崩溃/会话样本、卡教程、丢档、支持反馈、D1与完整D7队列；D30等满窗口后再报告。

S0/S1出现时保留日志和受影响build，暂停扩量；按影响考虑暂停后续版本分阶段发布或停止新下载，由负责人执行商店动作。Claude做最小修复、保留存档兼容、回归、提高build号并重新审核；商店版本无法像服务端一样即时让所有用户降级，停止下载也不会卸载已安装的包。远程配置只能调已允许且经验证的参数，不能冒充客户端代码回滚。

Apple的7天分阶段发布用于**版本更新的自动更新人群**，不是首次发布按人数限流；用户仍可主动下载。首次软启动通过选定地区和招募控制规模；后续更新才按风险选择分阶段发布。[分阶段更新说明](https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases/)

首发稳定且留存证据支持后，重新制定P0-M：购买成功/取消/失败/待批准/中断恢复/退款/永久商品恢复、广告无填充/断网/奖励重复回调、年龄规则、ATT及隐私更新都需实际测试。不得把“上架成功”自动视为商业化实验通过。
