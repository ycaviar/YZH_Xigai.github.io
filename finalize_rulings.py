# -*- coding: utf-8 -*-
"""将留空的裁决（同意推荐）也标记为已解决，然后重新生成 questions.js。"""
import json
from collections import Counter

with open(r'd:\桌面\习概题库\questions_dedup.json', encoding='utf-8') as f:
    data = json.load(f)

# 把所有剩余的 conflict 题标记为已解决（保留推荐答案）
remaining = [p for p in data['pool'] if p['conflict']]
for p in remaining:
    p['conflict'] = False
    print(f"  标记已解决(保留推荐 {p['answer']}): {p['stem'][:50]}")

# 更新 meta
type_counts = Counter(p['type'] for p in data['pool'])
data['meta']['judge'] = type_counts.get('judge', 0)
data['meta']['single'] = type_counts.get('single', 0)
data['meta']['multi'] = type_counts.get('multi', 0)
data['meta']['conflicts'] = 0
data['meta']['resolved_conflicts'] = 37

with open(r'd:\桌面\习概题库\questions_dedup.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n剩余冲突: {sum(1 for p in data['pool'] if p['conflict'])}")
print("已写回 questions_dedup.json")
