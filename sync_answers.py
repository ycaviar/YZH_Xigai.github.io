# -*- coding: utf-8 -*-
"""将去重题池中已修正的答案同步回原始 questions.json（3260 题）。
   按 normalized stem 匹配，把 pool 中修正后的 answer 和 type 写回每条原始题目。"""
import json, re

def normalize(s):
    if not s: return ''
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[，。、,．.\?？!！:：;；""''\'\"\(\)（）【】\[\]《》<>\-—_·]', '', s)
    return s.lower()

with open(r'd:\桌面\习概题库\questions_dedup.json', encoding='utf-8') as f:
    pool = json.load(f)['pool']

# 建 normalized stem -> (answer, type) 索引
stem_map = {}
for p in pool:
    stem_map[normalize(p['stem'])] = (p['answer'], p['type'])

with open(r'd:\桌面\习概题库\questions.json', encoding='utf-8') as f:
    orig = json.load(f)

changed = 0
type_changed = 0
for s in orig['sets']:
    for q in s['questions']:
        key = normalize(q['stem'])
        if key in stem_map:
            new_ans, new_type = stem_map[key]
            if q['answer'] != new_ans:
                q['answer'] = new_ans
                changed += 1
            if q['type'] != new_type:
                q['type'] = new_type
                type_changed += 1

with open(r'd:\桌面\习概题库\questions.json', 'w', encoding='utf-8') as f:
    json.dump(orig, f, ensure_ascii=False, indent=2)

print(f"已同步回 questions.json:")
print(f"  答案修正: {changed} 条")
print(f"  类型修正: {type_changed} 条")
print(f"  总题数: {sum(len(s['questions']) for s in orig['sets'])}")
