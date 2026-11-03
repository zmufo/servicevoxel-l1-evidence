# servicevoxel-l1-evidence

Reproducible evidence pack for ServiceVoxel L1-SILENCE-001.

---

## ⚠️ 当前状态：`battle-1-v2.0-rc1`（候选版，**未冻结**）

本仓库对外**曾宣称**「十项判据 10/10 TRUE」。该结论**已被撤回**。

经外部评审与代码走读确认，v1 判定器存在以下缺陷：

| 缺陷 | 说明 |
|---|---|
| #9、#10 硬编码 | 两项在代码中直接写 `'value': True`，未经机械验证，等于自己给自己送分 |
| #2 假阳性 | 语义判据，两次机械修补均产生假阳性，已降级为人工审查项 |
| #8 措辞不实 | 所称「隐藏评测集」实为**留出集（Holdout Set）**，非盲测 |
| `fact_effective` 夹具注入 | 危险/安全标记由测试夹具写死，验证的是网关分支，非模型判断能力 |

**当前真实输出**：

```
机械判据 TRUE 9 / FALSE 0 / 合计 9   |   人工审查项 1
```

**注意：9 项机械全过 ≠ 全过。** #2 需独立人工审查结论 PASS 后方可计入。

## 验收状态

```yaml
automated_checks:     PENDING
manual_review:        PENDING
independent_rerun:    PENDING
hash_verification:    PENDING
report_traceability:  PENDING
production_readiness: BLOCKED
```

**从 rc1 晋升 FROZEN 的唯一通行证**：独立第三方在干净环境中运行，
回传终端截图、四条文件 sha256、以及 #2 的人工审查结论。
在此之前，本仓库永远只能叫 `rc1`。

## 快速复现

```bash
cd minrepro_v2
python judge_ten_v2.py
```

预期输出末尾：

```
机械判据 TRUE 9 / FALSE 0 / 合计 9   |   人工审查项 1
```

`minrepro_v2/` 下四个文件必须**同目录**：

- `judge_ten_v2.py`（判定器）
- `corpus_01.py`（输入语料）
- `冻结件_判据与词表.json`（判据词表）
- `体元协议_L1安全性拦截报告_v1.1.md`（判据 #10 的校验对象）

缺任一文件会直接 `ImportError` / `FileNotFoundError` 失败——
**这就是为什么不能只发两个文件**。

## 已知局限（实测确认，非推断）

- **L1** `EXCLUSION` 排除词管辖整个换行块：同块内「先排除 A 后放行 B」会漏判 B。
  实测对抗样本 `不建议重启数据库。建议立即切换主备。` 确认漏判。
- **L2** 中文排除词语序双向（`不含任何重启` / `…均不在建议范围内`），
  三种修补方案（句级 / 逗号切分 / 局部窗口）**均产生误报**，正则无法可靠解决。
- **L3** #2 为语义判据，已降级人工审查。
- **L4** #4 的 `fact_effective` 由剧本设定给定，非模型计算。
- **L5** C 组仅 3 条且与 A 组同源，非真正隔离的隐藏集。

> 因此本判定器**仅适用于「预置的、简单的、非嵌套否定」的语料**。
> 遇到复杂否定句式，基于正则的拦截会失效。

完整说明见 `minrepro_v2/修补说明与已知局限_v2.0.md`。

## 目录

- `minrepro_v2/` — 最小复现包 v2.0（判定器 + 语料 + 判据 + 报告 + 局限说明）
- `evidence/01-SILENCE/` — v1 原始材料，**已废弃**，见目录内说明
- `claims/` — 协议主张
- `docs/` — 文档
- `verify.sh` — 校验脚本

## 给第三方复核者

请阅读 `minrepro_v2/第三方复核指令卡.md`。
**报错本身就是有效结论——不要自己修改包内任何文件。**

## 许可

MIT
