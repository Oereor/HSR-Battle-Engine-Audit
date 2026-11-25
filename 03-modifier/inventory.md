# 03 · Modifier 参考清单

此清单以 [核心与 Rt 作用域表](definitions.tsv) 为索引。每个定义按文件和 JSON Pointer 定位，另记录父 Ability、定义键、直接字段和回调选择器。核心来自公共索引 v1 的 `Config/ConfigAbility/` 与 `Config/ConfigGlobalModifier/`。Rt 补集读取公共索引所列 `Config/Activity/RtBattle/` 和 `Config/Activity/RtDefence/` 的已解析文件，并提取三个相同位置的字典。补集为 439 个定义节点，与公共索引 v2 扩展所得 RtBattle 433 和 RtDefence 6 一致。探索构造及结论见 [研究报告](report.md)。

| 范围 | Ability 局部 | 资源内 `GlobalModifiers` | 公共 `ModifierMap` | 合计 |
| --- | ---: | ---: | ---: | ---: |
| 核心 | 15,127 | 7,121 | 481 | 22,729 |
| RtBattle 与 RtDefence | 154 | 241 | 44 | 439 |
| 两组合计 | 15,281 | 7,362 | 525 | 23,168 |

核心定义有 21,547 个不同名称。核心有 26 种直接字段，Rt 有 11 种直接字段。回调选择器核心 216 种、35,295 项，Rt 38 种、601 项。各组选择器可能有同名。

## 定义字段

| 配置目的 | 实际出现的直接字段 |
| --- | --- |
| 时序与持续 | `LifeTime`、`LifeStepMoment`、`PerformTime`、`WorkingTurn`、`Priority` |
| 层数与重施 | `Count`、`Stacking`、`MaxLayer`、`LayerAddWhenStack` |
| 行为、目标与快照 | `BehaviorFlagList`、`TargetSelectRestrict`、`TargetSelectRestrictType`、`UseSnapshotEntity`、`ApplyBehaviorFlagBindEffects` |
| 类型化参数及任务复用 | `DynamicValues`、`DynamicStrings`、`TaskListTemplate` |
| 回调及监听 | `_CallbackList`、`OnDynamicValueChange`、`OnAbilityPropertyChange`、`OnElationPointChange` |
| 显示、预览与附加对象 | `UIConfig`、`AdditionConfig`、`ModifierAffectedPreshowConfig`、`ModifierStancePreshowConfig`、`ModifierCreateEntityPreshowConfig` |

上述是核心观测到的 26 个字段。逐字段的 JSON 形态、语料计数及原始位置见 [definition-fields.tsv](definition-fields.tsv)。[policy-values.tsv](policy-values.tsv) 保留主要策略原值及出现次数，数组 `BehaviorFlagList` 按元素统计，数字旗标照录。核心组的 571 个 `UIConfig` 中 10 个是空对象，UI 可见性需结合状态表和回调任务。

## 操作入口及状态查询

| 类别 | 代表入口 | 确定性 |
| --- | --- | --- |
| 指名、按旗标和当前上下文变更成员 | `AddModifier`、`RemoveModifier`、`RemoveModifierByBehaviorFlag`、`RemoveSelfModifier`、`DispelStatus` | Observed。任务节点、原始参数和引用方式可查 |
| 状态值、动态参数和属性 | `SetModifierValue`、`SetModifierDynamicValue`、`SetDynamicValueByModifierValue`、`StackProperty` | Observed。分别存在值字段、动态键、读目标或写属性 |
| 条件、搜索和上下文重绑定 | `ByIsContainModifier`、`ByCompareModifierValue`、`Remodifier`、`InfectModifier` | Observed 有结构。筛选、传播和重绑定的具体执行细节有 Inferred 或 Unknown 项 |
| 回调请求 | `TriggerModifierCustomEvent`、`TriggerModifierEnterBattle`、`TriggerModifierLeaveBattle`、`AbortModifierPhasePerform` | Observed 有独立类型。分发算法 Unknown |
| Rt 变体 | `AGPMEJILJBO` 和其他含 `IFNAGLOMHBK` 的类型，另有 `RtStackProperty` | 字面字段与名称链接 Observed 或 Derived；不透明操作的行为多为 Unknown |

入口与相邻类型全集按显式核对类型、短类型名包含 `Modifier|DispelStatus`，以及 Rt 中具特定符号字段的类型作机械筛选，包含查询、AI、表现及玩法类型候选。相关入口内嵌的任意类型可另外用 `occurrences.anchor_kind='modifier'` 搜索，领域专属不透明节点继续保留 Unknown。完整 `$type`、计数和位置见 [entry-types.tsv](entry-types.tsv)，全字段统计见 [entry-fields.tsv](entry-fields.tsv)。表中 `full_corpus_nodes` 统计整个已解析语料中的类型节点，一些类型同样可出现在定义容器之外。

`AddModifier` 有 33,537 个节点，`RemoveModifier` 有 9,674 个，`RemoveSelfModifier` 有 2,248 个，`RemoveModifierByBehaviorFlag` 有 176 个，`DispelStatus` 有 865 个。命名节点数要和符号引用行数分开。动态名、执行上下文、自引用或旗标选择可能不产生静态符号，一个添加节点也可同时有 `ReferenceModifierName` 和 `ModifierName`。

## 引用与事件文件

| 文件 | 行语义及读取方式 |
| --- | --- |
| [references.tsv](references.tsv) | 70,594 个 v1 宽口径 Modifier 字面引用，`status` 表示同文件或词法可识别、跨文件候选、多候选及未解析。保留最靠近的根、父类型和定义候选定位 |
| [unresolved-or-ambiguous.tsv](unresolved-or-ambiguous.tsv) | 同一表的 7,485 个未解析或多候选。其内含表现、冒险或运行时上下文的字段 |
| [graph.tsv](graph.tsv) | 57,979 个源位置→候选配置的边，`kind` 为目标类别，`anchor_kind` 为源类别。条件、任务和设置操作通过 `parent_type` 区分 |
| [feedback-examples.tsv](feedback-examples.tsv) | 核心同文件已识别的 Add/Remove 自边和两向边，按端点和操作去重。只证明静态结构 |
| [addition-candidates.tsv](addition-candidates.tsv) | `AdditionConfig.SubModifierList[].Name` 的单独边集，含原始目标选择、入参与条件，按定义范围给出候选 |
| [rt-symbol-candidates.tsv](rt-symbol-candidates.tsv) | 1,521 个 `IFNAGLOMHBK` 字面值，作用域候选 876、其他唯一名 632、未解析 13。字段语义仅对有实样支撑的节点作标注 |
| [callback-selectors.tsv](callback-selectors.tsv) | 两组 Modifier 内直接 `_CallbackList[].Event` 的选择器、计数和第一个来源，范围监听等其他形式见 [阶段 04](../04-callback-trigger/report.md) |
| [evidence.jsonl](evidence.jsonl) | 报告使用的源相对路径、JSON Pointer 与原始片段，编号 M01–M54 |
| [validation.log](validation.log) | 实际复算和证据节点解析输出 |

冒险状态采用 `AddAdventureModifier` 等不同入口。公共 v2 中对应 `ConfigAdventureAbility` 与 `ConfigAdventureModifier` 的发现节点分别为 229 与 2,882。DiceCombat 的 `Modifiers[]` 及 ID、TrainParty、ChimeraDuel 等独立小游戏的近名类型保留在类型清单或样本证据中，生命周期统计仅用于上述两组战斗结构。

## 复算

```sh
PYTHONDONTWRITEBYTECODE=1 python3 03-modifier/catalog.py > 03-modifier/validation.log
PYTHONDONTWRITEBYTECODE=1 python3 03-modifier/evidence.py >> 03-modifier/validation.log
python3 tools/query.py definition M_Asta_Passive
python3 tools/query.py reference MAvatar_Asta_00_Passive_Charge
```
