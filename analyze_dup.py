# -*- coding: utf-8 -*-
"""分析题库重复情况，输出报告以辅助决策去重策略。"""
import json
import re
from collections import defaultdict, Counter

with open(r'd:\桌面\习概题库\questions.json', encoding='utf-8') as f:
    data = json.load(f)

def normalize(s):
    """标准化：去空白、去标点、转小写，用于检测近似重复。"""
    if not s:
        return ''
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[，。、,．.\?？!！:：;；""''\'\"\(\)（）【】\[\]《》<>\-—_·]', '', s)
    return s.lower()

sets = data['sets']
all_questions = []  # [(set_id, q_id, type, stem_raw, stem_norm, answer)]
for s in sets:
    for q in s['questions']:
        all_questions.append((s['id'], q['id'], q['type'], q['stem'], normalize(q['stem']), q['answer']))

total = len(all_questions)
print(f"总题数: {total}")
print(f"套数: {len(sets)}")

# 1. 完全相同题干（原始字符串）
raw_groups = defaultdict(list)
for item in all_questions:
    raw_groups[item[3]].append((item[0], item[1], item[5]))
exact_dups = {k: v for k, v in raw_groups.items() if len(v) > 1}
exact_dup_extra = sum(len(v) - 1 for v in exact_dups.values())
print(f"\n[1] 完全相同题干（原始字符）: {len(exact_dups)} 组, 多余 {exact_dup_extra} 条")

# 2. 标准化后相同（容错空白/标点差异）
norm_groups = defaultdict(list)
for item in all_questions:
    norm_groups[item[4]].append((item[0], item[1], item[3], item[5]))
norm_dups = {k: v for k, v in norm_groups.items() if len(v) > 1}
norm_dup_extra = sum(len(v) - 1 for v in norm_dups.values())
print(f"[2] 标准化后相同（容错空白/标点）: {len(norm_dups)} 组, 多余 {norm_dup_extra} 条")

# 3. 重复的分布：跨套 vs 套内
cross_set_groups = 0
within_set_groups = 0
for k, v in norm_dups.items():
    set_ids = set(x[0] for x in v)
    if len(set_ids) > 1:
        cross_set_groups += 1
    else:
        within_set_groups += 1
print(f"    - 跨套重复: {cross_set_groups} 组")
print(f"    - 套内重复: {within_set_groups} 组")

# 4. 跨套重复中，答案是否一致？
inconsistent = 0
samples_inconsistent = []
for k, v in norm_dups.items():
    set_ids = set(x[0] for x in v)
    if len(set_ids) > 1:
        answers = set(x[3] for x in v)
        if len(answers) > 1:
            inconsistent += 1
            if len(samples_inconsistent) < 5:
                samples_inconsistent.append((k, v))
print(f"    - 跨套重复中答案不一致: {inconsistent} 组")

# 5. 输出样本
print("\n[样本] 跨套重复（前 10 组，截断 60 字）:")
shown = 0
for k, v in norm_dups.items():
    set_ids = set(x[0] for x in v)
    if len(set_ids) > 1:
        locs = ', '.join(f"套{x[0]}#{x[1]}" for x in v)
        ans_set = set(x[3] for x in v)
        ans_mark = ' ⚠答案不一致' if len(ans_set) > 1 else ''
        stem_preview = v[0][2][:60] + ('...' if len(v[0][2]) > 60 else '')
        print(f"  [{stem_preview}]")
        print(f"    出现: {locs}{ans_mark}")
        shown += 1
        if shown >= 10:
            break

print("\n[样本] 套内重复（前 5 组）:")
shown = 0
for k, v in norm_dups.items():
    set_ids = set(x[0] for x in v)
    if len(set_ids) == 1:
        locs = ', '.join(f"套{x[0]}#{x[1]}" for x in v)
        stem_preview = v[0][2][:60] + ('...' if len(v[0][2]) > 60 else '')
        print(f"  [{stem_preview}]")
        print(f"    出现: {locs}")
        shown += 1
        if shown >= 5:
            break

# 6. 每套题的重复情况
print("\n[每套] 套内重复条目数:")
for s in sets:
    seen = {}
    dups = 0
    for q in s['questions']:
        n = normalize(q['stem'])
        if n in seen:
            dups += 1
        else:
            seen[n] = q['id']
    if dups > 0:
        print(f"  第{s['id']}套 ({s['title']}): 套内重复 {dups} 条 / 共 {len(s['questions'])} 条")

# 7. 答案不一致样本详情
if samples_inconsistent:
    print("\n[详情] 答案不一致的跨套重复:")
    for k, v in samples_inconsistent[:3]:
        print(f"  题干: {v[0][2][:80]}")
        for x in v:
            print(f"    套{x[0]}#{x[1]} 答案: {x[3]}")
