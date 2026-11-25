# 05 · 执行上下文、目标选择与数值表达式

## 证据与清点口径

本专题复用 v2 公共索引。全域类型候选从类型实际位置、结构接口和可读标识筛选，相邻模式单列。未索引的无类型对象由索引选出的 2,942 份定义、角色配置和目标字典局部提取，定位和范围可重建。观察到 142 种主口径目标结构候选、252 种判定候选、15 种显式 `VE_` 求值类型、93 种变量或数据操作候选和 12 种控制流候选。角色可见技能、/AbilityList 各阶段、Modifier 回调及 Task 结构请与前一批报告对读。[机械口径和表](inventory.md) · [操作边界](../02-atomic-operations/report.md)

下文的 **Observed** 是直接字段、枚举、对象和原始数值。**Derived** 是具名路径、作用域候选或值池绑定的静态结果。**Inferred** 是通过多处结构及本地辅助文本约束的语义。**Unknown** 保留状态、默认值和运行时执行的问题。证据 ID 可在 [evidence.jsonl](evidence.jsonl) 定位源相对路径、JSON Pointer 与原始摘录。[独立校核日志](verification.log)

## 目标字典补充与组合

**Observed**。字典由两层配置提供。公共 `Config/GlobalConfig/TargetAliasConfig.json#/AliasDict` 有 196 条命名条目，`Config/GlobalConfig/TargetOperationConfig.json#/OperationDict` 有 80 条命名目标操作。另有 RtBattle 的 28 个别名、7 个目标操作，RtDefence 的 12 个别名以及仅有 `AvatarIDMin` 的同名操作资源。公共 v2 已索引核心 Ability 文件里的 362 条 `GlobalTargetAlias` 定义。名字在模式、资源和来源均有边界。

```json
{"$type":"RPG.GameCore.TargetSequence","Sequence":[{"$type":"RPG.GameCore.TargetAlias","Alias":"Caster"},{"$type":"RPG.GameCore.TargetMapEnemyTeamEntity"},{"$type":"RPG.GameCore.TargetMapAllTeamMember"}]}
```

上方是 `Config/GlobalConfig/TargetAliasConfig.json#/AliasDict/AllEnemy` 的完整对象。对照 `/AliasDict/AllTeamMember`，后者从 Caster 映射队友，序列少一段。 `/AliasDict/AllLightTeam` 先选固定阵营 `LightTeamEntity`。 `/AliasDict/AllEnemyWithUnSelectable/Sequence/2` 显式写 `RemoveUnselectable:false`。例外的存在约束了缺省行为研究，同时任何空缺字段继续保持空缺。 `/AliasDict/AbilityTargetAndAdjoinEntity` 用 `TargetConcat.Targets` 拼接主 Ability 目标和独立相邻查询。这些结构是多段查询、组合与可重用命名的 **Observed** 证据。列表顺序、去重和有效对象筛选的底层行为保持 **Unknown**。

**Derived**。补充解析固定使用同文件和已标记模式允许的字典，不进行运行时加载猜测。在 v2 的 261,121 个别名字面位置中，共 1,184 个不同值。有 250,243 个 v2 unresolved 位置获得单一精确候选。包含 `+`、`-`、`|` 或点号的样本另做词法分段，只报告所有组件可定位的候选。 `ParamEntity.GetSummoner` 按别名 `ParamEntity` 与操作 `GetSummoner` 分别命中，带 `|` 的 `AbilityTargetEntity.GetSummoner | AbilityTargetEntity.GetServant` 也可见于公共字典。分隔符运算、优先级、失败行为和空值处理为 **Unknown**。模式存在覆盖反例，RtBattle 的 `AllLightTeam` 在公共和模式资源都定义。Pollux 的局部名在另一活动文件引用，补充表保留为 `outside-domain-or-file`。不同形态和未解析项完整保存在引用表中。[所有定义](target-dictionaries.tsv) · [别名逐位置](alias-references.tsv) · [状态汇总](alias-counts.tsv)

### 效果节点怎样使用查询

| 用途 | 原始证据 | 证据界限 |
| --- | --- | --- |
| 自身、某个选定实体与主目标 | 公共字典的 `Caster`、`AbilityTargetEntity` 指向不同 fetch 类型，`CurrentAimAtMainTarget` 的对象为 `TargetFetchAimAtTargetList(TargetType="MainTarget")`；`Config/ConfigCharacter/Avatar/Avatar_Himeko_00_Config.json#/SkillList/1/TargetInfo` 同时配置 `EnemySelect` 和 `TargetAdjoinEntity` | **Observed**，目标查询还可能是角色入口的选取字符串 |
| 友方、敌方与相邻 | `AllTeamMember`、`AllEnemy`、`AbilityTargetAdjoinEntity` 与 `AbilityTargetAndAdjoinEntity` 采用公共映射和拼接 | **Derived**，角色技能的 `DamageByAttackProperty.TargetType` 与装备的 `HealHP.TargetType` 可引用统一查询体系，技能入口的选定目标和任务实际目标分别读取 |
| 过滤、排序、数量和随机 | `/AliasDict/AvatarNextTurnOwnerEntity` 配置队伍、角色与存活 mask，继以 `TargetSortByActionOrder(FilterNoActionEntity=true)` 和 `TargetTake(Count=1)`。停云 `/GlobalModifiers/MAvatar_TingYun_ByIsTingYun/_CallbackList/0/CallbackConfig/0` 的 `Retarget` 以 `AllLightTeam`、`ByIsContainModifier`、`ByRandom:true`、`MaxNumber:1` 过滤并运行子任务 | **Observed**，独立目标管道与取样后执行任务的复合节点并存。排序同分规则、随机分布、失败分支判定时点未知 |
| 随机位置、相邻实例与状态排序 | `Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json#/GlobalTargetAlias/AcheronPassiveModifierTarget/Sequence/2` 是 `TargetShuffle`。`Config/ConfigAbility/Activity/Activity_FateChess_Ability.json#/GlobalModifiers/MActivity_FateChess_Archer_02_GlobalBuff/_CallbackList/0/CallbackConfig/1/SuccessTaskList/1/SuccessTaskList/0/TargetType/Sequence/1` 是 `TargetSortByProperty` | **Observed**，相关筛选还有 `TargetSortByModifierValue`、`TargetSortByPredicate`、`TargetFilterAliveState` |
| 保存目标和提取上下文 | 姬子新形态 `Config/ConfigAbility/Avatar/Avatar_HimekoNova_00_Ability.json#/AbilityList/33/OnStart/0` 写 `DynamicKey="HimekoNova_00_Assist"`，`/GlobalTargetAlias/HimekoNova_00_AssistTarget/Sequence/1` 读取同键 | **Derived**，两节点均以 `TargetAlias_HimekoNova` 指定实体来源，键和目标相合。缓存时长、对象失效后处理为 Unknown |

## 执行者、持有者、事件实体和攻防数据

配置中可直接区分以下槽位。实际角色可以在一次技能中重合，同一个事件中的绑定必须按发出者与监听者核对。公共别名定义提供独立取值接口，任务实参进一步显示同一节点可携带不同角色的引用。

| 候选身份 | 所见配置与反例 |
| --- | --- |
| 能力的执行方与继承目标 | **Observed**。黄泉 `Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json#/AbilityList/11/OnStart/8` 的 `TriggerAbility` 同时报 `TargetType.Alias="Caster"` 与 `AbilityInherentTargetType.Alias="AllEnemy"`。另见主角 `Config/ConfigAbility/Avatar/Avatar_PlayerBoy_40_Ability.json#/AbilityList/7/OnStart/7` 带 `DynamicValues.Nihilux_AhaArrival_ExtraElationSkillDamageRatio` 调用 Phase02。实际调用负责人的实例字段和目标继承规则未知 |
| Modifier 持有者、施加者 | **Observed**。公共字典分别以 `TargetFetchModifierOwner`、`TargetFetchCallBackModifierCaster`、`TargetFetchCaster` 绑定 `ModifierOwnerEntity`、`CallBackModifierCaster`、`Caster`。艾丝妲速度 Modifier 施加任务对 `AllTeamMember` 写状态，`OnStack` 对 `ModifierOwnerEntity` 写属性。单一 identity 槽解释与结构不符 |
| 攻击者、受击者和战斗轮次 | **Observed**。 `DamageAttackerEntity` 与 `DamageDefenderEntity` 分别在 `Caster` 后调用 `TargetMapDamageAttacker` 和 `TargetMapDamageDefender`。 `CurrentDamageAttackerEntity`、`CurrentDamageDefenderEntity` 各用专门 fetch，`CurrentTurnActionEntity` 和 `CurrentTurnOwnerEntity` 也有不同 fetch。何时取照、父子攻击覆盖与延迟后的引用跨度均为 Unknown |
| 技能选择与事件参数 | **Observed**。 `SkillTargetEntityList` 从 Caster 映射技能目标，`ParamEntity`、`ParamEntity2`、`ParamEntityList` 分别是 `TargetFetchParamEntity`、`TargetFetchPassiveEntity`、`TargetFetchParamEntityList`。赛飞儿 `OnListenAfterBeingHitAll` 样本明确从 `ParamEntity2` 选取 `Result_FinalDamageBase` 并写 `_TMP_Damage`。某类事件里的来源、目标和第二参数不会因此外推到其他选择器 |
| 召唤者、忆灵与战斗事件 | **Observed**。 `CasterSummoner` 以 `TargetMapSummoner` 派生，`CasterServant` 用 `EntityTypeMask:"Servant"`、`AliveStateMask:"Mask_AliveOrLimbo"` 及 `ByCompareTarget(ParamEntity.GetSummoner,Caster)` 过滤。 `BattleEventCaster` 另有 fetch。阿格莱雅 `CreateServant` 写入 ID 11402 及具名动态入参，Excel 的独立 `ServantID` 行提供实体入口。创建、继承和同步时点仍为 Unknown |
| 投射物与模板 | **Observed**。公共字典提供 `ProjectileHitEntity`、`ProjectileHitPos`、`TemplateParamEntityList`。模板调用可带 `ParamTarget` 和 `TemplateParamSequences`。同一个参数实体是否按每目标、每任务或每命中重新绑定为 Unknown |

因此能可靠重建配置对上下文的多槽位引用，以及显式目标查询与效果任务的连接。进入子 Ability、加状态或执行 `Retarget.TaskList` 后究竟复制或共享哪些对象，以及默认解析任何未指定槽位的优先级，均保留为 **Unknown**。[身份及调用证据](evidence.jsonl) · [事件专题](../04-callback-trigger/report.md)

## 数值形态与有限求值

**Observed**。固定数值样本为 `{"IsDynamic":false,"FixedValue":{"Value":11402}}`。动态样本将基础常量表、哈希表及 Base64 指令字节分列。

```json
{"IsDynamic":true,"PostfixExpr":{"OpCodes":"AQAR","FixedValues":[],"DynamicHashes":[-1126825319]}}
```

该值出现在 `Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json#/AbilityList/1/OnStart/7/AttackProperty/DamagePercentage`。哈希 `-1126825319` 出现在角色同技能 `DynamicValues.Floats` 声明，`ReadInfo` 为 `{"Type":"SkillParam","TriggerKey":"Skill01","Index":0}`。角色的 `AvatarConfig.SkillList` 数字 ID、技能等级行与 `SkillTriggerKey` 合看可求出 0.5、0.6。单哈希编码 `AQAR` 对应字节 `01 00 11`，在已定位、空固定常量表、只含一条具名声明的样本中支持 **Derived** 的参数值联接。选区里有 74,704 个 `PostfixExpr`，700 种 Base64 字面图样。频度最大的 `AQAR` 有 55,680 个，`AQABAQQR` 有 3,498 个，`AQABAQIR` 有 1,931 个。

**Inferred**。 `01 00 01 01 02 11` 的两动态输入案例与相加相容，布洛妮娅战技的 `ByRankActivated` 分支提供 Rank06 值，同一效果的失败分支用单个基础值。停云在 `ModifySPNew.FixedAddValue` 使用相同编码与同阶门槛。核验角色所属 RankID 后，基础输入为 50，星魂输入为 10，支持相加候选 60。艾丝妲 PointB1 的 `01 00 01 01 04 11` 的两输入与相乘相容，结合本地描述直接表明效果依赖普攻值的一个参数比例，可对两级输入求得候选结果。这两种操作的具名习惯、局部描述和首尾形态提供独立约束，其他字节指令语义、浮点舍入与运行时栈模型仍未知。

根目录 `EquipmemtAbility.json` 的同名 `Ability20000` 使用并列形态 `DynamicValues.Values`、`ReadInfo.Str` 与 `AQAK`，字节为 `01 00 0a`。结合 `Equip/` 版数据可证序列化表示变体共存。脚本只在指定表达式、指令和输入均通过精确检查时解释值。复杂常量池、其他代码图样、缺失绑定、运行时间输入和跨版本替换均保留 Unknown。哈希配对另有双累加器候选，从源里的 2,507 个单键配对位置及 684 条星魂 TriggerHash 逐条实验。该算法区分施加实参名的计算哈希、参数值引用中的来源哈希、目标作用域局部声明或写入的内部键。[哈希证据和误配反例](hash-probe.md) · [全部表达式图样](postfix-shapes.tsv)

### 实际绑定与复算

| 路径 | 静态结果与证据 |
| --- | --- |
| 艾丝妲普通攻击 | **Derived**。Avatar 1009 的 `SkillID=100901` 等级 1/2，经 `Skill01`、Phase01 的具名请求、Phase02 的 `DamageByAttackProperty`，静态 `DamagePercentage` 输入 0.5/0.6。参见 `ExcelOutput/AvatarSkillConfig.json#/191/ParamList/0/Value` 和 `#/192/ParamList/0/Value` |
| 艾丝妲灼烧行迹 | **Derived**。 `ExcelOutput/AvatarSkillTreeConfig.json#/487` 的 PointID 1009101、AvatarID 1009、`PointB1`，经成功分支 `/AbilityList/1/OnStart/6/SuccessTaskList/0` 施加 `MCommon_DOT_Burn`，明文入参为基础概率 0.8 和时长 3。**Inferred**。乘积候选 0.25/0.30 对应两级技能配行迹比例 0.5。配置共用 Burn 定义 `Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json#/ModifierMap/MCommon_DOT_Burn/_CallbackList/1/CallbackConfig/2/AttackProperty/DamagePercentage` 读取 `Modifier_Burn_DamagePercentage` 的候选哈希及另一动态量。因此加状态入参的候选乘积和实际 DOT 值分层。辅助文字见 `TextMap/TextMapCHS.json#/16178627604319461393` |
| 布洛妮娅战技及星魂 | **Derived**。Skill 110102 等级 1 的参数 index 2 为 1，经 Phase01 的 FailedTaskList 具名请求进入 Phase02 分支，写入 `MAvatar_Bronya_00_BPSkill_DamageUp.LifeTime`。Rank 110106 的 TriggerHash `-1445815962` 在同 Ability 的 `ByRankActivated` 分支出现，Param[0] 为 1。**Inferred**。真分支两个输入的相加候选为 2。施加实参 `MDF_DamageAddedRatio=0.33` 由 index 0 联接，接收方 `OnStack` 读其候选哈希并写 `AllDamageTypeAddedRatio`。辅助文字见 `TextMap/TextMapCHS.json#/7244991336643732642` |
| 停云终结技 | **Derived**。Avatar 1202 的 Skill 120203 对应的等级 1 行以 `Skill03` 进入 Phase01，`OnStart/5` 请求 Phase02， `Config/ConfigAbility/Avatar/Avatar_Tingyun_00_Ability.json#/AbilityList/6/OnStart/7/FailedTaskList/0/FixedAddValue` 绑定数值 50。**Derived**。 `ExcelOutput/AvatarConfig.json#/22/RankIDList/5` 给出 120206，匹配 `ExcelOutput/AvatarRankConfig.json#/149/Param/0/Value` 的 10。**Inferred**。同段真分支是两输入加法候选 60。 `ExcelOutput/AvatarRankConfig.json#/143` 的同哈希行属于另一角色 1201，其空参数是作用域误配反例 |
| 光锥 Ability20000 | **Derived**。 `EquipmentConfig.SkillID=20000` 与 `EquipmentSkillConfig` 等级 1/2 的 `AbilityName` 对接 `Equip/` 定义，两个 `SkillEquip` 索引输入分别成为本地 Modifier `OnStack.StackProperty.CriticalChanceBase` 的 0.12/0.15 和施加点寿命 3/3。同步存在名同而表示有异的根定义，加载选择未知 |
| 遗器 Ability51061 | **Derived**。 `ExcelOutput/RelicSetSkillConfig.json#/11` 的 SetID 106、RequireNum 4、AbilityName 与 `SkillRelic.TriggerKey="106_4"` 对应。 `OnStart` 给 Caster 装上状态，`OnPhase1` 对状态持有者配置 HP 比例比较 `LessEqual 0.5`，成功分支 `HealHP.FormulaType="HealByTargetMaxHP"` 的比例为 0.08，及 `ModifySPNew.AddValue=5`。比例阈值、治疗比例与能量入参可静态求值，触发时血量与最终效果未知 |
| 黄泉 ExRank | **Derived**。混淆表 `ExcelOutput/AvatarExRankConfig.json#/2` 同时含角色 ID 1308 和 Ability `Avatar_Acheron_00_ExRank01`，其 `NNACKOBKFGE[1].Value` 为 1。 `SkillRank.ExRank01` 的 Index 1 从黄泉角色声明联到插入 Phase02 的 `ModifySpecialSP.FixedAddValue`。同文件 Phase01 明文请求 Phase02。仅此具名链可解释该表行在案例中的输入角色，其他混淆字段、运行时上限及调用时点保持未知 |

[逐节点路径和值](binding-results.tsv) · [122 条证据摘录](evidence.jsonl)

## 变量、读写和控制流

| 接口 | 可证形态及界限 |
| --- | --- |
| 显式声明及目标实体 | **Observed**。`DefineDynamicValue` 的 `DynamicKey` 有包装对象和字符串，常见 `TargetType`、`ContextScope`、可选 `ResetValue`。 `SetDynamicValue` 用 `DynamicKey`、`Value` 配置写入，也可带 `TargetType` 和 `ContextScope`。 `TargetEntity` 是选区中最常见的 `ContextScope`，实际跨行动或轮次保存时段为 Unknown |
| Ability、Modifier、Caster、Owner | **Observed**。 `ContextAbility`、`ContextModifier`、`ContextCaster`、`ContextOwner` 同时出现在配置。砂金的 `SetDynamicValueByRandom` 写 `ContextModifier` 内的 `MDF_Coin`，输入包含固定下界 1、动态上界和 `IsInt:true`。战斗事件两个相近样本分别在 `OnAdd` 用 `ContextCaster` 定义计数，在 `OnDynamicValueChange` 以 `ContextOwner` 注册范围。槽位或实例存储位置仍未知 |
| 回调临时、调用实参和模板 | **Derived**。Evanescia 的 `CallbackTemporary` 示例在同一成功分支先定义 `_ElationPoint`，下游比较任务读同键。示例有匿名中间写入候选，值的来源和派发间共享范围为 Unknown。 `ContextTaskTemplate` 在 BattleEvent 模板中显式定义 `TDF_NoPhysical`，`TriggerAbility.DynamicValues`、`AddModifier.DynamicValues`、`IncludeTaskListTemplate.DynamicValues` 分别显示具名调用入参 |
| 事件载荷与副作用 | **Observed**。 `TriggerParamModifierCustomEvent` 同时提交 `EventType`、`DynamicKey` 与动态 `Value`。另有 `ByCompareParamValue` 的 `CompareValue`、可选 `ParamIndex`，天赋回调中有使用样本。配置能够引用事件载荷位置，生产和消费同时性，以及事件参数池与数值池是否共享仍为 Unknown |
| 属性、资源、层数与保存目标 | **Observed**。黄泉 `SetDynamicValueByProperty` 从 Caster 读取 `CurrentSpecialSP` 到 `CurrentSP`，另一个 `SetDynamicValueByModifierValue` 从 `ParamEntity` 指定 Modifier，输入有 `Multiplier:1`。其他样本区分 `LifeTime` 的显式读取，读取省略 `ValueType` 的缺省值仍未知。姬子新形态对实体参数做同键写入和目标映射，说明数值变量以外还可表达实体参数 |
| 战斗范围候选 | **Observed**。 `SetDynamicValueByBattleTargetParam(BattleTargetID=5001802)` 可读关卡目标入参。`BattleEvent`、`StageBattleEvent`、`FloorCustomData` 是不同 `ReadInfo.Type`。另有 `AddGlobalDynamicOffset` 及模式专用 `ChimeraDuelGlobalDynamicValueGetter`。通用持久全局变量、全局黑板、跨波次清理和 key 覆盖优先级保持 Unknown |
| 比较、布尔、控制流与选择 | **Observed**。 `PredicateTaskList` 用 `Predicate`、`SuccessTaskList`、`FailedTaskList`。 `ByAnd`、`ByOr`、`ByNot` 和各种 `CompareType` 与属性、状态、数值比较组合。 `Retarget`、循环和模板将筛选、分支或重复与子任务关联。实时玩法的 `VE_Predicate` 同时有 `Predicate=QueryHoyoTag` 和条件权值 1000，包在 `VE_Group.Values` 中。布尔求值短路、分支调度、表达式求值顺序、概率及循环边界缺省仍未知 |

目标数量既可固定，也可由动态包装对象输入，定义见 [字段形态](target-field-shapes.tsv)、[类型及位置](typed-context-inventory.tsv)。例如 `Config/ConfigAbility/BattleEvent/Avatar_HeliobusActionAbilityFormChange_Ability.json#/AbilityList/2/OnStart/7/MaxNumber` 的 `PostfixExpr.DynamicHashes=[-672936222]`。

## 可证范围与未解

- **CTX-001 · Observed**。公共别名和目标操作字典分别有 196 和 80 条。`AllEnemy` 和 `AllTeamMember` 采用两种可复查的映射序列。
- **CTX-002 · Derived**。补充索引让 v2 未匹配的 250,243 个别名位置得到单一精确候选。另有 5,513 个 v2 未匹配位置的词法组件均可定位。模式字典碰撞、未解析名字和语法行为须分开。
- **CTX-003 · Observed**。Caster、状态持有者、施加者、选定目标、事件参数及召唤关系均有取值接口。同一效果链可分别引用多个角色。见公共字典、黄泉调用与艾丝妲状态路径。
- **CTX-004 · Derived**。现代 `ReadInfo` 的 Type、TriggerKey、Index 与作用域数字哈希可建立部分具名、级别和对象绑定。常量及部分单输入表达式已静态求值。停云与角色 1201 的同阶哈希相同，装备定义也有同名变体，两个例子都要求先确定归属。
- **CTX-005 · Inferred**。基于多个实际样本与本地辅助描述，`AQABAQIR` 和 `AQABAQQR` 在指定样本支持和式、乘积候选。完整操作码、执行实现与舍入、误差处理未知。
- **CTX-006 · Observed**。配置显式提供九个观察到的 `ContextScope` 值，以及事件参数、动态实体、模板参数和状态参数机制。词法可见性和运行时实例生存期需要独立证据。
- **CTX-010 · Inferred**。双累加器有符号哈希候选支持文本键和数字引用的多实例配对。目标容器的同名覆盖、Unicode 处理与剩余反例仍待明确。

[可复现目录](inventory.md) · [参数与上下文检查](verify_bindings.py)
