import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'questions_dedup.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转成 JS 文件，挂到 window.QUESTIONS_DATA
js = 'window.QUESTIONS_DATA = ' + json.dumps(data, ensure_ascii=False) + ';'
with open(os.path.join(BASE_DIR, 'questions.js'), 'w', encoding='utf-8') as f:
    f.write(js)

print(f'生成 questions.js, 大小 {len(js)/1024:.1f} KB')
print(f'唯一题数: {data["meta"]["total_unique"]}, 套数: {data["meta"]["total_sets"]}')
