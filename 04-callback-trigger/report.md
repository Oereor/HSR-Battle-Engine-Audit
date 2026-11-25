# 04 · Callback、Trigger 与事件接口

## 配置结构

公共索引 v2 有 35,896 个具名回调选择器，共 224 个原始名称。核心 `ConfigAbility`、`ConfigGlobalModifier`、`ConfigGlobalTaskListTemplate` 中有 35,295 处及 216 个名字，RtBattle/RtDefence 有 601 处及 38 个名字。两域共享 30 个名字，作用域、行为体及所属定义分别保留。两个 `CallbackConfig` 另以全局行为标记为键，省略具名 `Event`。完整索引与分域规则见 [参考清单](inventory.md)。

| 结构 | Observed 与定位 | 边界 |
| --- | --- | --- |
| Modifier 选择器 | `Config/ConfigAbility/Avatar/Avatar_Robin_00_Ability.json#/GlobalModifiers/MAvatar_Robin_00_SkillRank04_DispelControl/_CallbackList/1` 为 `{"Event":"OnListenTurnEnd","CallbackConfig":[{"$type":"RPG.GameCore.RemoveSelfModifier"}]}`。 | `Event` 是数据值，`CallbackConfig` 是任务容器。安装后实际注册、分发和注销者为 **Unknown**。 |
| Ability 生命周期字段 | 艾丝妲普攻 `Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json#/AbilityList/0/OnStart`，关卡配置 `Config/ConfigAbility/Level/Level_MazeChallengeBuff_Ability.json#/AbilityList/42/OnAdd`，Archer 插入取消 `Config/ConfigAbility/Avatar/Avatar_Archer_00_Ability.json#/AbilityList/11/OnInsertAbort`。 | 这些列表属于各自宿主。Ability 的 `OnAdd`、Modifier 的 `OnModifierAdd` 及任务的 `OnBattleEventCreate` 能否共用内部派发设施为 **Unknown**。 |
| 按旗标路由的回调 | `Config/GlobalConfig/GameCoreConstValue.json#/ModifierBehaviorFlagEventMap/501/ModifierBehaviorFlagEventConfigs/0/CallbackConfig/0` 为 `DispelStatus`，目标 `ModifierOwnerEntity`，条件引用 `CallBackModifierCaster` 和 `STAT_ForceControl`。键 500 也配置驱散，省略 501 的敌我判定。 | 两个命名空间条目只有数字键，具体派发时点未知。 |
| 变更观察器 | `Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json#/AbilityList/15/Modifiers/MAvatar_Acheron_00_PassiveUltra/OnAbilityPropertyChange/0` 有 `Property:"CurrentSpecialSP"`、`Ranges[].Min`、`TriggerClampedChange` 和 `OnChange`。`Config/ConfigAbility/Avatar/Avatar_Cerydra_00_Ability.json#/AbilityList/7/Modifiers/MAvatar_Cerydra_00_PassiveSkill/OnDynamicValueChange/0` 有 `Key.Hash:-545645004` 和 `ContextScope:"ContextOwner"`。 | 两类观察器分别选定属性或动态键，均配置后续任务。范围边界、合批与派发时机未知。 |
| 请求与实体 | `TriggerAbility` 携带 `AbilityName`，`TriggerModifierCustomEvent` 携带 `EventType` 与 `TargetType`，`CreateBattleEvent` 携带事件 ID、队伍及子任务。 | 接口可分辨。BattleEvent 还可成为寻址实体，见[景元的 11203](../01-entity-ability/report.md)。 |
| 场景同词结构 | `Config/Level/GroupGraph/F10000002/Group_F10000002_G63.json#/OnStartSequece/0/TaskList/0` 为实际的 `RPG.GameCore.CallBack`，`OnDispose` 写 `FCV_Mar7thBedConflict`。公共索引共 10 个同型节点，集中于场景或任务图。 | 独立 `$type` 节点与上述无类型的选择器容器并存。索引内未见 `MixTrigger`、`MixAbility` 同名对象、数组容器或独立序列化类型；混淆字段及未导出部分未知。 |

回调声明的可选直接字段 `Priority` 出现 1,524 次，整数范围 -101 至 999999。活动三月七同一文件内为 `OnEnterBattle` 写入 -80 和 999999，见 `Config/ConfigAbility/Activity/Avatar/Avatar_SwordTraining_Mar_7th_10_Ability.json#/AbilityList/9/Modifiers/M_ST_GlobalListener/_CallbackList/3/Priority` 与 `Config/ConfigAbility/Activity/Avatar/Avatar_SwordTraining_Mar_7th_10_Ability.json#/AbilityList/17/Modifiers/M_ST_Power_4/_CallbackList/0/Priority`。比较方向、缺省值和跨宿主优先级合并仍为 **Unknown**。过滤、次数和延时的字段多出现于后续任务体，见 [逐位置清单](callback-sites.tsv)。

## 事件粒度与上下文

下表的选择器、任务、字段均为 **Observed**。粒度和行为联系是由多个实际配置支撑的 **Inferred** 解释，精确时点、派发次数及去重规则仍需运行时证据。

| 主题 | 原始配置与局部证据 |
| --- | --- |
| 入场与波次 | `Config/Level/StageCommonTemplate.json#/OnStartSequece/1/TaskList/29` 为 `TriggerModifierEnterBattle`，同列表的 `/13` 是 `WaveMonster`，`/35` 是 `StartBattle`。`Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json#/TaskListTemplate/4/TaskList/2` 的 `Wave_CommonProcess` 亦显式请求 `TriggerModifierEnterBattle`。黄泉被动的 `Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json#/AbilityList/15/Modifiers/MAvatar_Acheron_00_PassiveUltra/_CallbackList` 分开配置 `OnEnterBattle`（索引 7）和 `OnWaveMonster`（9）。初始关卡与波次模板都可发出入场请求，每波及每实体的实际次数未知。 |
| 回合与行动 | 黄泉 `Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json#/GlobalModifiers/MAvatar_Acheron_00_ExRank01_Listener/_CallbackList/0/Event` 为 `OnListenTurnBegin`。知更鸟的 `OnListenTurnEnd` 自移除，并在 `Config/ConfigAbility/Avatar/Avatar_Robin_00_Ability.json#/GlobalModifiers/MAvatar_Robin_00_Passive/_CallbackList/1/Event` 处理 `OnActionPhaseBegin`。公共控制状态 `Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json#/ModifierMap/MCommon_MindControl/_CallbackList/3/Event` 为 `OnActionEnd`。自然回合、插入行动和阶段的对应关系仍未知。 |
| 请求、资格与使用 | `Config/ConfigGlobalModifier/GlobalModifier.json#/ModifierMap/BattleEventAbility_Challenge_Month_35_FixSub/_CallbackList/38` 的 `OnListenAnySkillExecution` 下有 `DebugLog`，同状态索引 46 是 `OnListenInsertAbilityCheck`。公共 `MCommon_Windfury` 还分别监听 `OnBeforeSkillCost`、`OnBeforeSkillUse`、`OnAfterSkillUse`。可见执行、资格、费用和使用的不同选择器，诊断样本触发条件未知。 |
| 单次命中、聚合命中与攻击 | `Config/ConfigAbility/Avatar/Avatar_Archer_00_Ability.json#/AbilityList/10/Modifiers/MAvatar_Archer_00_AttackListner/_CallbackList/0/Event` 为 `OnBeforeHit`，相邻索引 1 为 `OnAfterAttack`。砂金 `Config/ConfigAbility/Avatar/Avatar_Aventurine_00_Ability.json#/GlobalModifiers/MAvatar_Aventurine_Passive_OnAfterBeingAttacked/_CallbackList` 同时含 `OnAfterHitAll`（0）和 `OnAfterAttack`（3），另一个状态还有 `OnAfterAttackEnd`。`BeingHit` 与 `Hit` 也分别存在。`All` 是否每个技能或目标批只调用一次仍未知。 |
| 伤害数据、治疗、护盾 | 光锥 `Config/ConfigAbility/Equip/EquipmemtAbility.json#/AbilityList/95/Modifiers/MEquip_23020_Main/_CallbackList/0/CallbackConfig/2` 在 `OnBeforeHitAll` 中写 `ModifyDamageData.Attacker_CriticalDamage`。活动单位 `Config/ConfigAbility/Avatar/Avatar_AetherDivide_W1_Mecha02_00_Ability.json#/GlobalModifiers/MAvatar_W1_Mecha02_00_ListenHeal/_CallbackList/0/CallbackConfig/0` 在 `OnAfterDealHeal` 读取 `Result_HealRealAmount` 到 `_TMP_HEAL`，指定读目标 `ModifierOwnerEntity`。白厄 `Config/ConfigAbility/Avatar/Avatar_Phainon_00_Ability.json#/AbilityList/28/Modifiers/M_Phainon_00_SkillTree02/_CallbackList/3/Event` 是 `OnListenInitShield`。支持可分开的数据接口，提交及内部结算顺序未知。 |
| 资源变化与消费 | `Config/ConfigAbility/Avatar/Avatar_Archer_00_Ability.json#/AbilityList/14/Modifiers/MAvatar_Archer_00_SkillTree03/_CallbackList/0` 的 `OnListenBpChange` 配置 `SetDynamicValueByCurrentBP` 与 `SetDynamicValueByBPChange`。黄泉的属性范围观察器分别读取 `CurrentSpecialSP` 和 `ValueType:"ClampedAdd"`。公共 `MCommon_Windfury` 的索引 9 监听 `OnBeforeEnergyPointChange`。变更值的符号与同次变更的派发次数仍未知。 |
| 状态变更与负面效果 | `Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json#/GlobalModifiers/MAvatar_Acheron_00_OnListenDeBuffAdd/_CallbackList/0` 为 `OnModifierOnStack`。其 `CallbackConfig/0/Predicate/PredicateList/0` 为 `ByCheckModifierCallBackStatusType(TargetStatusType:"Debuff")`；同组还检查具名冷却和角色情景，成功路径包含 `ModifySpecialSP`。另见 `OnModifierAdd`、`OnModifierRemove`、`OnListenModifierOnStack`。该机制用状态类别过滤通用入口，实际施加、层数变化和通知的映射仍未知。 |
| 破韧、死亡与召唤 | 强化流萤 `Config/ConfigAbility/Avatar/Advanced/Avatar_Advanced_Sam_00_Ability.json#/GlobalModifiers/MAvatar_Advanced_Sam_00_PassiveSkill_RedMode/_CallbackList/6/Event` 为 `OnTriggerBreak`。罗刹 `Config/ConfigAbility/Avatar/Avatar_Luocha_00_Ability.json#/AbilityList/7/Modifiers/MAvatar_Luocha_00_InsertSkill02_Mark/_CallbackList/1/Event` 使用 `OnBeforeDying`。景元 `Config/ConfigAbility/Avatar/Avatar_JingYuan_00_Ability.json#/AbilityList/9/Modifiers/MAvatar_JingYuan_00_BattleEvent_ForceKill/_CallbackList/0/Event` 为 `OnListenCharacterDie`，其召唤仍通过 BattleEvent 配置建立归属和调度。不同事件宿主的继承及派发规则未知。 |
| 插入行动、插入能力及终结技 | 白厄 `Config/ConfigAbility/Avatar/Avatar_Phainon_00_Ability.json#/GlobalModifiers/MAvatar_Phainon_00_Ultra_VisualManager/_CallbackList/9/Event` 使用 `OnListenInsertActionFinish`，同文件 `/GlobalModifiers/MAvatar_Phainon_00_Ultra/_CallbackList/12/Event` 使用 `OnListenInsertAbilityFinish`。真理医生 `Config/ConfigAbility/Avatar/Avatar_Dr_Ratio_00_Ability.json#/GlobalModifiers/MAvatar_Dr_Ratio_00_Skill03_TheFool/_CallbackList/6/Event` 使用 `OnListenInsertUltraSkill`。额外行动计入何种回合统计仍未知。 |
| 技能复制与事件链 | 刻律德菈 `Config/ConfigAbility/Avatar/Avatar_Cerydra_00_Ability.json#/GlobalModifiers/MAvatar_Cerydra_00_Skill02_Target/_CallbackList/1/CallbackConfig/2` 在 `OnBeforeSkillUse` 选中 `MCommon_Windfury` 并读取 `Windfury_Flag` 到局部上下文。公共定义 `Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json#/ModifierMap/MCommon_Windfury/_CallbackList/5/CallbackConfig/0/SuccessTaskList/3/SuccessTaskList/0/FailedTaskList/3` 在 `OnAfterSkillUse` 分支配置 `TurnInsertAction`，带 `InsertActionPriority:"Windfury"`、动态 `SkillIndex`、`AutoCastTargetType:ModifierOwnerSkillTargetEntityList` 和 `OnInsertAbort`。可见共享状态与上下文参与再请求，执行帧是否复制及重算边界未知。 |

## 自定义事件的生产与路由

`Config/GlobalConfig/GameCoreConstValue.json#/ModifierCustomEvents` 有 14 条声明，均为 `EnumIndex:4`，带 `BehaviorFlags`。值 1–6 显式给出 `SortBy:"Phase1Priority"`，值 1 包含 `STAT_DOT` 和四种具名 DOT 旗标。值 13、15 分别配置数字旗标 1006、1008。值 11 使用 `CustomEvent_TargetStancePreshow`。这些字段提供局部匹配与排序策略的结构证据。

**Derived**。令牌 `(4,13)` 同时有发出请求、全局声明及接收条件：

1. `Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json#/TaskListTemplate/0/TaskList/0` 的 `TriggerModifierCustomEvent` 面向 `BattleAllEntity.GetAliveOrLimbo` 请求该值，含 `IncludeLimbo:true`。同文件 `/TaskListTemplate/2/TaskList/0` 另外写 `OverrideParamEntity:ParamEntity`。
2. `Config/GlobalConfig/GameCoreConstValue.json#/ModifierCustomEvents/8` 是 `{"BehaviorFlags":[1006],"EventType":{"EnumIndex":4,"Value":13}}`。
3. `Config/ConfigAbility/Avatar/Avatar_Nihilux_10_Ability.json#/AbilityList/16/Modifiers/MAvatar_Nihilux_10_SkillAeon_DirtyHP_Property` 具有 `BehaviorFlagList:[1006,"KeepOnDeathrattle"]`。其 `_CallbackList/1` 为 `OnCustomEvent`，条件同时比较 `ParamEntity` 与 `ModifierOwnerEntity` 及令牌 `(4,13)`。成功体设置 `MDF_DirtyHPRatio=0`。GridFight 中同名定义也具这组条件。

同一请求的实际参与者、派发时点和允许重入次数仍未知。对照可见，值 11 仅有声明，值 15 有接收比较但缺同口径发送样本。[14 个令牌](custom-event-links.tsv)中，12 种有发出请求，7 种有明确字面比较或动画候选，6 种同时满足。位置数为 162 个 `TriggerModifierCustomEvent`、1 个 `TriggerParamModifierCustomEvent`、15 个 `ByCompareModifierCustomEvent` 及 3 个 `TriggerAnimStateOnModifierCustomEvent`。后一种以动画配置和令牌并列，只计消费侧候选。

另有 21 个 `TriggerBattleStatisticEvent`。`Config/ConfigAbility/BattleEvent/Activity_LuckyScroll_Ability.json#/GlobalModifiers/Modifier_BattleEventAbility_Activity_LuckyScroll_BuffLayer/_CallbackList/1/CallbackConfig/0/EventType` 是字符串 `TelevisionActivity_UpdateMazeBuffLayer`，与数字令牌分表。`DynamicKey`、`Value`、`OverrideParamEntity` 是部分接口的显式字段。其参数能否在通用监听中共享同一结构仍未知。

## 动画、延时及请求终止

- **Derived**。26 个 `WaitAnimEvent` 节点位于 Claymore 基础与 FateRin Ability 文件，使用 16 种名称。`Config/ConfigAbility/Monster/Monster_W4_Claymore_02_Ability.json#/AbilityList/1/OnStart/2` 请求 `Event_Skill01_Attack01`。同名 Ability 出现在 Claymore 配置的技能成员列表，其 `Config/ConfigCharacter/Monster/Monster_W4_Claymore_02_Config.json#/AnimEventConfigList/3` 明文导入 `Config/ConfigAnimEvents/Monster/Logic/Monster_W4_Claymore_02_Logic_AnimEvent.json#/LogicAnimEvents/0` 所在文件。该记录配 `AnimStateName:"Skill01"` 与 `Time:0.320988`。26 个等待均至少有一个经角色导入的同名匹配。实际资源变体与时序仍待确定。[导入匹配](animation-wait-links.tsv)
- **Observed**。另一种动画配置按状态和归一化时间挂任务。`Config/ConfigAnimEvents/Avatar/Designer/Avatar_Asta_00_Designer_AnimEvent.json#/AnimatorStateEvents/0` 有 `AnimatorStateName:"Die"`、`NormalizedTime:0.9` 及 `EventList:[TriggerDeadHandler]`。同文件的状态组另有 `OnEnter` 和 `OnExit`，而 Claymore 的 `LogicAnimEvents` 按具名事件索引。数据提供动画可发出死亡处理相关任务的直接证据。
- **Observed**。`Config/ConfigAbility/Avatar/Avatar_SilverWolf999_00_Ability.json#/AbilityList/19/OnStart/7/TaskList/2/FailedTaskList/0` 为 `PerformDelayExecute`，配置动态 `Delay`、`TargetType:ParamEntity` 和 `PerformTaskList:[TriggerAnimState]`。`Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json#/TaskListTemplate/4/TaskList` 另有 `WaitFrame`、`WaitSecond` 与 `WaitFrameForBattleServer`。延时及等待的请求形态可辨，实际时钟与线程语义未知。
- **Observed**。知更鸟的 `OnListenTurnEnd` 使用 `RemoveSelfModifier`。`Config/ConfigAbility/Avatar/GlobalSkill/Avatar_GlobalSkill_Castorice_00_Ability.json#/GlobalModifiers/MAvatar_GlobalSkill_Castorice_DeathTime/_CallbackList/1/CallbackConfig/1/FailedTaskList/0` 请求 `AbortModifierPhasePerform`。Archer 插入取消分支可静态请求自身，同时具 `PreCheck.Type:"AbilityOwnerInsertUnusedCount"` 及数量 1。自定义事件也有静态和动态 `MaxNumber`，例如 `Config/ConfigAbility/BattleEvent/FantasticStoryHard_Ability_7.json#/GlobalModifiers/Modifier_FantasticStory_BaseAbility_2260_plus2_sub/_CallbackList/0/CallbackConfig/0/MaxNumber` 为固定 1。该数字属于请求字段，战斗级一次性回调仍无充分证据。
- **Observed**。`Config/GlobalConfig/GameCoreConstValue.json#/ForbidRecallModifierEventList` 有 12 个名称，含 `OnModifierAdd`、`OnModifierOnStack`、`OnListenModifierRemove`、`OnBeforeDealHeal` 和 `OnTriggerBreak`。同根 `ServantModifierEventWhiteList` 是空数组。**Inferred**。部分 Modifier 事件有专门的 Recall 策略入口。空表的默认策略、Recall 的运行时定义及选择器如何被抑制仍未知。通用的事件消费或取消协议未获证实，局部清理和取消插入各有可定位的配置。

## 派发与调度的候选模型

| Hypothesis | 能解释的数据 | 判别所需证据 |
| --- | --- | --- |
| 部分同步嵌套 | 命中前的伤害数据写入、参数实体和选择器分支可由同一调用过程承接；Recall 列表可用于部分重入规则。 | 监听是否与原始伤害共享同一调用帧，嵌套是否阻塞外层。 |
| 显式请求与延迟处理 | 插入请求含检查、取消、目标与优先级；延时任务和等待节点表达后续动作。 | 待执行项由什么结构承载，`ActivePredicate` 何时读取状态。 |
| 按阶段成批派发 | 配置区分实体创建、入场、波次、回合、攻击、命中及状态寿命，另有排序字段。 | 分批边界、阶段的精确入口、每批投递次序。 |
| 多种派发机制并存 | 具名选择器、显式令牌、属性观察器与动画任务各有配置协议。 | 能将具体表面机制定位到同一或不同调度器的实测轨迹。 |

静态偏序可以标明某条件的分支体、等待节点的后续任务、发出请求后才可能收到对应事件，以及显式的引用依赖。对同一任务列表、多个监听者或多个调度请求，数组下标和名字无法单独确定实际提交时序。线程、队列、栈、调用帧、事件参数生命周期均为 **Unknown**。

## 研究命题

| ID | 等级 | 命题 |
| --- | --- | --- |
| CBK-001 | Observed | 具名 Modifier 选择器、Ability 直接钩子、属性观察器、行为旗标回调与动画记录存在各自的配置结构。 |
| CBK-002 | Derived | `(4,13)` 的发出请求、全局旗标声明、接收条件以及下游写值能静态对接。 |
| CBK-003 | Observed | 监听优先级、事件 `SortBy`、请求 `MaxNumber` 与 Recall 名单均有配置证据。 |
| CBK-004 | Derived | Claymore 的具名动画等待可跟随角色配置导入，关联对应逻辑动画记录。 |
| CBK-005 | Inferred | 伤害数据、当前目标、传入实体及状态持有者可成为不同的上下文角色，共同支持过滤后的跨实体响应。 |
| CBK-006 | Unknown | 同步与延迟的运行时边界、通用事件消费协议、跨宿主排序及内部调度实现。 |
