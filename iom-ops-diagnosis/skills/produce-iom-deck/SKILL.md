# S6: Produce IOM Deck - 交付生产技能

## 职责契约

| 属性 | 描述 |
|------|------|
| **职责** | 组装 VF 页面为可编辑 PPT + 审阅包 (review pack) |
| **输入契约** | 仅 VF 状态的页面（page_register 中状态=VF 的 PG-ID 清单） |
| **输出契约** | 可编辑 PPTX 文件、审阅包 (Markdown/PDF) |
| **守边界红线** | ❌ 不修改已确认内容<br>❌ 不生成结论或补充内容<br>❌ 不决定内容是否可用（仅按 VF 清单组装）<br>❌ 非 VF 页面绝对禁止纳入交付物 |

## 方法论内核

### 交付物组装规则 (Deck Assembly Rules)

#### PPT 结构规范

| 章节 | 页面类型 | 必选/可选 | 说明 |
|------|----------|-----------|------|
| 封面 | `cover` | 必选 | 项目名称、客户 Logo、日期、保密标识 |
| 目录 | `agenda` | 必选 | 章节导航、页码索引 |
| 高管摘要 | `executive_summary` | 必选 | 1-2 页，核心 Finding+Insight+Implication |
| 第一章：问题界定 | `governing_question`, `issue_tree`, `hypothesis_matrix` | 必选 | GQ、结构化分解、假设验证状态 |
| 第二章：现状分析 | `vsm_current`, `kpi_dashboard`, `pain_point_map` | 必选 | 价值流图、KPI 基线、痛点地图 |
| 第三章：方案选择 | `root_cause_tree`, `solution_option`, `impact_feasibility` | 必选 | 根因分析、方案对比、优先级矩阵 |
| 第四章：实施规划 | `roadmap_100day`, `business_case`, `org_design` | 必选 | 百日计划、商业案例、组织设计 |
| 附录 | `backup_analysis`, `data_tables` | 可选 | 支持性分析、详细数据表 |

#### 审阅包规范 (Review Pack Spec)

审阅包是交付给客户的完整留痕文档，包含：

1. **执行摘要** (1 页)
   - 项目目标达成情况
   - 核心建议摘要
   - 关键财务影响量化

2. **完整 Storyline** (3-5 页)
   - 版本历史与变更追溯
   - Finding → Insight → Implication 全链路
   - 证据链索引

3. **证据台账摘要** (2-3 页)
   - A/B 级证据清单
   - 关键数据来源说明
   - 未决假设与风险

4. **决策日志** (1-2 页)
   - 方案取舍记录
   - 用户 VF 批复原文引用
   - Gate 通过记录

5. **实施路线图** (1 页)
   - 百日计划里程碑
   - Owner 与依赖关系
   - 速赢项标识

### 治理强制检查

在生成交付物前，必须执行以下检查：

| 检查项 | 失败处理 |
|--------|----------|
| 所有纳入 PPT 的页面状态必须为 VF | 自动过滤非 VF 页面，并生成警告清单 |
| page_register 与 VF 页面清单一致 | 不一致时终止生成，要求先更新台账 |
| gate_log 中 G4 Gate 状态为 PASS | 未通过 G4 则禁止进入 S6 |
| deck 页码连续且与目录一致 | 自动生成目录并校验页码 |

## 脚本说明

### build_deck.py

**功能**：将 VF 页面组装为可编辑 PPTX 文件。

**输入**：
- `--vf-pages`：VF 页面清单文件路径（JSON 或文本格式，每行一个 PG-ID）
- `--template`：PPT 模板文件路径（可选，默认使用内置模板）
- `--output-file`：输出 PPTX 文件路径（默认 `outputs/decks/iom_diagnosis_deck.pptx`）

**输出**：
- `.pptx` 文件：可编辑的 PowerPoint 演示文稿

**治理强制**：
- 自动验证每个 PG-ID 在 page_register 中的状态是否为 VF
- 发现非 VF 页面时，自动跳过并记录警告
- 若 VF 页面数量为 0，终止生成并报错

### build_review_pack.py

**功能**：生成完整的审阅包文档。

**输入**：
- `--state-dir`：State 目录路径（包含台账文件）
- `--output-dir`：输出目录（默认 `outputs/review/`）

**输出**：
- `review_pack.md`：完整审阅包（Markdown 格式，可转换为 PDF）
- `evidence_summary.md`：证据台账摘要
- `decision_log.md`：决策日志

**治理强制**：
- 必须包含完整的证据链追溯
- 必须引用用户 VF 批复原文
- 必须包含 Gate 通过记录

## 参考文档

- `deck-assembly-rules.md`：PPT 组装规则详解
- `review-pack-spec.md`：审阅包规范与模板

## 模板文件

- `templates/deck_skeleton.pptx`：PPT 骨架模板（含封面、目录、章节分隔页）
- `templates/review_pack.md`：审阅包 Markdown 模板

## 使用示例

```bash
# 示例 1：构建 PPT 交付物
python scripts/build_deck.py \
  --vf-pages state/vf_pages_list.txt \
  --output-file outputs/decks/iom_diagnosis_v1.pptx

# 示例 2：生成审阅包
python scripts/build_review_pack.py \
  --state-dir state/ \
  --output-dir outputs/review/

# 示例 3：完整交付流程
python scripts/build_deck.py --vf-pages state/vf_pages_list.txt && \
python scripts/build_review_pack.py --state-dir state/
```

## 与其他 Skills 的协作

```
[用户 VF 授权所有章节页面]
    ↓ [page_register 全部状态=VF]
    ↓ [G4 Gate PASS]
S6 (produce-iom-deck) ← 本技能
    ↓ [PPTX + Review Pack]
[交付客户 / 项目归档]
    ↓
[G5 Gate 自动校验 → 项目闭环]
```

## G5 交付门检

S6 完成后，自动触发 G5 Gate 检查：

| 检查项 | 通过标准 |
|--------|----------|
| deck 仅含 VF 页 | 100% VF，无 draft/confirmed 混入 |
| review pack 含全链路留痕 | 证据链/Storyline/决策日志完整 |
| gate_log 归档 | G0-G5 所有 Gate 记录完整 |
| 台账一致性 | page_register / evidence_register / gate_log 相互印证 |

**G5 PASS 后，项目正式闭环。**
