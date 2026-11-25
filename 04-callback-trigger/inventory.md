# 04 · 事件、回调与触发参考清单

目录中的表以 TurnBasedGameData 根为路径基准，使用零基 JSON Pointer。命令 `python3 04-callback-trigger/build_events.py` 依赖 [公共索引 v2](../index/README.md)，只读取索引与索引定位到的原始文件。`python3 04-callback-trigger/verify.py` 复核计数、声明与关键关联，参见 [构建日志](build.log) 和 [复核日志](validation.log)。

## 清点范围与结果

| 配置形态 | 口径 | 数量 | 查表 |
| --- | --- | ---: | --- |
| Modifier 具名选择器 | v2 全部 `callback-selector`，按文件和指针计 | 35,896 处，224 名 | [按原名聚合](callback-catalog.tsv) · [全部位置](callback-sites.tsv) |
| 核心与 Rt 原名 | 核心为 ConfigAbility、ConfigGlobalModifier、全局任务模板。Rt 为 RtBattle 和 RtDefence | 核心 35,295 处、216 名。Rt 601 处、38 名。交集 30 名 | [分域清单](callback-catalog.tsv) |
| 具名 hook 或容器 | 核心、Rt、动画、战斗演出 Story、StageCommon、全局行为旗标映射，包含嵌套字段 | 83,668 处、84 个分域和位置类键 | [类型与直接项](hook-catalog.tsv) · [全部位置](hook-sites.tsv) |
| 动画与相邻领域 | `AnimatorStateName` 状态记录、动画组或行为记录、逻辑事件名和被选中的 EventName 引用 | 34,560 个状态记录、3,253 个组或行为记录、18 个具名逻辑动画记录，另有 26 个核心名字字段引用 | [按形式分类](named-event-catalog.tsv) · [原始位置和上下文](named-event-sites.tsv) |
| 具名等待 | `WaitAnimEvent` 与逻辑记录和角色动画文件导入做候选联接 | 26 处，16 个不同名字，都有至少一条显式导入匹配 | [动画等待联接](animation-wait-links.tsv) |
| 数字自定义事件 | `GameCoreConstValue.ModifierCustomEvents` 加显式生产与接收候选 | 14 个令牌，181 处具类型引用，6 个令牌同时有发送与消费候选 | [定义及候选链接](custom-event-links.tsv) · [引用位置](custom-event-sites.tsv) |
| 字符串统计事件 | `TriggerBattleStatisticEvent.EventType` 按字符串独立计 | 21 个位置 | [原始位置](named-event-sites.tsv) |
| 公共策略和匿名回调 | `ForbidRecallModifierEventList`、`ServantModifierEventWhiteList`、`ModifierBehaviorFlagEventMap` | 12 个 Recall 名称、空 Servant 数组、2 个旗标映射 | [原始策略](global-event-policies.tsv) |
| 有类型的触发／事件相关候选 | 全语料类型名末段中匹配 `Trigger/CallBack/Callback/Event/Listen`，并保留已观察到有相邻职责的命中、调度、等待、状态操作等显式类型 | 368 个序列化类型，含场景及其他玩法 | [候选和位置](trigger-type-candidates.tsv) |

各行可能引用同一个配置的不同部分。统计分别按位置、原名、名字和域、或序列化类型分组。相邻场景脚本中的大批 `EventName` 留在公共索引，专题的逐位置表只导出战斗、Rt、动画及少数邻域的名字字段。候选表的范围包含同词异义的事件、监听或表现资源，结构分类按原任务位置验证。

## Callback 的读法

`callback-sites.tsv` 的 `definition_pointer` 及 `definition_name` 为其所属 Modifier 定义，`definition_scope` 为所属 Ability 或字典类别。跨文件同名需以指针复核。`declaration_fields` 保留直接可选字段，当前仅出现 `Priority`。`filters` 记录任务体的谓词候选和明确条件字段子节点，`nested_control_fields` 标示次数、优先级、延时等字段实际出现于行为体。`payload_evidence` 包含原样目标、事件相关别名、上下文名称和可定位的键字段。`direct_tasks` 按数组位置列出直接任务，`nested_nonquery_types` 是内部类型的去重集合。记录的目标角色须结合具体谓词和嵌套路径阅读。

`callback-catalog.tsv` 的 `producer_evidence` 对可定位的自定义事件给交叉索引，`OnEnterBattle` 给出已有显式入场请求的候选性质。其余声明式事件默认保留 `Unknown`，包括只从命名可以联想到伤害或行动的条目。一个同名选择器可能同时出现于角色、敌方、战斗事件、装备和玩法资源。回调的真正注册与分发仍无运行轨迹。

## 结构化钩子的读法

直接根 Ability 钩子可在 `hook-sites.tsv` 筛选 `domain=core`、`anchor_kind=ability`、`relative_depth=1`，其中 `OnStart` 11,855、`OnAdd` 5,481、`OnInsertAbort` 110、`OnRemove` 35。含任务内嵌取消路径的更宽 `OnInsertAbort` 在核心共有 200 处。核心 `OnDynamicValueChange` 386、`OnAbilityPropertyChange` 221、`OnElationPointChange` 21 处分别为容器观察位置。`OnChange` 的相邻区间字段及直接任务见 `range_fields`、`direct_typed_members`。动画、战斗事件创建、子弹命中和场景落地的局部钩子按同一定位规则收录。

## 同名与同值

- `custom-event-links.tsv` 对 `EnumIndex`、`Value` 组合比较再连接全局声明。`candidate_equal_tuple_pairs` 计发送位置 × 消费候选位置，运行时附带目标、旗标和调用状态策略。具名 `OnCustomEvent` 位于核心 292 处，分支中可以继续核对令牌、旗标与事件参数。
- `animation-wait-links.tsv` 中同时保留同名候选和角色配置据以导入的文件证据。能力名的跨文件同名也保留，可跟随候选查到具体目录版本。动画记录的 `NormalizedTime`、`Time` 等字段分别列出，其领域与单位由实际资源说明。
- `CallBack`、`TriggerAbility`、`TriggerModifierCustomEvent`、`CreateBattleEvent`、`TriggerBattleStatisticEvent` 形成不同结构。反向搜索原名可从共享 SQLite 查询任意类型或配置位置。角色手册见 [01](../01-entity-ability/inventory.md)，任务类型见 [02](../02-atomic-operations/inventory.md)，Modifier 定义见 [03](../03-modifier/inventory.md)。
