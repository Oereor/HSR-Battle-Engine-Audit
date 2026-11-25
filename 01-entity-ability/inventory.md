# 01 · 实体与 Ability 参考清单

清单基于公共 [SQLite 索引](../index/README.md) 和源 JSON 的选择性校核。静态索引单位为原始 JSON 节点。相同名称可以分布于多个文件，同一技能 ID 可以有多个等级行。所有证据文件路径以 TurnBasedGameData 为根，指针为零基 JSON Pointer。

## 表与图

| 数据文件 | 口径 |
| --- | --- |
| [ability-definitions.tsv](ability-definitions.tsv) | 公共 v1 核心 Config/ConfigAbility 的 17,102 个定义节点、16,941 个不同名称，保留字段形态及定位。 |
| [other-ability-domains-v2.tsv](other-ability-domains-v2.tsv) | v2 新发现的 1,189 个 Ability 定义位置，按 RtBattle 557、RtDefence 34、Adventure 589、Chess 9 分列路径。两库核心定义数相同，v2 全域统计为 18,291 个节点、18,128 个名字。扩展域独立保留，适用加载、调用规则未在本专题推断。 |
| [ability-references.tsv](ability-references.tsv) | 公共 v1 识别的 47,073 个字面 Ability 符号位置，包括 v1 解析范围的核心之外引用，如 RtBattle 指向其自身定义的数据在 v1 中可能记为 unresolved。 |
| [ambiguous-ability-candidates.tsv](ambiguous-ability-candidates.tsv) | 616 个存在歧义的符号位置，展开全部同名定义，计 1,232 行匹配候选。 |
| [ability-static-graph.tsv](ability-static-graph.tsv) | 68,291 条带节点锚点和源 JSON 指针的符号记录。图的 source_id 与 destination_id 来自 v1 defs，源为 Ability、Modifier 或 TaskListTemplate。空目标表示悬空或歧义。图包括请求、安装、移除、数据/模板及 Modifier 引用。 |
| [static-cycles.tsv](static-cycles.tsv) | 三种静态执行相关子图的有环 SCC 及原始定义位置，见下方口径。 |
| [excel-character-skill.tsv](excel-character-skill.tsv) | Avatar / Enhanced / LD / Trial / Servant / Monster / BattleEventData 的实体→技能参数行→角色配置→技能入口机械联接，保留模板位置、等级、同名定义计数和无匹配类别。 |
| [excel-extension-entries.tsv](excel-extension-entries.tsv) | 行迹、星魂、装备、套装、敌人、BattleEvent 与 Stage 的字面注入或关联字段，同名候选逐条展开。ExcelOutput/StageConfig.json 有 6,979 个 StageAbilityConfig 位置，均有一个核心同名候选。StageConfigLD.json 另有 149 处，分列于 [公共补充索引](../index/reference-overlay.tsv)。 |
| [verification.txt](verification.txt) | 实际生成日志、独立样本寻址、SCC 检查和参数联接断言。 |

公共索引 v1 跨域收录的 Ability 字面引用状态为 scoped 6,297、candidate 36,179、ambiguous 616、unresolved 3,981。v1 同文件定义和符号字面值匹配为 scoped，独一跨文件名称为 candidate。状态表达符号解析证据，调用条件与真正执行另行分析。`AbilityList`、`EntryAbility`、`PrepareAbility`、`RankAbility` 等来源另外以 relation 保存。安装、移除、计数查询和执行请求在语义上有不同用途。对 `TriggerAbility`、`TurnInsertAbility`、`TriggerParallelAbility` 等用现有类型和位置给出请求类别，标签保留原始 parent_type 供复核。名字动态组装、模板实参、目标实体装载、别名求值和是否进入分支等仍为静态抽象的边界。

### 图的三个覆盖口径

| 子图 | 去重边 | 有环 SCC | 边的筛选 |
| --- | ---: | ---: | --- |
| direct-scoped | 3,332 | 14 | Ability→Ability 请求，只纳入同作用域选定目标。 |
| direct-with-unique-candidates | 6,305 | 14 | 包含单一跨文件候选。 |
| with-modifier-and-template-bridges | 35,832 | 213 | 含请求及可解析的 Modifier 施加、模板引用，覆盖 Modifier 或模板回调中的静态请求线索。 |

后两列统计单位分别是唯一节点对和强连通分量，自环计入。SCC 不表示实际无限递归，也不表示每条图边会执行。第三图仅纳入选定目标，不含歧义候选和未识别格式。引用行带源指针与角色，允许后续扩大图规则。

### Excel 联接口径

- 角色联接以已明确来源的 `SkillList`、`SkillIDList` 为首键。Enhanced 取 `AvatarSkillConfig` 的功能数据，LD 和 Trial 各自取后缀表。敌方还经 `MonsterTemplateID` 连接模板，普通表与 Unique 表均纳入候选。
- 先按明文 `JsonPath`、`Config`、`JsonConfig` 找实体，再按技能表 `SkillTriggerKey` 匹配实体 `SkillList[n].Name`，最后读 `EntryAbility`。结果在已指定主表和解析路径范围内有 21,372 个入口行，因多等级及多主数据行可重复同一入口。另有配置路径缺失 82、未见入口 60、技能主表未匹配 25、实体配置中技能名未匹配 413、触发键空 115。该状态表示加入规则的残差，运行时有效性仍待证明。
- 扩展联接共含 1,030 个非空 `AbilityName` 位置，其中 608 个各有两个同名候选，422 个为单一候选。 `RankAbility` 76 个位置均单一候选。 `AbilityNameList` 中 379 个单一候选、4 个无命中。 `BattleEventConfig.AbilityList` 中 356 个单一候选、36 个无命中。Ability 名称为空但仍有属性或分支的情况见 [报告](report.md)。
- 表外的实体及玩法资源可以通过公共索引查询，联接脚本没有为所有临时、冒险或棋盘玩法定义实体 ID 规则。覆盖范围以代码所列主表为准。

## 核心定义直接字段

| 字段 | 节点数 | 可复查用途 |
| --- | ---: | --- |
| `Name` | 17,102 | 名称符号，定义位置是作用域的重要线索。 |
| `TargetInfo` | 12,542 | 目标相关配置，可与 Task 的 TargetType 同时出现。 |
| `OnStart` | 11,855 | 配置任务容器，见艾丝妲普攻。 |
| `Modifiers` | 7,530 | 局部具名定义映射，空映射也统计字段出现。 |
| `OnAdd` | 5,481 | 配置任务容器，见关卡与 BattleEvent。 |
| `DynamicValues` | 3,813 | 表达式与参数绑定，存在不同字段形态。 |
| `TaskListTemplate` | 290 | 定义附带的模板。 |
| `OnInsertAbort` | 110 | 插入请求相关清理或下一次请求。 |
| `Tag` | 52 | 显式标签，含义需按样本确认。 |
| `OnRemove` | 35 | 移除相关任务容器。 |
| `ServantWhiteList` | 5 | 显式 ID 选择数据，运行时判断规则未知。 |
| `DynamicStrings` | 4 | 独立的字符串动态配置口径。 |

共有 260 个核心 Ability 同时列出 `OnAdd` 和 `OnStart`。角色配置已索引 SkillType 的显式取值计数为 Passive 2,871、Skill 2,153、Ultra 521、Maze 284、Elation 52、Servant 43、Assist 9。缺字段的条目不推测为某一枚举。字符串 MixAbility 和 MixTrigger 在核心索引中没有对应类型及同名已索引容器。直接字段与任务语义的例证见 [正文](report.md)。

## 复算

```sh
python3 01-entity-ability/build_ability.py
python3 tools/query.py definition Avatar_Asta_00_Skill01_Phase01
python3 tools/query.py reference Avatar_Archer_00_Insert_Phase01
```

主清单引用 v1 的 audit.sqlite，扩展域清单另外只读 v2。生成器复用 tools/query.py 的路径读取及查找。它只读选中的源配置和已索引数据库，生成文件限制在本专题。
