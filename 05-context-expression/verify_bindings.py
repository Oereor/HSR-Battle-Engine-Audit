#!/usr/bin/env python3
"""Check static parameter, target and dataflow witnesses in the local dump."""
from base64 import b64decode
from decimal import Decimal
import csv
from functools import lru_cache
import json

from catalogue import HERE, lookup, source
from probe_named_values import alternating_djb2

ASTA = 'Config/ConfigAbility/Avatar/Avatar_Asta_00_Ability.json'
ASTA_CHAR = 'Config/ConfigCharacter/Avatar/Avatar_Asta_00_Config.json'
BRONYA = 'Config/ConfigAbility/Avatar/Avatar_Bronya_00_Ability.json'
BRONYA_CHAR = 'Config/ConfigCharacter/Avatar/Avatar_Bronya_00_Config.json'
TINGYUN = 'Config/ConfigAbility/Avatar/Avatar_Tingyun_00_Ability.json'
TINGYUN_CHAR = 'Config/ConfigCharacter/Avatar/Avatar_Tingyun_00_Config.json'
ACHERON = 'Config/ConfigAbility/Avatar/Avatar_Acheron_00_Ability.json'
ACHERON_CHAR = 'Config/ConfigCharacter/Avatar/Avatar_Acheron_00_Config.json'
EQUIP = 'Config/ConfigAbility/Equip/EquipmemtAbility.json'
EQUIP_OLD = 'Config/ConfigAbility/EquipmemtAbility.json'
RELIC = 'Config/ConfigAbility/Equip/RelicAbility.json'
ASC = 'ExcelOutput/AvatarSkillConfig.json'
ATC = 'ExcelOutput/AvatarSkillTreeConfig.json'
ARC = 'ExcelOutput/AvatarRankConfig.json'
AC = 'ExcelOutput/AvatarConfig.json'
EC = 'ExcelOutput/EquipmentConfig.json'
ESC = 'ExcelOutput/EquipmentSkillConfig.json'
RSC = 'ExcelOutput/RelicSetSkillConfig.json'
EXR = 'ExcelOutput/AvatarExRankConfig.json'
ALIAS = 'Config/GlobalConfig/TargetAliasConfig.json'
OP = 'Config/GlobalConfig/TargetOperationConfig.json'
HIMEKO = 'Config/ConfigAbility/Avatar/Avatar_HimekoNova_00_Ability.json'
AGLAEA = 'Config/ConfigAbility/Avatar/Avatar_Aglaea_00_Ability.json'
EVAN = 'Config/ConfigAbility/Avatar/Avatar_Evanescia_00_Ability.json'
COMMON_MOD = 'Config/ConfigGlobalModifier/GlobalModifier_Common_Specific.json'

load = lru_cache(maxsize=25)(source)
evidence = {}

def read(path, pointer):
    return lookup(load(path), pointer)

def expect(path, pointer, expected):
    actual = read(path, pointer)
    assert actual == expected, (path,pointer,actual,expected)
    return actual

def save(label, path, pointer, keys=None):
    value = read(path, pointer)
    if keys is not None:
        value = {k:value[k] for k in keys}
    assert label not in evidence
    evidence[label] = {'id':label,'path':path,'pointer':pointer,'excerpt':value}
    return value

def fixed(expr):
    assert expr['IsDynamic'] is False and set(expr) == {'IsDynamic','FixedValue'}
    return Decimal(str(expr['FixedValue']['Value']))

def one(expr, hash_value):
    assert expr['IsDynamic'] is True and set(expr) == {'IsDynamic','PostfixExpr'}
    raw = expr['PostfixExpr']
    assert b64decode(raw['OpCodes'],validate=True) == bytes([1,0,17]), raw
    assert raw['FixedValues'] == [] and raw['DynamicHashes'] == [hash_value], raw

def two(expr, first, second, op, values):
    """Evaluate just two observed program shapes under the arithmetic hypothesis."""
    allowed = {2: lambda a,b: a+b, 4: lambda a,b: a*b}
    assert expr['IsDynamic'] is True and set(expr) == {'IsDynamic','PostfixExpr'}
    raw = expr['PostfixExpr']
    assert b64decode(raw['OpCodes'],validate=True) == bytes([1,0,1,1,op,17]), raw
    assert raw['FixedValues'] == [] and raw['DynamicHashes'] == [first,second], raw
    return allowed[op](*values)

def series(id, master_file, master_row, root_field, index, path, pointer, declaration_path, declaration_ptr, kind, trigger):
    read_info = expect(declaration_path, declaration_ptr+'/ReadInfo',
                       {'Type':kind,'TriggerKey':trigger,'Index':index})
    token = int(declaration_ptr.rsplit('/',1)[-1])
    expr = save(id+'-expression',path,pointer)
    one(expr,token)
    value_p = f'{master_row}/{root_field}/{read_info["Index"]}/Value'
    val = save(id+'-source',master_file,value_p)
    save(id+'-declaration',declaration_path,declaration_ptr+'/ReadInfo')
    return Decimal(str(val)), (path,pointer,master_file,value_p,declaration_path,declaration_ptr)

def entry(base, character, skills, ar, cr, idx, level):
    expect(AC, f'/{ar}/JsonPath', character)
    cr_skill = read(character, f'/SkillList/{idx}')
    skill = read(ASC, f'/{cr}')
    assert skill['SkillTriggerKey'] == cr_skill['Name'] and skill['Level'] == level
    assert skill['SkillID'] in read(AC, f'/{ar}/SkillList')
    matching = [i for i,item in enumerate(load(skills)['AbilityList']) if item['Name'] == cr_skill['EntryAbility']]
    assert len(matching)==1
    pointer = f'/AbilityList/{matching[0]}'
    save(base+'-avatar',AC,f'/{ar}',('AvatarID','JsonPath','SkillList','RankIDList'))
    save(base+'-skill',ASC,f'/{cr}',('SkillID','SkillTriggerKey','Level','ParamList'))
    save(base+'-entry',character,f'/SkillList/{idx}',('Name','TargetInfo','EntryAbility'))
    save(base+'-phase',skills,pointer+'/Name')
    return pointer

def record(results, case, out, expected, grade, pointer_details, annotation):
    assert out == Decimal(str(expected)), (case,out,expected)
    path,pointer,master,master_pointer,decl,decl_ptr = pointer_details
    results.append((case,str(out),grade,path,pointer,master,master_pointer,decl,decl_ptr,annotation))

def bindings():
    results = []
    trigger = entry('asta-basic',ASTA_CHAR,ASTA,7,191,0,1)
    expect(ASTA,trigger+'/OnStart/1/AbilityName/Value',read(ASTA,'/AbilityList/1/Name'))
    for level,row in [(1,191),(2,192)]:
        id = f'asta-basic-L{level}'
        val, detail = series(id,ASC,f'/{row}','ParamList',0,ASTA,
           '/AbilityList/1/OnStart/7/AttackProperty/DamagePercentage',ASTA_CHAR,
           '/DynamicValues/Floats/-1126825319','SkillParam','Skill01')
        record(results,id,val,[0.5,0.6][level-1],'Derived',detail,'direct input')
    chance = '/AbilityList/1/OnStart/6/SuccessTaskList/0'
    expect(ASTA,'/AbilityList/1/OnStart/6/Predicate/PointTriggerKey','PointB1')
    expect(ATC,'/487/PointTriggerKey','PointB1')
    expect(ATC,'/487/AvatarID',read(AC,'/7/AvatarID'))
    for name,key,index,num in [('Chance',-1761699449,0,0.8),('LifeTime',-826297499,1,3)]:
        id = f'asta-point-{name}'
        val,detail=series(id,ATC,'/487','ParamList',index,ASTA,chance+'/'+name,ASTA_CHAR,
                          f'/DynamicValues/Floats/{key}','SkillTreeParam','PointB1')
        record(results,id,val,num,'Derived',detail,'PointB1 true branch')
    burn = chance+'/DynamicValues/Modifier_Burn_DamagePercentage'
    expr = save('asta-point-product-expression',ASTA,burn)
    expect(ASTA,chance+'/ModifierName/Value','MCommon_DOT_Burn')
    save('asta-point-source-product',ATC,'/487/ParamList/2')
    expect(ASTA_CHAR,'/DynamicValues/Floats/-741625860/ReadInfo',{'Type':'SkillTreeParam','TriggerKey':'PointB1','Index':2})
    for lvl, row in [(1,191),(2,192)]:
        operands = [Decimal(str(read(ASC,f'/{row}/ParamList/0/Value'))),Decimal(str(read(ATC,'/487/ParamList/2/Value')))]
        val=two(expr,-1126825319,-741625860,4,operands)
        record(results,f'asta-point-product-L{lvl}',val,[0.25,0.3][lvl-1],'Inferred',
               (ASTA,burn,ATC,'/487/ParamList/2',ASTA_CHAR,'/DynamicValues/Floats/-741625860'),
               f'candidate product, other operand ExcelOutput/AvatarSkillConfig.json#/{row}/ParamList/0')
    damage = '/ModifierMap/MCommon_DOT_Burn/_CallbackList/1/CallbackConfig/2'
    dot = save('burn-damage',COMMON_MOD,damage,('$type','TargetType','AttackProperty'))
    expr = dot['AttackProperty']['DamagePercentage']['PostfixExpr']
    assert alternating_djb2('Modifier_Burn_DamagePercentage') in expr['DynamicHashes']

    trigger=entry('bronya-skill',BRONYA_CHAR,BRONYA,9,312,1,1)
    expect(BRONYA,trigger+'/OnStart/0/FailedTaskList/2/AbilityName/Value',read(BRONYA,'/AbilityList/3/Name'))
    guard='/AbilityList/3/OnStart/4'
    expect(BRONYA,guard+'/Predicate/$type','RPG.GameCore.ByRankActivated')
    expect(BRONYA,guard+'/Predicate/TriggerKey/Hash',read(ARC,'/71/Trigger/Hash'))
    assert read(ARC,'/71/RankID') in read(AC,'/9/RankIDList')
    lifetimes=[]
    for arm in ('Failed','Success'):
        save('bronya-'+arm,BRONYA,guard+f'/{arm}TaskList/0',
             ('$type','TargetType','ModifierName','LifeTime','DynamicValues'))
        lifetimes.append(guard+f'/{arm}TaskList/0/LifeTime')
    val,detail=series('bronya-base',ASC,'/312','ParamList',2,BRONYA,lifetimes[0],BRONYA_CHAR,
                      '/DynamicValues/Floats/1483309121','SkillParam','Skill02')
    record(results,'bronya-base',val,1,'Derived',detail,'Rank06 false branch')
    expect(BRONYA_CHAR,'/DynamicValues/Floats/1727293081/ReadInfo',{'Type':'SkillRank','TriggerKey':'Rank06','Index':0})
    rank=Decimal(str(save('bronya-rank',ARC,'/71/Param/0/Value')))
    result=two(read(BRONYA,lifetimes[1]),1483309121,1727293081,2,(val,rank))
    record(results,'bronya-E6',result,2,'Inferred',
           (BRONYA,lifetimes[1],ARC,'/71/Param/0/Value',BRONYA_CHAR,'/DynamicValues/Floats/1727293081'),
           'candidate sum, other operand ExcelOutput/AvatarSkillConfig.json#/312/ParamList/2')
    val,detail=series('bronya-boost',ASC,'/312','ParamList',0,BRONYA,
            guard+'/SuccessTaskList/0/DynamicValues/MDF_DamageAddedRatio',BRONYA_CHAR,
            '/DynamicValues/Floats/147328743','SkillParam','Skill02')
    record(results,'bronya-boost',val,0.33,'Derived',detail,'input to named modifier argument')
    save('bronya-modifier',BRONYA,'/GlobalModifiers/MAvatar_Bronya_00_BPSkill_DamageUp/_CallbackList/0')
    assert alternating_djb2('MDF_DamageAddedRatio') == 625640552

    trigger=entry('tingyun-ultra',TINGYUN_CHAR,TINGYUN,22,940,2,1)
    expect(TINGYUN,trigger+'/OnStart/5/AbilityName/Value',read(TINGYUN,'/AbilityList/6/Name'))
    compare='/AbilityList/6/OnStart/7'
    rank_row = '/149'
    expect(AC,'/22/RankIDList/5',120206)
    expect(ARC,rank_row+'/RankID',read(AC,'/22/RankIDList/5'))
    expect(TINGYUN,compare+'/Predicate/TriggerKey/Hash',read(ARC,rank_row+'/Trigger/Hash'))
    expect(ARC,'/143/Trigger/Hash',read(ARC,rank_row+'/Trigger/Hash'))
    expect(ARC,'/143/Param',[])
    assert read(ARC,'/143/RankID') not in read(AC,'/22/RankIDList')
    save('tingyun-rank-hash-collision',ARC,'/143',('RankID','Rank','Trigger','Param'))
    save('tingyun-rank',ARC,rank_row,('RankID','Rank','Trigger','Param'))
    declaration = '/DynamicValues/Floats/-1752447704'
    expect(TINGYUN_CHAR,declaration+'/ReadInfo',{'Type':'SkillRank','TriggerKey':'Rank06','Index':0})
    save('tingyun-rank-declaration',TINGYUN_CHAR,declaration+'/ReadInfo')
    add_path = compare+'/SuccessTaskList/0/FixedAddValue'
    add_expr = save('tingyun-success-expression',TINGYUN,add_path)
    val,detail=series('tingyun-base',ASC,'/940','ParamList',0,TINGYUN,compare+'/FailedTaskList/0/FixedAddValue',
                      TINGYUN_CHAR,'/DynamicValues/Floats/-1349665456','SkillParam','Skill03')
    record(results,'tingyun-base',val,50,'Derived',detail,'Rank06 false branch')
    rank = Decimal(str(read(ARC,rank_row+'/Param/0/Value')))
    result = two(add_expr,-1349665456,-1752447704,2,(val,rank))
    record(results,'tingyun-E6',result,60,'Inferred',
           (TINGYUN,add_path,ARC,rank_row+'/Param/0/Value',TINGYUN_CHAR,declaration),
           'candidate sum; RankID checked against AvatarID 1202, same hash on other avatar excluded')

    for lvl,row in [(1,0),(2,1)]:
        expect(ESC,f'/{row}/SkillID',read(EC,'/0/SkillID'))
        expect(ESC,f'/{row}/AbilityName',read(EQUIP,'/AbilityList/1/Name'))
        expect(ESC,f'/{row}/Level',lvl)
        for name,index,num,h,p in [
            ('crit',0,0.12 if lvl==1 else 0.15,-1330896030,
             '/AbilityList/1/Modifiers/MEquip_20000_Main/_CallbackList/0/CallbackConfig/0/PropertyValue'),
            ('lifetime',1,3,-1970381737,'/AbilityList/1/OnStart/0/LifeTime')]:
            id=f'equip20000-{name}-L{lvl}'
            val,detail=series(id,ESC,f'/{row}','ParamList',index,EQUIP,p,EQUIP,
                              f'/AbilityList/1/DynamicValues/Floats/{h}','SkillEquip','')
            record(results,id,val,num,'Derived',detail,'Equip/ definition, same-name root definition separate')
    old='/AbilityList/1/Modifiers/MEquip_20000_Main/_CallbackList/0/CallbackConfig/0/PropertyValue'
    expect(EQUIP_OLD,old+'/PostfixExpr/OpCodes','AQAK')
    save('old-equip-expr',EQUIP_OLD,old)
    save('old-equip-read',EQUIP_OLD,'/AbilityList/1/DynamicValues/Values/-1330896030/ReadInfo')

    expect(RSC,'/11/AbilityName',read(RELIC,'/AbilityList/7/Name'))
    expect(RSC,'/11/SetID',106)
    expect(RSC,'/11/RequireNum',4)
    a='/AbilityList/7/Modifiers/MRelic_106_Main/_CallbackList/0'
    expect(RELIC,a+'/Event','OnPhase1')
    for name,index,num,h,end in [
        ('hp-check',0,0.5,-1366832712,'/Predicate/CompareValue'),
        ('heal-rate',1,0.08,-1668979317,'/SuccessTaskList/0/HealPercentage'),
        ('recover-energy',2,5,229419792,'/SuccessTaskList/1/AddValue')]:
        id='relic106-'+name
        val,detail=series(id,RSC,'/11','AbilityParamList',index,RELIC,a+'/CallbackConfig/0'+end,RELIC,
                         f'/AbilityList/7/DynamicValues/Floats/{h}','SkillRelic','106_4')
        record(results,id,val,num,'Derived',detail,'local 106_4 key via SetID and RequireNum')
    save('relic106-modifier',RELIC,a)

    expect(EXR,'/2/ACCJKGEKHKP',read(AC,'/51/AvatarID'))
    expect(EXR,'/2/NNFEGHLLEPH/0',read(ACHERON,'/AbilityList/16/Name'))
    expect(ACHERON,'/AbilityList/18/OnStart/7/AbilityName/Value',read(ACHERON,'/AbilityList/19/Name'))
    val,detail=series('acheron-exrank',EXR,'/2','NNACKOBKFGE',1,ACHERON,'/AbilityList/19/OnStart/10/FixedAddValue',
                      ACHERON_CHAR,'/DynamicValues/Floats/21888035','SkillRank','ExRank01')
    record(results,'acheron-exrank',val,1,'Derived',detail,'obfuscated row separately bound to named Ability and AvatarID')
    save('acheron-exrank-row',EXR,'/2',('ACCJKGEKHKP','OIBKPJEGPOK','NNFEGHLLEPH','NNACKOBKFGE'))
    save('acheron-exrank-sp',ACHERON,'/AbilityList/19/OnStart/10')

    sample='/AbilityList/3/OnStart/1/SuccessTaskList/0/ServantID'
    val=fixed(save('aglaea-fixed-servant',AGLAEA,sample))
    record(results,'aglaea-fixed-servant',val,11402,'Observed',(AGLAEA,sample,'','','',''),'numeric ID input')
    return results

def context_samples():
    names=['Caster','AbilityTargetEntity','ModifierOwnerEntity','CallBackModifierCaster','AllEnemy','AllTeamMember',
           'ParamEntity','ParamEntity2','ParamEntityList','CasterServant','CasterSummoner','BattleEventCaster',
           'DamageAttackerEntity','DamageDefenderEntity','CurrentTurnActionEntity','CurrentTurnOwnerEntity','ProjectileHitEntity',
           'AbilityTargetAndAdjoinEntity','ParamEntityActualOwner','AvatarNextTurnOwnerEntity','AllLightTeam','AllDarkTeam']
    for name in names:
        save('target-'+name,ALIAS,'/AliasDict/'+name)
    for name in ('GetSummoner','GetActualOwner','RemoveServant','GetAliveOrLimbo'):
        save('operation-'+name,OP,'/OperationDict/'+name)
    assert [read(ALIAS,f'/AliasDict/{n}/$type') for n in ('Caster','ModifierOwnerEntity','CallBackModifierCaster','AbilityTargetEntity')] == [
      'RPG.GameCore.TargetFetchCaster','RPG.GameCore.TargetFetchModifierOwner','RPG.GameCore.TargetFetchCallBackModifierCaster','RPG.GameCore.TargetFetchAbilityTarget']
    write=save('saved-entity-write',HIMEKO,'/AbilityList/33/OnStart/0')
    fetch=save('saved-entity-read',HIMEKO,'/GlobalTargetAlias/HimekoNova_00_AssistTarget')
    assert write['ReadTargetType']['Alias']==fetch['Sequence'][0]['Alias']
    assert write['DynamicKey']==fetch['Sequence'][1]['DynamicKey']
    save('create-servant-arguments',AGLAEA,'/AbilityList/3/OnStart/1/SuccessTaskList/0')
    save('servant-record','ExcelOutput/AvatarServantConfig.json','/0',('ServantID','Config','SkillIDList','HPBase','HPInherit','SpeedBase','SpeedInherit'))
    save('callback-temporary',EVAN,'/AbilityList/14/Modifiers/MAvatar_Evanescia_00_Passive/_CallbackList/6/CallbackConfig/0/SuccessTaskList/0')
    save('callback-temporary-compare',EVAN,'/AbilityList/14/Modifiers/MAvatar_Evanescia_00_Passive/_CallbackList/6/CallbackConfig/0/SuccessTaskList/2/Predicate/PredicateList/0')
    save('ability-distinct-target',ACHERON,'/AbilityList/11/OnStart/8')
    save('ability-named-arguments','Config/ConfigAbility/Avatar/Avatar_PlayerBoy_40_Ability.json','/AbilityList/7/OnStart/7')
    save('read-damage-parameter','Config/ConfigAbility/Avatar/Avatar_Cipher_00_Ability.json',
         '/AbilityList/10/Modifiers/MAvatar_Cipher_00_PointB2_ListenNoKuosan/_CallbackList/0/CallbackConfig/0/SuccessTaskList/0')
    save('read-modifier-count',ACHERON,'/AbilityList/3/OnStart/1/SuccessTaskList/2/SuccessTaskList/0/TaskList/0/TaskList/1')
    save('read-special-energy',ACHERON,'/AbilityList/15/OnStart/1')
    save('random-min-max','Config/ConfigAbility/Avatar/Avatar_Aventurine_00_Ability.json',
         '/GlobalModifiers/MAvatar_Aventurine_00_Skill03_CoinAdd/_CallbackList/0/CallbackConfig/0')
    save('scope-caster','Config/ConfigAbility/BattleEventAbility_2.json','/AbilityList/5/OnAdd/1')
    save('scope-template','Config/ConfigAbility/BattleEventAbility_2.json','/GlobalTemplates/0/TaskList/0/SuccessTaskList/0/SuccessTaskList/0')
    save('scope-owner','Config/ConfigAbility/BattleEventAbility_2.json',
         '/AbilityList/17/Modifiers/Modifier_BattleEventAbility_Challenge_Month_26/OnDynamicValueChange/0',('Key','ContextScope'))
    save('event-custom-value','Config/ConfigAbility/Level/Level_RogueBuff_Ability_Nous.json',
         '/AbilityList/32/Modifiers/StageAbility_650303_Modifier_Sub/_CallbackList/0/CallbackConfig/0/SuccessTaskList/0/TaskList/0/TaskList/2')
    save('battle-target-value','Config/ConfigAbility/Level/Level_LocalLegend_Ability.json','/AbilityList/1/OnAdd/3')
    save('main-target','Config/ConfigCharacter/Avatar/Avatar_Himeko_00_Config.json','/SkillList/1/TargetInfo')
    save('rt-predicate-value','Config/Activity/RtBattle/Ability/Avatar/RtBattleAvatar_Background_Acheron_00_Ability.json',
         '/AbilityList/0/OnStart/0/PosTargetType/Sequence/1/GridEvaluator/Values/0')
    flag=save('retarget',TINGYUN,'/GlobalModifiers/MAvatar_TingYun_ByIsTingYun/_CallbackList/0/CallbackConfig/0')
    assert flag['ByRandom'] and flag['MaxNumber']['FixedValue']['Value']==1
    # Domesticized local copy uses the full original string unchanged.
    for label, key in [('bronya-rank-local-text','7244991336643732642'),('asta-point-local-text','16178627604319461393')]:
        save(label,'TextMap/TextMapCHS.json','/'+key)

def main():
    results = bindings()
    context_samples()
    with (HERE/'binding-results.tsv').open('w',encoding='utf-8',newline='') as handle:
        out = csv.writer(handle,delimiter='\t',lineterminator='\n')
        out.writerow(['case','static_value','evidence_grade','task_file','task_pointer','data_file','data_pointer','declaration_file','declaration_pointer','comment'])
        out.writerows(results)
    with (HERE/'evidence.jsonl').open('w',encoding='utf-8') as handle:
        for entry in evidence.values():
            handle.write(json.dumps(entry,ensure_ascii=False,separators=(',',':'))+'\n')
    print(f'{len(evidence)} exact fragments; {len(results)} static checks')
    for case,value,grade,*_ in results:
        print(case,value,grade)

if __name__=='__main__':
    main()
