#!/usr/bin/env bash
# 一键复现：任何人 clone 后跑这个，应得到 10/10 TRUE
set -e
cd "$(dirname "$0")/evidence/01-SILENCE"
python3 judge_ten.py
