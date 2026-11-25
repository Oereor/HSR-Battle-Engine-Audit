# 05 · 上下文、目标和表达式参考清单

本清单保持原始类型、字段、字面值与零基 JSON Pointer。主要研究对象是共享 v2 索引所覆盖的主战斗配置及两个实时玩法。运行时含义在 [研究报告](report.md) 分级。执行下面命令使用公共索引及少量确定范围的原始 JSON。输入只读，结果写入本专题。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 05-context-expression/catalogue.py
PYTHONDONTWRITEBYTECODE=1 python3 05-context-expression/verify_bindings.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/probe_named_values.py
```

## 统计单位与覆盖规则

| 内容 | 主口径 | 规则和范围 |
| --- | ---: | --- |
| 可观察目标结构候选 | 142 类型，240,421 个位置 | 类型前缀 `Target*`/`RtTarget*` 或落于目标字段的带类型对象。独立 Task 类按类型末尾和任务槽单列。扩展到全 v2 解析域有 196 个不同候选类型 |
| 判定候选 | 252 类型，77,006 个位置 | 位于 `Predicate`、`PredicateList`、`UsableCondition`、`PreCheck` 等判定槽或已知前缀 `By*`、`RtBy*`、`VP_*`。相邻领域合计有 508 个候选类型 |
| 显式值求值器 | 15 类型，1,638 个位置 | 带 `VE_` 前缀的序列化类型，含固定常量、属性、随机和模式专有网格值 |
| 数据读取、写入与状态候选 | 93 类型，37,793 个位置 | 以动态变量、参数、快照和 Ability 属性为主要命名证据，区分写状态和读取表达式 |
| 控制流候选 | 12 类型，55,944 个位置 | 条件任务、循环、`Retarget`、模板展开和模板参数序列候选 |
| 目标相关字段形态 | 90 个字段，273,758 个位置 | 在 [原始文件清单](raw-scan-manifest.tsv) 的固定选区中逐对象遍历，保留字段原始值类型 |
| 目标串值字段 | 25,316 个位置 | 含角色或能力入口直接使用字符串指定的目标类型，作为形态单列 |
| 别名字面值 | 1,184 个值，261,121 个位置 | v2 的 `kind='alias'` 全部逐位置保留 |
| 数值容器 | 106,799 个 FixedValue，74,704 个 PostfixExpr 与 53,269 个 ReadInfo | 2,942 份由原始定义、显式角色根类型和目标字典索引出的文件，含 2,744 核心、2 公共、182 RtBattle 和 14 RtDefence |
| ContextScope | 9 个字面值，9,431 个位置 | 同一局部原始文件选区，另按所属任务或无类型容器统计 |

主口径把 `Config/ConfigAbility`、`Config/ConfigGlobalModifier`、`Config/ConfigGlobalTaskListTemplate`、`Config/ConfigCharacter`、`Config/ConfigCommonSkillPool` 作为 core，`Config/GlobalConfig`、RtBattle、RtDefence 各自成组。其他域进入 `adjacent`。一个类型可因不同位置出现不同角色，角色数与工作树全类型数分别读。类型字段形态按全 v2 索引中的同类对象统计。任何名字均按字面角色候选使用，含 `TargetTimeSlow` 等由任务槽和上下文解释的边界对象。无类型目标容器、直接字符串与混淆字段的可见形态由字段清单、原始对象和类型上下文补充。

## 结构化条目

| 表 | 行内容 |
| --- | --- |
| [typed-context-inventory.tsv](typed-context-inventory.tsv) | 每个完整类型在每种候选角色下的位置数、域、父字段、直接字段形态和样例指针。所有相邻域也在表内 |
| [typed-context-positions.tsv](typed-context-positions.tsv) | 同一类型依不同的角色、父字段、父类型和定义锚点拆分，适合检索表达式和目标类型的嵌套语法 |
| [target-dictionaries.tsv](target-dictionaries.tsv) | 公共 `AliasDict`/`OperationDict`、每文件 `GlobalTargetAlias`、RtBattle 和 RtDefence 的命名定义与来源 JSON |
| [alias-references.tsv](alias-references.tsv) | 每个 v2 别名位置、定义作用域候选、状态、词法组件和候选路径/指针 |
| [alias-counts.tsv](alias-counts.tsv)、[alias-literals.tsv](alias-literals.tsv) | 别名位置按域和匹配状态聚合，字面值保留位置样本 |
| [target-field-shapes.tsv](target-field-shapes.tsv)、[target-string-values.tsv](target-string-values.tsv) | 已观察目标字段形态和直接枚举/别名字符串 |
| [postfix-shapes.tsv](postfix-shapes.tsv)、[fixed-value-shapes.tsv](fixed-value-shapes.tsv) | 各域指令 Base64、十六进制、常量及哈希池大小、包装字段、位置与计数。固定值另分容器和内值形态 |
| [read-info-shapes.tsv](read-info-shapes.tsv) | 来源类别、TriggerKey 与 Index 的形态、字段、计数和代表节点，包括 Values/Str 变体 |
| [context-scopes.tsv](context-scopes.tsv)、[context-variable-fields.tsv](context-variable-fields.tsv) | 作用域枚举、涉及任务或无类型容器、变量与参数读写形态 |
| [binding-results.tsv](binding-results.tsv)、[evidence.jsonl](evidence.jsonl) | 七组案例的 19 条静态校核和 120 条片段，以及针对角色区分、目标管道和异常配置的定位 |
| [hash-probe-pairs.tsv](hash-probe-pairs.tsv)、[hash-probe.log](hash-probe.log) | 2,507 处具名单键候选及不同算法对照。另见 [文本哈希实验](hash-probe.md) |
| [raw-scan-manifest.tsv](raw-scan-manifest.tsv)、[catalogue.log](catalogue.log)、[verification.log](verification.log) | 局部原始读取范围、生成计数及运行记录 |

[alias-references.tsv](alias-references.tsv) 中，`exact-unique` 表示可见候选列表中命中一个完全相同的定义键，`exact-multiple` 保留全部同名定义。可见候选来自同文件、公共字典，再加所处的实时玩法字典。 `component-candidates` 按字符串中的 `.` 和已观察的 `+`、`-`、`|` 进行词法切分，各部分均有候选。 `components-unresolved` 至少有一个部分未匹配。 `outside-domain-or-file` 仅命中别的文件或模式的同名定义。 `unresolved` 表示当前规则下无解释。词法切分用于定位，语法有效性、优先级和运行时加载选择保持 Unknown。关键残差包括无法在当前活动文件直接找到 Pollux 分组局部名、公共与 RtBattle 都定义 `AllLightTeam`。

## 目标类型与操作速查

| 可复用结构 | 字段与实例 |
| --- | --- |
| `TargetAlias` | `Alias` 引用显式命名字典，也可使用复合字符串。例见 `ParamEntity.GetSummoner`；目标实例语义随调用上下文变化 |
| `TargetSequence`、`TargetConcat` | 查 `Sequence`、`Targets`。基础值可来自另一个 `TargetAlias`，后接映射、筛选、排序和截取 |
| `TargetFetchCaster`、`TargetFetchAbilityTarget`、`TargetFetchModifierOwner`、`TargetFetchCallBackModifierCaster` | 四个不同 fetch，可对照 `Caster`、`AbilityTargetEntity`、`ModifierOwnerEntity`、`CallBackModifierCaster` |
| `TargetFetchParamEntity`、`TargetFetchPassiveEntity`、`TargetFetchParamEntityList`、`TargetFetchParamEntityByIndex` | 各用不同类型引用参数和被动实体，其中显式索引形态见 `Index`；真实参数位置按事件核对 |
| `TargetQuery` | `TeamTypeMask`、`EntityTypeMask`、`AliveStateMask`、可选 `Predicate`。见 `AvatarNextTurnOwnerEntity`、`CasterServant` |
| `TargetMapEnemyTeamEntity`、`TargetMapAllTeamMember`、`TargetMapAllTeamMemberFromFirstEntity` | 队伍及成员派生，筛除项、不可选项和主人源配置须按原始字段读 |
| `TargetMapAdjoinEntity`、`TargetMapSkillTarget`、`TargetMapSkillSubTarget` | 相邻和技能目标映射，另有直接字符串 `SubTargetType="TargetAdjoinEntity"` |
| `TargetMapSummoner`、`TargetMapSummonedMinions`、`TargetFetchActualOwner` | 可组合的召唤者、创建成员和实际主人查询。召唤 ID 配置与目标派生是两种结构 |
| `TargetMapDamageAttacker`、`TargetMapDamageDefender`、`TargetFetchCurrentDamageAttacker`、`TargetFetchCurrentDamageDefender` | 攻击两侧的不同映射和 fetch。涉及事件来源或当前上下文时，优先找同一事件的消费证据 |
| `TargetFilter`、`TargetFilterAliveState`、`TargetSortByProperty`、`TargetSortByModifierValue`、`TargetSortByValueEvaluator` | 属性、状态、标签、生命状态、可插入的求值器与排序，字段含 `Predicate`、`PropertyType`、`HighestFirst`、`AliveOnly`、`Evaluator` |
| `TargetTake`、`TargetShuffle`、`TargetIndex`、`Retarget` | 数量、随机重排和索引可沿管道表达，`Retarget` 还能配置 `MaxNumber`、`ByRandom`、`TaskList`，支持目标查询后立即配置任务单元 |
| `SetDynamicEntityParam`、`TargetMapDynamicEntityParam` | 可用 `DynamicKey` 引用保存的实体，带 `ReadTargetType`、`ParamTargetType`；姬子新形态保存和读取由同文件两处键和目标联接 |

## 数值、求值和控制速查

| 类型或结构 | 关键字段与证据 |
| --- | --- |
| 固定数值 | `IsDynamic:false.FixedValue.Value` 的可观测固定包装。出现在 Ability、查询上限、条件、动画和实体创建等多个域 |
| 动态数值 | `IsDynamic:true.PostfixExpr.OpCodes/FixedValues/DynamicHashes`。以索引和哈希池联接，用报告中经样本约束的单哈希与有限算术解释 |
| 声明来源 | `DynamicValues.Floats/哈希/ReadInfo(Type,TriggerKey,Index)`；`SkillParam`、`SkillTreeParam`、`SkillRank`、`SkillEquip`、`SkillRelic` 已有参数实例。还观察到 `None`、`Activity`、`BattleEvent`、`ClientOnly`、`StageBattleEvent`、`FloorCustomData` 和一例数值 `12` |
| 显式求值器 | `VE_Const`、`VE_Group`、`VE_Value`、`VE_Predicate`、`VE_Random`，另有 Rt 网格距离、属性与技术专用输入。用 [类型参考](typed-context-inventory.tsv) 精确区分 Value 与 Weight 形态 |
| 属性、资源与层数读 | `SetDynamicValueByProperty`、`SetDynamicValueByDamageDataProperty`、`SetDynamicValueByModifierValue`，可带各自的 `ReadTargetType`、`ModifierName`、`ValueType` 和属性字段 |
| 条件、比较与逻辑 | `ByCompareDynamicValue`、`ByCompareHPRatio`、`ByCompareParamValue` 和 `ByAnd`、`ByOr`、`ByNot` 与特定实体查询结合；常见 `CompareType`、`CompareValue`、`PredicateList` |
| 控制流 | `PredicateTaskList`、`Retarget`、`LoopExecuteTaskList`、`LoopExecuteTaskListWithInterval`、`ConditionLoopExecuteTaskList`、`IncludeTaskListTemplate` 等见表。按实际位置及子任务字段判断，运行时解释保留 Unknown |
| 随机 | `ByRandomChance`、`RandomSelectInTargetList`、`SetDynamicValueByRandom`、`TargetShuffle` 分别提供判定、选择、数值写入和查询步骤，配置可含范围、整数标志、概率或截取字段 |
| 作用域 | 观察到九个值 `TargetEntity`、`ContextModifier`、`ContextCaster`、`ContextAbility`、`ContextOwner`、`ContextTaskTemplate`、`AITag`、`CallbackTemporary`、`SummonerEntity` |
| 调用实参 | `TriggerAbility`、`AddModifier`、`CreateServant`、`IncludeTaskListTemplate` 可携具名 `DynamicValues`；模板还带 `TemplateParamSequences` 与 `ParamTarget`；事件存在 `ParamIndex` 及自定义值请求 |

关键静态判断的直接原始位置可在 [证据摘录](evidence.jsonl) 与 [校验脚本](verify_bindings.py) 互查。优先使用全类型字段及位置表查族内例外。注重区别显式配置名、引用键、解析候选、运行时上下文管理。
