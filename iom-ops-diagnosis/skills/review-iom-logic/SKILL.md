# S4: Review IOM Logic - 逻辑审核器技能

## 职责契约

| 属性 | 描述 |
|------|------|
| **职责** | 逻辑检查/修正/补证计划；证据分级审计 |
| **输入契约** | Storyline、证据台账 (evidence_register.md)、假设矩阵 |
| **输出契约** | 逻辑审核报告 (logic_audit_report.md)、补证计划 (evidence_plan.md) |
| **守边界红线** | ❌ 不创建新 Storyline<br>❌ 不替代用户决策<br>❌ 不直接产出正式页面<br>❌ 关键结论无 A/B 级证据必须标记 FAIL |

## 方法论内核

### 逻辑审核清单 (Logic Review Checklist)

基于 MBB 问题解决方法论与 IOM 特化要求，执行以下维度的审核：

#### 1. 证据链完整性 (Evidence Chain)

| 检查项 | 通过标准 | 失败处理 |
|--------|----------|----------|
| 每个假设是否有≥1 条证据支撑？ | 是 → 继续 | 否 → 生成补证计划 |
| 关键 Finding 是否有 A/B 级证据？ | 是 → 继续 | 否 → 标记为"待验证" |
| 证据来源是否多元化？ | ≥2 个独立来源 | 单源证据需降级处理 |
| 证据时效性是否在 6 个月内？ | 是 → 认可 | 否 → 标注"可能过时" |

#### 2. So-What 逻辑链 (Logical Flow)

| 检查项 | 通过标准 | 失败处理 |
|--------|----------|----------|
| Finding → Insight 是否有明确推导？ | 有因果链条 | 补充"因此..."连接 |
| Insight → Implication 是否指向行动？ | 有具体行动建议 | 追问"那又怎样？" |
| 是否存在逻辑跳跃？ | 每步可追溯 | 补充中间推理步骤 |
| 是否有替代解释被忽略？ | 已考虑并排除 | 补充替代假设分析 |

#### 3. IOM 特化检查 (IOM-Specific)

| 检查项 | 通过标准 | 失败处理 |
|--------|----------|----------|
| 所有 Finding 是否折算财务语言？ | OTIF/周转/人均产值/利润 | 补充财务影响量化 |
| 方案是否满足三柔性约束？ | 设备/人员/产线柔性 | 标注"柔性风险" |
| 是否端到端视角而非局部优化？ | Concept-to-Cash 全链路 | 补充上下游影响分析 |
| 是否符合 HMLV 特征？ | 多品种小批量适配 | 标注"大批量假设风险" |

#### 4. MECE 原则复核 (MECE Re-check)

| 检查项 | 通过标准 | 失败处理 |
|--------|----------|----------|
| 分类是否互斥？ | 无重叠 | 重新定义分类维度 |
| 分类是否穷尽？ | 无遗漏 | 补充缺失类别 |
| 层级是否清晰？ | 同一层级粒度一致 | 调整归类 |

### 证据分级标准

| 等级 | 定义 | 示例 | 可信度权重 |
|------|------|------|------------|
| **A** | 客户系统统计数据 | ERP 出库记录、MES 设备日志 | 1.0 |
| **B** | 多源交叉访谈 | ≥3 人独立陈述一致 | 0.8 |
| **C** | 单源或外部对标 | 单人访谈、行业报告 | 0.5 |
| **D** | 假设待补证 | 未验证的推测 | 0.2 |

**审核规则**：
- 关键结论（影响方案选择的 Finding）必须有≥1 条 A 级或≥2 条 B 级证据
- 次要结论可以有 C 级证据支撑，但需标注"待进一步验证"
- D 级证据不能作为结论依据，仅可作为假设列入补证计划

## 脚本说明

### logic_audit.py

**功能**：对 Storyline 和证据台账进行逻辑审核，生成审核报告与补证计划。

**输入**：
- `--storyline`：Storyline 文件路径（state/storyline.md）
- `--evidence-register`：证据台账文件路径（state/evidence_register.md）
- `--hypothesis-matrix`：可选，假设矩阵文件路径
- `--output-dir`：输出目录（默认 `outputs/review/`）

**输出**：
- `logic_audit_report.md`：详细审核报告（含问题清单、严重程度、修复建议）
- `evidence_plan.md`：补证计划（列出需补充的证据项、优先级、建议来源）

**治理强制**：
- 关键结论无 A/B 证据时，审核结果自动标记为 FAIL
- 发现逻辑跳跃时，必须给出具体修复建议
- 所有问题必须关联到具体的 Finding/Insight/Implication

## 参考文档

- `logic-review-checklist.md`：逻辑审核清单详解
- `evidence-grading.md`：证据分级标准与判定规则

## 模板文件

- `templates/logic_audit_report.md`：审核报告模板
- `templates/evidence_plan.md`：补证计划模板

## 使用示例

```bash
# 示例 1：完整审核流程
python scripts/logic_audit.py \
  --storyline state/storyline.md \
  --evidence-register state/evidence_register.md \
  --output-dir outputs/review/

# 示例 2：带假设矩阵的深度审核
python scripts/logic_audit.py \
  --storyline state/storyline.md \
  --evidence-register state/evidence_register.md \
  --hypothesis-matrix state/hypothesis_matrix.md \
  --output-dir outputs/review/
```

## 与其他 Skills 的协作

```
[Agent 推理核心完成取证与综合]
    ↓ [Storyline + 证据台账]
S4 (review-iom-logic) ← 本技能
    ↓ [审核报告 + 补证计划]
┌───────────────────────┐
│ 若审核 FAIL:          │
│   → 返回推理核心补证  │
│   → 或更新 Storyline  │
└───────────────────────┘
    ↓ [审核 PASS]
S5 (generate-iom-visuals)
```

## 审核状态机

```
draft_storyline 
    ↓ [提交审核]
under_review ──(FAIL)──> needs_evidence / needs_logic_fix
    │                        ↓
    │                   [补证/修正后重新提交]
    │                        ↓
    └──────(PASS)─────────→ audit_passed
                              ↓
                         confirmed (可进入 S5 渲染)
```
