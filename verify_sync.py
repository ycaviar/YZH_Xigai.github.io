import json, re

def normalize(s):
    if not s: return ''
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[，。、,．.\?？!！:：;；""''\'\"\(\)（）【】\[\]《》<>\-—_·]', '', s)
    return s.lower()

with open(r'd:\桌面\习概题库\questions.json', encoding='utf-8') as f:
    orig = json.load(f)

checks = [
    ('党在新时代的强军目标', 'ABC'),
    ('中国式现代化是中国共产党领导人民长期探索', '对'),
    ('针对国际金融危机后世界经济低迷', 'B'),
    ('党对军队的', 'B'),
    ('十三个方面的成就', '对'),
    ('为民造福是', 'ABC'),
]

print("=== questions.json 原始文件校验（跨套检查）===")
for kw, expected in checks:
    occurrences = []
    for s in orig['sets']:
        for q in s['questions']:
            if kw in q['stem']:
                mark = '✓' if q['answer'] == expected else '✗ ' + q['answer']
                occurrences.append(f"套{s['id']}#{q['id']}={mark}")
    print(f"  {kw[:25]}... 期望={expected}")
    print(f"    {' '.join(occurrences)}")
