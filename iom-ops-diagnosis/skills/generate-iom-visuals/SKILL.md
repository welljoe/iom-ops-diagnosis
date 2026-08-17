# S5: Generate IOM Visuals - 单页可视化技能

## 职责契约

| 属性 | 描述 |
|------|------|
| **职责** | 将**已确认 (confirmed)** 的单页内容渲染为 MBB 风格视觉稿 |
| **输入契约** | confirmed 状态的页面内容（来自 page_register 标记为 confirmed 的 PG-ID） |
| **输出契约** | 单页视觉稿（Markdown 格式，可转换为 PPT） |
| **守边界红线** | ❌ 不判断内容正确性<br>❌ 不补充证据或修改内容<br>❌ 不输出未确认 (draft) 状态的内容<br>❌ 不决定内容是否可用 |

## 方法论内核

### 页面原型库 (Page Archetypes)

基于 MBB 咨询交付标准与 IOM 领域特化，预置以下页面类型：

| 页面类型 | 用途 | 关键元素 | 适用章节 |
|----------|------|----------|----------|
| `executive_summary` | 高管摘要 | 核心 Finding+Insight+Implication 三段式 | 开篇 |
| `governing_question` | 问题界定 | GQ 陈述、量化目标、项目章程 | 第一章 |
| `issue_tree` | 结构化分解 | 层级树状图、MECE 检查标记 | 第一章 |
| `hypothesis_matrix` | 假设矩阵 | H-ID、可证伪表述、验证状态 | 第一章 |
| `vsm_current` | 价值流图 (现状) | 工序、库存点、前置时间、MCE | 第二章 |
| `vsm_future` | 价值流图 (未来) | 改善后状态、目标指标 | 第二章 |
| `abc_xyz_matrix` | ABC-XYZ 矩阵 | 二维散点图、象限策略 | 第二章 |
| `kpi_dashboard` | KPI 仪表盘 | OTIF、周转率、人均产值趋势 | 第二章 |
| `pain_point_map` | 痛点地图 | HMLV 痛点模式、影响程度 | 第二章 |
| `root_cause_tree` | 根因分析树 | 5Why 展开、根因标记 | 第三章 |
| `solution_option` | 方案选项对比 | 多方案并列、优缺点、财务影响 | 第三章 |
| `impact_feasibility` | 影响/可行性矩阵 | 二维优先级、速赢标识 | 第三章 |
| `roadmap_100day` | 百日计划 | 阶段里程碑、Owner、依赖关系 | 第四章 |
| `business_case` | 商业案例 | 投入产出、NPV/ROI、风险 | 第四章 |
| `org_design` | 组织设计 | 角色职责、KPI 对齐、治理机制 | 第四章 |

### 视觉风格指南 (Visual Style Guide)

#### 色彩规范
- **主色**: 深蓝 (#003366) — 标题、关键信息
- **辅色**: 灰色 (#666666) — 次要信息、注释
- **强调色**: 
  - 绿色 (#28A745) — 正面指标、速赢项
  - 橙色 (#FD7E14) — 警示、风险
  - 红色 (#DC3545) — 重大问题、Critical

#### 字体规范
- **标题**: Arial Bold, 24-32pt
- **正文**: Arial Regular, 14-18pt
- **注释**: Arial Light, 10-12pt

#### 布局原则
- **一页一观点**: 每页只传达一个核心信息
- **标题即结论**: Page Title 必须是完整的 Insight 表述
- **MECE 分组**: 内容分组符合互斥穷尽原则
- **视觉层次**: 重要信息置于左上角（第一视觉落点）

## 脚本说明

### render_page.py

**功能**：读取 confirmed 状态的页面内容，渲染为 MBB 风格单页视觉稿。

**输入**：
- `--page-id`：页面 ID（如 PG-01, PG-02）
- `--content-file`：页面内容文件路径（可选，若不提供则从 outputs/pages/ 读取）
- `--page-type`：页面类型（见上方原型库，可选）
- `--output-dir`：输出目录（默认 `outputs/pages/`）

**输出**：
- `<page_id>_visual.md`：渲染后的单页视觉稿（Markdown 格式）

**治理强制**：
- 自动检查 page_register.md 中该 PG-ID 的状态
- 仅当状态为 `confirmed` 时才允许渲染
- 状态为 `draft` 时拒绝渲染并提示用户先确认内容
- 状态为 `VF` 时提示"页面已 VF 冻结，如需修改需先撤销 VF"

## 参考文档

- `visual-style-guide.md`：完整视觉风格规范
- `page-archetypes.md`：页面原型详解与使用场景

## 模板文件

- `templates/vsm_page.md`：价值流图页面模板
- `templates/matrix_page.md`：矩阵类页面模板（ABC-XYZ、影响/可行性等）
- `templates/roadmap_page.md`：路线图页面模板
- `templates/kpi_page.md`：KPI 仪表盘页面模板
- `templates/executive_summary.md`：高管摘要页面模板

## 使用示例

```bash
# 示例 1：渲染已确认的 VSM 页面
python scripts/render_page.py \
  --page-id PG-03 \
  --page-type vsm_current \
  --output-dir outputs/pages/

# 示例 2：带内容文件的渲染
python scripts/render_page.py \
  --page-id PG-05 \
  --content-file state/confirmed_content/PG-05.md \
  --page-type abc_xyz_matrix \
  --output-dir outputs/pages/
```

## 与其他 Skills 的协作

```
S4 (review-iom-logic)
    ↓ [审核 PASS 的 Storyline]
[用户章节 Review → 确认页面内容]
    ↓ [page_register 状态=confirmed]
S5 (generate-iom-visuals) ← 本技能
    ↓ [单页视觉稿]
[用户 VF 授权]
    ↓ [page_register 状态=VF]
S6 (produce-iom-deck)
```

## 页面状态机

```
draft ──(用户确认)──> confirmed ──(S5 渲染)──> visualized
                          │
                          └──(用户 VF 授权)──> VF (冻结，不可修改)
```
