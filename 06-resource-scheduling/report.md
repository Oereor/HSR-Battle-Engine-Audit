# 06 · 资源、行动调度与结算控制

本专题使用公共索引 v2 和 01–03 的实体、任务、状态口径。源数据定位由文件相对路径与零基 JSON Pointer 组成。文中的顺序关系来自引用、分支归属、显式事件选择或配置参数。数组下标仅作定位。标准能量、队伍战技点和角色专属值在同一层拥有独立配置接口，行动编辑与请求又有各自的输入和资格检查。可以证实为配置可见的待处理顺序条件，运行时容器、优先级比较方法、全局结算和费用提交时刻均为 Unknown。

## 资源接口与支付边界

| 资源 | 原始证据 | 可证规则及限制 |
| --- | --- | --- |
| 标准能量 SP | ExcelOutput/AvatarConfig.json · /22/SPNeed/Value=130。ExcelOutput/AvatarSkillConfig.json · /940，SkillID=120203、SkillTriggerKey=Skill03、SPNeed.Value=130。Config/ConfigAbility/Avatar/Avatar_Tingyun_00_Ability.json · /AbilityList/6/OnStart/7/FailedTaskList/0 使用 ModifySPNew，向 AbilityTargetEntity 配置 FixedAddValue 与 Tag。Config/ConfigAbility/Avatar/Avatar_Huohuo_00_Ability.json · /AbilityList/6/OnStart/1 使用同类型的 FixedAddMaxSPRatio，目标 AllTeammateOnlyAddSPOnceForServant | Observed。SP 的数值和比例分开。配置别名体现召唤相关过滤，能量归属和实际去重由运行时决定 |
| 队伍 BP | ExcelOutput/AvatarSkillConfig.json · /1751，SkillID=120202、BPNeed.Value=1。Config/ConfigAbility/Avatar/Avatar_Sparkle_00_Ability.json · /AbilityList/7/OnStart/2/FailedTaskList/0 使用 ModifyTeamBoostPoint/Add。公共操作表的 ModifyTeamBoostPoint 样本无显式实体目标 | Observed。另有独立 ModifyTeamBoostPointMax 和 StackAdditionalTeamBoostPoint，详见下文。战技点与标准能量的内部组件边界 Unknown |
| 实体 BP 与专属资源 | Config/ConfigAbility/Avatar/Avatar_DanHengIL_00_Ability.json · /AbilityList/15/Modifiers/MAvatar_DanHengIL_PassiveModifier/OnDynamicValueChange/1/Ranges/0/OnChange/0 和 Config/ConfigAbility/Avatar/Avatar_Sparxie_00_Ability.json · /AbilityList/12/OnStart/6 使用 ModifyEntityBoostPoint，分别对 ModifierOwnerEntity 与 Caster 配置 Set | Observed。实体 BP 可和私有变量、Modifier 层、显示数据并用。替代支付的精确扣减优先级 Unknown |
| 特殊 SP | ExcelOutput/AvatarSkillConfig.json · /2561/SPNeed/Value=9、/4221/SPNeed/Value=12。同角色 Ability 分别采用 ModifySpecialSP。两例在下面展开 | Observed。SPNeed 同一字段出现在不同资源角色，不能仅凭它推断支付存储 |
| 生命 HP | Config/ConfigAbility/Avatar/Avatar_Natasha_00_Ability.json · /AbilityList/3/OnStart/4 的 HealHP 使用 HealByHealerMaxHP 和目标别名。Config/ConfigAbility/Avatar/Avatar_MortenaxBlade_00_Ability.json · /AbilityList/5/OnStart/1 的 LoseHPByRatio 使用 Caster、MaxHP 和 Floor=1 | Observed。治疗、生命消耗和伤害配置有不同任务簇。Floor 是该节点指定值。生命费用是否可统一退款不明 |
| 韧性 Stance | ExcelOutput/MonsterConfig.json · /0/StanceModifyRatio/Value=1。Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json · /AbilityList/1/OnStart/7/AttackProperty 中有 StanceValue。Config/ConfigAbility/Monster/Monster_W5_Vtuber_00_Ability_IF.json · /AbilityList/3/OnStart/4 单列 DamageStance，携带 StanceDamageType、StanceValue、ForceStanceDamage、TriggerCountDown | Observed。可随攻击携带或直接作用。状态转换、弱点倍率与取整算法 Unknown |

这里把可见配置中处理终结技容量和恢复的接口记作 SP，把队伍战技点操作记作 BP。BySkillPointActivated 配有 PointTriggerKey，例如 Acheron 角色的 PointB1，属于行迹资格信号。它与 OnListenBpChange 和 ByCompareBP 的用法不同。Excel 中 BPNeed=-1 只登记原始数值。增强普攻同类结构下能显式取 1、2、3，不能把 AttackType=Normal 读成没有 BP 成本。

加减可以复用同一配置原语。花火的 ModifyTeamBoostPoint/Add 对照 Config/ConfigAbility/Avatar/Avatar_TohsakaRin_00_Ability.json · /AbilityList/5/OnStart/6/FailedTaskList/0/TaskList/0，其 ModifyFunction 同为 Add，ModifyValue.FixedValue.Value=-1。Config/ConfigAbility/BattleEvent/Avatar_RogueBattleevent123_Ability.json · /AbilityList/4/Modifiers/MAvatar_RogueBattleevent123_Limbo2/_CallbackList/0/CallbackConfig/0/SuccessTaskList/0/SuccessTaskList/5 使用常见的 ModifySPNew，FixedAddValue.FixedValue.Value=-100。**Observed**，队伍 BP 和标准 SP 两者均可接受符号增量。这些是配置实例，不能推出所有常规技能的成本都由同样任务发起。

### SCH-001 · 技能费用、资格和支付可独立配置

**Derived。** Archer、DanHengIL、Phainon 可将 Excel 的 SkillTriggerKey 连到 CharacterConfig 的 SkillList/Name，EntryAbility 再连到 Ability 定义。费用键在 Excel 行，释放资格也可来自另外的 UsableConditions、战技禁用 Modifier 或请求中的 PreCheck。原始支付路径可以经过通用消费，显式配置中的充值、费用提交调整或特殊资源门控只覆盖各自见到的节点。

| 入口链 | 可读出的费用或资格 |
| --- | --- |
| ExcelOutput/AvatarConfigLD.json · /1（AvatarID=1015）→ ExcelOutput/AvatarSkillConfigLD.json · /76（SkillID=101502、Level=1）→ Config/ConfigCharacter/Avatar/Avatar_Archer_00_Config.json · /SkillList/1/EntryAbility | Skill02 声明 BPNeed.Value=2，Ability 为 Avatar_Archer_00_Skill02_Phase01 |
| ExcelOutput/AvatarSkillConfig.json · /1333、/1342、/1351 → Config/ConfigCharacter/Avatar/Avatar_DanHengIL_00_Config.json · /SkillList/3 至 /SkillList/5 | Skill11、Skill12、Skill13 的 BPNeed.Value 分别为 1、2、3，AttackType 全为 Normal。/1360 的 Skill02 本身记录 BPNeed=-1。按钮和强化攻击有不同入口 |
| Config/ConfigCharacter/Avatar/Avatar_Phainon_00_Config.json · /SkillList/2/UsableConditions/0/UsableCondition 与 /SkillList/4/UsableConditions/0/UsableCondition | 第一个是反转的 ByTargetListAny，筛 SpecialBattleArea 行为旗标。第二个检查自身是否拥有 MAvatar_Phainon_00_Ultra。/SkillList/2 与 /SkillList/4 同时保有 EntryAbility |
| Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json · /ModifierMap/MCommon_Windfury_SkillNoNeed/_CallbackList/1 | OnBeforeSkillCost 在目标交集和回放标识条件下调用 ModifySkillPropertyByType，Properties 显式列 BPNeed。缺少 Value 的语义未知。另有可确定固定取值的丹恒样本 |

OnBeforeSkillCost 是可确认事件选择值。Config/ConfigAbility/Avatar/Avatar_Gilgamesh_00_Ability.json · /GlobalModifiers/Avatar_Gilgamesh_00_UltraSPListener/_CallbackList/0 在该事件下按 SkillType=Ultra 保存 IsUltraSkill。Config/ConfigAbility/Equip/Equip44.json · /AbilityList/2/Modifiers/MEquip_23062_UltraDamageUp/_CallbackList/0 同样记录 Ultra 标志。战斗模式还可储存待扣费用变量，见 Config/ConfigAbility/BattleEvent/GridFight/4.7/SeasonAbility/GridFight_SpotLight_01.json · /AbilityList/19/Modifiers/MStageAbility_GridFight_SpotLight_131000018_UnitEffect/_CallbackList/3 的 MDF_PendingSPCost、MDF_SPCostToDeduct。几个样本支持费用具有可感知配置阶段。它们未确定 UI 承诺、实际扣除、退还、某次失败与伤害启动之间的完整偏序。

### SCH-002 · Archer 的连发、退款候选和专用取消路径

本段配置均在 Config/ConfigAbility/Avatar/Avatar_Archer_00_Ability.json。Excel 对应 LD 行见上表。

1. /AbilityList/2/OnStart/7 明示 TriggerAbility 指向 /AbilityList/3，后者在 /OnStart/1 增加 MAvatar_Archer_00_BonusTrigger，在 /OnStart/8 有 DamageByAttackProperty。/OnStart/13 从 Skill02 的 BPNeed 读到 MDF_BPNeed。/OnStart/14/Predicate/PredicateList/0 是 ByCompareBP，比较方式 GreaterEqual，输入哈希 494116178。/OnStart/14 的成功与失败分支写 MDF_InBonus=1 或 0，同时依赖使用次数和 MCommon_Windfury。动态表项 /AbilityList/3/DynamicValues/Floats/494116178 的 ReadInfo.Type 为 None，此处不把它化简为固定 2。
2. /GlobalModifiers/MAvatar_Archer_00_BonusTrigger/_CallbackList/1 监听 OnListenAfterAction。/CallbackConfig/0 同时判断未用 Ultra 与未用插入 Ability 数量。/CallbackConfig/1/SuccessTaskList/1/SuccessTaskList/0 使用 TurnInsertAction，字段有 SkillType=ControlSkill02、CanInsertUltraSkill=true、FollowSameTagNormalAction=true、CustomTags.Value=Archer_Bonus。其 OnInsertAbort 归零 MDF_InBonus 并 RemoveSelfModifier。失败分支还能按 CasterIs、ActionTypeIs=Normal 及标签过滤下一未使用的插入行动。该请求表达一条条件下的新行动，基础费用实际扣除未在该任务中展平。
3. /AbilityList/3/OnStart/10 在 Rank1 哈希 2089636447 与 MDF_Skill02UseCount 比较成功后，用 ModifyTeamBoostPoint/Add 加回动态量。从 ExcelOutput/AvatarRankConfigLD.json · /6 可核对同角色 Rank1 和同哈希，参数原列表 [3,2]。角色配置的 `/DynamicValues/Floats/952868987/ReadInfo` 与 `/DynamicValues/Floats/1424168145/ReadInfo` 分别选择 Rank01 的 Index 0、1。按 AvatarConfigLD 的 RankIDList 联到 101501 后，门槛输入为 3，BP 增量输入为 2，等级为 **Derived**。返还的机制解释为 **Inferred**，实际提交及退还的时序仍未知。
4. 取消 UI 入口 Skill21 在 CharacterConfig /SkillList/2/EntryAbility 指向 /AbilityList/4，其 /OnStart/3 触发 /AbilityList/5。取消 Phase02 的 /OnStart/1、/OnStart/2、/OnStart/3 分别列出移除连发 Modifier、重置 MDF_InBonus、技能表演结束。该分支没有可见 BP 退款任务。/GlobalModifiers/MAvatar_Archer_00_BonusTrigger/_CallbackList/3 另以 OnListenInsertAbilityAbort 和资源不足、待处理计数为清理条件。两个取消路径支持显式反馈与资格恢复，涉及的回调触发边界 Unknown。

### SCH-003 · 丹恒·饮月、花火、火花有不同的支付状态表示

**Observed／Derived。** Config/ConfigAbility/Avatar/Avatar_DanHengIL_00_Ability.json 的 /AbilityList/9/Modifiers/MAvatar_DanHengIL_00_BPCost_1/_CallbackList/1 为 OnStack，/CallbackConfig/0 映射控制技能到 Skill11，/CallbackConfig/3 通过 ModifySkillPropertyByName 给该技能固定 BPNeed=1。/_CallbackList/0 为 OnDestroy，恢复 Skill01 并用 OperatorType=Unset 清除 BPNeed 覆盖。/AbilityList/9/OnStart/3 用 ByCompareBP 和成功、失败分支控制 Avatar_DanHengIL_00_BPDisable。该定义 /GlobalModifiers/Avatar_DanHengIL_00_BPDisable/_CallbackList/0 用 AttachSkillTypeDisable 禁用 ControlSkill02，/_CallbackList/1 在 OnListenBpChange 提供移除自身条件，/_CallbackList/2 在 OnInsertActionStart 重查。

同文件 /AbilityList/15/Modifiers/MAvatar_DanHengIL_PassiveModifier/_CallbackList/3 从 BP 事件读取 RawDelta，若 ParamEntity 与 Caster 匹配且 _BPChange<0，调用含 BPExChange 私有键的 LAJIKDENEOO。/AbilityList/15/Modifiers/MAvatar_DanHengIL_PassiveModifier/OnDynamicValueChange/1/Ranges/0/OnChange 将相关数据用于 ModifyEntityBoostPoint/Set、SetEnergyBarState 与 MAvatar_DanHengIL_00_BPCostChange 的层数或值，条件失败可移除显示状态。**Inferred** 角色通过私有储备与实体 BP 协作表达替代支付。确认了输入和反应，尚不能从不透明写操作和配置字段确定队伍与实体实际分担规则。

花火用队伍级接口。Config/ConfigAbility/Avatar/Avatar_Sparkle_00_Ability.json · /AbilityList/9/Modifiers/Avatar_Sparkle_00_PassiveSkill_Listen/_CallbackList/0 用 ModifyTeamBoostPointMax/Add，能力释放时的 /AbilityList/7/OnStart/2 用 ModifyTeamBoostPoint/Add。前者另有 /_CallbackList/1 给出第二个写上限的动态表达式。配置明确区分库存和容量，容量变动时如何截断或保留旧库存仍为 Unknown。Archer 的 /AbilityList/14/Modifiers/MAvatar_Archer_00_SkillTree03/_CallbackList/0 同时读当前 BP 及 UnclampedDelta，正增量且当前值达到门限后施加行迹 Modifier。可见未裁剪变化有独立观测字段，无法据此宣称超过上限的整笔成为可支付余额。

火花保留标准 SPNeed=160（ExcelOutput/AvatarConfig.json · /74），另有角色变量。Config/ConfigAbility/Avatar/Avatar_Sparxie_00_Ability.json · /GlobalModifiers/MAvatar_Sparxie_00_Passive01/_CallbackList/0 与丹恒样本共用 OnListenBpChange → RawDelta → 同主体负变动 → LAJIKDENEOO 结构，键改为 Sparxie_EnergyPoint。其 /OnDynamicValueChange/0 从哈希 1469843529 所指键读取变化，同范围指向 SetEnergyBarState、SetDynamicValueByChangeValue 与 MAvatar_Sparxie_00_EnergyPoint 的层变化。/_CallbackList/2 监听 OnListenElationTimeEnd，在 Rank2 分支对活敌条件请求 TurnInsertAction，同时操作私有键和 ModifyEntityBoostPoint。处理失败与 OnInsertAbort 都可挂 MAvatar_Sparxie_00_Rank02_InsertActionSave。/GlobalTemplates/3 是 Avatar_Sparxie_00_Skill02_GrandPrize，其 /TaskList/3 用 ModifyTeamBoostPoint/Add，单独表达队伍回补。技能 /AbilityList/3/OnStart/14 从 Skill21 的 BPNeed 取得 _BPNeed，ExcelOutput/AvatarSkillConfig.json · /5485 对应 Level1 BPNeed.Value=1。精确代扣、概率事件、费用可重新检查的先后顺序保留 Unknown。

### SCH-004 · 特殊 SP、溢出和事件回馈

**Observed／Derived。** Acheron 与 Phainon 两者都在 Modifier.OnStack 用 ModifySP/Set(0) 处理标准 SP，在独立路径改 ModifySpecialSP。前者使用特殊 SP + 作为溢出痕迹的 Modifier 层，后者可将溢出加到 Caster 的动态变量。

| 角色 | 源定位和可证路径 |
| --- | --- |
| 黄泉 | Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json · /GlobalModifiers/MAvatar_Acheron_00_BlockModifySp/_CallbackList/0/CallbackConfig/1 是 ModifySP、ModifyFunction=Set、值 0、IgnoreBlock=true。/GlobalModifiers/MAvatar_Acheron_00_OnListenDeBuffAdd/_CallbackList/0 使用 OnModifierOnStack 和 ByCheckModifierCallBackStatusType.TargetStatusType=Debuff，另查施放旗标和冷却 Modifier，成功条件下有 ModifySpecialSP.FixedAddValue=1。/AbilityList/15/Modifiers/MAvatar_Acheron_00_PassiveUltra/OnAbilityPropertyChange/0 监听 CurrentSpecialSP，TriggerClampedChange=true。/Ranges/0/OnChange/1 取得 ClampedAdd，满资源且正增量时加 MAvatar_Acheron_00_UltraSkillSpareCount_PointB1，并动态设置 MaxLayer 与 LayerAddWhenStack |
| 黄泉的回收 | 同文件 /GlobalModifiers/MAvatar_Acheron_00_UltraSkillSpareCount/_CallbackList/2 用 CallBack_SettleSkillOrInsertAbility 标记、SkillType=Ultra 及特殊 SP 比例<1 筛选 RemoveSelfModifier，/_CallbackList/0 的 OnDestroy 再带 ModifySpecialSP。该配置允许把一部分余量存进状态再回补。运行时何时截断、回补是否只发生一次与命中去重仍未知 |
| 白厄 | Config/ConfigAbility/Avatar/Avatar_Phainon_00_Ability.json · /AbilityList/24/Modifiers/MAvatar_Phainon_00_PassiveSkill01/_CallbackList/0/CallbackConfig/1 清标准 SP。/GlobalTemplates/1（Phainon_00_Passive_ChargeEnergyToGainSP）中的 /TaskList/0/TaskList/0 按 ByCompareSpecialSPRatio<1 分别执行 ModifySpecialSP+1 或给 ContextCaster 的 CurOverflowSpecialSP 加 1。/GlobalModifiers/MAvatar_Phainon_00_SPOverflow/_CallbackList/1 在 Ultra Modifier 移除且比例<1 时请求 RemoveSelfModifier，/_CallbackList/0 写溢出键为零并用参数再次调用充能模板 |
| 白厄的标准能量输入 | 同文件 /AbilityList/28/Modifiers/M_Phainon_00_SkillTree02_SubListener/_CallbackList/1 用 OnSPChange，在队友与技能标志条件下读 ParamValue2，后续分支以 ByCompareSPChangeTag.TagList=[{EnumIndex:6,Value:1}] 过滤，再传实参给特殊 SP 模板。作为可比较样本，藿藿普通能量恢复携带同形 Tag，停云写 Tag=1。具体枚举映射和数值换算只在相应样本确认 |

资源变化可以连到新 Ability 请求。Config/ConfigAbility/Avatar/Avatar_SilverWolf999_00_Ability.json · /GlobalModifiers/MAvatar_SilverWolf999_00_Ultra_Aura/_CallbackList/2/Event 是 OnListenBpChange，/CallbackConfig/0/SuccessTaskList/1/TaskList/0/SuccessTaskList/1 出现 TurnInsertAbility，指 Avatar_SilverWolf999_00_Item_Insert，定义在同文件 /AbilityList/22。AbilityTarget 为 AllEnemy，ActivePredicate 还检查 ParamEntity 上的 Ultra Modifier。HP 有对照，Config/ConfigAbility/Activity/ActivitySummon/ActivitySummon_Junk_BattleEvent_04_Ability.json · /AbilityList/12/Modifiers/Junk_BattleEvent_04_Status/_CallbackList/4，Event=OnHPChange，/CallbackConfig/0/SuccessTaskList/0/SuccessTaskList/4 请求 TurnInsertAbility。**Derived** 为静态可达。普通资源事件、阈值辅助器、队列和技能提交的相对时点为 Unknown。

## 行动编辑、请求、暂停和实体

### SCH-005 · 行动量与行动请求是不同配置结构

| 类别 | 样本及证据 | 限制 |
| --- | --- | --- |
| 速度与自然行动量输入 | Config/ConfigAbility/Avatar/Avatar_JingYuan_00_Ability.json · /GlobalModifiers/MAvatar_JingYuan_00_BattleEvent_SpeedUp/_CallbackList/0/CallbackConfig/1 配置 StackProperty.Property=SpeedDelta，/CallbackConfig/2/SuccessTaskList/0 另有 SetActionDelay(0)。知更鸟倒计时实体使用 StackProperty.BaseSpeed | Observed。速度修正与行动值设置分离。无法还原自然调度的速度曲线 |
| 相对或绝对行动值编辑 | Config/ConfigAbility/Avatar/Avatar_Bronya_00_Ability.json · /AbilityList/3/OnStart/6 的 SetActionDelay.Value=0。Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json · /ModifierMap/RedStanceState/_CallbackList/0/CallbackConfig/1 ModifyActionDelay.AddNormalizedValue=0.25。Config/ConfigAbility/Avatar/Assistant/Avatar_Asta_00_Assistant.json · /AbilityList/1/OnStart/2 则为 -0.35 | Observed。支持两种加量方向和显式设值。以常用途解释为提前或延后属 Inferred，零值不证明可以无条件立刻执行 |
| 手动 Ability 请求 | Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json · /AbilityList/0/OnStart/1 的 TriggerAbility 指同文件 Phase02，IsSkillPerform=true | Derived。静态调用关系，是否即时或嵌套 Unknown |
| 插入 Ability 或追加攻击请求 | Config/ConfigAbility/Avatar/Avatar_Himeko_00_Ability.json · /AbilityList/7/Modifiers/Avatar_Himeko_Passive1_Modifier/_CallbackList/0/CallbackConfig/0/SuccessTaskList/0/SuccessTaskList/0/SuccessTaskList/0 用 TurnInsertAbility，AbilityName=Avatar_Himeko_Passive1Atk_Ability，AbortBehaviorFlags=[STAT_CTRL,DisableAction]，InsertAbilityPriority=AvatarInsertAttackSelf | Derived。调用指向独立已命名配置；追加攻击样本并不建立自然回合 |
| 插入一次行动 | Archer 的连发 TurnInsertAction 见上文。Config/ConfigAbility/Avatar/Avatar_Boothill_00_Ability.json · /AbilityList/5/OnStart/4 附 PrepareAbilityName=Avatar_Boothill_00_Bonus、CancelPrepareAbilityIfDelayed=true。其他出现 IgnoreBPDec、IgnoreSPDec、OnInsertAbort 与 ActivePredicate | Observed。资格、准备阶段和成本开关独立可见。术语“额外回合”是否对应自然回合计时需额外证据 |
| 终结技插入 | Config/ConfigAbility/Avatar/Avatar_Archer_00_Ability.json · /AbilityList/3/OnStart/11 有 AITryInsertUltra。Config/ConfigAbility/BattleEvent/Avatar_MissionBattleEvent60025_Ability.json · /AbilityList/0/OnAdd/1 用 AutoUseUltraSkill。Config/ConfigAbility/BattleEvent/Heliobus_Action_Ability.json · /AbilityList/0/Modifiers/Modifier_Heliobus_Action_Ability/_CallbackList/4 使用 OnListenInsertUltraSkill、SetDynamicValueByWaitUltraCount 与计时消费 | Observed。可见请求、待用计数和事件输入，玩家插入窗口及优先级算法未知 |
| 暂停、重置及行为限制 | Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json · /TaskListTemplate/3/TaskList/0 是 PauseToTurnEnd.Pause=true，/TaskList/3 是 WaitForTurnEnd.GoNextImmediately=true。/TaskListTemplate/4/TaskList/6 也用 PauseToTurnEnd 但 Pause 省略。Config/ConfigAbility/Avatar/Avatar_HimekoNova_00_Ability.json · /AbilityList/33/OnStart/3/SuccessTaskList/0 是 ResetActionDelay.SkipTargetTurn=true。Config/ConfigAbility/Avatar/Avatar_Robin_00_Ability.json · /GlobalModifiers/MAvatar_Robin_00_Skill03Area_sub_disableAction 的 BehaviorFlagList=[DisableAction] | Observed。分开描述待回合结束、自然行动重置和主动行动禁用。省略 Pause 的默认值及回合计时的恢复约定不能用名称确定 |
| 战斗阶段 | OnActionPhaseBegin、OnListenBeforeTurnPhase1End、OnListenTurnPhase1Begin、OnListenTurnPhase2Begin、OnInsertAbilityStart/Finish/Abort、OnInsertActionStart/Finish 同时可见。[事件表](events.tsv) | Observed。阶段钩子存在。跨监听者排序、同名缩写关系和内部结算阶段数量 Unknown |

恢复边界也可显式配置。Config/ConfigAbility/Activity/Activity_FateBoss_Ability.json · /GlobalModifiers/MActivity_HeiShengBei_Endurance/_CallbackList/2 的 OnStack 使用 LockActionDelayChange，/_CallbackList/0 的 OnDestroy 使用同类型且 IsLock=false，目标指 ModifierOwnerEntity。/_CallbackList/1 的 OnPhase2 整体子任务为 RemoveSelfModifier。**Derived**，一条生命周期可静态连接状态清理与明确的解锁输入。暂停自然行动与屏蔽行动值修改仍属不同接口。

### SCH-006 · 计时事件、召唤与忆灵各有独立载体

- 知更鸟。Config/ConfigAbility/Avatar/Avatar_Robin_00_Ability.json · /GlobalModifiers/MAvatar_Robin_00_Skill03Area_sub/_CallbackList/1 使用 OnStack 创建 EventID=11309，同时换 Phase2 并施加 DisableAction。ExcelOutput/BattleEventConfig.json · /46 为 AssistEvent，AbilityList[0] 指 BattleEventAbility_Robin_00_Skill03，找到同文件 /AbilityList/8，OnAdd 配 BaseSpeed Modifier 和带白名单的 LockActionDelayChange。/GlobalModifiers/MAvatar_Robin_00_PassiveSkill01_BattleEvent/_CallbackList/0 的 OnPhase1 目标是 BattleEventCaster，任务含结束动画、SetEntityActionState、SetActionDelay(0)。/GlobalModifiers/MAvatar_Robin_00_Skill03Area/_CallbackList/3/CallbackConfig/2 引用 MAvatar_Robin_00_Skill03_BonusAction，后者在 OnStack 对 ModifierOwnerEntity 置行动延迟为零并自移除。**Derived**，事件计时与施法者自身状态互相引用。全体行动栏变更的每对象顺序仍未知。
- 景元。Config/ConfigAbility/Avatar/Avatar_JingYuan_00_Ability.json · /AbilityList/7/OnStart/4 以 CreateBattleEvent 出现 EventID=11203、TeamLight。ExcelOutput/BattleEventConfig.json · /42 对应 DummyCharacter，TeamNeutral，列出 BattleEventAbility_JingYuan_Passive 与 BattleEventAbility_JingYuan_Passive_Insert。第一个在该 Ability 文件 /AbilityList/9；其路径关联 /GlobalModifiers/MAvatar_JingYuan_00_BattleEvent/_CallbackList/0 的 OnPhase1，TurnInsertAbility.AbilityName 指 /AbilityList/10 定义 Avatar_JingYuan_00_Passive_Insert，执行目标别名为 BattleEventCaster。**Observed** 队伍字段冲突。**Derived** ID、配置引用和召唤者目标形态可以追踪。运行时如何决定队伍和行动身份不能读出。
- 阿格莱雅。Config/ConfigAbility/Avatar/Avatar_Aglaea_00_Ability.json · /AbilityList/12/OnStart/1/SuccessTaskList/0 使用 CreateServant，/OnStart/9 则 CreateBattleEvent，数字均为 11402。ExcelOutput/AvatarServantConfig.json · /0 的 11402 是忆灵，Config 指 Servant_AglaeaServant_00_Config.json，SpeedBase=0、SpeedInherit=#4、SpeedSkill=140204。ExcelOutput/BattleEventConfig.json · /48 的同数字是 AssistEvent，并指 Avatar_Aglaea_00_PassiveSkill01_BattleEvent。两类表绑定不同实体。该 Ability 文件 /AbilityList/13/Modifiers/MAvatar_Aglaea_00_PassiveSkill01_BattleEvent/_CallbackList/0/CallbackConfig/1/TaskList/0 用 TurnInsertAbility 请求忆灵清理，另在 /_CallbackList/1 用 StackProperty.BaseSpeed。**Derived** 两个 ID 域彼此独立，实体各自参与调度的方式可以不同。
- 白厄。Config/ConfigAbility/Avatar/Avatar_Phainon_00_Ability.json · /AbilityList/17/OnStart/8 切 PhainonBattleArea。/AbilityList/18/OnStart/4/TaskList/0 创建 EventID=11408，ExcelOutput/BattleEventConfig.json · /50 的 AbilityList 连接同文件 /AbilityList/19。其 /Modifiers/MAvatar_Phainon_00_Skill03_BattleEvent_Passive/_CallbackList/1 使用 OnPhase1。成功分支请求 TurnInsertAbility，并检查 AbilityOwnerInsertUnusedCount、Count=1 和 ActivePredicate；失败分支另可对 BattleEventCaster 使用 TurnInsertAction、CanInsertUltraSkill=true，并标 Phainon_BEInsertAction。**Derived**，变身期间的事件节奏能分支提交不同种类的请求。此链没有给出实际行动间隔和初始化顺序。

## 调度器的可观测边界

**SCH-007 · Observed／Unknown。** 存在能询问“第一个待插入 Ability 位置”和“下一个未用插入行动属性”的序列化接口。RPG.GameCore.ByIsFirstInsertAbilityInQueue 在 v2 只出现一次。Config/ConfigAbility/Avatar/Avatar_RuanMei_00_Ability.json · /AbilityList/8/OnStart/0/Predicate 使用 Inverse=true，其 /SuccessTaskList/0 发 Stage_ShowDefaultCameraAfterTimeline。Archer 额外使用 ByCompareNextUnusedInsertAction 与两个计数检查，白厄单独可约束同 Ability 持有者的待用计数，Heliobus 有待用终结技计数。观察到的“顺序”相对不同请求的可查询位置，不足以确定入队顺序、排序键、先进先出策略、优先级冲突处理或共享容器。

| 候选模型 | 配置证据和可反驳限制 |
| --- | --- |
| 同步递归为部分局部能力执行 | TriggerAbility 和模板参数可沿引用嵌套。该模型单独不能从语义上解释被查询的待处理计数、选择下一项目或显式中止 |
| 有待处理请求的有序模型 | ByIsFirstInsertAbilityInQueue、ByCompareNextUnusedInsertAction、ByCompareUnusedInsertAbilityCount 与 PendingInsertAbilityPriority 等字段相容。配置无需承诺物理队列，也可能从调度表排序得到谓词 |
| 嵌套技能执行上下文 | TargetType、AbilityTarget、PreCheck、ActivePredicate 与参数作用域并列，可由调用帧或传参结构实现。回调任务递进不能区分真实调用栈、栈外上下文或事件迭代器 |
| 事件和阶段调度 | OnStart、OnActionPhaseBegin、OnBeforeSkillCost、OnInsertActionStart/Finish、OnInsertAbilityStart/Finish/Abort、PauseToTurnEnd、WaitForTurnEnd、DamagePerformFinish 等公开选择和任务形态相容。公开钩子数量与实际阶段、线程和处理批次无直接等号 |
| 混合模型 | 自然行动值、待插入请求、局部回调、表现等待和波次模板有不同接口。混合实现可以同时满足这些约束。是否分为独立 scheduler、是否跨模式共享实现为 Unknown |

对资源路径能确认的偏序是“事件选择条件控制其配置分支”“引用的名字和参数必须能解析才可能执行”“OnInsertAbort 分支绑定于该请求”“模板内部的成功与失败目标不同”。绝对时序、某次结算何时提交、同优先级并发、动作是否消耗自然回合、异常时怎样回滚均需运行时跟踪。报告中的候选模型保留相容性，不重建官方引擎。

## 静态验证

[未解析请求](unresolved-requests.tsv) 列出公共 v2 视图中相关类型的 25 个歧义或未解析节点。TurnInsertAbility 的 AbilityName 共 8 个未解析，包括 Config/ConfigAbility/Monster/Monster_W1_Svarog_00_Ability.json · /GlobalModifiers/Svarog_Skill06_Insert_Modifier/_CallbackList/0/CallbackConfig/0/AbilityName/Value 的 Monster_W1_GS_Svarog_Insert_Phase01。TriggerAbility 另有 15 个未解析和 2 个多候选。这里只比较配置字面值和索引规则，装载和运行时有效性保留 Unknown。

[参考目录](inventory.md) 记录全量检索口径。[索引生成](catalogue.py) 用公共索引 v2 生成类型、主数据及事件清单。[验证脚本](validate.py) 对原始角色、费用、事件与插入配置作独立断言，输出 [validation.log](validation.log)。没有运行游戏，也没有模拟伤害、随机、支付或行动调度。
