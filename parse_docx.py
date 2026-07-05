# -*- coding: utf-8 -*-
"""
习概题库 docx 解析脚本
读取 9 个 docx 文件，输出 questions.json
每套题序号从 1 开始重新编号
兼容 4 种格式变体
"""
import os
import re
import json
from docx import Document

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCX_FILES = [
    '1-5.docx', '6-10.docx', '11-15.docx', '16-20.docx', '21-25.docx',
    '26-30.docx', '31-35.docx', '36-40.docx', '41-45.docx'
]

SETS_PER_FILE = 5


def is_ai_note(text):
    t = text.strip()
    if not t:
        return True
    if 'AI 生成' in t or 'AI生成' in t:
        return True
    if '图片内全部文字' in t:
        return True
    if t.startswith('|'):
        return True
    return False


def split_into_sections(paragraphs):
    """按空段落切分成 section（连续非空段为一个 section），过滤 AI 注释"""
    sections = []
    current = []
    for p in paragraphs:
        text = p.text
        if not text.strip():
            if current:
                sections.append(current)
                current = []
        elif is_ai_note(text):
            if current:
                sections.append(current)
                current = []
        else:
            current.append(text)
    if current:
        sections.append(current)
    return sections


def split_by_answer(text):
    """按"答案：X"切分题目（用于无题号段落）"""
    questions = []
    parts = re.split(r'(答案[:：][对错ABCDE]+)', text)
    current_q = ''
    for part in parts:
        if re.match(r'^答案[:：][对错ABCDE]+', part):
            current_q += part
            q_text = current_q.strip()
            if q_text:
                questions.append((q_text, None))
            current_q = ''
        else:
            current_q += part
    if current_q.strip():
        questions.append((current_q.strip(), None))
    return questions


def extract_questions_from_section(section_paragraphs):
    """从 section 段落中提取题目文本列表
    返回 [(q_text, qnum), ...]
    """
    text = '\n'.join(section_paragraphs)
    lines = text.split('\n')

    # 找题号位置
    question_starts = []
    for i, line in enumerate(lines):
        m = re.match(r'^\s*(\d{1,3})\s*[\.、．]\s*', line)
        if m:
            question_starts.append((i, int(m.group(1))))

    if question_starts:
        questions = []
        # 处理题号之前的内容（可能含无题号判断题）
        if question_starts[0][0] > 0:
            pre_text = '\n'.join(lines[:question_starts[0][0]]).strip()
            if pre_text:
                questions.extend(split_by_answer(pre_text))
        # 按题号切分
        for idx, (start_line, qnum) in enumerate(question_starts):
            end_line = question_starts[idx + 1][0] if idx + 1 < len(question_starts) else len(lines)
            q_text = '\n'.join(lines[start_line:end_line]).strip()
            if q_text:
                questions.append((q_text, qnum))
        return questions

    # 无题号，按答案切分
    return split_by_answer(text)


def parse_single_question(q_text, qnum=None):
    """解析单题"""
    if not q_text:
        return None

    answer_match = re.search(r'答案[:：]\s*([对错ABCDE]+)', q_text)
    if not answer_match:
        return None
    answer = answer_match.group(1).strip()
    q_text_no_answer = q_text[:answer_match.start()].strip()
    q_text_no_answer = re.sub(r'^\s*\d{1,3}\s*[\.、．]\s*', '', q_text_no_answer).strip()

    # 判断题：无 A-E 选项
    if not re.search(r'(?<![A-Za-z])[A-E]\s*\.', q_text_no_answer):
        stem = re.sub(r'\s+', ' ', q_text_no_answer).strip()
        return {
            'type': 'judge',
            'stem': stem,
            'options': [],
            'answer': answer,
            'qnum': qnum
        }

    # 选择题
    a_match = re.search(r'(?<![A-Za-z])A\s*\.', q_text_no_answer)
    if not a_match:
        return None
    stem = q_text_no_answer[:a_match.start()].strip()
    options_text = q_text_no_answer[a_match.start():]

    option_pattern = r'([A-E])\s*\.\s*(.*?)(?=\s*[A-E]\s*\.|$)'
    options = []
    for m in re.finditer(option_pattern, options_text, re.DOTALL):
        key = m.group(1)
        opt_text = m.group(2).strip()
        # 去尾部顿号/逗号/句号
        opt_text = re.sub(r'[、，,。．\.]\s*$', '', opt_text).strip()
        opt_text = re.sub(r'\s+', ' ', opt_text)
        if opt_text:
            options.append({'key': key, 'text': opt_text})

    if not options:
        return None

    qtype = 'single' if len(answer) == 1 else 'multi'
    stem = re.sub(r'\s+', ' ', stem).strip()

    return {
        'type': qtype,
        'stem': stem,
        'options': options,
        'answer': answer,
        'qnum': qnum
    }


def group_questions_into_sets(questions_with_section):
    """把题目按 section 边界 + 题型顺序合并为套
    规则：
    - 判断题 qnum=1：开始新套
    - 判断题 qnum=None 且当前套空：开始新套
    - 判断题 qnum=None 且上一题非判断题：开始新套
    - single/multi：若 section 变化且当前套已有该题型，开始新套；否则加入当前套
    """
    sets = []
    current_set = []
    current_section = None

    for q, sec_id in questions_with_section:
        section_changed = (sec_id != current_section)
        current_section = sec_id

        start_new = False
        if q['type'] == 'judge':
            qnum = q.get('qnum')
            if qnum == 1:
                start_new = True
            elif qnum is None:
                if not current_set:
                    start_new = True
                elif current_set[-1]['type'] != 'judge':
                    start_new = True
        else:
            # single / multi
            if section_changed and current_set:
                has_same_type = any(qq['type'] == q['type'] for qq in current_set)
                if has_same_type:
                    start_new = True

        if start_new and current_set:
            sets.append(current_set)
            current_set = []

        current_set.append(q)

    if current_set:
        sets.append(current_set)
    return sets


def main():
    all_sets = []
    set_id = 0
    stats = {'total': 0, 'judge': 0, 'single': 0, 'multi': 0, 'failed': 0}

    for fname in DOCX_FILES:
        fpath = os.path.join(BASE_DIR, fname)
        if not os.path.exists(fpath):
            print(f'[WARN] 文件不存在: {fname}')
            continue
        doc = Document(fpath)

        # 切分 sections
        sections = split_into_sections(doc.paragraphs)

        # 提取所有题目（带 section_id）
        questions_with_section = []
        for sec_id, section in enumerate(sections):
            q_texts = extract_questions_from_section(section)
            for q_text, qnum in q_texts:
                parsed = parse_single_question(q_text, qnum)
                if parsed is None:
                    stats['failed'] += 1
                    print(f'  [FAIL] {fname} sec{sec_id} 解析失败: {q_text[:80]}')
                    continue
                questions_with_section.append((parsed, sec_id))

        # 合并为套
        sets_of_questions = group_questions_into_sets(questions_with_section)

        print(f'\n=== {fname}: section{len(sections)} → 题{len(questions_with_section)} → 套{len(sets_of_questions)} ===')

        if len(sets_of_questions) != SETS_PER_FILE:
            print(f'  [WARN] 套数 {len(sets_of_questions)} != {SETS_PER_FILE}')

        for qs in sets_of_questions:
            set_id += 1
            for j, q in enumerate(qs):
                q['id'] = j + 1
                q.pop('qnum', None)
                stats['total'] += 1
                stats[q['type']] += 1

            all_sets.append({
                'id': set_id,
                'title': f'第{set_id}套',
                'source': fname,
                'questions': qs
            })
            type_count = {'judge': 0, 'single': 0, 'multi': 0}
            for q in qs:
                type_count[q['type']] += 1
            print(f'  套{set_id}: 共 {len(qs)} 题 '
                  f'(判断{type_count["judge"]} / 单选{type_count["single"]} / 多选{type_count["multi"]})')

    output = {
        'meta': {
            'total_sets': len(all_sets),
            'total_questions': stats['total'],
            'judge': stats['judge'],
            'single': stats['single'],
            'multi': stats['multi'],
            'failed': stats['failed']
        },
        'sets': all_sets
    }

    out_path = os.path.join(BASE_DIR, 'questions.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'\n=== 完成 ===')
    print(f'总套数: {len(all_sets)}')
    print(f'总题数: {stats["total"]}')
    print(f'判断题: {stats["judge"]}')
    print(f'单选题: {stats["single"]}')
    print(f'多选题: {stats["multi"]}')
    print(f'解析失败: {stats["failed"]}')
    print(f'输出: {out_path}')


if __name__ == '__main__':
    main()
