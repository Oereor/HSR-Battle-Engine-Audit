# 引擎抽象参考与功能职责表

本表按序列化对象、具体职责和假设关联组织。字段与位置服从对应专题的收录范围。行内的功能是观察到的配置能力或推断职责，官方实现边界保持 Unknown。

| 抽象 | 直接配置形态 | 可复核入口与运行时边界 |
| --- | --- | --- |
| Entity | `AvatarID`、`MonsterID` 与模板号、`ServantID`、`BattleEventID` | 各表命名空间独立。ID 11402 的两类实体来自不同表及创建任务 [01](../01-entity-ability/report.md) · [召唤案例](../07-case-studies/10-summons.md) |
| CharacterConfig | `SkillList`、`SkillAbilityList`、`AbilityList`、`DynamicValues` | 关联资源及行为入口。装载优先级未知 [字段清单](../01-entity-ability/inventory.md) |
| Skill | `SkillID`、`Level`、`SkillTriggerKey`、`Name`、`EntryAbility`、`PrepareAbility`、资格、选择目标、费用 | 数值和执行入口可分开定位。一技能可关联多 Ability [01](../01-entity-ability/report.md) |
| Ability | 具名定义，直接生命周期槽，参数字典和嵌套状态，目标提示和复用 | 核心 17,102 个定义，静态请求有环及跨文件候选 [引用图](../01-entity-ability/ability-static-graph.tsv) |
| Modifier | `Modifiers`、`GlobalModifiers`、`ModifierMap`、`LifeTime`、`Stacking`、`BehaviorFlagList` | 状态身份、衍生行为和持有上下文有证据，运行时实例键与可见性未知 [生命周期](../03-modifier/report.md) |
| Callback / Trigger | `_CallbackList[].Event`、范围监听、直接钩子、`TriggerModifierCustomEvent`、动画等待 | 条件、目标和参数可以定位，注册、重入和调用时刻未知 [04](../04-callback-trigger/inventory.md) |
| Task | 带 `$type` 的槽对象，或封装其他任务的复合对象 | 角色与字段形态由操作表给出，执行粒度和事务边界未知 [操作表](../02-atomic-operations/operations.tsv) |
| Condition | `Predicate`、`ByAnd`、`UsableConditions`、`PreCheck`、`ActivePredicate` | 门控技能、执行请求、选目标或选子列表。布尔短路语义与检查时点未知 [05](../05-context-expression/report.md) |
| Target | 内嵌对象、直接选择串、公共/文件级别名、可重用操作字典 | 选择实体、派生实体关系、筛选、排序及数量。组合时的去重与取照未知 [目标字典](../05-context-expression/target-dictionaries.tsv) |
| Expression / Variable | `FixedValue`、`PostfixExpr`、`ReadInfo`、`DynamicKey`、多个 Scope、属性和模板载荷 | 单输入与少数双输入可静态复算；指令全集、键冲突、跨阶段寿命未知 [绑定](../05-context-expression/binding-results.tsv) |
| Resource | 标准 SP、特殊 SP、队伍 BP、实体 BP、HP 与韧性接口及各自观察器 | 消费、容量和溢出有单独形态。提交、退款优先级和实际变化未知 [06](../06-resource-scheduling/report.md) |
| Action | `SetActionDelay`、`ModifyActionDelay`、`TurnInsertAbility`、`TurnInsertAction` | 调整自然行动，与可带限额、目标、成本开关的请求相区分。实际回合语义未定 [接口](../06-resource-scheduling/interfaces.tsv) |
| Scheduling Context | 队首、下一项、计数、`InsertAbilityPriority`、取消、延时与阶段相关字段 | 支持可查询的待处理顺序及策略。底层队列、栈、时钟或统一调度器是候选 [验证](../06-resource-scheduling/validation.log) |
| TaskListTemplate | `IncludeTaskListTemplate.Name`、`TaskListTemplate`、`ParamTarget`、`TemplateParamSequences` | 具名模板与实参。嵌套调用、展开或复用的内部实现未知 [补充解析](../index/reference-overlay.tsv) |

## 运行时功能职责

以下职责是根据多个配置入口提出的解释。模块独立性、类与数据结构为 Hypothesis。

| 功能 | 配置依据 | 仍需验证 |
| --- | --- | --- |
| 实体生命周期与状态 | 创建/移除事件单位、召唤/回收、状态引用与目标查询 | 实体 ID 分配、出生/死亡与状态回收的先后 |
| 行为启动与参数绑定 | 入口/准备/后续调用、触发键、ReadInfo、调用实参 | 帧寿命、作用域查找、加载和同名覆盖 |
| 状态应用与通知 | 添加、叠加、生命步进、清理、范围监听与跨状态挂载 | 状态实例标识、消散原因、重入和默认值 |
| 监听派发 | 具名回调、数字令牌、旗标、Priority 与 Recall | 订阅表、排序、消费、全局与局部次序 |
| 条件、表达式、目标 | 临时值、条件组合、属性快照、目标字典和技能掩码 | 值类型、精度、容器写入、查询缓存 |
| 资源与行动 | 当前量/最大量、费用/门槛、观察器、待处理请求和显式延时 | 扣减与提交、延时推进规则、优先级数据结构 |
| 战斗数值 | AttackData、ModifyDamageData、伤害事件、生命、护盾、韧性 | 公式、伤害阶段、合并、死亡收束与精度 |
| 表现 | 动画导入、WaitAnimEvent、镜头 Ability、时间归一化字段 | 表现与逻辑时钟的交接和并行单位 |

[指标复算脚本](../tools/reconstruction_metrics.py) 使用 02 操作清单。 [交叉指标](composition-shapes.tsv) 按类型计，`type also occurs in core task slots` 先取存在核心节点的类型，其它属性仍由该类型全部选入节点聚合。 [26 个接口的位置及对照](composition-witnesses.tsv) 保留原有父域、所选次数和嵌套槽。 [实际运行日志](metrics.log)
