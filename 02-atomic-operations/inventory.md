# 操作参考清单

[全部任务类型及字段](operations.tsv) 是本专题的逐类型参考目录，一行一个完整 $type。以原始类型名称查询，保留不透明标识和单例。1,279 种类型由 6,222 个已选数据文件中的 364,136 个定位节点生成。核心、相邻和专用计数及源范围见 [专题报告](report.md)。查找伤害、HP、护盾、韧性、资源、状态、属性、实体、控制流、召唤、延时、表现和专有类型可按 category 或字段筛选。对于同名类型在不同位置的可能语义差异，以 placement 和对照样本为准。

| 表 | 查阅方法 |
| --- | --- |
| [operations.tsv](operations.tsv) | 1,279 行完整任务类型。全域计数和各选区计数并列，由多个配置位置、字段类型、目标形式、嵌套和符号字段描述其配置形态 |
| [semantic-notes.tsv](semantic-notes.tsv) 和 [semantic-evidence.tsv](semantic-evidence.tsv) | 69 种人工整理类型及证据等级。常用和对照节点的选定字段片段用于定位和验证。片段中的大对象、数组或子任务有所裁剪，计数均来自完整节点 |
| [symbol-links.tsv](symbol-links.tsv) | 关联到最近选中任务祖先的 Ability、Modifier、Template 符号，按索引的 scoped、candidate、ambiguous、unresolved 区分。单个任务可以承担多个引用 |
| [template-links.tsv](template-links.tsv) | IncludeTaskListTemplate.Name 的独立完整补充，使用最近的同文件定义容器和全语料候选。该字段的系统装载规则、分发与参数运行时仍未知 |
| [supporting-types.tsv](supporting-types.tsv) | 按目标、判定与值求值分列支持结构的全量位置汇总及样本，覆盖目录构建器所列字段及类型模式。支持结构的细分见 05 |
| [review-outside.tsv](review-outside.tsv) | 相同任务槽但位于主清单选区之外的位置，按原始类型、字段、目录和一个可查定位列示。未将这些位置推定为传统回合制战斗 |

## 主清单字段

| 列 | 口径 |
| --- | --- |
| type · category · semantic_grade · configured_role | 完整类型、手工类别或候选标签、语义等级和有证据时的配置用途。候选标签只按名称用于检索，Unknown 仍有可核验的结构数据 |
| all_indexed_occurrences · core · adjacent · special | 前者为整个公共索引内同类型全部位置，后三列为本专题中互斥的三类选中节点 |
| slots · placement · families | 配置键与计数。placement 同时记录范围、父字段、最近带类型的祖先及最近定义锚点角色 |
| fields · inputs | 字段名及 JSON 形态的频数。除机械 $type 外的字段都保留，未被认定为运行时必选输入。dict、list、int、float、str、bool 和 null 按实际反序列结果记录 |
| targets · contexts | 以常见目标、来源、持有者、读取端字段名识别潜在目标或主体输入。值记为字面量、@Alias、对象类型或结构形态；contexts 按明确的上下文类字段键记录。完整表达式嵌套需查原节点 |
| children | 对最近上层选中任务的路径首段与子任务类型聚合。计数单位是父节点，每个父节点同一槽位和子类型只记一次 |
| link_fields | 直接观察的 Ability、Modifier、Template、Event 或 Callback 相关字段。符号解析状态见独立表。监听、引用和发出请求的证据不能互换 |
| usual_path · usual_pointer · usual_anchor | 优先选核心、该类型最大文件族与最常见字段签名，按路径和指针稳定排序 |
| contrasting_path · contrasting_pointer · contrasting_anchor | 优先选其他文件和不同槽，其次选稀有字段签名。若类型在选区仅出现一次，对照留空 |

在研究目录执行以下命令重建和验证。索引由 [00](../00-data-survey/report.md) 管理，构建器不会重新遍历整个 dump，仅打开索引选中的数据文件及证明样本。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 02-atomic-operations/catalogue.py
PYTHONDONTWRITEBYTECODE=1 python3 02-atomic-operations/validate.py
python3 tools/query.py type RPG.GameCore.DamageByAttackProperty --limit 8000
python3 tools/query.py show Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json /AbilityList/1/OnStart/7
```
