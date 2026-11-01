# 接入方案：在不可逆副作用之前加一道事实闸门

**本仓库：** `zmufo/servicevoxel-l1-evidence`
**目标上游：** `deepseek-ai/dsh-superagent-prototype`
**状态：** 仅为提案。**未集成，未在原型上运行过。**

> **本文是英文版 `integration-proposal.md` 的翻译件。两者若有分歧，以英文版为准。**
> 文件名与冻结件逐字节对应，不改名，以免破坏可复核性。

---

## 1. 摘要

我们不提议新标准，也不提议替换你们架构里的任何东西。

我们只提议**一个很窄的插入点**：在 Worker 的结论被当作对外事实、或触发不可逆副作用之前，断言这个结论的证据是否（a）存在、（b）与被测主体匹配、（c）自身自洽、（d）来源处于已知状态。

任一项不通过 → 结论标记为 `UNCONFIRMED`，**不允许继续**。失败即关闭（fail closed）。

我们附带四个测试用例，约 30 分钟可跑完，仓库里已有零依赖复现脚本。

---

## 2. 我们明确**不**提议什么

这部分我们最希望被正确理解。

| 层 | 回答什么问题 | 归属 |
|---|---|---|
| Authorization / Mandate | *谁可以让谁干什么？*（权限边界） | 你们已有设计 |
| Watchdog | *有没有进展？方向跑没跑偏？*（过程） | 你们已有设计 |
| **ServiceVoxel（本提案）** | *这个结论凭什么成为事实？*（证据资格） | **本提案** |

三者是**串联关系，不是竞争关系**。我们这一层在授权**之前**：先问"算不算事实"，再问"允不允许做"。

**我们不提议：**
- 替换 Router、Worker 或 Watchdog
- 在热路径上加模型调用（闸门是确定性的，不需要 LLM）
- 对你们内部类型强制 schema
- 改变 Worker 会话的隔离方式

---

## 3. 闸门插在哪里

### 3.1 公开材料中**可以**确认的

根据已发布文章与仓库 README：

- Router：常驻，负责分派，不执行。
- Worker：隔离上下文，挂载完整工具，把状态与结果汇报给 Router。
- Watchdog：独立会话，定时消息驱动的外部控制回路；判断 Worker 是否取得实质进展、方向是否偏离。
- 原型是研究代码；**文章讨论的部分设计属于未来方向，本原型未实现。**

### 3.2 证据状态——读 §3.3 前请先读这段

**我们尚未阅读实现源码。** 在我们的环境中，`raw.githubusercontent.com`、GitHub `contents` API、`blob` 页面均无法获取。以下全部是**二手材料**：多篇第三方技术拆解文章的交叉印证，不是源码。

**对一次"修正"的再修正（2026-11-02）**：我们曾在某一版中写"Effects queue **并未出现**在原型自身的材料中"。**这个说法过头了，我们予以撤回。** 多篇独立转述都描述了持久化的 **Effects** 队列（事务内 enqueue、commit 后执行、同一 kind/key 只有一行、指数退避、抛 `Later` 延迟）。该组件是真实存在的。我们错的是**锚点**：真正的对外投递点是另一个组件——**Outbox**（`src/app/outbox.ts`），其 `send()` 被描述为在一个事务里同时落消息回执与排队 reply 效果，使"发出去"与"记下来"原子。

| 组件 | 转述中的职责 |
|---|---|
| **Effects** | 通用持久化副作用队列（assessment / launch / delivery / relay / notice / reply） |
| **Outbox** | 出站消息回执与投递效果；原子、按 ticket+会话保序、退避重试 |

改述后的锚点：

> **Engine 接受 Worker 报告之后、`Outbox.send()` 入队之前** —— 即 SQLite 事务提交之前

二手来源给出的文件：`src/core/engine.ts`、`src/app/runtime.ts`、`src/app/outbox.ts`、`src/app/replies.ts`、`docs/002-authorization.md`、`docs/003-execution.md`。引用的固定 commit：`6337fc823ce20251c8de8085948165c81aaa701e`。

**在断言为事实之前，这些仍必须回到源码核对。**

#### 3.2.1 收窄：原型已有的区分比我们最初暗示的更多

为避免对立稻草人，我们明确承认原型**已经**具备：

- `Report` 状态机：progress / waiting / ready / blocked / failed / dropped；
- 待审阶段——带 PR 的工单报告 ready 后通常进入待审，PR 的关闭或合并才继续推动工单状态；
- 严格的自动合并约束（仅限本 Ticket 开的 PR、审批覆盖 head、改动少于 200 行、须用另一账号的 CLI 执行）。

所以我们**不是**在说"原型把 ready 当成已交付"。它没有。

我们的问题更窄：

> 当 Worker 的报告中含有一条**自然语言事实断言**——"tests passed""已验证""可以合并"——而该报告进入系统时，**这条断言的证据在哪里被检查？**

并且，原型自身的转述已经承认了底层原则：

> 一个模型回合结束，只能说明这轮生成结束，不能据此认定代码已经交付；已经发生在外部的事还得核实。

——这正是 Candidate / Fact 之分。

#### 3.2.2 一处有用的精细化

`Channel` 被描述为有类型划分——`acknowledgement`、`answer`、`result`、`attention`——各有允许规则（`src/app/outbox.ts`、`src/app/replies.ts`）。

因此事实闸门**不必阻塞全部出站流量**。它可以只作用于**承载断言的信道**（`result`、`answer`），而完全不动 `acknowledgement`。这样不会妨碍正常工作流。

### 3.3 提案本身，表述为一个可证伪的命题

不论具体机制如何，我们的主张是结构性的：

> **在 Worker 产出结果之后、该结果成为对外事实或不可逆副作用之前，存在这样一个点位。证据断言就属于这个点位。**

如果这样的唯一点位不存在，维护者比我们清楚，我们希望被纠正。

```
Worker → 结果/Candidate → [ 事实闸门 ] → 授权 → 副作用
                                │
                                └─ 失败 → 标记 UNCONFIRMED，不继续
```

---

## 4. 为什么 Watchdog 在这里不够

这不是批评 Watchdog，是范围区分。

Watchdog 问的是：*Worker 有没有进展？方向对不对？*

闸门问的是：*这个具体主张有没有证据支撑？*

一个 Worker 可以进展顺利、方向完全正确，却仍然产出一个证据过期、为空、或指向另一主体的结论。**进展**和**证据资格**是两种属性。

我们的 `L1-SILENCE-001` 证据包里有九条真实模型响应，恰好是这个形状：观测通道已失效（`probe_status=DEAD`），响应却断言"数据库实例不可用"，**全文无一处承认未知**。任务完成了，方向是对的，结论没有支撑。

---

## 5. 实例：编码 Agent 的证据缺口

选这个切入口，是因为 `dsh-superagent-prototype` 本身就是编码 Agent。

四个构造用例（见同级 `L1-CODING-EVIDENCE-GAP-001`）：

| # | 缺口 | 危险在哪 |
|---|---|---|
| E1 | 根本没有测试报告 | 声称已验证，背后什么都没有 |
| E2 | 测试报告属于**旧 commit** | 拿已经不是被测代码的绿灯冒充新验证 |
| E3 | 零用例，报"通过" | 空集合被当成成功 |
| E4 | CI 红灯，报"绿灯" | 被事实来源明确否定 |

三类防线的结果：

| 组别 | 正确拦截 | **误放行** | 过度拦截 |
|---|---|---|---|
| A 直通（无闸门） | 0/4 | **4** | 0 |
| B 浅层规则（报告存在 + 关键字） | 1/4 | **3** | 0 |
| C 证据闸门 | **4/4** | **0** | **0** |

**真正要紧的发现**：B 只挡住 E1。它漏掉 E2、E3、E4——恰恰是真正造成损失的三类，因为它们**看起来像**有效证据。

浅层检查不是没用，是校准错了失效模式：它抓"缺失"，抓不住"错配"。

---

## 6. 最小接口

示意性 TypeScript，对齐你们的技术栈。不是 PR，是草图。

```typescript
/** 指向某条证据的引用。永远不是证据本身。 */
interface EvidenceRef {
  /** 产物标识：文件路径、CI run id、命令摘要等 */
  locator: string;
  /** 这条证据是关于什么的。必须与 candidate 的主体一致。 */
  subject: string;
  /** 证据产生时，被测主体的摘要。 */
  subjectDigest: string;
  /** 来源状态：产出系统自身是否成功？ */
  sourceStatus: "PASS" | "FAIL" | "UNKNOWN";
  /** 非空性断言：例如用例数 > 0。 */
  volume: number;
  producedAt: string;
}

interface Candidate {
  claim: string;
  subject: string;
  subjectDigest: string;
  evidence: EvidenceRef[];
}

type Verdict =
  | { ok: true }
  | { ok: false; reason: string };

function factGate(c: Candidate): Verdict {
  if (c.evidence.length === 0) {
    return { ok: false, reason: "NO_EVIDENCE" };
  }
  for (const e of c.evidence) {
    if (e.subject !== c.subject || e.subjectDigest !== c.subjectDigest) {
      return { ok: false, reason: "SUBJECT_MISMATCH" };
    }
    if (e.volume <= 0) {
      return { ok: false, reason: "EMPTY_EVIDENCE" };
    }
    if (e.sourceStatus !== "PASS") {
      return { ok: false, reason: "SOURCE_NOT_PASS" };
    }
  }
  return { ok: true };
}
```

两条我们认为不可谈判的性质：

1. **失败即关闭。** 闸门无法判定时，答案是 `UNCONFIRMED`，永远不是 `OK`。
2. **比对摘要，而不是比对时间。**"最近"不等于"匹配"。报告只有在主体摘要一致时才有效。

---

## 7. 我们没有资格声称什么

这一节是本文最重要的部分。上面所有内容都以它为边界。

- **我们尚未与原型集成。** 这里的一切都没有在 `dsh-superagent-prototype` 上运行过。
- **我们尚未阅读实现源码。** §3.3 的插入点是结构性主张，不是已验证的代码位置。§3.2 中的机制名称（Effects、Outbox、`send()`）来自我们无法回到源码核对的二手转述；我们甚至不得不**对自己此前的"修正"再做一次修正**。所有这些都应视为暂定。
- **编码 Agent 用例没有调用任何模型 API。** 输入全为构造。它们证明的是**三类防线的能力差异**，**不是**"DeepSeek 的原型会犯这些错"。
- **`L1-SILENCE-001` 只用了单一模型**（`deepseek-chat`），3 个种子、9 条响应。它**不能**外推为"大模型都如何"。它只是关于一个模型、一类场景的证据。
- **没有声称任何错误率下降。** 我们没有在真实系统上的前后对比测量。

如果读者得出的结论是"DeepSeek 的 Agent 有安全漏洞"，那是误读了本文。

---

## 8. 约 30 分钟如何验证

```bash
git clone https://github.com/zmufo/servicevoxel-l1-evidence.git
cd servicevoxel-l1-evidence
bash verify.sh          # 注意是 `bash verify.sh`，不是 `./verify.sh`
```

`verify.sh` 只需要 `python3` 及其标准库。它会重跑十项冻结判据，逐条打印 TRUE/FALSE。判据以 SHA-256 冻结，记录在 `evidence/01-SILENCE/pre_run_gate_v1.0.json` 中，**在判定之前**计算——因此判据不可能在事后被调整去适配结果。

当前输出：**10/10 TRUE**。

---

## 9. 我们希望得到回答的问题

1. 在"Worker 产出结果"与"结果成为对外事实或副作用"之间，是否存在唯一点位？如果不是唯一的，实际边界在哪？
2. Worker 目前的结果是否携带任何结构化溯源信息，还是仅有结果文本？
3. 你们更希望确定性的事前断言放在哪一侧——Worker 侧、Router 侧，还是副作用派发层？

我们在提问，不是在替你们决定。

---

*由 ServiceVoxel 工作组准备。欢迎纠正——尤其是关于 §3.2 的部分。*
