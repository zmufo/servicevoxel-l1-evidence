#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claim_gate.py —— 声明闸门（ServiceVoxel 自应用实例）

用途：约束本项目的产出方（含参与生成的 AI agent）在输出任何
      「已完成 / 已核验 / N 字节 / CRC OK」类断言之前，必须先跑本脚本。

设计原则（与体元主张同构）：
  - 断言与证据分离：声明先写进 claims 文件，判定由本脚本独立执行
  - fail-closed：脚本跑不通、文件不存在、哈希不符 → 一律 FALSE
  - 不自我豁免：本脚本自身也可被声明并检查

用法：
    python3 claim_gate.py                      # 检查 claims.json 全部条目
    python3 claim_gate.py --file 相对路径       # 只检查指定文件
    python3 claim_gate.py --strict             # 任一 FALSE 则以退出码 1 结束

零依赖，仅用标准库。
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)          # .../github
CLAIMS = os.path.join(HERE, "claims.json")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_one(entry, repo_root):
    rel = entry.get("path")
    want = entry.get("expect", {})
    got = {}
    reasons = []
    ok = True

    abs_path = os.path.join(repo_root, rel)
    if not os.path.exists(abs_path):
        return {
            "path": rel,
            "verdict": "FALSE",
            "reasons": ["文件不存在 —— 声明所指对象未被创建"],
            "got": {},
        }

    # 1) 存在性
    got["exists"] = True

    # 2) 字节数
    size = os.path.getsize(abs_path)
    got["bytes"] = size
    if "bytes" in want:
        if size != want["bytes"]:
            ok = False
            reasons.append(
                f"字节数不符：声明 {want['bytes']}，实测 {size}"
            )

    # 3) 最小字节（防止建了空文件充数）
    min_b = want.get("min_bytes", 1)
    if size < min_b:
        ok = False
        reasons.append(f"低于最小字节 {min_b}（实测 {size}）—— 疑似占位/空文件")

    # 4) SHA-256
    if "sha256" in want:
        actual = sha256_of(abs_path)
        got["sha256"] = actual
        if actual != want["sha256"]:
            ok = False
            reasons.append(
                f"哈希不符：声明 {want['sha256'][:16]}…，实测 {actual[:16]}…"
            )

    # 5) 内容标记（断言文件内含某字符串）
    for marker in want.get("contains", []):
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                body = f.read()
        except Exception as e:
            ok = False
            reasons.append(f"读取失败：{e}")
            body = ""
        if marker not in body:
            ok = False
            reasons.append(f"缺少必要内容标记：{marker!r}")

    return {
        "path": rel,
        "verdict": "TRUE" if ok else "FALSE",
        "reasons": reasons,
        "got": got,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="只检查指定相对路径")
    ap.add_argument("--strict", action="store_true",
                    help="任一 FALSE 时退出码为 1")
    args = ap.parse_args()

    if not os.path.exists(CLAIMS):
        print(f"[FALSE] claims.json 不存在：{CLAIMS}")
        print("        没有声明台账，就没有任何东西被声明过。")
        return 1

    with open(CLAIMS, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("claims", [])
    if args.file:
        entries = [e for e in entries if e.get("path") == args.file]
        if not entries:
            print(f"[FALSE] 台账中没有对 {args.file} 的声明。")
            print("        未被声明的文件，不得被描述为已完成。")
            return 1

    results = [check_one(e, REPO_ROOT) for e in entries]

    true_n = sum(1 for r in results if r["verdict"] == "TRUE")
    false_n = sum(1 for r in results if r["verdict"] == "FALSE")

    print("=" * 68)
    print(f"声明闸门 · 共 {len(results)} 条声明")
    print("=" * 68)
    for r in results:
        flag = "TRUE " if r["verdict"] == "TRUE" else "FALSE"
        print(f"[{flag}] {r['path']}")
        if r["got"].get("bytes") is not None:
            print(f"        实测 {r['got']['bytes']} 字节", end="")
            if r["got"].get("sha256"):
                print(f"  sha256:{r['got']['sha256'][:16]}…")
            else:
                print()
        for reason in r["reasons"]:
            print(f"        ↳ {reason}")
    print("-" * 68)
    print(f"TRUE {true_n} / FALSE {false_n}")
    if false_n:
        print("存在 FALSE —— 相应文件不得被描述为「已完成 / 已核验」。")
    print("=" * 68)

    if args.strict and false_n:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
