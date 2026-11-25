# 具名参数与有符号哈希的静态检验

## 结构与算法

**Observed**。艾丝妲终结技的 `AddModifier` 参数字典有键 `MDF_PropertyValue`，局部状态回调的 `StackProperty` 表达式读取有符号整数 `2128130574`。施加指令为 `Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json#/AbilityList/6/OnStart/2`，目标状态回调见同文件 `/AbilityList/6/Modifiers/MAvatar_Asta_00_Ultra_SpeedUP/_CallbackList/0/CallbackConfig/0`。读值表达式的最小片段为：

```json
{"OpCodes":"AQAR","FixedValues":[],"DynamicHashes":[2128130574]}
```

**Inferred**。以上样本和大规模对照支持双累加器的文本哈希候选。下面是静态计算规则，用于检验 dump 中的已存数值。官方源码、内部命名和运行时绑定算法仍为 **Unknown**。

1. 两个 32 位累加器初值均为 5381。
2. 依次处理 UTF-16 码元，按位置奇偶交替选择累加器，以 `(a * 33) XOR code_unit` 更新，保留低 32 位。
3. 把 `a0 + a1 * 1566083941` 的低 32 位解释为有符号整数。

该规则算出 `MDF_PropertyValue → 2128130574`、`MDF_1 → 909832565`、`ADF_1 → 909827945`。同一算法预测 `Rank02 → 523552506`，与 `ExcelOutput/AvatarRankConfig.json#/55/Trigger/Hash` 一致。按序数构造 `Rank01` 到 `Rank06` 的对照在普通、LD、Trial 表的 630、24、30 行分别全数匹配。可从 `ExcelOutput/AvatarRankConfig.json#/0/Trigger/Hash`、`ExcelOutput/AvatarRankConfigLD.json#/0/Trigger/Hash`、`ExcelOutput/AvatarRankConfigTrial.json#/0/Trigger/Hash` 核对各表形态。ASCII 主导样本对非 ASCII 文本编码与名称规范化的约束有限。

## 范围、对照与反例

通过公共 v2 的 scoped 同文件 `AddModifier.ModifierName` 枚举候选。施加点的 `DynamicValues` 必须只有一个键，状态定义 `DynamicValues.Floats` 也必须只有一个整数键，且该整数在状态某个 `DynamicHashes` 中被取用。专用玩法只在路径位于 `Config/ConfigAbility/` 时纳入。该筛选产生 2,507 个位置、480 个具名键与 501 组不同名/候选编号对。它是一条可运行的静态候选联接。

| 验证项 | 结果 |
| --- | --- |
| 双累加器候选与配对哈希一致 | 2,394 / 2,507 个位置，444 / 501 组不同配对 |
| 剩余位置的状态仍读取候选算法预测值 | 100 / 113 |
| CRC32、Adler32、FNV1、FNV1a、乘 31、BKDR 131、djb2、djb2xor、sdbm | 每个算法对 UTF-8 和 UTF-16LE 字节分别测试，各模式均为 0 / 2,507 |
| 星魂 RankNN 取值对照 | 684 / 684 行 |

一个能够定位的单键误配例来自 `Config/ConfigAbility/Activity/Activity_FateChess_Ability.json#/GlobalModifiers/MActivity_FateChess_Rider_02_GlobalBuff/_CallbackList/0/CallbackConfig/0/DynamicValues`。施加键为 `MDF_PropertyValue`，目标状态的唯一 Float 声明为 1662446059。然而状态的 `StackProperty` 同时引用 2128130574 和 1662446059，并在此前配置把层数读入文本键 `MDF_Layer`。后者恰好预测为 1662446059。这个样本分离了施加实参和状态自身声明。见 `Config/ConfigAbility/Activity/Activity_FateChess_Ability.json#/GlobalModifiers/MActivity_FateChess_Rider_02_SpeedUp/_CallbackList/0/CallbackConfig`。

13 个剩余位置在目标状态内未找到预测值。例如 `Config/ConfigAbility/BattleEvent/TotalAttack_Ability.json#/AbilityList/1/OnAdd/12` 的 `CustomDamage` 对应同文件 `/AbilityList/1/Modifiers/Modifier_StageAbility_3107001` 的单一局部候选 194532370。现有证据仅表明算法预测与该单键联接不合，需要上下文、模板或变量用途的其他证据。Cerydra 的 `DV_AddPoint` 也提示绑定中可能有多层取值，文本候选计算为 -1559105366，某些同名参数的表达式输入读取 -1083076378。哈希预测值、调用输入的源哈希与接收作用域中的绑定应分别追踪。

[复算脚本](../tools/probe_named_values.py) · [全部候选](hash-probe-pairs.tsv) · [实跑日志](hash-probe.log)
