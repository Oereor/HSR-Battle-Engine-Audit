# 02 · 战斗配置操作

## 范围与分类

本专题将一个带字符串 $type、直接占据已识别任务槽的对象计为一个**配置操作候选**。统计单元是 JSON 节点，定义单元是完整序列化类型字符串。任务、选取器、表达式、判定和状态容器可以都具有 $type。数组成员、标识前缀、名称中的 Damage 或 Trigger 各自都不足以判断操作角色。用任务槽建立角色证据后，再用原始节点的字段、相邻条件、上下文与后续引用解释该操作。证据等级沿用研究规范。

本地 4.7.0 公共索引 v1 提供 4,636 种类型的全部位置。 [目录构建器](catalogue.py) 从索引选出下列范围，再按文件回读各选中节点，对全部 364,136 个定位核对 $type。输入字段和字段形态通过这些精确节点聚合。全量主清单、位置、样本和统计口径见 [inventory.md](inventory.md)。

| 结构范围 | 类型数 | 节点数 | 证据和用途 |
| --- | ---: | ---: | --- |
| 核心任务槽 | 980 | 296,845 | Ability、Modifier、具名模板等锚点和已确认的配置树。也从实时活动的实际文件路径补录 v1 尚未建立的定义锚点 |
| 相邻任务槽 | 313 | 65,011 | 战斗 AI、动画事件、召唤单元、角色接线、战斗表现与可识别的场景脚本。保留同形表现操作 |
| 专用战斗玩法 | 138 | 2,280 | DiceCombat、ChenLingBattle、PixAir、ConfigChessAbility 的任务槽及可识别专用效果家族。其中可能包含以任务槽承担控制流的判定节点 |
| 合并去重 | 1,279 | 364,136 | 同一类型可以跨范围，节点的范围标签互斥。260 种为十一位大写字母标识，191 种只在选区出现一次 |

核心角色判定主要用 OnStart、OnAdd、OnRemove、CallbackConfig、TaskList、SuccessTaskList、FailedTaskList 等，另有嵌套的 OnProjectileHit、OnBattleEventCreate、OnInsertAbort、PerformTaskList、OnEnterRange 等。Role 可以跨类型复用。事件序列 EventList、OnEnter 与 OnExit 中可见表现任务。PredicateList 下的 ByAnd 成员、TargetSequence 的 Sequence 成员以及 AttackProperty 中的 AttackData 数据结构单独保留为支持结构。MakeSuccess 的单对象 Task、SwitchCase 的 DefaultTask、FireWaveProjectile 的 PerProjectileDamage 允许直接嵌套任务，无需数组包装。

非助记字段采用明确样本登记。RtBattle Aventurine 的 /AbilityList/1/Modifiers/RTMAvatar_Aventurine_Skill02_BounceCoin/_CallbackList/0/CallbackConfig/0/ELGMGKGMCCM 下同时出现 Retarget、PredicateTaskList 与 LoopExecuteTaskListWithInterval。FuXuan 的 /GlobalTemplates/0/TaskList/0/SuccessTaskList/0/FailedTaskList/0/SuccessTaskList/1/CABHEAGLNDD 下同时出现 DefineDynamicValue 与 SetDynamicValue。由此纳入槽位，外层不透明类型的控制时序仍为 Unknown。原始路径分别为 Config/Activity/RtBattle/Ability/Avatar/RtBattleAvatar_Aventurine_00_Ability.json 和 Config/Activity/RtBattle/Ability/Avatar/RtBattleAvatar_FuXuan_00_Ability.json。

全量清单中的结构、计数和定位均为 Observed。手工阅读覆盖了下文和注释表中的代表类型，其他类型保留 Unknown 的运行时语义。候选语义标签使用名字便于检索，不能作为定义。路径和槽位覆盖之外的 691,981 个同形位置留在 [review-outside.tsv](review-outside.tsv)，包括大量探索脚本。编辑器 layout 与文本表遵守公共索引排除口径。专用玩法家族规则可能遗漏其他独立语言的本地容器，外部候选和公共任意类型反查使这部分可继续核对。

## 伤害、韧性、治疗、护盾

### 基本伤害与命中表达

**OPS-001 · Observed／Derived。** RPG.GameCore.DamageByAttackProperty 在不同主体和攻击入口之间复用，损伤类型、目标、比例以及附带语义通过字段变化传入。以下片段为原始对象中的值摘录。

| 原始文件及 JSON Pointer | 原始结构与绑定 | 能确认的边界 |
| --- | --- | --- |
| Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json · /AbilityList/1/OnStart/7 | Ability 名 Avatar_Asta_00_Skill01_Phase02。TargetType.Alias 为 AbilityTargetEntity，AttackProperty.DamageType.DamageType 为 Fire，DamagePercentage.PostfixExpr.DynamicHashes 为 [-1126825319] | CharacterConfig 入口另见 Config/ConfigCharacter/Avatar/Avatar_Asta_00_Config.json 的 /SkillList/0/EntryAbility，串接 /AbilityList/0/OnStart/1 的 TriggerAbility。该伤害样本的 AttackType 缺省 |
| Config/ConfigAbility/Avatar/Avatar_Himeko_00_Ability.json · /AbilityList/9/OnStart/7 | Ability 名 Avatar_Himeko_Passive1Atk02_Ability。TargetType.Alias 为 AllEnemy，AttackProperty.AttackType 为 Insert，DamagePercentage 动态哈希为 [1246667513] | /AbilityList/7/Modifiers/Avatar_Himeko_Passive1_Modifier/_CallbackList/0/CallbackConfig/0/SuccessTaskList/0/SuccessTaskList/0/SuccessTaskList/0 静态请求 Passive1Atk_Ability，由 /AbilityList/8/OnStart/0/SuccessTaskList/7 调用 Passive1Atk02_Ability |
| Config/ConfigAbility/Monster/Monster_W1_Bronya_00_Ability.json · /AbilityList/1/OnStart/1/OnProjectileHit/0 | AttackProperty.AttackType 为 Normal，DamageType 为 Wind，TargetType.Alias 为 AbilityTargetEntity | 伤害节点归属投射命中钩子。该位置证明配置有命中挂点，数组位置无法证明逐帧或即时执行 |
| Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json · /AbilityList/19/OnStart/5 | TargetType.Alias 为 AllEnemy，AttackProperty.AttackType 为 Insert，伤害比例包含两个动态哈希，StanceValue.FixedValue.Value 为 30 | 数值模板不限定单一目标或固定值。30 是源字段，不等于任意游戏状态中的实际损伤 |

**OPS-002 · Observed。** 可分离的组成项与任务合并两种形态共存。上一组样本把目标与 AttackData 分列，同一个 AttackData 把伤害数值、StanceValue、SPHitRatio、HitAnimation 和 HitEffect 等字段组合为整体。Activity Lycan 的 Config/ConfigAbility/Activity/Avatar/Avatar_AvatarChange_W2_Lycan_00_Ability.json · /AbilityList/1/OnStart/4 同时展示独立 DamageStance，配置 DefenderTargetType、StanceValue、IgnoreAttackerAddRatio 与 TriggerCountDown。Monster Vtuber 的 Config/ConfigAbility/Monster/Monster_W5_Vtuber_00_Ability_IF.json · /AbilityList/3/OnStart/4 把受击方指定为 Caster，并显式 ForceStanceDamage、IgnoreMuteBreak。独立韧性任务与 AttackData 内联参数由此均可见。Klara 在 Config/ConfigAbility/Avatar/Avatar_Klara_00_Ability.json · /AbilityList/3/OnStart/3 使用 FireWaveProjectile，并在 /PerProjectileDamage 保留同一伤害类型。Monster Svarog 同样嵌入该任务，见 Config/ConfigAbility/Monster/Monster_W1_Svarog_00_Ability.json · /AbilityList/9/OnStart/4/PerProjectileDamage。FireWaveProjectile 的 Count、Interval、Projectile、WaitProjectileFinish 和 OnProjectileHitClientOnly 提示配置支持打包多步行为。客户端标识描述配置字段，实际逻辑执行位置未知。

ModifyDamageData 提供另一条接口。光锥的 Config/ConfigAbility/Equip/EquipmemtAbility.json · /AbilityList/95/Modifiers/MEquip_23020_Main/_CallbackList/0，Event 为 OnBeforeHitAll，前置任务含 SetDynamicValueByStatusCount，CallbackConfig/2 写 Attacker_CriticalDamage。遗器的 Config/ConfigAbility/Equip/RelicAbility.json · /AbilityList/2/Modifiers/MRelic_102_Main/_CallbackList/0 在同名 Event 内经过 PredicateTaskList 后使用同类型。符玄的 Config/ConfigAbility/Avatar/Avatar_FuXuan_00_Ability.json · /GlobalModifiers/MAvatar_FuXuan_00_HitDamageSplit/_CallbackList/1/Event 为 OnBeforeBeingHitAll，分支中的 HitDamageSplit 携带 SplitTarget.Alias 为 Caster、SelfSplitRatio 与 TargetSplitRatio。**Inferred**，配置从攻击侧与受击侧开放不同形式的结算上下文接口。回调的 All 粒度、多个修正的合成和伤害公式仍为 Unknown。Acheron 的 /AbilityList/1/OnStart/3 显式存在 DamagePerformFinish。该类型的其他样本出现 SkipDeathSettlement 字段，证据最多到配置显式声明一个结束位及可选设置。

### HP 与护盾操作

| 原始证据 | 可确认内容 |
| --- | --- |
| Config/ConfigAbility/Avatar/Avatar_Natasha_00_Ability.json · /AbilityList/3/OnStart/4；Config/ConfigGlobalModifier/GlobalModifier_Common_Gluttony.json · /ModifierMap/MCommon_Gluttony_LV2/TaskListTemplate/0/TaskList/0/SuccessTaskList/16 | HealHP 跨角色与公共规则复用。两例 FormulaType 分别为 HealByHealerMaxHP 和 HealByTargetMaxHP，后例 HealPercentage.FixedValue.Value 为 1。Observed |
| Config/ConfigAbility/Avatar/Avatar_MortenaxBlade_00_Ability.json · /AbilityList/5/OnStart/1 | LoseHPByRatio 配置自己为目标、RatioType 为 MaxHP、Floor.FixedValue.Value 为 1，并标记 BPSkill。生命支付 API 的资源扣除时序未知。Observed |
| Config/ConfigAbility/Avatar/Avatar_Mar_7th_00_Ability.json · /GlobalModifiers/MAvatar_March7th_00_BPSkill_Shield/_CallbackList/3/CallbackConfig/1 及 /GlobalModifiers/MAvatar_March7th_00_BPSkill_Shield/_CallbackList/1/CallbackConfig/0 | OnStack 下 InitShield，FormulaType 为 ShieldByCasterDefence，目标为 ModifierOwnerEntity。OnDestroy 下 RemoveShield。Observed |
| Config/ConfigAbility/Monster/Monster_AetherDivide_Add_Ability.json · /AbilityList/0/Modifiers/MMonster_AetherDivide_Add_Challenge_01_Gepard_Shield_Shield/_CallbackList/2/CallbackConfig/0 | 同一个 InitShield 类型使用 ShieldByTargetMaxHP。护盾和 Modifier 相联且有独立任务接口。护盾覆盖、来源身份和吸收顺序未知。Observed |

## 状态、资源和上下文组合

Asta 的 OnStart 所载 AddModifier 使用 ModifierName.Value 为 M_Asta_Passive 和目标 Caster。源节点为 Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json · /AbilityList/7/OnStart/0，定义为同文件 /AbilityList/7/Modifiers/M_Asta_Passive。行迹 /AbilityList/9/Modifiers/M_Asta_Tree02/_CallbackList/0/CallbackConfig/0 则通过 RemoveModifier 引用同文件 /GlobalModifiers/MAvatar_Asta_FireAddedRatio，并以 TargetConcat 组合 AllTeamMember 与 AllUnselectable。该全局定义在 /GlobalModifiers/MAvatar_Asta_FireAddedRatio/_CallbackList/0/CallbackConfig/0 用 StackProperty 给 ModifierOwnerEntity 配置 FireAddedRatio。这为目标查询、状态应用、状态持有者属性与移除分别建模提供 **Derived** 证据。RemoveModifier 的字段还允许 OnlyRemoveCasterAdded 与 RemoveAllInstance，DispelStatus 另用 BehaviorFlags、BuffType、Numbers、Order。不能据此确定所有移除的回调和数量语义相同。

数值与变量操作共享动态表达式形态。上述 Asta StackProperty 与 DamageByAttackProperty 共同出现 IsDynamic/PostfixExpr。Tingyun 的 Config/ConfigAbility/Avatar/Avatar_Tingyun_00_Ability.json · /GlobalModifiers/MAvatar_TingYun_ByIsTingYun/_CallbackList/0/CallbackConfig/0 使用 Retarget，从 AllLightTeam 按 ByIsContainModifier 过滤，ByRandom 为 true，MaxNumber 为 1，再在 TaskList/0 用 SetDynamicValueByModifierValue 从 ParamEntity 读取同名 Modifier 的 LifeTime 到 TingYun_EnergyBarLayer。副作用任务的直接目标和读源处于不同字段。数据不显示随机分布、发生时点或新上下文栈帧。

资源操作复用了相同的选择器与动态值接口，资源本身存在多个独立类型。

| 入口 | 任务和最小证据 | 等级与局限 |
| --- | --- | --- |
| Config/ConfigAbility/Avatar/Avatar_Tingyun_00_Ability.json · /AbilityList/3/OnStart/18 | ModifySPNew，TargetType.Alias 为 Caster，AddRatio.FixedValue.Value 为 1 | Observed。该节点只是其技能内一项 SP 变更 |
| Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json · /AbilityList/19/OnStart/10 | ModifySpecialSP，TargetType.Alias 为 Caster，FixedAddValue 的动态哈希为 21888035 | Observed。独立类型证明该路径显式选择特殊 SP 接口，动态存储结构 Unknown |
| Config/ConfigAbility/Avatar/Avatar_Sparkle_00_Ability.json · /AbilityList/7/OnStart/2/FailedTaskList/0 与 /AbilityList/9/Modifiers/Avatar_Sparkle_00_PassiveSkill_Listen/_CallbackList/1/CallbackConfig/0 | ModifyTeamBoostPoint 与 ModifyTeamBoostPointMax 都使用 ModifyFunction=Add，分别传入动态值 | Observed。队伍资源和上限可分别配置，退款、替代支付策略与封顶均需单独追踪 |
| Config/ConfigAbility/Avatar/Avatar_Aglaea_00_Ability.json · /AbilityList/3/OnStart/1/SuccessTaskList/0；ExcelOutput/AvatarServantConfig.json · /0/ServantID | CreateServant 直接传入固定 ID 11402，且携带 DynamicValues；Excel 行 ID 相同 | Derived。ID 有静态连接，召唤主外属性传递和自然行动资格仍需实体资料 |
| Config/ConfigAbility/GridFight/3.5/Monster/Monster_GridFight_FireProwler_00_Ability.json · /AbilityList/7/OnStart/6 | SummonMonster 的 SummonMonsterDataList 含四项、每项从同哈希读 ID，另有 DelayRatio=0 的固定配置 | Observed。单配置对象可包含多实体请求 |

## 能力调用、行动和流程结构

**OPS-003 · Observed／Derived。** TriggerAbility、TurnInsertAbility、TurnInsertAction、SetActionDelay 和 ModifyActionDelay 在不同实例中有独立位置与输入。

- Asta 的入口 /AbilityList/0/OnStart/1（Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json）在 TriggerAbility 指定同文件 Phase02，并有 TargetType.Alias=Caster、IsSkillPerform=true。Himeko 的 TurnInsertAbility 则并列请求目标、AbilityTarget、AbortBehaviorFlags、InsertAbilityPriority 和 ShowInActionBar，位置见上文。
- Config/ConfigAbility/Avatar/Avatar_Boothill_00_Ability.json · /AbilityList/5/OnStart/4 采用 TurnInsertAction，PrepareAbilityName 为 Avatar_Boothill_00_Bonus，CancelPrepareAbilityIfDelayed 为 true。战斗事件 Config/ConfigAbility/BattleEvent/Avatar_MissionBattleEvent60059_Ability.json · /AbilityList/1/OnStart/6 则指定可接目标及 InsertActionPriority=Character_ChainSkill。其他样本可写 IgnoreBPDec、IgnoreSPDec、OnInsertAbort、PreCheck，表明资源扣除开关和资格检查字段可独立表达。
- Config/ConfigAbility/Avatar/Avatar_Bronya_00_Ability.json · /AbilityList/3/OnStart/6 SetActionDelay 输入 Value.FixedValue.Value=0。Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json · /ModifierMap/RedStanceState/_CallbackList/0/CallbackConfig/1 的 ModifyActionDelay 输入 AddNormalizedValue.FixedValue.Value=0.25。Config/ConfigAbility/Avatar/Assistant/Avatar_Asta_00_Assistant.json · /AbilityList/1/OnStart/2 又提供固定 -0.35 的同类归一化增量。除这两种外还有相对目标的 SetActionDelayNearTarget 和显式锁定参数的 LockActionDelayChange。没有足够证据换算绝对行动值或等价为立即行动。
- Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json · /TaskListTemplate/0/TaskList/0 用 TriggerModifierCustomEvent 配置 EventType={"EnumIndex":4,"Value":13}，目标为 BattleAllEntity.GetAliveOrLimbo。仅能确认发出请求的显式字段，接收者顺序和同步性 Unknown。
- Config/ConfigAbility/ElationBattle/Avatar_ElationBattle_Sparkle_00_Ability.json · /AbilityList/3/OnStart/6/TaskList/0/TaskList/6 的 PerformDelayExecute 有固定 Delay=0.4 及 PerformTaskList 中的 VCameraConfigChange。Config/ConfigAbility/Avatar/Avatar_SilverWolf999_00_Ability.json · /AbilityList/19/OnStart/7/TaskList/2/FailedTaskList/0 写动态 Delay，并委派 TriggerAnimState，说明表现调度有显式延后容器。由此不能证明战斗结算等待同一计时器。

PredicateTaskList 的 Predicate、SuccessTaskList、FailedTaskList 构成局部条件关系。Retarget 同时含目标、筛选、随机与 TaskList，表示目标和调用能组合在同一任务，也说明这些职责并非处处正交。循环由 LoopExecuteTaskList、LoopExecuteTaskListWithInterval 与 ConditionLoopExecuteTaskList 等形态承载，最大次数、间隔和谓词可分别出现。模板 Acheron 调用 Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json · /AbilityList/19/OnStart/6/TaskList/0 指定 Name=Bounce_SelectTarget、TemplateParamSequences.ParamTaskList.TaskList 中的实参是 DamageByAttackProperty。具名模板定义位于 Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json · /TaskListTemplate/30，/TaskList/0 为 GLOABNLLLEL，/TaskList/0/TaskList/0 是 TaskTemplateFetchParamSequence。**Derived** 有静态名称及任务参数的对应，模板是否原地展开、何时为每个目标生成调用帧仍为 Unknown。

## 罕见、专用和复合接口

**OPS-004 · Observed。** Config/ConfigAbility/Avatar/Avatar_HimekoNova_00_Ability.json · /GlobalModifiers/MAvatar_HimekoNova_00_AssistAsBpSkill/_CallbackList/1/CallbackConfig/0 是全索引唯一 AddRegardAsSkillType 样本，值为 OriginalSkillType=Assist、RegardSkillType=Skill，目标为 ModifierOwnerEntity。相同 Modifier 的 /_CallbackList/0/CallbackConfig/0 是唯一 ClearRegardAsSkillType 样本，仍给出 Assist 和同形目标。事件选择分别是 OnStack 与 OnDestroy。同一配置可显式映射技能分类语义，但作用域、与其他类型覆盖的优先级以及单例类型能否用于任意角色都为 Unknown。

GridFightOverrideBackEndHP 单例嵌在 Config/ConfigAbility/BattleEvent/GridFight/4.7/AvatarAbility/BattleEvent_GridFight_S2_Castorice_00_Ability.json · /AbilityList/4/OnStart/1/SuccessTaskList/0/OnBattleEventCreate/6。其类型名和出现位置支持专用模式接口存在，BackEnd 指向何种系统仍为 Unknown。欢愉活动的 ElationActivityActionBarAbilityChange 位于 Config/ConfigAbility/ElationBattle/Avatar_ElationBattle_Aventurine_00_Ability.json · /AbilityList/3/OnInsertAbort/0。实时玩法另有 RtInsertSkill，其 TargetType、SkillTargetType、Priority、SkillName 同时出现，不能据字段名将其与主配置 TurnInsertAbility 同义替换。两种小玩法分别用 DiceCombatTaskConfig_AttackDamage、ChenLingBattleEffect_ApplyDamage 完成独立语法的伤害表达，证据见 Config/Gameplays/LittleGame/DiceCombat/DiceCombatSkill_1003.json · /InsertAbilitys/0/OnStart/4 和 Config/Gameplays/ChenLingBattle/Skills/ChenLingBattle_AreaAttack_Skill.json · /PromotionAbility/AbilitySequence/1/Effects/0。不透明节点、模式家族专用节点和有界的通用原语均进入清单。专用名字可证明参与该配置；本调查没有证据据此归属某段官方硬编码实现。

**OPS-005 · Unknown。** 单个任务类型可以引用其他 Ability、委派可配置子任务、加状态后响应事件，或封装命中、表现和多个属性变化。就配置而言，原子性只表示被引用的声明粒度。即使通过名字、槽位、监听者和触发请求重建了静态可达，也无法推出任务不可重入、可回滚、落入某个队列或按数组顺序结算。同步调用、显式排队、事件分批与带优先级的混合实现都可以实现这些接口。完整的运行时证据缺口在执行器、上下文绑定和事件/调度跟踪。

## 验证与复查入口

[源索引与工具说明](../index/README.md)、[全量清单构建](catalogue.py)、[类型和字段查表](inventory.md)、[源节点检查](validate.py)、[复算输出](catalogue.log)、[校验结果](validation.log)。独立检查核对了全部类型的分组频数、各交叉样本的源字段值以及目标模板、召唤 ID 和技能类别映射。清单重新打开所有选中源节点，逐一验证游标定位和类型匹配。

符号状态遵循 v1 公共索引规则。AddModifier.ModifierName 中 27,915 个为同作用域匹配，5,416 个为全库单候选，108 个含多个候选，150 个暂未匹配。TurnInsertAbility.AbilityName 有 8 个未匹配。补充解析 5,715 个 IncludeTaskListTemplate.Name 字面值，其中 3,888 个同作用域，1,736 个全库单候选，91 个多候选。配置装载、隐式作用域和动态表达式不能由名称匹配补全。[符号状态](symbol-links.tsv)、[模板状态和定位](template-links.tsv)
