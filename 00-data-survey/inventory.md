# 数据与公共索引清单

由 [survey.py](../tools/survey.py) 从 SQLite 生成。字节为实际文件大小。同一类型或名称可跨多个类别出现。

## 文件及解析

| 类别 | 状态 | 文件 | 字节 |
| --- | --- | --- | --- |
| layout | excluded | 9076 | 6050478 |
| non-json | excluded | 1 | 966 |
| scan | parsed | 134609 | 1742876973 |
| text | excluded | 29 | 964722759 |

## 顶层目录

| 目录 | 文件 | 字节 | 成功解析 |
| --- | --- | --- | --- |
| . | 1 | 966 | 0 |
| Config | 131677 | 1145609510 | 122610 |
| ExcelOutput | 2317 | 283045017 | 2317 |
| Stages | 3561 | 291256406 | 3561 |
| Story | 6130 | 29016518 | 6121 |
| TextMap | 29 | 964722759 | 0 |

## 类型与符号

观测到 4,636 个不同的字符串 `$type`，共 2,778,581 次出现。

| 定义类别 | 定义节点 | 不同名称 |
| --- | --- | --- |
| ability | 17102 | 16941 |
| alias | 362 | 362 |
| modifier | 22729 | 21547 |
| skill_pool | 70 | 70 |
| template | 1739 | 1494 |

| 引用状态 | 节点 |
| --- | --- |
| ambiguous | 1321 |
| candidate | 58751 |
| confirmed | 240672 |
| scoped | 51038 |
| unresolved | 270719 |

| 事件索引形态 | 记录 | 不同原始值 |
| --- | --- | --- |
| animation-record | 18 | 18 |
| callback-selector | 35896 | 224 |
| container | 56291 | 2 |
| event-type-field | 217 | 22 |
| hook | 286537 | 441 |
| named-event-field | 157333 | 1955 |

详见 [全部类型 counts](types.tsv)、[引用汇总](ref-totals.tsv)、[同名定义](definition-collisions.tsv) 和 [JSON 解析失败](parse-failures.tsv)。

## Config 子树

| 目录 | 文件 | 字节 | 成功解析 |
| --- | --- | --- | --- |
| . | 42 | 10798347 | 40 |
| Activity | 1157 | 9508509 | 740 |
| AssetPreload | 924 | 6726471 | 924 |
| BattleCollegeCaption | 21 | 9260 | 21 |
| BattleLineupPage | 12 | 24441 | 12 |
| BattleMode | 8 | 8670 | 3 |
| CameraTemplate | 6 | 102356 | 4 |
| CharacterOutfit | 26 | 142348 | 26 |
| Chronicle | 2 | 1096 | 2 |
| ConfigAI | 1477 | 8670732 | 814 |
| ConfigAbility | 3496 | 174917099 | 1748 |
| ConfigActivityClockPark | 54 | 151766 | 54 |
| ConfigAdventureAbility | 552 | 3474153 | 297 |
| ConfigAdventureModifier | 39 | 414267 | 28 |
| ConfigAnimEvents | 5084 | 17201772 | 3500 |
| ConfigAnimZone | 379 | 757725 | 379 |
| ConfigAvatarPathChange | 12 | 7832 | 12 |
| ConfigBattlePerform | 1 | 2524 | 1 |
| ConfigBooklet | 80 | 2603606 | 80 |
| ConfigCharacter | 3558 | 14449064 | 3039 |
| ConfigChessAbility | 13 | 30855 | 7 |
| ConfigCommonSkillPool | 55 | 147769 | 49 |
| ConfigEntity | 3479 | 2918078 | 3479 |
| ConfigFreeStyle | 1871 | 4914978 | 1693 |
| ConfigGlobalModifier | 32 | 2275167 | 16 |
| ConfigGlobalTaskListTemplate | 20 | 593439 | 10 |
| ConfigLockModule | 1 | 7213 | 1 |
| ConfigMapRotation | 1 | 7765 | 1 |
| ConfigMazeBuff | 1 | 31 | 1 |
| ConfigMunicipal | 15 | 7991 | 15 |
| ConfigNPCComplexity | 1 | 11314 | 1 |
| ConfigOptionalLoadBlocks | 4 | 24808 | 4 |
| ConfigPlayerOutfit | 81 | 36535 | 81 |
| ConfigPointQuery | 1 | 625 | 1 |
| ConfigQteCatchGhost | 1 | 462 | 1 |
| ConfigRedDot | 2 | 1898 | 2 |
| ConfigReplaceCharacterMaterial | 114 | 527942 | 114 |
| ConfigSceneProp | 27 | 6572 | 27 |
| ConfigServerPrefs | 1 | 22176 | 1 |
| ConfigSkin | 11 | 38389 | 11 |
| ConfigSpecialVision | 1 | 2308 | 1 |
| ConfigSummonUnit | 150 | 319485 | 77 |
| CutSceneCaption | 173 | 130322 | 173 |
| Device | 4 | 296089 | 4 |
| Entity | 1 | 177 | 1 |
| GamePlay | 2 | 2692 | 2 |
| Gameplays | 2629 | 176497269 | 2608 |
| GlobalConfig | 19 | 1083608 | 14 |
| HoyoTag | 1 | 39804 | 1 |
| KraterWorldShop | 1 | 22 | 1 |
| Level | 69863 | 227604178 | 66321 |
| LevelOutput | 32690 | 194873968 | 32690 |
| LevelOutput_Baked | 1709 | 281158785 | 1709 |
| Manikin | 3 | 15322 | 3 |
| MissionRes | 1 | 117111 | 1 |
| NpcMaterialVariant | 1 | 423579 | 1 |
| OperationRecord | 4 | 1188 | 4 |
| Performance | 9 | 50245 | 9 |
| PhotoGraph | 2 | 6122 | 2 |
| Props | 1739 | 1269917 | 1737 |
| Resolution | 2 | 11049 | 2 |
| Sound | 1 | 2006 | 1 |
| StandalonePerformance | 1 | 49064 | 1 |
| Test | 1 | 475 | 1 |
| Transition | 4 | 37548 | 2 |
| UIAdaption | 5 | 71132 | 5 |
