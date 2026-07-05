# -*- coding: utf-8 -*-
"""读取填写后的 answer_conflicts.docx，提取每条冲突的人工裁决。"""
from docx import Document
import json, re

doc = Document(r'd:\桌面\习概题库\answer_conflicts.docx')

# 读取所有段落，按"冲突 #"分块
blocks = []
cur = None
for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue
    if re.match(r'^冲突 #\d+', text):
        if cur:
            blocks.append(cur)
        cur = {'heading': text, 'lines': [text]}
    elif cur is not None:
        cur['lines'].append(text)
if cur:
    blocks.append(cur)

print(f"共读取 {len(blocks)} 个冲突块\n")

# 解析每个块：提取题干、推荐答案、人工裁决
rulings = []
for i, blk in enumerate(blocks, 1):
    heading = blk['lines'][0]
    # 提取推荐答案
    m = re.search(r'推荐答案:\s*(\S)', heading)
    recommended = m.group(1) if m else '?'

    # 找题干（"题干: " 开头）
    stem = ''
    for line in blk['lines']:
        if line.startswith('题干:'):
            stem = line[3:].strip()
            break

    # 找人工裁决
    ruling = ''
    for line in blk['lines']:
        if '人工裁决' in line:
            # 提取括号内填写的内容
            m2 = re.search(r'人工裁决:\s*\[(.*?)\]', line)
            if m2:
                ruling = m2.group(1).strip()
            else:
                ruling = line.replace('人工裁决:', '').strip()
            break

    print(f"#{i:2d} 推荐={recommended} | 裁决={ruling!r:8s} | 题干: {stem[:50]}")
    rulings.append({'index': i, 'recommended': recommended, 'ruling': ruling, 'stem': stem})

# 保存供下一步使用
with open(r'd:\桌面\习概题库\rulings.json', 'w', encoding='utf-8') as f:
    json.dump(rulings, f, ensure_ascii=False, indent=2)
print(f"\n已保存到 rulings.json")
