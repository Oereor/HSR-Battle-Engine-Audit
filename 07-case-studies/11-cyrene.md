# 昔涟 · 忆灵能力与跨角色状态桥接

本案沿 1415 的终结技、忆灵自动准备和刻律德菈专属状态，追踪战斗中同一次配置链如何跨越角色、忆灵及队友三个上下文。

## 入口和实参

**Derived**。 `ExcelOutput/AvatarConfig.json#/73` 列出 141503。 `ExcelOutput/AvatarSkillConfig.json#/4809` 等级 1 的 `SkillTriggerKey="Skill03"`，参数 0 到 3 为 1、24、0.25、12。 `Config/ConfigCharacter/Avatar/Avatar_Cyrene_00_Config.json#/SkillList/2` 的 `EntryAbility` 为 `Avatar_Cyrene_00_Skill03_Phase01`。 `Config/ConfigAbility/Avatar/Avatar_Cyrene_00_Ability.json#/AbilityList/7/OnStart/13` 请求 Phase02，定义于 `/AbilityList/8`。其 `/OnStart/7` 固定创建：

```json
{"$type":"RPG.GameCore.CreateServant","ServantID":{"IsDynamic":false,"FixedValue":{"Value":11415}}}
```

`ExcelOutput/AvatarServantConfig.json#/4` 的 11415 给出独立 `Config` 和 `SkillIDList`，列有 1141502、1141523；其 HP 相关字段 `HPBase="0"`、`HPInherit="#1"`、`HPSkill=141503` 指回角色 Skill03，且没有充分证据从此给出最终生命值。 `ExcelOutput/AvatarServantSkillConfig.json#/220` 的 1141502 为 Skill02； `ExcelOutput/AvatarServantSkillConfig.json#/400` 的等级 1 记录 1141523 为 SkillCY11，参数 0、1 分别为 0.15、1。 `Config/ConfigCharacter/Servant/Servant_CyreneServant_00_Config.json#/DynamicValues/Floats/-587280964/ReadInfo` 和 `Config/ConfigCharacter/Servant/Servant_CyreneServant_00_Config.json#/DynamicValues/Floats/477870958/ReadInfo` 把这两个值绑定到下述专属状态施加任务，字段分别为 `MDF_DamageIncrease`、`MDF_ExtraPoint`。

## Ability 图与实体上下文

```mermaid
flowchart LR
    A["角色 Skill03 Phase01 · /7"] -->|TriggerAbility| B["Phase02 · /8"]
    B -->|"CreateServant"| C["11415 · 独立忆灵配置"]
    B -->|"局部成功支 · CasterServant"| R["Skill02_Ready · 忆灵 /3"]
    C -->|"SkillList/1 EntryAbility"| D["Skill02 Phase01 · 忆灵 /4"]
    R -->|"TurnInsertAction · ControlSkill02"| S["控制技能入口候选"]
    S -.-> D
    D -->|"TriggerAbility"| E["Phase02 · 忆灵 /5"]
    E -->|"目标 ID=1412"| F["AmazingBuff_Cerydra"]
    F -->|"OnListenModifierAdd"| G["随 Cerydra_00_PromoteTarget 重设子状态"]
```

**Observed**。角色 Phase02 的 `/OnStart/15` 两个分支分别请求同一 `CasterServant` 上的 Skill02 Ready 或 Skill01 Ready。 `Config/ConfigAbility/Servant/Servant_CyreneServant_00_Ability.json#/AbilityList/3/OnStart/1` 的插入行动声明 `SkillType="ControlSkill02"`、`InsertActionPriority="Character_ChainSkill"` 和准备能力 `Servant_CyreneServant_00_FormationReset`。同文件 `/AbilityList/25` 有该准备定义。忆灵独立配置的 `/SkillList/1/EntryAbility` 为 Skill02 Phase01，定义于 `/AbilityList/4`，其 `OnStart/4` 请求 `/AbilityList/5`。控制技能路由需在执行时选择，因此图中该段为虚线。 `Config/ConfigCharacter/Servant/Servant_CyreneServant_00_Config.json#/SkillList/1`。

**Derived**。忆灵 Skill02 Phase02 在 `Config/ConfigAbility/Servant/Servant_CyreneServant_00_Ability.json#/AbilityList/5/OnStart/21` 检查 `AbilityTargetEntity` 的角色号 1412，成功时施加 `MServant_CyreneServant_00_AmazingBuff_Cerydra` 并传上面的两个参数。普通语音 fallback 则用 `ByIsInCharacterIDGroup(Group="Chrysos",Inverse=true)`，显示群组与单一角色分支共存。 `Config/ConfigAbility/Servant/Servant_CyreneServant_00_Ability.json#/AbilityList/5/OnStart/6`。

## 跨角色 Modifier 协议

**Observed**。忆灵的 `/GlobalModifiers/MServant_CyreneServant_00_AmazingBuff_Cerydra` 在 OnStack 对持有者执行 `SetDynamicValueByAddValue`，键 `_WindfuryCostFixValue`，作用域 `TargetEntity`。OnDestroy 则对同键给出不同表达式。第三个回调 `OnListenModifierAdd` 只接受刻律德菈的目标 Lv1 或 Lv2 名，成功分支先配置在我方集合内删除其子状态，再对 `Cerydra_00_PromoteTarget` 施加子状态并传伤害参数。该别名可在刻律德菈文件独立定位，依次选队伍、筛 `MAvatar_Cerydra_00_Skill02_Target`、取一项。子状态的 OnStack 明文 `StackProperty(CriticalDamageBase)`，并声明 `DependencyOnRemove.DependentModifier="MAvatar_Cerydra_00_Skill02_Target"`。 `Config/ConfigAbility/Avatar/Avatar_Cerydra_00_Ability.json#/GlobalTargetAlias/Cerydra_00_PromoteTarget` · `Config/ConfigAbility/Servant/Servant_CyreneServant_00_Ability.json#/GlobalModifiers/MServant_CyreneServant_00_AmazingBuff_Cerydra_Sub`。

**Inferred**。以 05 的候选哈希，`_WindfuryCostFixValue` 计算为 840429360。刻律德菈 Lv2 移除监听的成功分支读取此哈希，与自身点数和门槛输入并列。这支持忆灵通过目标实体键接入另一角色的点数逻辑。 `Config/ConfigAbility/Avatar/Avatar_Cerydra_00_Ability.json#/GlobalModifiers/MAvatar_Cerydra_00_Skill02_Target_Lv2/_CallbackList/4/CallbackConfig/0/SuccessTaskList/0/Value/PostfixExpr` · [候选哈希检验](../05-context-expression/hash-probe.md)。

已知偏序为配置中的创建与具名引用、选中目标 1412 才进入专属分支、监听匹配状态名才进入重设子状态分支。**Unknown**。跨文件别名在该调用处的实际装载可见性、选择目标切换与子状态移除同帧时的派发次序、点数表达式整体算术、控制映射动态覆盖和三种不透明节点 `LMHLABELCDJ`、`FCCIDFIMONC`、`LAPKGFCDPCD` 的实现仍有残差。此案支持跨角色按具名状态、参数与别名组合能力。 [刻律德菈案例](09-cerydra.md) · [Modifier](../03-modifier/report.md) · [Callback](../04-callback-trigger/report.md)

[静态校验脚本](verify_cross_entity.py) · [实跑日志](cross-entity-validation.log)
