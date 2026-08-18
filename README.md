# iom-ops-diagnosis Agent

**基于 MBB 问题解决方法论 × "端到端敏捷运营体系重构"的集成运营管理（IOM）咨询诊断 Agent**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 目录

- [什么是 iom-ops-diagnosis Agent？](#什么是-iom-ops-diagnosis-agent)
- [核心能力](#核心能力)
- [适用场景](#适用场景)
- [快速开始](#快速开始)
- [六大技能模块](#六大技能模块)
- [治理机制](#治理机制)
- [项目结构](#项目结构)
- [使用示例](#使用示例)
- [输出产物](#输出产物)
- [贡献与扩展](#贡献与扩展)

---

## 什么是 iom-ops-diagnosis Agent？

**iom-ops-diagnosis Agent** 是一个面向制造企业的智能咨询诊断系统，融合了：

1. **MBB 问题解决方法论**（麦肯锡/波士顿/贝恩的结构化问题解决框架）
2. **IOM 集成运营管理方法论**（端到端敏捷运营体系重构）
3. **工程化治理机制**（阶段门控制、VF 授权、全链路台账留痕）

### 核心价值

| 角色 | 价值主张 |
|------|----------|
| **CEO/高管** | 以 CEO 视角审视端到端运营，所有发现折算为财务语言（OTIF、库存周转、人均产值、利润） |
| **运营总监** | 识别 HMLV（多品种小批量）环境下的系统性瓶颈，避免局部优化 |
| **项目经理** | 受治理的咨询流程，确保每一步都有证据支撑、可追溯、可审计 |
| **变革推动者** | 百日速赢计划 + 长期能力建设双轨并行，降低变革风险 |

---

## 核心能力

```
┌─ 04 决策与交付 ─────────────────────────────────────────┐
│  决策内容 (诊断/对标/方案/Roadmap) →【用户决策权·唯一 VF】→ 生产交付 (仅收 VF 页) │
├─ 03 项目治理 ─────────────────────────────────────────┤
│  Engagement Controller(Storyline/工作流/依赖) ⇄ 项目中枢 ⇄ 阶段门与台账   │
├─ 02 问题求解核心 ──────────────────────────────────────┤
│  动态推理核心 (问题→假设→证据→综合→选择) → 方法选择器 → 逻辑审核器          │
├─ 01 证据与知识底座 ────────────────────────────────────┤
│  现状与问题 (痛点/柔性约束) │ 内部知识库 (IOM 方法论/案例) │ 外部证据 (对标)     │
└──────────────────────────────────────────────────────┘
```

### IOM 动态推理闭环（8 步）

| 步骤 | IOM 特化内容 | 主输出 |
|------|----------|--------|
| 01 决策问题 | "如何在 HMLV 高波动下重构端到端敏捷运营，使 OTIF、库存周转、人均产值同步突破？" | Governing Question + 项目章程 |
| 02 初始假设 | 调用 H1–H8 根因假设库（如"插单无围栏击穿计划"） | 假设矩阵 |
| 03 结构化分解 | 四模块 MECE：计划大脑／柔性制造／供应链延迟／组织绩效 | Issue Tree |
| 04 证据检验 | 按 IOM 数据清单取证（齐套率、换线时间、OEE、SKU 盈利 - 周转矩阵…） | 证据台账 |
| 05 方法选择 | 按逻辑瓶颈调用最小方法栈（VSM、ABC-XYZ、SMED、延迟制造…） | 分析计划 |
| 06 行动设计 | 百日计划：灯塔线试点→速赢验证→推广固化；Owner/依赖/节奏 | Roadmap |
| 07 方案选择 | 影响/可行性矩阵 + 三柔性约束筛选；取舍与边界 | 决策记录 |
| 08 综合判断 | Finding→Insight→Implication，全部折算财务语言 | 章节结论页 |

---

## 适用场景

### 典型客户画像

- **行业**：离散制造（电子装配、机械加工、汽车零部件等）
- **生产模式**：多品种小批量（HMLV）、插单频繁、小单多
- **痛点特征**：
  - P1: 插单混乱，计划变更率 >40%
  - P2: 呆滞与缺料并存，库存周转天数 >60 天
  - P3: 齐套率低 (<80%)，车间待料严重
  - P4: 换线时间长，占有效工时 >25%
  - P5: 人海战术，人均产值低于行业基准
  - P6: 交付投诉多，OTIF <90%

### 量化目标承诺（G0 准入条件）

- ✅ 齐套率 ≥95%
- ✅ 库存周转 +30%
- ✅ OTIF（准时足额交付）≥98%
- ✅ 客户投诉率 -80%
- ✅ 人均产值 +20%

---

## 快速开始

### 前置要求

- Python 3.8+
- Git（用于版本管理）

### 安装与初始化

```bash
# 1. 克隆或进入项目目录
cd iom-ops-diagnosis

# 2. 初始化项目工作空间
python skills/manage-iom-engagement/scripts/init_workspace.py --project-name my-iom-project

# 3. 查看生成的台账文件
ls state/
# 输出：evidence_register.md  gate_log.md  page_register.md  project_state.json  storyline.md
```

### 运行阶段门检查

```bash
# G0 门检：界定阶段（检查 Governing Question 和量化目标）
python skills/manage-iom-engagement/scripts/gate_check.py --gate G0

# G1 门检：分解阶段（检查 Issue Tree MECE 完整性）
python skills/manage-iom-engagement/scripts/gate_check.py --gate G1
```

---

## 六大技能模块

| Skill | 模块名 | 职责 | 关键脚本 |
|-------|--------|------|----------|
| **S1** | `manage-iom-engagement` | 项目编排与状态治理 | `init_workspace.py`, `gate_check.py`, `update_register.py` |
| **S2** | `frame-iom-problem` | 问题界定与结构化分解 | `painpoint_mapper.py`, `mece_checker.py` |
| **S3** | `select-iom-methods` | 方法选择器（最小方法栈） | `method_selector.py` |
| **S4** | `review-iom-logic` | 逻辑审核器 | `logic_audit.py` |
| **S5** | `generate-iom-visuals` | 单页可视化渲染 | `render_page.py` |
| **S6** | `produce-iom-deck` | 交付生产（PPT+ 审阅包） | `build_review_pack.py` |

### S1: Manage IOM Engagement（项目编排）

**职责**：维护项目状态、执行阶段门检查、更新台账

```bash
# 初始化新项目
python skills/manage-iom-engagement/scripts/init_workspace.py \
  --project-name "ACME 柔性转型项目" \
  --owner "张三" \
  --start-date "2025-01-15"

# 更新台账状态
python skills/manage-iom-engagement/scripts/update_register.py \
  --type page \
  --action confirm \
  --id PG-001

# 执行 G0 门检
python skills/manage-iom-engagement/scripts/gate_check.py --gate G0
```

### S2: Frame IOM Problem（问题界定）

**职责**：将客户痛点映射到假设库，生成 MECE Issue Tree

```bash
# 痛点→假设映射
python skills/frame-iom-problem/scripts/painpoint_mapper.py \
  --painpoints P1,P2,P4 \
  --output outputs/hypothesis_matrix.md

# MECE 检查
python skills/frame-iom-problem/scripts/mece_checker.py \
  --issue-tree outputs/issue_tree.md \
  --framework iom-4module
```

### S3: Select IOM Methods（方法选择）

**职责**：根据瓶颈标签调用最小方法栈（≤5 个方法）

```bash
# 方法选择
python skills/select-iom-methods/scripts/method_selector.py \
  --bottlenecks "呆滞与缺料并存，换线损失大，齐套率低" \
  --output outputs/analysis_plan.md
```

**内置方法栈映射表**（部分）：

| 瓶颈标签 | 最小方法栈 | 财务锚定 |
|----------|-----------|----------|
| 插单混乱/计划被击穿 | 订单分级 + 时间围栏、S&OP/S&OE | 减少紧急采购溢价 |
| 呆滞与缺料并存 | ABC-XYZ 矩阵、VMI/寄售设计 | 库存资金释放 |
| 齐套率低/车间待料 | 齐套控制塔、齐套前移分析 | OEE 与人工浪费下降 |
| 换线损失大 | SMED、内外作业分离 | 小单边际成本下降 |
| 人海战术/人均产值低 | Cell/U 型线、线平衡&Takt、水蜘蛛 | 人均产值 +20% |

### S4: Review IOM Logic（逻辑审核）

**职责**：证据链审计、逻辑链检查、补证计划

```bash
# 逻辑审核
python skills/review-iom-logic/scripts/logic_audit.py \
  --storyline state/storyline.md \
  --evidence-tape state/evidence_register.md \
  --output outputs/review/logic_audit_report.md
```

**审核维度**：
1. 证据链完整性（A/B/C/D 分级）
2. 逻辑链严密性（Finding→Insight→Implication）
3. IOM 特化检查（三柔性约束、财务锚定）
4. MECE 原则遵守

### S5: Generate IOM Visuals（可视化渲染）

**职责**：将已确认（confirmed/VF）内容渲染为 MBB 风格页面

```bash
# 渲染单页
python skills/generate-iom-visuals/scripts/render_page.py \
  --page-id PG-001 \
  --template vsm_page \
  --status confirmed

# 渲染高管汇报页
python skills/generate-iom-visuals/scripts/render_page.py \
  --page-id PG-EXEC \
  --template exec_summary_page \
  --status VF
```

**支持模板**：
- `vsm_page`：价值流图
- `matrix_page`：影响/可行性矩阵
- `roadmap_page`：百日转型路线图
- `kpi_page`：KPI 追踪仪表板
- `exec_summary_page`：高管汇报摘要（金字塔三段式）

### S6: Produce IOM Deck（交付生产）

**职责**：组装 VF 页面为可编辑 PPT + 审阅包

```bash
# 生成审阅包
python skills/produce-iom-deck/scripts/build_review_pack.py \
  --state-dir state/ \
  --outputs-dir outputs/ \
  --project-name "ACME 柔性转型项目"
```

**输出物**：
- `review_pack.md`：完整审阅包
- `evidence_summary.md`：证据链摘要
- `decision_log.md`：决策日志（含用户 VF 批复原文）

---

## 治理机制

### 阶段门 G0–G5

| Gate | 名称 | 准入条件（PASS 判定） | 授权者 |
|------|------|---------------------|--------|
| G0 | 界定 | Governing Question + 章程量化目标获用户确认 | 用户 |
| G1 | 分解 | Issue Tree 通过 MECE 检查；假设矩阵覆盖四模块 | 用户 |
| G2 | 证据 | 证据台账无 D 级关键证据；每个假设≥1 条 A/B 级证据 | S4 审核 + 用户 |
| G3 | 综合 | 逻辑审核 PASS；Finding→Insight→Implication 链完整 | 用户 |
| G4 | 页面 | 章节 Review 通过；用户显式批复 VF | **用户唯一** |
| G5 | 交付 | deck 仅含 VF 页；review pack 含全链路留痕 | S6 自动校验 |

### 页面状态机

```
draft ──[用户确认]──> confirmed ──[用户 VF 批复]──> VF
   ↑                       ↓                           │
   └──────────────[禁止回退]───────────────────────────┘
```

- **VF（Verified & Frozen）**：仅用户可授权，VF 后不可被任何 Skill 修改
- **治理强制**：S6 生产时自动过滤非 VF 页面

### 证据分级标准

| 等级 | 来源 | 可信度 | 示例 |
|------|------|--------|------|
| A | 客户系统统计数据 | ★★★★★ | ERP 齐套率报表、MES 换线时间日志 |
| B | 多源交叉访谈 | ★★★★☆ | 生产 + 计划 + 财务三方一致陈述 |
| C | 单源或外部对标 | ★★★☆☆ | 单一部门访谈、行业基准数据 |
| D | 假设待补证 | ★★☆☆☆ | 未验证的推测、需进一步取证 |

---

## 项目结构

```
iom-ops-diagnosis/
├── .codex-plugin/
│   └── plugin.json              # 插件元数据、skill 清单、治理声明
├── README.md                    # 本文件
├── GOVERNANCE.md                # 治理宪章全文
├── skills/                      # 六大技能模块
│   ├── manage-iom-engagement/   # S1: 项目编排与状态治理
│   │   ├── SKILL.md             # 技能职责契约
│   │   ├── scripts/             # 可执行脚本
│   │   ├── references/          # 参考文档
│   │   └── templates/           # 输出模板
│   ├── frame-iom-problem/       # S2: 问题界定与结构化分解
│   ├── select-iom-methods/      # S3: 方法选择器
│   ├── review-iom-logic/        # S4: 逻辑审核器
│   ├── generate-iom-visuals/    # S5: 单页可视化
│   └── produce-iom-deck/        # S6: 交付生产
├── knowledge/                   # 知识底座
│   ├── context/                 # 客户上下文
│   ├── internal/                # 内部方法论
│   └── external/                # 外部对标数据
├── state/                       # 运行时台账（唯一事实源）
│   ├── project_state.json       # 项目状态 JSON
│   ├── storyline.md             # 动态 Storyline
│   ├── evidence_register.md     # 证据台账
│   ├── page_register.md         # 页面台账
│   └── gate_log.md              # 阶段门日志
└── outputs/                     # 输出产物
    ├── pages/                   # 单页视觉稿
    ├── decks/                   # PPT 交付物
    └── review/                  # 审阅包
```

---

## 使用示例

### 完整工作流演示

```bash
# Step 1: 初始化项目
python skills/manage-iom-engagement/scripts/init_workspace.py \
  --project-name "ACME 柔性转型项目"

# Step 2: 痛点映射（假设用户输入了 P1,P2,P4）
python skills/frame-iom-problem/scripts/painpoint_mapper.py \
  --painpoints P1,P2,P4 \
  --output outputs/hypothesis_matrix.md

# Step 3: 生成 Issue Tree 并检查 MECE
# （手动创建 issue_tree.md 后）
python skills/frame-iom-problem/scripts/mece_checker.py \
  --issue-tree outputs/issue_tree.md

# Step 4: 选择分析方法
python skills/select-iom-methods/scripts/method_selector.py \
  --bottlenecks "插单混乱，呆滞与缺料并存，换线损失大" \
  --output outputs/analysis_plan.md

# Step 5: 逻辑审核（模拟证据已收集）
python skills/review-iom-logic/scripts/logic_audit.py \
  --storyline state/storyline.md \
  --evidence-tape state/evidence_register.md

# Step 6: 渲染页面（需先更新台账状态为 confirmed）
python skills/manage-iom-engagement/scripts/update_register.py \
  --type page --action confirm --id PG-001

python skills/generate-iom-visuals/scripts/render_page.py \
  --page-id PG-001 --template vsm_page

# Step 7: 用户 VF 批复（模拟）
python skills/manage-iom-engagement/scripts/update_register.py \
  --type page --action vf --id PG-001 \
  --vf-comment "同意此页内容，纳入最终交付"

# Step 8: 生成审阅包
python skills/produce-iom-deck/scripts/build_review_pack.py \
  --state-dir state/ --outputs-dir outputs/

# Step 9: 执行 G5 门检
python skills/manage-iom-engagement/scripts/gate_check.py --gate G5
```

### 输出产物示例

**审阅包目录** (`outputs/review/`)：
```
review_pack.md              # 完整审阅包（含执行摘要、Storyline、所有章节）
evidence_summary.md         # 证据链摘要（EV-ID→假设→结论追溯）
decision_log.md             # 决策日志（含用户 VF 批复原文引用）
```

**审阅包内容节选** (`review_pack.md`)：
```markdown
# ACME 柔性转型项目 - 审阅包

## 执行摘要

### 重塑大脑（计划协同）
- 发现：插单无时间围栏，计划变更率 47%
- 洞察：物理柔性有余，计划协同瘫痪
- 行动：建立订单分级 + 时间围栏机制

### 激活四肢（柔性制造）
- 发现：换线时间占有效工时 28%
- 洞察：内外部作业未分离，调机经验未标准化
- 行动：SMED 改造，目标换线时间 -80%

### 打通神经（组织绩效）
- 发现：部门墙导致救火文化
- 洞察：KPI 冲突（销售要灵活 vs 生产要稳定）
- 行动：设立价值流经理，共担 OTIF 与周转 KPI

## 量化承诺
| KPI | 基线 | 目标 | 改善幅度 |
|-----|------|------|----------|
| 齐套率 | 78% | ≥95% | +17pp |
| 库存周转 | 45 天 | 32 天 | +30% |
| OTIF | 82% | ≥98% | +16pp |
| 客户投诉率 | 15 次/月 | 3 次/月 | -80% |
| 人均产值 | 85 万/年 | 102 万/年 | +20% |

## 证据链追溯
- EV-01 (A): ERP 齐套率报表 (2024-Q4) → 支撑 H3
- EV-03 (B): 计划 + 生产 + 销售三方访谈 → 支撑 H1
- EV-07 (A): MES 换线时间日志 → 支撑 H4

## 用户 VF 批复
- PG-001 (VSM 页): "同意此页内容，纳入最终交付" — CEO 张三，2025-01-20
- PG-002 (矩阵页): "方案优先级合理，批准执行" — COO 李四，2025-01-21
```

---

## 核心原则

| 类别 | 原则 | 说明 |
|------|------|------|
| **继承** | 流程驱动 | G0–G5 阶段门 + 主线流程脚本化检查 |
| **继承** | 治理为先 | Stage Gate 不通过不进入下一阶段 |
| **继承** | 用户决策 | 用户是唯一 VF（Verified & Frozen）授权者 |
| **IOM** | 柔性约束 | 所有方案必须满足"设备 + 人员 + 产线"三柔性特征 |
| **IOM** | 财务锚定 | 所有 Finding 必须折算为 OTIF/周转/人均产值/利润语言 |
| **IOM** | 端到端 | 分解框架覆盖 Concept-to-Cash 全价值流，禁止局部优化 |

---

## 贡献与扩展

### 添加新方法

1. 在 `skills/select-iom-methods/references/bottleneck-method-map.md` 中添加瓶颈→方法映射
2. 在 `knowledge/internal/iom-methodology-notes.md` 中补充方法详细说明
3. 更新 `skills/select-iom-methods/SKILL.md` 的方法目录

### 新增页面模板

1. 在 `skills/generate-iom-visuals/templates/` 创建新模板 `.md` 文件
2. 在 `skills/generate-iom-visuals/references/page-archetypes.md` 中注册模板
3. 更新 `skills/generate-iom-visuals/scripts/render_page.py` 的模板加载逻辑

### 自定义阶段门

1. 修改 `skills/manage-iom-engagement/references/stage-gates.md`
2. 同步更新 `skills/manage-iom-engagement/scripts/gate_check.py` 的检查逻辑
3. 更新 `GOVERNANCE.md` 治理宪章

---

## 许可证

MIT License

---

## 联系方式

- GitHub: [welljoe/iom-ops-diagnosis](https://github.com/welljoe/iom-ops-diagnosis)
- 问题反馈：请提交 Issue

---

**版本**: v1.1 (包含三大错位诊断透镜、呆滞清理 PMO 行动卡、高管汇报页模板)

**最后更新**: 2025 年 1 月
