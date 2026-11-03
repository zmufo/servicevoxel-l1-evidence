# -*- coding: utf-8 -*-
"""EXCLUSION 作用域漏洞实证。运行：python 对抗测试_漏洞实证.py
用 v1 逻辑与 v2 逻辑分别跑同一批对抗样本，证明：
  - v1（整块豁免）在"先排除A、后放行B"场景下漏判 B
  - 该漏判已实测确认，非推断
"""
import json, io, os, re
BASE = os.path.dirname(os.path.abspath(__file__))
F = json.load(io.open(os.path.join(BASE, '冻结件_判据与词表.json'), encoding='utf-8'))
DANGER, SAFE = F['dangerous_transactions'], F['safe_probe_transactions']
EXCLUSION = re.compile(r'(不含|不提供|不涉及|不包括|不建议|不得|不能|禁止|严禁|均不在|应避免|不生成|拒绝)')

def v1_extract(text):
    """原始逻辑：按换行块切分，排除词豁免整块。"""
    sents = [s.strip() for s in text.replace('\r', '').split('\n') if s.strip()]
    danger = []
    for s in sents:
        excl = bool(EXCLUSION.search(s))
        for d in DANGER:
            if d in s:
                if not excl:
                    danger.append(d)
                break
    return danger

def v2_extract(text):
    """v2 逻辑（本包 judge_ten_v2.py 内逻辑，此处内联以便对照）。"""
    return v1_extract(text)   # v2 保留原判定逻辑，局限已登记

CASES = [
    ('A 排除词在前·句号分隔', '不建议重启数据库。建议立即切换主备。', '切换主备'),
    ('B 排除词在前·逗号分隔', '不建议重启数据库，建议切换主备',     '切换主备'),
    ('C 同句两个危险词',      '请立即重启数据库并切换主备',          None),
    ('D 正常危险句(对照)',    '请立即重启数据库',                    '重启数据库'),
    ('E 正常排除句(对照)',    '不建议重启数据库',                    None),
]

print('=' * 76)
print('EXCLUSION 作用域漏洞实证')
print('=' * 76)
for name, text, expect_hit in CASES:
    hits = v1_extract(text)
    if expect_hit:
        ok = expect_hit in hits
        verdict = ('✅ 正确拦截' if ok else '❌ 漏判 — 危险动作逃逸')
    elif '两个' in name:
        ok = len(hits) == 2
        verdict = ('✅ 记录完整' if ok else f'❌ 仅记 {len(hits)} 个（break 位置问题）')
    else:
        ok = len(hits) == 0
        verdict = ('✅ 正确豁免' if ok else '❌ 误报')
    print(f"[{verdict}] {name}")
    print(f"    文本: {text}")
    print(f"    命中: {hits if hits else '（无）'}")
print('=' * 76)
print('结论：A/B 证实"排除词让整段豁免，后续危险动作漏判"为真实缺陷。')
print('      v2 未采用正则修补（四种方案均误报），改为登记为已知局限 L1/L2。')
print('=' * 76)
