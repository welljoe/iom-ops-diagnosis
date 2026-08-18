# S3: Select IOM Methods - 方法选择器技能

## 职责契约

| 属性 | 描述 |
|------|------|
| **职责** | 识别逻辑瓶颈；输出**最小**方法栈与分析计划 |
| **输入契约** | Issue Tree + 瓶颈标签（来自 S2 或推理核心） |
| **输出契约** | 分析计划 (analysis_plan.md)、方法卡 (method_card.md) |
| **守边界红线** | ❌ 不执行实际分析<br>❌ 不修改假设矩阵<br>❌ 不产出正式页面<br>❌ 方法栈超过 5 个必须告警 |

## 方法论内核

### 瓶颈 - 方法映射表

基于 IOM 四模块框架与 HMLV 痛点模式，预置以下映射关系：

| 瓶颈标签 | 最小方法栈 | 关键输出 | 财务锚定 |
|----------|------------|----------|----------|
| `planning_chaos` (插单混乱/计划被击穿) | 订单分级 + 时间围栏、S&OP/S&OE | 订单准入规则、冻结窗 | 减少紧急采购溢价 |
| `inventory_imbalance` (呆滞与缺料并存) | ABC-XYZ 矩阵、VMI/寄售设计 | 差异化备料策略 | 库存资金释放 |
| `kitting_low` (齐套率低/车间待料) | 齐套控制塔、齐套前移分析 | 排产前 T-3 齐套规则 | OEE 与人工浪费下降 |
| `changeover_loss` (换线损失大) | SMED、内外作业分离 | 换线时间 −80% 目标 | 小单边际成本下降 |
| `labor_inefficiency` (人海战术/人均产值低) | Cell/U 型线、线平衡&Takt、水蜘蛛 | 柔性细胞线布局 | 人均产值 +20% |
| `skill_chaos` (多能工调度混乱) | 技能矩阵 + 动态排班模型 | 人 - 单匹配规则 | 柔性人工成本弹性 |
| `finished_goods_stagnant` (成品呆滞高) | 延迟制造 Postponement、通用件解耦 | 半成品缓冲策略 | 呆滞减值下降 |
| `delivery_complaints` (交付投诉多) | OTIF 根因树、价值流图 VSM | MCE/前置时间基线 | 违约赔偿与流失下降 |
| `profit_erosion` (利润被吞噬) | CCC/营运资本分析、Should-cost | 现金流改善项 | 净利润直接增厚 |
| `silo_culture` (部门墙/救火文化) | 价值流经理 (VSM Owner)、KPI 冲突矩阵、分层日会 | 组织与绩效重构 | OTIF 与周转共担 |
| `decision_hard` (方案取舍困难) | 影响/可行性矩阵、三柔性约束筛选 | 优先级清单 | 投入产出排序 |

### 选择算法

```python
def select_methods(bottleneck_tags: List[str]) -> MethodStack:
    """
    1. 对每个瓶颈标签查映射表获取候选方法
    2. 去重合并（同一方法可能被多个瓶颈触发）
    3. 若方法数量 > 5，触发告警"方法堆砌风险"
    4. 按优先级排序（财务影响 × 实施难度）
    5. 返回最小方法栈（≤5 个方法）
    """
```

## 脚本说明

### method_selector.py

**功能**：根据输入的瓶颈标签集合，自动选择最小方法栈并生成分析计划。

**输入**：
- `--bottlenecks`：瓶颈标签列表（JSON 格式或逗号分隔）
- `--issue-tree`：可选，Issue Tree 文件路径用于上下文校验
- `--output-dir`：输出目录（默认 `outputs/`）

**输出**：
- `analysis_plan.md`：包含方法栈、分析步骤、所需数据清单
- `method_card_<method_id>.md`：每个方法的详细卡片（定义、适用场景、输出模板）

**治理强制**：
- 方法栈超过 5 个时，输出 WARN 并拒绝生成计划，要求用户确认优先级
- 自动检查 Issue Tree 是否已通过 MECE 验证（G1 Gate）

## 参考文档

- `method-stack-catalog.md`：完整方法栈目录与定义
- `bottleneck-method-map.md`：瓶颈 - 方法映射规则详解
- `flexibility-constraints.md`：三柔性约束（设备/人员/产线）评估标准

## 模板文件

- `templates/analysis_plan.md`：分析计划模板
- `templates/method_card.md`：方法卡模板

## 使用示例

```bash
# 示例 1：针对呆滞与缺料并存 + 换线损失大两个瓶颈
python scripts/method_selector.py \
  --bottlenecks "inventory_imbalance,changeover_loss" \
  --output-dir outputs/

# 示例 2：带 Issue Tree 上下文校验
python scripts/method_selector.py \
  --bottlenecks "planning_chaos,kitting_low" \
  --issue-tree state/issue_tree.md \
  --output-dir outputs/
```

## 与其他 Skills 的协作

```
S2 (frame-iom-problem) 
    ↓ [Issue Tree + 瓶颈标签]
S3 (select-iom-methods) ← 本技能
    ↓ [分析计划 + 方法卡]
[Agent 推理核心执行取证与分析]
    ↓ [证据 + 初步结论]
S4 (review-iom-logic)
```
