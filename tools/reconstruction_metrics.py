#!/usr/bin/env python3
"""Compare selected role shapes used in the reconstruction; one row per task type."""
import csv
import json
from collections import Counter
from query import ROOT

OP = ROOT / '02-atomic-operations' / 'operations.tsv'
OUT = ROOT / '08-engine-reconstruction'

REPRESENTATIVE = {
    'DamageByAttackProperty', 'FireWaveProjectile', 'HealHP', 'InitShield',
    'AddModifier', 'RemoveModifier', 'ModifyDamageData', 'StackProperty',
    'PredicateTaskList', 'Retarget', 'IncludeTaskListTemplate', 'LoopExecuteTaskList',
    'SetDynamicValue', 'SetControlSkillMapping', 'TriggerModifierCustomEvent',
    'TriggerAbility', 'TurnInsertAbility', 'TurnInsertAction', 'ModifyActionDelay',
    'SetActionDelay', 'ModifySPNew', 'ModifySpecialSP', 'ModifyEntityBoostPoint',
    'ModifyTeamBoostPoint', 'CreateBattleEvent', 'CreateServant',
}

def parse(row, field):
    return json.loads(row[field])

def main():
    totals = Counter()
    witnesses = []
    with OP.open(encoding='utf-8') as handle:
        for row in csv.DictReader(handle, delimiter='\t'):
            typ = row['type']
            fields = {pair.split(':', 1)[0] for pair in parse(row, 'fields')}
            family = set(parse(row, 'families'))
            children = parse(row, 'children')
            input_target = bool(parse(row, 'targets'))
            core = int(row['core']) > 0
            flags = {
                'typed task role': True,
                'literal TargetType field': 'TargetType' in fields,
                'target/source-shaped input': input_target,
                'selected nested task': bool(children),
                'TargetType and selected nested task': 'TargetType' in fields and bool(children),
                'Avatar and Monster ability resource families':
                    {'Config/ConfigAbility/Avatar', 'Config/ConfigAbility/Monster'} <= family,
                'opaque identifier': row['category'] == '不透明标识',
            }
            for metric, present in flags.items():
                if present:
                    totals['all selected task types', metric] += 1
                    if core:
                        totals['type also occurs in core task slots', metric] += 1
            if typ.rsplit('.', 1)[-1] in REPRESENTATIVE:
                witnesses.append((typ, row['core'], row['adjacent'], row['special'],
                                  row['usual_path'], row['usual_pointer'],
                                  row['contrasting_path'], row['contrasting_pointer'],
                                  row['families'], row['children']))
    assert {t.rsplit('.', 1)[-1] for t, *_ in witnesses} == REPRESENTATIVE
    outputs = [
        ('composition-shapes.tsv', ['population', 'metric', 'types'],
         [(scope, metric, n) for (scope, metric), n in sorted(totals.items())]),
        ('composition-witnesses.tsv',
         ['type', 'core', 'adjacent', 'special', 'example_path', 'example_pointer',
          'contrast_path', 'contrast_pointer', 'families', 'children'], witnesses),
    ]
    for path, header, rows in outputs:
        with (OUT / path).open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
            writer.writerow(header)
            writer.writerows(rows)
    for scope, metric, n in outputs[0][2]:
        print(f'{scope}\t{metric}\t{n}')
    print('representative type positions:', len(witnesses))

if __name__ == '__main__':
    main()
