# 00 · 数据普查与公共索引

## 数据版本与边界

研究开始时，`TurnBasedGameData` 当前 revision 为 `2c8a218502ebfccaf6e01675b0bdf6948d723bbb`，提交时间为 `2026-11-19T04:36:40+01:00`，提交主题提供版本标记 `OSPRODWin4.7.0_D17216325_A17211182_L17175930`。初始 `git --no-optional-locks status --porcelain=v1 -uall` 输出为空。数据扫描以实际工作树字节为准。记录在 [初始 Git 状态](../index/source-start.git.txt)，逐文件 SHA-256 存在 `files` 表。

对非 Git 普通文件记录路径、大小及散列。Config、ExcelOutput、Stages 和 Story 下所有非 layout JSON 用 Python 标准库按单文件解析，并遍历每个对象和数组。当前 134,609 份成功解析，零失败。9,076 份 layout、29 份本地 TextMap、一份 README 仅进入文件指纹。任何专题从 TextMap 读取的中文名称仅作辅助，可根据本地表哈希核对。最大解析开销受最大单文件大小和索引汇总的工作集限制。扫描不跟随符号链接，排除 `.git` 元数据。实际文件数、字节数和各子树清单见 [inventory.md](inventory.md)。

## 数据域地图

| 用途 | 观察入口与证据 | 注意事项 |
| --- | --- | --- |
| 玩家、技能、等级 | `ExcelOutput/AvatarConfig.json#/0` 有 `AvatarID: 1001`、`JsonPath`、数字 `SkillList`；角色路径指向 `Config/ConfigCharacter/Avatar/Avatar_Mar_7th_00_Config.json` | 技能数字 ID 与角色配置内的技能名使用不同字段 |
| 敌人 | `ExcelOutput/MonsterConfig.json#/0` 有 `MonsterID: 1002011`、`MonsterTemplateID: 1002011`、`SkillList: [100201101]`；模板、技能及行为资源散在 `MonsterTemplateConfig`、`MonsterSkillConfig` 与 `ConfigAbility/Monster` | ID 等值联接、文件名归属和直接路径的置信度各异 |
| 召唤及忆灵 | `ExcelOutput/AvatarServantConfig.json#/0` 有 `ServantID: 11402`、`Config`、`SkillIDList`；`Config/ConfigSummonUnit/SummonUnit_Cipher_00_Config.json#/OnCreate/0` 另有 `AdvMarkAsTauntProxy` 和 `CasterSummoner` | 数据存在多套路由，前一表是战斗忆灵入口，后一文件含大世界任务 |
| Ability 与 Modifier | `Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json#/AbilityList/0/Name` 为 `Avatar_Asta_00_Skill01_Phase01`；`Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json#/ModifierMap/StanceBreakState` 有 `_CallbackList` | 定义容器名称、文件级作用域与角色实际装载分别调查 |
| 光锥及遗器 | `ExcelOutput/EquipmentSkillConfig.json#/0/AbilityName` 为 `Ability20000`；`ExcelOutput/RelicSetSkillConfig.json#/0` 有非空 `PropertyList`、空 `AbilityName`；聚合文件为 `EquipmemtAbility.json` 和 `RelicAbility.json` | 保留 dump 原拼法，装备效果也可只经主数据属性字段 |
| 关卡与玩法 | `ExcelOutput/StageConfig.json#/0/LevelGraphPath` 指向 `Config/Level/StageCommonTemplate.json`；`ExcelOutput/BattleEventConfig.json#/0/AbilityList` 含 `BattleEventAbility_ChallengeTurnLimit` | Stages 与 LevelOutput 等目录含地图和图资源。《棋盘》一类 Config/BattleMode 中也出现任务列表，应保留局部行为证据 |
| 动画与演出 | `Config/ConfigAnimEvents/Avatar/Designer/Avatar_Asta_00_Designer_AnimEvent.json#/AnimatorStateEvents/0` 有动画状态、`NormalizedTime: 0.9`、`TriggerDeadHandler`；`Story/BattlePerformance/429201/BattlePerform42920101.json#/OnStartSequece/0/TaskList/0` 为 `BattlePerformInit` | 动画记录有多套形态。初始索引中 `animation-record` 的 18 条仅指具有 `EventName` 的动画数组记录，其他动画任务仍在类型索引中 |
| 公共模板与技能池 | `Config/ConfigGlobalTaskListTemplate/GlobalTaskListTemplate.json#/TaskListTemplate/0/Name` 为 `Monster_ChangePhase`；`ConfigCommonSkillPool` 的 `PoolList` 包含 `UniqueName` 和技能条目 | 任务模板名与 Alias 等字符串的可用范围需另行验证 |
| 资源与编辑器 | `Config/ConfigEntity/NPCMonster/NPCMonster_W3_TV_02_Entity.json#/$type` 为 `RPG.GameCore.EntityLodLoadingData`，同文件有模型资源路径；`*.layout.json` 独立归类 | 目录名 Entity 单独不足以证明战斗实体对象；部分任务属于画面、地图、剧情或 UI |

## 复用与引用置信度

`occurrences` 支持任意序列化类型反查。Indexed 对象保留直接父字段、最近上层类型、数组成员标记及最近定义锚点。字段统计包括明确出现的类型形状，如 dict、list、str、int、float、bool 与 null。可选字段缺省保持原样。

“确认”目前只用于明确写出的本地 JSON 文件路径及文件存在性。符号引用采用同文件及可见 Ability 局部定义的保守候选、全语料单一候选、多候选或未解析。以艾丝妲为例：

```json
{"$type":"RPG.GameCore.TriggerAbility","AbilityName":{"Value":"Avatar_Asta_00_Skill01_Phase02"}}
```

该摘录位于 `Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json#/AbilityList/0/OnStart/1`，对应定义是同文件 `/AbilityList/1`，索引为 scoped。角色配置 `Config/ConfigCharacter/Avatar/Avatar_Asta_00_Config.json#/SkillAbilityList/0/AbilityList/2` 也出现同一名字，索引为跨文件单一候选。查找条件和覆盖限制见 [索引说明](../index/README.md)。

别名引用中的大量 unresolved 主要来自仅索引具名 `GlobalTargetAlias` 声明，像 `Caster` 一类实际常用别名可能由配置之外或其他容器提供。引用汇总按形态分列，在读数时应结合原字段、锚点和上下文。入选 Excel 表的键联接保留全部候选行及无匹配项，后续专题追加具名参数和作用域验证。

全量类型复算、固定随机种子的指针回读及 SQLite 检查见 [验证脚本](../tools/validate_index.py) 和 [日志](../index/validation.log)。作用域解析以离线可验证的字面证据为限。布局、运行时默认值和引擎注册机制另记 Unknown。

## 数据质量与索引修订

严格检查中未发现未加引号的非有限数值。15 份 ExcelOutput 常量文件出现共 263 次重复对象键，其中 `ExcelOutput/ConstValueClient.json` 有 126 次，见 [质量日志](../index/json-quality.log)。当前 JSON 对象视图遵循 Python 标准库保留末项的行为。重复键相关配置须回读文件文本，无法据此确认游戏解析器的取值规则。

核心统计以 ConfigAbility / ConfigGlobalModifier 为准确标明的口径。v2 追加索引观察到的具名定义包括 RtBattle 的 557 Ability、433 Modifier，RtDefence 的 34 Ability、6 Modifier，ConfigAdventureAbility 的 589 Ability、229 Modifier，ConfigAdventureModifier 的 2,882 Modifier，以及 ConfigChessAbility 的 9 Ability。它们的路径与主战斗域分列。v2 字面名识别还让 `Config/ConfigAbility/Monster/Monster_W4_DawnsEye_00_Ability.json` 中 `IncludeTaskListTemplate` 的 `Name: "Monster_ChangePhase"` 可关联 [全局任务模板的已索引定义](../index/README.md)。静态联接仍需考虑同名局部模板与装载规则。

两版本的文件指纹与 `$type` 基准统计完全一致，差异限于定义、引用、事件形态与主数据联接覆盖。见 [版本比较](../index/index-version-comparison.tsv)。

**验收记录。** v1 和 v2 分别复算 134,609 文件、4,636 个类型、2,778,581 个节点，四类指针共 128 个固定种子样本均回读通过。候选主数据联接中，v1 的 126,387 行含 1,020 个无目标行，v2 的 127,555 行含 526 个无目标行。无目标行保留原字段及候选目标表。版本差异的原因同时包括新增规则及纠正旧规则，不能从这个差值推断多少独立实体得到补全。 [v1 日志](../index/validation.log) · [v2 日志](../index/validation-v2.log)

重复键下被覆盖的值未发现字符串 `$type` 注解。[补充引用表](../index/reference-overlay.tsv)包含 Excel `StageAbilityConfig` 的 7,128 个显式项，其中 16 项无名称匹配。模板选择器根据定义祖先路径考察词法候选，有 43 个选择器只有其他词法子树的候选。这个数量归属于补充解析规则，不能和 v2 基础状态表直接相加。
