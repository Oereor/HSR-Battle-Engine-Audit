# 研究命题

| ID | 领域 | 等级 | 命题及定位 | 边界、反例或未解 |
| --- | --- | --- | --- | --- |
| DAT-001 | 数据 | Observed | 本地 TurnBasedGameData 工作树启动 revision 为 2c8a218502ebfccaf6e01675b0bdf6948d723bbb，版本标记 OSPRODWin4.7.0_D17216325_A17211182_L17175930。见 [初始状态](index/source-start.git.txt) | Git 摘要与实际工作树文件指纹分别记录 |
| DAT-002 | 数据 | Observed | 非 layout 的 Config、ExcelOutput、Stages、Story JSON 全部解析成功，合计 134,609 文件及 4,636 种字符串类型。见 [普查](00-data-survey/inventory.md) | 包含周边领域；战斗角色统计以专题结构筛选为准 |
| DAT-003 | 索引 | Derived | 艾丝妲 Phase01 的字面调用在同文件找到 Phase02 定义；角色侧 SkillAbilityList 的同名引用来自另一文件。见 [作用域示例](00-data-survey/report.md) | 配置指向可静态核实，实际装载及执行须独立证据 |
| DAT-004 | 数据 | Observed | 134,609 份已解析文件中，15 份 Excel 常量文件涉及 263 次重复对象键。见 [质量与修订](00-data-survey/report.md) | 常规索引保留末项；原始并存键及运行时选择仍须分开看 |
| DAT-005 | 索引 | Derived | RtBattle 与 RtDefence 的顶层具名 Ability 及 Modifier 同样呈现可机械索引的结构。见 [扩展统计](00-data-survey/report.md) | 须按玩法域分组，混淆字段不依通用字面字段推导 |
| ABL-001 | Ability | Derived | 艾丝妲、可可利亚武器的敌方模板和衣匠均可追到各自的技能入口和具名 Ability，连接以实体 ID、路径与技能触发键为证据。见 [身份链](01-entity-ability/report.md#主数据身份与技能入口) | 事件 1 可直接注入 Ability，部分主数据缺路径或触发键 |
| ABL-002 | Ability | Contradicted | 「每个技能绑定恰好一个 Ability」被艾丝妲普攻的 `SkillAbilityList/0` 和同文件两个 `TriggerAbility` 请求否定。见 [组合](01-entity-ability/report.md#skill-与-ability-组合) | 成员关联与实际走到的分支不同，执行时序仍未知 |
| ABL-003 | Ability | Derived | 普攻、追击、忆灵和欢愉技沿用具名 Ability 及通用任务。见 [分类与公共能力](01-entity-ability/report.md#技能分类与公共能力) | 仍有专用原语和非选择型入口 |
| ABL-004 | Ability | Derived | 行迹与星魂有既有任务分支、Excel 参数、具名能力注入；强化镜流另有技能映射切换。见 [参数与替换](01-entity-ability/report.md#参数注入与替换) | 装备重复定义、星魂共享哈希均需先核定作用域 |
| ABL-005 | Ability | Unknown | 同名装备定义实际装载规则，跨 Ability 请求的完整调度与执行顺序。见 [静态图](01-entity-ability/report.md#生命周期动画事件与引用图) | Archer 自引用有条件和候选控制，静态图 14 个直接 scoped 循环分量不确定运行时次数 |
| MOD-001 | Modifier | Observed | 核心 22,729 个定义包含 Ability 局部 15,127、文件 GlobalModifiers 7,121、独立 ModifierMap 481。见 [结构](03-modifier/report.md#定义名称和归属) | Rt 两种玩法及 Adventure 各自单列 |
| MOD-002 | Modifier | Contradicted | 「Modifier 仅表达可见数值增益或减益」被知更鸟挂载和清理只声明 `BehaviorFlagList:["DisableAction"]` 的定义否定。见 [M17–M19](03-modifier/evidence.jsonl) | 实际 UI 显示、底层实例字段未知 |
| MOD-003 | Modifier | Derived | 艾丝妲 Skill03 的等级 1 输入 36 和 2 绑定到同一 `AddModifier` 的参数和寿命字段。见 [M01–M08](03-modifier/evidence.jsonl) | 默认寿命及实际扣减时点未知 |
| MOD-004 | Modifier | Observed | `OnStack`、`OnDestroy` 等选择器、`LifeStepMoment` 与 `Stacking` 枚举在不同配置中并存。见 [生命周期矩阵](03-modifier/report.md#生命周期矩阵) | 各枚举的完整执行策略未知 |
| MOD-005 | Modifier | Inferred | `InfectModifier` 具有从遐蝶向 `CasterServant` 传递选中具名状态的结构。见 [M26](03-modifier/evidence.jsonl) | 复制、共享或重新实例化皆可能 |
| OPS-001 | 操作 | Observed | `DamageByAttackProperty` 同时出现在艾丝妲普攻、姬子插入追击、敌方布洛妮娅投射物命中分支。见 [操作样本](02-atomic-operations/report.md) | 输入、命中与结算配置各自变化 |
| OPS-002 | 操作 | Observed | `FireWaveProjectile.PerProjectileDamage` 可直接嵌入伤害任务，`DamageByAttackProperty.AttackProperty` 可并置 HP 伤害、韧性与表现相关设置。见 [操作证据](02-atomic-operations/semantic-evidence.tsv) | 组合粒度由各任务结构决定 |
| OPS-003 | 操作 | Derived | `TriggerAbility`、`TurnInsertAbility`、`TurnInsertAction` 与行动延迟操作具有不同类型、输入与位置。见 [操作目录](02-atomic-operations/operations.tsv) | 由相同或不同子系统承接皆可能 |
| OPS-004 | 操作 | Observed | `HimekoNova` 的同一 Modifier 在不同回调中声明设置与清除 Assist → Skill 的映射。见 [操作样本](02-atomic-operations/report.md) | 角色形态与专用任务内部职责待确证 |
| OPS-005 | 操作 | Unknown | 序列化单任务的可中断性、事务性和边界内阶段次序。见 [原子性与组合](02-atomic-operations/report.md) | 有输入和嵌套子任务的证据，缺少运行时轨迹 |
| MOD-006 | Modifier | Derived | 知更鸟光环等配置以 `AdditionConfig.SubModifierList` 引用子状态，和任务中的显式施加路径并存。见 [M51–M52](03-modifier/evidence.jsonl) 与 [关系清单](03-modifier/inventory.md) | 加载位置可核实，子状态刷新、传播及清理时序未知 |
| MOD-007 | Modifier | Contradicted | 「全语料同名状态对应唯一配置」被可可利亚阶段二与 XP Elite 分别定义 `EnterBattleRage` 否定。见 [定义作用域](03-modifier/report.md#定义名称和归属) | 不同施加者在同一持有者的运行时实例键未知 |
| CTX-010 | 上下文 | Inferred | 双累加器文本哈希候选匹配 2,394/2,507 个单键启发式联接位置和 684/684 个 RankNN 触发对照。见 [哈希实验](05-context-expression/hash-probe.md) | 单一声明可对应另一局部变量，13 个位置的接收方未读算法候选值；完整编码和运行时绑定仍未知 |
| CBK-001 | 回调 | Observed | 35,896 个具名 Modifier 选择器与 Ability 的直接钩子、范围监听、动画等待等独立结构并存。见 [事件清点](04-callback-trigger/inventory.md) | 名字交集须去重，场景和玩法另分域 |
| CBK-002 | 回调 | Derived | 自定义令牌 (4,13) 可从 `Monster_ChangePhase` 的发送接至全局旗标和 Nihilux 监听者的令牌条件及写值。见 [自定义令牌](04-callback-trigger/report.md) | 能否同时命中取决于目标、旗标和过滤条件 |
| CBK-003 | 回调 | Observed | `GameCoreConstValue.ModifierCustomEvents` 14 个二元令牌，6 个显式 SortBy=Phase1Priority；另有 12 项 ForbidRecallModifierEventList。见 [策略表](04-callback-trigger/global-event-policies.tsv) | 同名事件的排序和递归保护算法未确定 |
| CBK-004 | 回调 | Derived | 26 个 `WaitAnimEvent` 位置均有至少一个角色配置显式导入的动画名匹配。Claymore 是具体跨文件证据。见 [动画联接](04-callback-trigger/animation-wait-links.tsv) | 同名快照和动画时间与战斗逻辑时钟换算未知 |
| CBK-005 | 回调 | Inferred | 数字事件目标、旗标、接收者过滤及写入上下文支持受约束的跨实体分发。见 [回调报告](04-callback-trigger/report.md) | 各事件 ParamEntity 的实际绑定规则及动态装载未知 |
| CBK-006 | 回调 | Unknown | 监听注册和解绑时机、跨监听者优先级和跨事件真实顺序。见 [运行时边界](04-callback-trigger/report.md) | 局部配置门槛和具体令牌可以独立核对 |
| CTX-001 | 上下文 | Observed | 公共目标别名和操作字典分别有 196 和 80 条，`AllEnemy` 和 `AllTeamMember` 可比较到不同映射序列。见 [目标选择](05-context-expression/report.md) | Rt 可重定义同名目标；运行时覆盖范围未知 |
| CTX-002 | 上下文 | Derived | v2 未匹配的别名字面位置中 250,243 条得到单一精确字典候选，另有完整分词候选。见 [别名汇总](05-context-expression/alias-counts.tsv) | 分隔符优先级、运算和实际查找规则仍待验证 |
| CTX-003 | 上下文 | Observed | 目标槽可区分 Caster、ModifierOwner、CallBackModifierCaster、事件参数、攻防实体和召唤者，见 [角色与数据槽](05-context-expression/report.md) | 上下文是否捕获、复制、共享及何时失效未知 |
| CTX-004 | 上下文 | Derived | 技能等级、行迹、星魂、光锥及遗器的特定参数可通过主表、触发键、声明索引与整数引用定位。见 [校验明细](05-context-expression/binding-results.tsv) | 停云 Rank06 参数缺失；同名装备的序列化形态不同 |
| CTX-005 | 上下文 | Inferred | 两输入 `AQABAQIR` 和 `AQABAQQR` 在布洛妮娅、停云及艾丝妲的对照中分别支持加法和乘法解释。见 [表达式校验](05-context-expression/report.md) | 整套字节指令、舍入、求值器及作用域未知 |
| SCH-001 | 调度 | Derived | Archer 战技费用、饮月增强技能费用与白厄入口资格分别由主数据、技能字段和条件表达。见 [资源与支付](06-resource-scheduling/report.md) | UI 承诺、正式提交与结算次序未知 |
| SCH-002 | 调度 | Inferred | Archer 的连发结构有独立插入请求、取消、BP 检查与星魂条件返还的证据。见 [资源报告](06-resource-scheduling/report.md) | 当前局部字典未恢复所有回补量绑定 |
| SCH-003 | 调度 | Observed | 队伍 BP 与实体 BP 有不同操作，花火分别修改队伍存量和上限，饮月与火花还读取 BP 事件 RawDelta。见 [接口清单](06-resource-scheduling/interfaces.tsv) | 替代支付确切扣减顺序、溢出截断和派发时点未知 |
| SCH-004 | 调度 | Derived | 黄泉和白厄分别展示状态层数及动态变量的特殊 SP 超限路径。银狼 999 的 BP 监听成功分支可追到下一 Ability。见 [资源报告](06-resource-scheduling/report.md) | 特殊资源内部存储、去重与提交时点未知 |
| SCH-005 | 调度 | Observed | Delay 设置和增量、调用 Ability、插入 Ability、插入 Action 有独立结构。见 [行动接口](06-resource-scheduling/report.md) | 各类动作请求如何共享底层调度未知 |
| SCH-006 | 调度 | Derived | 景元、知更鸟与白厄存在带独立行动相关参数的 BattleEvent；衣匠从 Servant ID 接入。见 [实体对照](06-resource-scheduling/report.md) | Team 字段优先次序及同速度并列规则未知 |
| SCH-007 | 调度 | Observed | 阮·梅样本可查询队首插入请求，Archer 样本可查询下一未用插入行动和计数。见 [排序证据](06-resource-scheduling/report.md) | 配置可观察顺序，FIFO、LIFO、堆和优先级比较实现未知 |
