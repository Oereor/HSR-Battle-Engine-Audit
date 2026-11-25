# HSR 战斗引擎配置语言审计

数据为本地 TurnBasedGameData 工作树 `2c8a218502ebfccaf6e01675b0bdf6948d723bbb`，版本标记 `OSPRODWin4.7.0_D17216325_A17211182_L17175930`。当前阶段和校验结果见 [PROGRESS.md](PROGRESS.md)；研究口径见 [AUDIT_SPEC.md](AUDIT_SPEC.md)、[PLAN.md](PLAN.md) 与 [CLAIMS.md](CLAIMS.md)。

| 专题 | 报告 | 清单 |
| --- | --- | --- |
| 00 数据 | [报告](00-data-survey/report.md) | [清单](00-data-survey/inventory.md) |
| 01 Entity / Ability | [报告](01-entity-ability/report.md) | [清单](01-entity-ability/inventory.md) |
| 02 原子操作 | [报告](02-atomic-operations/report.md) | [清单](02-atomic-operations/inventory.md) |
| 03 Modifier | [报告](03-modifier/report.md) | [清单](03-modifier/inventory.md) |
| 04 Callback / Trigger | [报告](04-callback-trigger/report.md) | [清单](04-callback-trigger/inventory.md) |
| 05 执行上下文、目标与表达式 | [报告](05-context-expression/report.md) | [清单](05-context-expression/inventory.md) |
| 06 资源与行动调度 | [报告](06-resource-scheduling/report.md) | [清单](06-resource-scheduling/inventory.md) |
| 07 机制案例 | [报告](07-case-studies/report.md) | [清单](07-case-studies/inventory.md) |
| 08 引擎抽象 | [报告](08-engine-reconstruction/report.md) | [清单](08-engine-reconstruction/inventory.md) |

[索引手册](index/README.md)提供 SQLite 库结构、重建命令及 JSON Pointer 查询。原始引用路径以 TurnBasedGameData 为根。配置事实、静态推导、语义推断与运行时假设分别标级。
