# iom-ops-diagnosis Agent 详细设计文档 v1.0

**——基于 MBB 问题解决方法论 × “端到端敏捷运营体系重构” 的集成运营管理（IOM）咨询诊断 Agent**

本设计完全对齐您附件案例的治理哲学（**模块各守边界、生产只接收已确认内容、用户唯一 VF 授权、全链路台账留痕**），并将 IOM 领域方法论（HMLV 痛点模式库、柔性制造方法栈、四模块重构框架）工程化注入。

---

## 1. 设计总览

### 1.1 定位与适用场景

面向 **“多品种小批量（HMLV）、插单多、小单多”** 制造企业，以 CEO 视角执行端到端 IOM 咨询诊断：从痛点界定 → 假设分解 → 证据检验 → 方案选择 → 页面确认 → 交付生产，全程受治理、可追溯。

### 1.2 设计原则（继承案例 + IOM 特化）

| 类别  | 原则    | 工程化落点                              |
| --- | ----- | ---------------------------------- |
| 继承  | 流程驱动  | G0–G5 阶段门 + 主线流程脚本化检查              |
| 继承  | 治理为先  | Stage Gate 不通过不进入下一阶段              |
| 继承  | 方法赋能  | 最小方法栈按需调用，禁止方法堆砌                   |
| 继承  | 用户决策  | 用户是唯一 VF（Verified & Frozen）授权者     |
| 继承  | 可追溯闭环 | 证据/页面/门径三台账全留痕                     |
| IOM | 柔性约束  | 所有方案必须满足“设备+人员+产线”三柔性特征            |
| IOM | 财务锚定  | 所有 Finding 必须折算为 OTIF/周转/人均产值/利润语言 |
| IOM | 端到端   | 分解框架覆盖 Concept-to-Cash 全价值流，禁止局部优化 |

### 1.3 关键状态定义

- **页面状态**：`draft → confirmed → VF`（仅用户可授权 VF；VF 后不可被 Skill 修改）
- **证据分级**：`A` 客户系统统计数据 ／ `B` 多源交叉访谈 ／ `C` 单源或外部对标 ／ `D` 假设待补证
- **Storyline**：动态“当前最佳解释”，版本号随证据迭代（v0.1→v1.0）

---

## 2. 总体架构（四层模型，对齐案例图 1）

```
┌─ 04 决策与交付 ─────────────────────────────────────────┐
│  决策内容(诊断/对标/方案/Roadmap) →【用户决策权·唯一VF】→ 生产交付(仅收VF页) │
├─ 03 项目治理 ─────────────────────────────────────────┤
│  Engagement Controller(Storyline/工作流/依赖) ⇄ 项目中枢 ⇄ 阶段门与台账   │
├─ 02 问题求解核心 ──────────────────────────────────────┤
│  动态推理核心(问题→假设→证据→综合→选择) → 方法选择器 → 逻辑审核器          │
├─ 01 证据与知识底座 ────────────────────────────────────┤
│  现状与问题(痛点/柔性约束) │ 内部知识库(IOM方法论/案例) │ 外部证据(对标)     │
└──────────────────────────────────────────────────────┘
```

### IOM 动态推理闭环（8 步特化，对齐案例图 2）

| 步骤       | IOM 特化内容                                       | 主输出                       |
| -------- | ---------------------------------------------- | ------------------------- |
| 01 决策问题  | “如何在 HMLV 高波动下重构端到端敏捷运营，使 OTIF、库存周转、人均产值同步突破？” | Governing Question + 项目章程 |
| 02 初始假设  | 调用 H1–H8 根因假设库（如“插单无围栏击穿计划”）                   | 假设矩阵                      |
| 03 结构化分解 | 四模块 MECE：计划大脑／柔性制造／供应链延迟／组织绩效                  | Issue Tree                |
| 04 证据检验  | 按 IOM 数据清单取证（齐套率、换线时间、OEE、SKU 盈利-周转矩阵…）        | 证据台账                      |
| 05 方法选择器 | 按逻辑瓶颈调用最小方法栈（VSM、ABC-XYZ、SMED、延迟制造…）           | 分析计划                      |
| 06 行动设计  | 百日计划：灯塔线试点→速赢验证→推广固化；Owner/依赖/节奏               | Roadmap                   |
| 07 方案选择  | 影响/可行性矩阵 + 三柔性约束筛选；取舍与边界                       | 决策记录                      |
| 08 综合判断  | Finding→Insight→Implication，全部折算财务语言           | 章节结论页                     |

中心为**动态 Storyline**：证据更新→修正假设→收敛→行动反馈重定义问题。

---

## 3. 目录框架（Plugin 完整树）

```
iom-ops-diagnosis/
├── .codex-plugin/
│   └── plugin.json                     # 元数据、skill 清单、治理声明(VF/ gates/ registers)
├── README.md                           # 人类可读总览：定位、边界、快速开始
├── GOVERNANCE.md                       # 治理宪章：阶段门、VF 机制、台账规范、红线
├── skills/
│   ├── manage-iom-engagement/          # S1 项目编排与状态治理
│   │   ├── SKILL.md
│   │   ├── references/  engagement-playbook.md | stage-gates.md | ledger-spec.md
│   │   ├── scripts/     init_workspace.py | update_register.py | gate_check.py
│   │   └── templates/   project_charter.md | storyline_ledger.md | registers.md
│   ├── frame-iom-problem/              # S2 问题界定与结构化分解支持
│   │   ├── SKILL.md
│   │   ├── references/  iom-4module-framework.md | hmlv-pain-patterns.md | hypothesis-library.md
│   │   ├── scripts/     painpoint_mapper.py | mece_checker.py
│   │   └── templates/   governing_question.md | issue_tree.md | hypothesis_matrix.md
│   ├── select-iom-methods/             # S3 方法选择器（最小方法栈）
│   │   ├── SKILL.md
│   │   ├── references/  method-stack-catalog.md | bottleneck-method-map.md | flexibility-constraints.md
│   │   ├── scripts/     method_selector.py
│   │   └── templates/   analysis_plan.md | method_card.md
│   ├── review-iom-logic/               # S4 逻辑审核器
│   │   ├── SKILL.md
│   │   ├── references/  logic-review-checklist.md | evidence-grading.md
│   │   ├── scripts/     logic_audit.py
│   │   └── templates/   logic_audit_report.md | evidence_plan.md
│   ├── generate-iom-visuals/           # S5 单页可视化（只处理已就绪内容）
│   │   ├── SKILL.md
│   │   ├── references/  visual-style-guide.md | page-archetypes.md
│   │   ├── scripts/     render_page.py
│   │   └── templates/   vsm_page.md | matrix_page.md | roadmap_page.md | kpi_page.md
│   └── produce-iom-deck/               # S6 交付生产（只接收 VF 页）
│       ├── SKILL.md
│       ├── references/  deck-assembly-rules.md | review-pack-spec.md
│       ├── scripts/     build_deck.py | build_review_pack.py
│       └── templates/   deck_skeleton.pptx | review_pack.md
├── knowledge/                          # 证据与知识底座
│   ├── context/     client_context.md(痛点清单) | flexibility_profile.md(五特征)
│   ├── internal/    iom-methodology-notes.md(端到端敏捷运营重构) | case_library.md
│   └── external/    benchmark_sources.md(周转/OTIF/OEE 行业基线)
├── state/                              # 运行时台账（脚本生成，唯一事实源）
│   ├── project_state.json   ├── storyline.md
│   ├── evidence_register.md ├── page_register.md └── gate_log.md
└── outputs/
    ├── pages/   ├── decks/   └── review/
```

---

## 4. Skills 详细设计（职责契约 + 守边界）

| Skill                        | 职责                                               | 输入契约                | 输出契约                  | 守边界（红线）                        |
| ---------------------------- | ------------------------------------------------ | ------------------- | --------------------- | ------------------------------ |
| **S1 manage-iom-engagement** | 编排问题/Storyline/台账；维护端到端状态；执行阶段门                  | 用户指令、各 Skill 状态变更请求 | 章程、台账更新、gate 报告       | 不生成结论；不修改证据；不生成正式页面            |
| **S2 frame-iom-problem**     | 界定 Governing Question；痛点→假设映射；Issue Tree MECE 分解 | 客户痛点清单、柔性特征         | GQ 文档、假设矩阵、Issue Tree | 不做证据检验；不下最终结论；不产出页面            |
| **S3 select-iom-methods**    | 识别逻辑瓶颈；输出**最小**方法栈与分析计划                          | Issue Tree + 瓶颈标签   | 分析计划、方法卡              | 不执行分析；不修改假设；不产出页面              |
| **S4 review-iom-logic**      | 逻辑检查/修正/补证计划；证据分级审计                              | Storyline、证据台账      | 审核报告、补证计划             | 不创建新 Storyline；不替代用户决策；不直接产正式页 |
| **S5 generate-iom-visuals**  | 将**已确认**单页内容渲染为 MBB 风格视觉                         | confirmed 页面内容      | 单页视觉稿                 | 不判断内容正确性；不补充证据；不输出未确认内容        |
| **S6 produce-iom-deck**      | 组装 VF 页为可编辑 PPT + 审阅包                            | 仅 VF 页面             | deck、review pack      | 不修改已确认内容；不生成结论；不决定内容是否可用       |

**协作主线**：S2 界定分解 → S3 选方法 →（Agent 推理核心执行取证与综合）→ S4 审核 → S5 渲染 → 用户章节 Review → VF → S6 生产；S1 全程编排与门检。

---

## 5. IOM 方法栈目录（方法选择器内核）

| 逻辑瓶颈标签     | 最小方法栈                          | 关键输出         | 财务锚定        |
| ---------- | ------------------------------ | ------------ | ----------- |
| 插单混乱/计划被击穿 | 订单分级+时间围栏、S&OP/S&OE            | 订单准入规则、冻结窗   | 减少紧急采购溢价    |
| 呆滞与缺料并存    | ABC-XYZ 矩阵、VMI/寄售设计            | 差异化备料策略      | 库存资金释放      |
| 齐套率低/车间待料  | 齐套控制塔、齐套前移分析                   | 排产前 T-3 齐套规则 | OEE 与人工浪费下降 |
| 换线损失大      | SMED、内外作业分离                    | 换线时间 −80% 目标 | 小单边际成本下降    |
| 人海战术/人均产值低 | Cell/U 型线、线平衡&Takt、水蜘蛛         | 柔性细胞线布局      | 人均产值 +20%   |
| 多能工调度混乱    | 技能矩阵+动态排班模型                    | 人-单匹配规则      | 柔性人工成本弹性    |
| 成品呆滞高      | 延迟制造 Postponement、通用件解耦        | 半成品缓冲策略      | 呆滞减值下降      |
| 交付投诉多      | OTIF 根因树、价值流图 VSM              | MCE/前置时间基线   | 违约赔偿与流失下降   |
| 利润被吞噬      | CCC/营运资本分析、Should-cost         | 现金流改善项       | 净利润直接增厚     |
| 部门墙/救火文化   | 价值流经理(VSM Owner)、KPI 冲突矩阵、分层日会 | 组织与绩效重构      | OTIF 与周转共担  |
| 方案取舍困难     | 影响/可行性矩阵、三柔性约束筛选               | 优先级清单        | 投入产出排序      |

> `method_selector.py` 逻辑：输入瓶颈标签集合 → 查映射表 → 去重合并 → 输出≤5 个方法的最小栈；超出即告警“方法堆砌”。

---

## 6. 治理机制：阶段门 × VF × 台账

### 6.1 阶段门 G0–G5（`gate_check.py` 自动核查准入条件）

| Gate  | 准入条件（PASS 判定）                                             | 授权者      |
| ----- | --------------------------------------------------------- | -------- |
| G0 界定 | Governing Question + 章程量化目标（齐套率≥95%、周转+30%、OTIF≥98%）获用户确认 | 用户       |
| G1 分解 | Issue Tree 通过 `mece_checker`；假设矩阵覆盖四模块                    | 用户       |
| G2 证据 | 证据台账无 D 级关键证据；每个假设≥1 条 A/B 级证据或补证计划                       | S4 审核+用户 |
| G3 综合 | 逻辑审核 PASS；Finding→Insight→Implication 链完整；方案选择记录取舍        | 用户       |
| G4 页面 | 章节 Review 通过；用户对页面显式批复 VF（page_register 状态=VF）            | **用户唯一** |
| G5 交付 | deck 仅含 VF 页；review pack 含全链路留痕；gate_log 归档               | S6 自动校验  |

### 6.2 台账规范（唯一事实源）

- `evidence_register.md`：EV-ID｜来源｜分级｜支撑假设｜时间戳
- `page_register.md`：PG-ID｜章节｜状态(draft/confirmed/VF)｜VF 批复原文引用
- `gate_log.md`：Gate｜时间｜PASS/FAIL｜缺失项｜操作者
- `storyline.md`：版本｜变更｜触发证据 EV-ID（保证可追溯闭环）

---

## 7. 脚本与工具设计（I/O 与强制逻辑）

| 脚本                   | 输入           | 输出                     | 内置治理强制                            |
| -------------------- | ------------ | ---------------------- | --------------------------------- |
| init_workspace.py    | 项目名          | state/、outputs/ 初始化    | 写入 G0 初始状态                        |
| painpoint_mapper.py  | 痛点清单(P1–P6)  | 痛点→假设(H1–H8)映射草稿       | 标注“待用户确认”                         |
| mece_checker.py      | Issue Tree   | 互斥/穷尽检查报告              | 对照四模块框架查漏                         |
| method_selector.py   | 瓶颈标签         | 最小方法栈+分析计划             | >5 方法告警                           |
| logic_audit.py       | Storyline+台账 | 审核清单（证据链/So-What/替代解释） | 关键结论无 A/B 证据=FAIL                 |
| update_register.py   | 变更请求         | 台账更新                   | 状态机校验：draft→confirmed→VF 单向；VF 禁改 |
| gate_check.py        | gate 编号      | PASS/FAIL+缺失项          | 不通过则阻断下游脚本                        |
| render_page.py       | PG-ID+内容     | 单页视觉稿                  | 校验 page_register≠draft 才渲染        |
| build_deck.py        | VF 页清单       | 可编辑 PPT                | **自动过滤非 VF 页**                    |
| build_review_pack.py | 全台账          | 审阅包                    | 含证据链与决策留痕                         |

---

## 8. 输出模板体系（核心示例）

**模板清单**：project_charter / governing_question / issue_tree / hypothesis_matrix / analysis_plan / method_card / logic_audit_report / evidence_plan / vsm_page / matrix_page / roadmap_page / kpi_page / review_pack / deck_skeleton。

**示例 1：hypothesis_matrix.md（节选）**

| H-ID | 可证伪假设               | 模块  | 验证数据      | 证据       | 状态  |
| ---- | ------------------- | --- | --------- | -------- | --- |
| H1   | 插单无时间围栏导致计划变更率>40%  | M1  | 订单变更日志    | EV-03(B) | 支持  |
| H4   | 换线时间占有效工时>25%       | M2  | 设备日志      | EV-07(A) | 支持  |
| H6   | 成品呆滞中>60% 源自定制件提前生产 | M3  | 库龄×BOM 分析 | EV-09(A) | 待验证 |

**示例 2：roadmap_page.md（百日计划骨架）**

- W1–2 诊断共识：VSM 基线+章程签核（Owner: 项目组；依赖: 数据权限）
- W3–6 灯塔线：首条柔性 Cell+齐套控制塔+围栏规则试点
- W7–10 速赢验证：齐套≥95%、换线−50%、OTIF≥98% 财务核验
- W11–16 推广固化：SOP+技能矩阵+分层日会+轻量 APS 固化

---

## 9. 工程化验证流程

```
PASS 插件清单与目录(plugin.json schema)
 → PASS ×6  Skill 结构验证(SKILL.md frontmatter+三目录齐备)
 → PASS ×5  ZIP 与聚合验证(路径引用一致/模板可渲染/脚本可执行)
 → PASS dry-run(init_workspace→gate_check(G0) 演示闭环)
 → 通过工程化验证：结构完整，可运行
```

**真实状态边界**：证明六个能力模块已工程化并通过结构验证；**不证明 Workspace Agent 已经创建，也不表示案例已完成。**

---

## 10. 端到端运行示例（以您的案例走一遍）

1. **G0**：S2 产出 GQ——“重构端到端敏捷运营，使齐套率≥95%、周转+30%、OTIF≥98%”；用户确认。
2. **G1**：痛点 P1–P6 经 `painpoint_mapper` 映射 H1–H8；Issue Tree 按四模块分解，`mece_checker` PASS。
3. **G2**：S3 针对瓶颈“呆滞与缺料并存”选最小栈｛ABC-XYZ、围栏、齐套控制塔｝；取证入台账（EV-01…EV-12）。
4. **G3**：推理核心综合：Finding“物理柔性有余、计划协同瘫痪”→Insight“大脑重构优先于硬件再投入”→Implication“灯塔线百日计划”；S4 审核 PASS；用户完成方案取舍。
5. **G4**：S5 渲染 VSM 页/矩阵页/Roadmap 页；用户章节 Review 后批复 VF。
6. **G5**：S6 仅以 VF 页组装 deck + review pack；gate_log 归档，闭环完成。

---

如需下一步，我可以：① 输出任一 SKILL.md / 脚本的完整可运行代码；② 生成 plugin.json 与 GOVERNANCE.md 全文；③ 将第 10 节的示例台账填充为完整 demo 数据。您希望先展开哪一项？
