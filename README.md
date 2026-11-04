# L2 外部验证包 v1.0

本包是待验证材料，不是验证结论。

本包目的：向未参与修订的外部复核人提供材料索引、复核任务书、回执模板与未完成项声明。发布本包不代表 L2 已开始、已通过或基线已获批准。

## 当前状态

- package_status: PUBLISHED_MATERIALS_ONLY
- local_archive_L0: COMPLETE
- repo_publish_L0: PENDING_UNTIL_POST_UPLOAD_HASH_CHECK
- hash_discrepancy: REGISTERED_NOT_ADJUDICATED
- independent_review: PENDING
- approval: PENDING
- baseline_record_corrected: false
- layer_A: PENDING
- layer_B: NOT_COVERED

README 不裁定哈希差异谁对谁错，不代填、不覆盖任何一个值。

## 未完成项声明

1. 第 5 项原始运行 stdout 缺失，状态为 `MISSING_NOT_CREATED`。不得重跑生成新 stdout 冒充原始输出。见 `MANIFEST.status.tsv`。
2. 修订版声明哈希与实算哈希存在差异，状态为 `REGISTERED_NOT_ADJUDICATED`。本包只登记差异，不代填、不覆盖、不判谁对谁错。
3. independent_review / approval 均为 `PENDING`，`BASELINE_RECORD_NOT_CORRECTED` 不得由发布方自行勾选。
4. decision_thresholds: `NOT_DESIGNED`，design_basis: `null`。
5. FIRST_WORK_ORDER_TYPE_NOT_SELECTED、SAMPLE_SIZE_NOT_DEFINED、SCHEMA_AND_ONTOLOGY_NOT_VERSIONED 均未解除。
6. 隐私、数据治理与伦理门未通过，本包不得包含真实工单、居民数据、凭据或生产配置。

## 禁止事项

- 不得加入真实居民数据或真实工单。
- 不得加入空占位文件伪装为已存在材料。
- 不得补写阈值、结论或人工项。
- 不得把发布材料表述为"已验证""已通过""L2完成"。
- 不得重跑缺失 stdout 冒充原始输出。

## 包结构

- `01_对照材料/` A 块（第 5 项仅状态行）
- `02_哈希与桥接/` B 块映射与索引
- `03_任务书与回执/` 复核任务书、回执模板
- `MANIFEST.sha256` 仅记录复制进包的原文件在本机实算哈希（新增文件不混入）
- `MANIFEST.status.tsv` 缺失项与差异登记
- `.gitattributes` = `* -text`，禁止 Git 换行归一化

上传成功后必须重新 clone / 下载压缩包，按 `MANIFEST.sha256` 复算一次；上传成功不等于哈希仍一致。