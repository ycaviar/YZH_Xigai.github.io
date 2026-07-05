# -*- coding: utf-8 -*-
"""将人工裁决回写到 questions_dedup.json，并重新生成 questions.js。"""
import json, re

with open(r'd:\桌面\习概题库\questions_dedup.json', encoding='utf-8') as f:
    data = json.load(f)
with open(r'd:\桌面\习概题库\rulings.json', encoding='utf-8') as f:
    rulings = json.load(f)

# 按顺序取出冲突题（与 docx 生成顺序一致）
conflict_pool = [p for p in data['pool'] if p['conflict']]
assert len(conflict_pool) == len(rulings), f"数量不匹配: 冲突{len(conflict_pool)} vs 裁决{len(rulings)}"

def infer_type(ruling):
    """根据裁决推断题型。"""
    if ruling in ('对', '错'):
        return 'judge'
    if len(ruling) == 1:
        return 'single'
    return 'multi'

changed = 0
type_changed = 0
skipped = 0
for pq, r in zip(conflict_pool, rulings):
    ruling = r['ruling'].strip()
    if not ruling:
        # 未填写，保留推荐答案
        skipped += 1
        print(f"  跳过 #{r['index']}: 未填写裁决，保留推荐 {pq['answer']}")
        continue

    old_answer = pq['answer']
    old_type = pq['type']
    new_type = infer_type(ruling)

    # 校验：裁决的字母必须都在选项 key 中
    if new_type != 'judge':
        avail_keys = {o['key'] for o in pq['options']}
        ruling_letters = set(ruling)
        if not ruling_letters.issubset(avail_keys):
            print(f"  ⚠ #{r['index']} 裁决 {ruling} 含选项外的字母，可选: {sorted(avail_keys)}")
            print(f"     题干: {pq['stem'][:60]}")
            # 仍然应用，但警告

    pq['answer'] = ruling
    pq['type'] = new_type
    pq['conflict'] = False  # 已解决

    ans_changed = (old_answer != ruling)
    typ_changed = (old_type != new_type)
    if ans_changed:
        changed += 1
    if typ_changed:
        type_changed += 1

    mark_a = '✎' if ans_changed else '='
    mark_t = f' [类型 {old_type}→{new_type}]' if typ_changed else ''
    print(f"  #{r['index']:2d} {mark_a} {old_answer}→{ruling}{mark_t}  {pq['stem'][:45]}")

# 更新 meta 统计（重新统计各题型）
from collections import Counter
type_counts = Counter(p['type'] for p in data['pool'])
remaining_conflicts = sum(1 for p in data['pool'] if p['conflict'])
data['meta']['judge'] = type_counts.get('judge', 0)
data['meta']['single'] = type_counts.get('single', 0)
data['meta']['multi'] = type_counts.get('multi', 0)
data['meta']['conflicts'] = remaining_conflicts
data['meta']['resolved_conflicts'] = len(rulings) - skipped

with open(r'd:\桌面\习概题库\questions_dedup.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n总结:")
print(f"  答案变更: {changed} 题")
print(f"  类型变更: {type_changed} 题")
print(f"  未填写(保留推荐): {skipped} 题")
print(f"  剩余冲突: {remaining_conflicts}")
print(f"  题型分布: 判断{type_counts['judge']}, 单选{type_counts['single']}, 多选{type_counts['multi']}")
print(f"已写回 questions_dedup.json")
