# -*- coding: utf-8 -*-
"""在 questions_dedup.json 中添加一个涵盖全部题池的套题，置于列表首位。"""
import json

with open(r'd:\桌面\习概题库\questions_dedup.json', encoding='utf-8') as f:
    data = json.load(f)

# 若已存在 id=0 的全题套题则先移除，避免重复
data['sets'] = [s for s in data['sets'] if s['id'] != 0]

all_uids = [p['uid'] for p in data['pool']]
all_set = {
    'id': 0,
    'title': '全部题库',
    'source': '综合（去重合并）',
    'questionUids': all_uids
}
data['sets'].insert(0, all_set)
data['meta']['total_sets'] = len(data['sets'])

with open(r'd:\桌面\习概题库\questions_dedup.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"已添加「全部题库」套题: id=0, {len(all_uids)} 题")
print(f"当前套数: {data['meta']['total_sets']}")
