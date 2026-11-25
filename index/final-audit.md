# 验收记录

本记录按 AUDIT_SPEC §17–19 核对现行文件和执行结果。研究内容、导航和源数据完整性均有可回读证据。现有 Git 仓库的目录条件已由用户明确豁免。

## 专题抽查与可执行证据

| 专题 | 实际查核 | 证据 | 状态 |
| --- | --- | --- | --- |
| 00 | 核对版本、范围、排除项和重复键政策。独立遍历复算类型、回读 128 个索引位置、双向比较两个索引的文件及类型表 | [普查](../00-data-survey/report.md) · [最终索引校验](validation-v2-final.log) · [版本比较](index-version-comparison.tsv) | 通过 |
| 01 | 复核角色、敌方、事件与忆灵的 ID 联接、技能与 Ability 一对多、同名装备和候选作用域。复跑引用拓扑与成环统计 | [定义与图](../01-entity-ability/inventory.md) · [校验](../01-entity-ability/verification.txt) | 通过 |
| 02 | 比对全量类型计数、任务槽和实际源对象，复核普通命中、插入追击、复合投射物、装备与条件。保留相邻和域外范围 | [目录](../02-atomic-operations/inventory.md) · [校验](../02-atomic-operations/validation.log) | 通过 |
| 03 | 重跑指针证据，抽查作用域、旗标限制、声明式子状态、生命周期变化与事件。并列未知时序及未解析符号 | [Modifier 资料](../03-modifier/inventory.md) · [校验](../03-modifier/validation.log) | 通过 |
| 04 | 复查选择器、字段、动画导入、显式数字桥及局部策略，核对 26 次动画等待与 181 个数字令牌引用 | [事件目录](../04-callback-trigger/inventory.md) · [校验](../04-callback-trigger/validation.log) | 通过 |
| 05 | 校验目标字典联接和 122 个证据片段及 20 项静态值。星魂以角色 ID 复查，修正停云误联，保留未覆盖指令 | [上下文](../05-context-expression/inventory.md) · [校验](../05-context-expression/verification.log) · [哈希实验](../05-context-expression/hash-probe.log) | 通过 |
| 06 | 核对资源字段、支付开关、条件和所选插入请求，复跑 231 个类型汇总、Archer 星魂双参数及事件实体样本 | [调度](../06-resource-scheduling/inventory.md) · [校验](../06-resource-scheduling/validation.log) | 通过 |
| 07 | 核对 15 篇独立案例，覆盖规范要求的 9 类机制。逐案检查证据路径、图、后继任务、局部约束、未解析处与未知时序 | [案例导航](../07-case-studies/inventory.md) · [辅助组](../07-case-studies/support-validation.log) · [资源组](../07-case-studies/resource-case-validation.log) · [跨实体组](../07-case-studies/cross-entity-validation.log) · [其他三例](../07-case-studies/selected-case-validation.log) | 通过 |
| 08 | 检查配置概念图、对照矩阵、运行时备选、复用边界与 17 节综合报告。复算跨域、目标、嵌套等存在性指标 | [抽象报告](../08-engine-reconstruction/report.md) · [复算](../08-engine-reconstruction/metrics.log) · [综合](../SUMMARY.md) | 通过 |

## 交付、完整性与目录状态

- [README](../README.md) 直接导航 00–08、纲领、综合与索引。 [命题](../CLAIMS.md) 包含 52 条命题及两处关联修订。 [文档校验](deliverables-validation.log) 检查必备文件、各案例入口、命题 ID、站内路径和独立的完整源指针。局部相对指针由各篇脚本和人工样本回读补充。
- [最终源数据完整性日志](source-integrity-final.log) 确认逐个重算 143,715 份源普通文件的大小与 SHA-256，观测到 0 修改、0 新增、0 缺失。源 Git revision 和只读 porcelain 快照与初始一致。源文件指纹范围排除 Git 元数据、Git 对象和符号链接。结论限定在该范围；其他相邻项目未作为研究输入，也未做全盘取证。
- 本任务的写入由审计目录内的报告、数据库、脚本和工作文件构成。处理原始 dump 用静态解析与只读 Git 查询，未执行数据内容，未申请扩大写权限。根目录启动及 [中途检查](source-integrity-mid.log) 均无 `.git`，最终复检中出现实际 Git 仓库。根目录 `.git` 的创建时间晚于上一轮研究的中途校验，在本轮恢复前已存在。现行权限对它只读，研究过程没有对其执行初始化、迁移、删除或其他写操作。
- **用户授权的验收豁免。** 用户明确选择保留现有仓库并豁免 §19 的该项目录条件。默认检查继续验证有无 Git 元数据，最终复验仅通过显式的 `--allow-existing-audit-git` 应用豁免。源数据完整性和其他验收项的判据保持原口径。见 [豁免前核验](source-integrity-pre-waiver.log) · [最终复验](source-integrity-final.log)。

**验收结果**。00–08、综合报告、52 项命题、15 篇案例、文档导航、源数据完整性与原范围内其他检查均通过。审计目录的 Git 条件按用户明确授权豁免。
