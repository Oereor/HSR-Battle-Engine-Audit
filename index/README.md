# 公共索引

`audit.sqlite` 用 Python 标准库 `sqlite3` 读取。研究目录内运行 `python3 tools/query.py` 可查看命令帮助。各视图的 `path` 相对于 TurnBasedGameData，`pointer` 使用零基 JSON Pointer，空字符串表示根。

| 表或视图 | 一行的含义 |
| --- | --- |
| `files` | 文件的路径、字节数、SHA-256、扫描或排除类别、解析状态与错误 |
| `occurrences` | 一个字符串 `$type` 的节点，附所属字段、最近的上层类型、数组成员证据及最近定义锚点 |
| `type_counts` / `type_context` / `fields` | 全解析范围内类型统计、上下文统计及同类型直接字段形态；计数单位为节点 |
| `definition_locations` | 一个 Ability、Modifier、全局 target alias、具名 task template 或 skill pool 的配置定义；`keys_json` 为直接字段数组 |
| `reference_locations` | 在预定符号字段中检测到的一个字面值及解析结果；`confirmed` 为存在的显式文件路径；`scoped` 为同文件或 Ability 局部候选；`candidate` 为全语料单一名称候选；`ambiguous` 为多候选；`unresolved` 为无匹配 |
| `event_locations` | 回调选择器、钩子、容器、命名事件字段、部分数值事件字段及动画记录；同一概念可对应多行不同形态 |
| `shapes` | 预定关键字段的原始 JSON 局部和所属定义类别 |
| `excel_rows` / `excel_edges` | 入选主数据表及基于字段/ID 的候选连接；一个 SkillID 可以连接多级配置；空目标为无匹配 |

引用算法不推断隐式装载、外部默认值、运行时字符串求值或目标实体上的定义。相同名字可能在多个资源中重复。父字段为对象键，数组索引由 JSON Pointer 保留。事件表中的动画名字与其他事件字段仅共享文本查找能力，各专题所用联接须另外给出作用域证据。完整 symbol 字段规则和 Excel 选表及连接口径见 [扫描代码](../tools/build_index.py)。`files` 为所有非 Git 普通文件提供指纹，layout 和 TextMap 只计文件及指纹。

```sh
python3 tools/query.py type RPG.GameCore.AddModifier
python3 tools/query.py definition Avatar_Asta_00_Skill01_Phase02
python3 tools/query.py reference Avatar_Asta_00_Skill01_Phase02
python3 tools/query.py event OnCreate
python3 tools/query.py show Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json /AbilityList/0/OnStart/0
python3 tools/query.py sql 'SELECT type,occurrences FROM type_counts ORDER BY occurrences DESC'
python3 tools/build_index.py --verify-source
python3 tools/validate_index.py
```

重新生成用 `python3 tools/build_index.py`，需本地同一份源。生成会用独立临时数据库，在检查后替换旧数据库。

## 扩展索引 v2

`audit.sqlite` 为 v1，供 00 普查和 Wave 1 的核心统计复现。`audit-v2.sqlite` 重用相同扫描范围和类型统计，扩展顶层 `AbilityList` 中的具名对象、顶层 Modifier maps、`IncludeTaskListTemplate.Name` 引用、动画状态和组记录，以及强化和活动事件的 Excel 键链。附加玩法需按路径分域。可用 `AUDIT_INDEX_VERSION=2 python3 tools/query.py …` 查询，用 `python3 tools/build_index.py --version 2` 重建。两个库的覆盖差异报告见 [index-version-comparison.tsv](index-version-comparison.tsv)。StageAbilityConfig、目标技能表、玩法混淆字段和模板覆盖仍须按语境校对，见对应专题。

[补充引用表](reference-overlay.tsv)从 v2 导出 7,128 个显式 `StageAbilityConfig` 项与 5,742 个 `IncludeTaskListTemplate.Name` 选择器，记录候选定义位置。后者增加祖先路径检验并优先保留最近作用域，43 条仅匹配其他词法子树。其运行时可见性保持 Unknown。前者 16 条无名称匹配。通过 `python3 tools/reference_overlay.py` 复算。[计数](reference-overlay-counts.tsv)
