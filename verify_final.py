import json
data = json.load(open(r'd:\桌面\习概题库\questions_dedup.json', encoding='utf-8'))
print('meta:', json.dumps(data['meta'], ensure_ascii=False))
for p in data['pool']:
    if '党在新时代的强军目标' in p['stem'] or '中国式现代化是中国共产党领导人民长期探索' in p['stem'] or '方向决定道路' in p['stem']:
        print(f"  {p['uid']}: type={p['type']} answer={p['answer']} conflict={p['conflict']}")
print('剩余冲突数:', sum(1 for p in data['pool'] if p['conflict']))
