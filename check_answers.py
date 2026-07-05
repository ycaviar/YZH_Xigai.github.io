import json
# 检查 questions.js (通过 questions_dedup.json) 中几条修正过的题目
with open(r'd:\桌面\习概题库\questions_dedup.json', encoding='utf-8') as f:
    data = json.load(f)

checks = [
    ('党在新时代的强军目标', 'ABC'),      # #4 BCD→ABC
    ('中国式现代化是中国共产党领导人民长期探索', '对'),  # #10 错→对
    ('针对国际金融危机后世界经济低迷', 'B'),  # #15 C→B
    ('党对军队的', 'B'),                  # #18 D→B
    ('十三个方面的成就', '对'),            # #22 错→对
    ('方向决定道路', '对'),               # #9 留空→对
    ('促进区域协调发展', 'ACD'),          # #26 ABC→ACD
    ('为民造福是', 'ABC'),               # #36 ACD→ABC
]

print("=== questions_dedup.json (题池) 答案校验 ===")
for kw, expected in checks:
    found = False
    for p in data['pool']:
        if kw in p['stem']:
            status = '✓' if p['answer'] == expected else '✗ 仍为 ' + p['answer']
            print(f"  {status}  {p['uid']} 期望={expected} 实际={p['answer']}  | {p['stem'][:40]}")
            found = True
            break
    if not found:
        print(f"  ?? 未找到: {kw}")

# 再检查 questions.js
with open(r'd:\桌面\习概题库\questions.js', encoding='utf-8') as f:
    js = f.read()
# questions.js = "window.QUESTIONS_DATA = {...};"
js_data = json.loads(js[len('window.QUESTIONS_DATA = '):-1])
print("\n=== questions.js (网页加载) 答案校验 ===")
for kw, expected in checks:
    for p in js_data['pool']:
        if kw in p['stem']:
            status = '✓' if p['answer'] == expected else '✗ 仍为 ' + p['answer']
            print(f"  {status}  {p['uid']} 期望={expected} 实际={p['answer']}  | {p['stem'][:40]}")
            break
