# 资源与行动调度接口清单

[interfaces.tsv](interfaces.tsv) 以完整字符串 $type 为键，登记公共 v2 中符合领域模式、显式关键字段或报告原始证据的 231 个类型。137 个类型在 02 的核心任务槽有过实例。除此之外还保留选取器、判定、结构容器、显示节点以及模式或探索中的同形配置。实际行为层由类型位置与原始节点共同判定。

| 清单 | 覆盖与查阅 |
| --- | --- |
| [interfaces.tsv](interfaces.tsv) | 9 个允许重叠的名称检索族。区分名称信号、类型直接字段、人工关联、v2 全语料计数、定义锚点计数、02 的三个任务槽计数、字段形态、实际样本位置 |
| [events.tsv](events.tsv) | 钩子字段与回调选择器分列。80 个 selector 名和 21 个 hook 名，记录覆盖锚点、次数和源 JSON Pointer。事件发送、订阅与运行时回调关系应查 04 专题 |
| [master-fields.tsv](master-fields.tsv) | 8 张观察表中 48 组实际存在的表与字段组合，给出存在行数、总行数、值形态和首个非缺省定位。缺失字段没有补默认值 |
| [unresolved-requests.tsv](unresolved-requests.tsv) | 5 个请求类型范围内 v2 公共引用视图中的歧义或未解析 Ability 字面值。覆盖读取规则已识别的字段，动态值与外部装载仍可能另有目标 |
| [catalogue.py](catalogue.py) | 可重现筛选，包括完整字段集合、正则式、表文件和少量不透明类型的显式证据 |
| [catalogue.log](catalogue.log) 与 [validation.log](validation.log) | 索引聚合与独立断言的实际执行结果 |

## 高价值接口

| 领域 | 写入与请求 | 读取、资格、生命周期 |
| --- | --- | --- |
| 标准及特殊 SP | ModifySP、ModifySPNew、ModifySpecialSP、SetEnergyBarState（表现） | SPNeed、SPMultipleRatio、SetDynamicValueByVariateType 的事件参数输入与 ByCompareSPRatio、ByCompareSpecialSPRatio、OnSPChange、OnAbilityPropertyChange.CurrentSpecialSP |
| 队伍及实体 BP | ModifyTeamBoostPoint、ModifyTeamBoostPointMax、StackAdditionalTeamBoostPoint、ModifyEntityBoostPoint | BPNeed、ByCompareBP、SetDynamicValueByCurrentBP、SetDynamicValueByBPChange（RawDelta、UnclampedDelta）、OnListenBpChange |
| HP、护盾、韧性 | SetHP、LoseHP、LoseHPByRatio、HealHP、InitShield、ModifyShield、DamageStance、TriggerBreak | OnHPChange、OnHPOverflow、OnBeforeBeingLoseHP、OnBeforeBeingStanceDamage、OnBeingStanceDamage、OnBeingBreak、OnStanceReset |
| 费用及可用性 | ModifySkillPropertyByName、ModifySkillPropertyBySlot、ModifySkillPropertyByType、SetControlSkillMapping、AttachSkillTypeDisable | UsableConditions、OnBeforeSkillCost、PreCheck、ActivePredicate、IgnoreBPDec、IgnoreSPDec |
| 自然行动输入及限制 | ModifyActionDelay、SetActionDelay、SetActionDelayNearTarget、ResetActionDelay、SetupActionDelayLink、LockActionDelayChange、StackProperty 的 BaseSpeed 或 SpeedDelta | ByIsTopActionDelayTarget、ByIsForbidChangeOthersActionDelay、OnListenGlobalActionDelayChanged |
| 行动请求及插入 | TriggerAbility、TurnInsertAbility、TurnInsertAction、AbortInsertAbility、AutoUseUltraSkill、AITryInsertUltra | TurnInsertAbilityCondition、ByIsFirstInsertAbilityInQueue、ByCompareNextUnusedInsertAction、ByHaveInsertUltraWait、ByCompareUnusedInsertAbilityCount、OnInsertAbilityStart/Finish/Abort、OnInsertActionStart/Finish |
| 倒计时与阶段 | CreateBattleEvent、CreateServant、SummonMonster、ConsumeActionCountDown、PauseToTurnEnd、WaitForTurnEnd、DamagePerformFinish | BattleEventConfig、AvatarServantConfig、OnPhase1、OnPhase2、OnListenTurnBegin、OnListenTurnEnd、OnListenInsertUltraSkill |
| 专属资源 | Acheron 的 CurrentSpecialSP 与 Modifier 层。Phainon 的 CurOverflowSpecialSP + 模板。丹恒与火花的 RawDelta 及独立实体 BP | 详见 [专题报告](report.md) 的源锚点与不透明原语限制 |

表中的“写入”和“读取”描述配置中提供的操作角色。判断有共享运行时、别名、同触发时点或执行顺序还需更强证据。字段使用地方未被类型名或字面值覆盖的，保留在 00 的反查表与 02 的逐类型目录。

## 复算

```sh
PYTHONDONTWRITEBYTECODE=1 python3 06-resource-scheduling/catalogue.py
PYTHONDONTWRITEBYTECODE=1 python3 06-resource-scheduling/validate.py
AUDIT_INDEX_VERSION=2 python3 tools/query.py type RPG.GameCore.ByIsFirstInsertAbilityInQueue
AUDIT_INDEX_VERSION=2 python3 tools/query.py event OnBeforeSkillCost
```
