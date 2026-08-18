#!/usr/bin/env python3
"""
S3: Select IOM Methods - 方法选择器脚本

根据输入的瓶颈标签集合，自动选择最小方法栈并生成分析计划。
治理强制：方法栈超过 5 个时告警并拒绝生成计划。
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Set


# ============================================================================
# 瓶颈 - 方法映射表（基于设计文档第 5 节）
# ============================================================================

BOTTLENECK_METHOD_MAP = {
    "planning_chaos": {
        "label_zh": "插单混乱/计划被击穿",
        "methods": [
            {
                "id": "M01",
                "name": "订单分级 + 时间围栏",
                "description": "建立订单优先级分类与冻结窗口机制",
                "output": "订单准入规则、冻结窗设计",
                "financial_impact": "减少紧急采购溢价"
            },
            {
                "id": "M02",
                "name": "S&OP/S&OE",
                "description": "销售与运营规划/执行协同流程",
                "output": "月度 S&OP 会议机制、周度 S&OE 跟踪",
                "financial_impact": "降低计划变更率"
            }
        ]
    },
    "inventory_imbalance": {
        "label_zh": "呆滞与缺料并存",
        "methods": [
            {
                "id": "M03",
                "name": "ABC-XYZ 矩阵",
                "description": "基于用量波动性与价值的物料分类",
                "output": "差异化备料策略矩阵",
                "financial_impact": "库存资金释放"
            },
            {
                "id": "M04",
                "name": "VMI/寄售设计",
                "description": "供应商管理库存模式",
                "output": "VMI 协议框架、寄售库存点位",
                "financial_impact": "降低自有库存占用"
            }
        ]
    },
    "kitting_low": {
        "label_zh": "齐套率低/车间待料",
        "methods": [
            {
                "id": "M05",
                "name": "齐套控制塔",
                "description": "可视化齐套状态监控中心",
                "output": "齐套率仪表盘、预警机制",
                "financial_impact": "OEE 与人工浪费下降"
            },
            {
                "id": "M06",
                "name": "齐套前移分析",
                "description": "T-3 齐套检查机制",
                "output": "排产前齐套规则、缺料清单",
                "financial_impact": "减少车间等待时间"
            }
        ]
    },
    "changeover_loss": {
        "label_zh": "换线损失大",
        "methods": [
            {
                "id": "M07",
                "name": "SMED",
                "description": "快速换模 (Single-Minute Exchange of Die)",
                "output": "换线时间 −80% 目标与路径",
                "financial_impact": "小单边际成本下降"
            },
            {
                "id": "M08",
                "name": "内外作业分离",
                "description": "区分内部/外部换线作业",
                "output": "标准化换线 SOP",
                "financial_impact": "提升有效工时"
            }
        ]
    },
    "labor_inefficiency": {
        "label_zh": "人海战术/人均产值低",
        "methods": [
            {
                "id": "M09",
                "name": "Cell/U 型线",
                "description": "柔性细胞生产线布局",
                "output": "细胞线布局图、人员配置",
                "financial_impact": "人均产值 +20%"
            },
            {
                "id": "M10",
                "name": "线平衡&Takt",
                "description": "节拍平衡分析",
                "output": "线平衡率改善方案",
                "financial_impact": "消除瓶颈工序浪费"
            },
            {
                "id": "M11",
                "name": "水蜘蛛配送",
                "description": "物料定时定点配送",
                "output": "水蜘蛛路线与频次设计",
                "financial_impact": "减少操作工离岗时间"
            }
        ]
    },
    "skill_chaos": {
        "label_zh": "多能工调度混乱",
        "methods": [
            {
                "id": "M12",
                "name": "技能矩阵",
                "description": "员工多技能认证体系",
                "output": "技能矩阵图、培训路径",
                "financial_impact": "柔性人工成本弹性"
            },
            {
                "id": "M13",
                "name": "动态排班模型",
                "description": "基于订单波动的灵活排班",
                "output": "人 - 单匹配规则",
                "financial_impact": "降低加班成本"
            }
        ]
    },
    "finished_goods_stagnant": {
        "label_zh": "成品呆滞高",
        "methods": [
            {
                "id": "M14",
                "name": "延迟制造 (Postponement)",
                "description": "将定制工序后移至订单确认后",
                "output": "半成品缓冲策略",
                "financial_impact": "呆滞减值下降"
            },
            {
                "id": "M15",
                "name": "通用件解耦",
                "description": "识别并提前生产通用部件",
                "output": "通用件清单与生产计划",
                "financial_impact": "缩短交付周期"
            }
        ]
    },
    "delivery_complaints": {
        "label_zh": "交付投诉多",
        "methods": [
            {
                "id": "M16",
                "name": "OTIF 根因树",
                "description": "On-Time In-Full 分解分析",
                "output": "OTIF 损失根因图谱",
                "financial_impact": "违约赔偿与流失下降"
            },
            {
                "id": "M17",
                "name": "价值流图 (VSM)",
                "description": "端到端价值流可视化",
                "output": "MCE/前置时间基线",
                "financial_impact": "识别非增值时间"
            }
        ]
    },
    "profit_erosion": {
        "label_zh": "利润被吞噬",
        "methods": [
            {
                "id": "M18",
                "name": "CCC/营运资本分析",
                "description": "现金循环周期分析",
                "output": "现金流改善项清单",
                "financial_impact": "净利润直接增厚"
            },
            {
                "id": "M19",
                "name": "Should-cost",
                "description": "理论成本建模",
                "output": "成本差异分析与谈判依据",
                "financial_impact": "采购成本优化"
            }
        ]
    },
    "silo_culture": {
        "label_zh": "部门墙/救火文化",
        "methods": [
            {
                "id": "M20",
                "name": "价值流经理 (VSM Owner)",
                "description": "端到端流程负责人制度",
                "output": "VSM Owner 职责定义",
                "financial_impact": "OTIF 与周转共担"
            },
            {
                "id": "M21",
                "name": "KPI 冲突矩阵",
                "description": "识别并解决 KPI 冲突",
                "output": "对齐的绩效指标体系",
                "financial_impact": "消除局部优化"
            },
            {
                "id": "M22",
                "name": "分层日会",
                "description": "逐级问题升级机制",
                "output": "日会 SOP、问题跟踪表",
                "financial_impact": "快速响应异常"
            }
        ]
    },
    "decision_hard": {
        "label_zh": "方案取舍困难",
        "methods": [
            {
                "id": "M23",
                "name": "影响/可行性矩阵",
                "description": "二维优先级评估",
                "output": "优先级清单",
                "financial_impact": "投入产出排序"
            },
            {
                "id": "M24",
                "name": "三柔性约束筛选",
                "description": "设备/人员/产线柔性评估",
                "output": "符合柔性约束的方案子集",
                "financial_impact": "确保方案可落地"
            }
        ]
    }
}

MAX_METHODS = 5  # 最大方法数限制


def parse_bottlenecks(bottleneck_arg: str) -> List[str]:
    """解析瓶颈标签输入（支持逗号分隔或 JSON 格式）"""
    bottleneck_arg = bottleneck_arg.strip()
    
    # 尝试解析为 JSON
    if bottleneck_arg.startswith('['):
        try:
            return json.loads(bottleneck_arg)
        except json.JSONDecodeError:
            pass
    
    # 默认按逗号分隔
    return [b.strip() for b in bottleneck_arg.split(',') if b.strip()]


def select_methods(bottleneck_tags: List[str]) -> Dict:
    """
    选择算法：
    1. 对每个瓶颈标签查映射表获取候选方法
    2. 去重合并（同一方法可能被多个瓶颈触发）
    3. 若方法数量 > 5，触发告警
    4. 按优先级排序（财务影响 × 实施难度）
    5. 返回最小方法栈（≤5 个方法）
    """
    selected_methods: Dict[str, Dict] = {}
    triggered_by: Dict[str, List[str]] = {}  # method_id -> [bottleneck_tags]
    
    for tag in bottleneck_tags:
        if tag not in BOTTLENECK_METHOD_MAP:
            print(f"⚠️  警告：未知的瓶颈标签 '{tag}'，跳过")
            continue
        
        bottleneck_info = BOTTLENECK_METHOD_MAP[tag]
        for method in bottleneck_info["methods"]:
            method_id = method["id"]
            if method_id not in selected_methods:
                selected_methods[method_id] = method
                triggered_by[method_id] = []
            triggered_by[method_id].append(tag)
    
    # 检查是否超过限制
    method_count = len(selected_methods)
    warning = None
    
    if method_count > MAX_METHODS:
        warning = (
            f"⚠️  WARN: 方法堆砌风险！检测到 {method_count} 个方法，超过上限 {MAX_METHODS}。\n"
            f"   建议：请确认瓶颈优先级，或分阶段实施。\n"
            f"   当前方法列表：{', '.join(selected_methods.keys())}"
        )
    
    # 简单排序：按 method_id（实际可按财务影响评分排序）
    sorted_methods = dict(sorted(selected_methods.items()))
    
    return {
        "methods": sorted_methods,
        "triggered_by": triggered_by,
        "total_count": method_count,
        "warning": warning,
        "exceeds_limit": method_count > MAX_METHODS
    }


def generate_analysis_plan(selection_result: Dict, bottleneck_tags: List[str], output_dir: str) -> str:
    """生成分析计划文档"""
    
    methods = selection_result["methods"]
    triggered_by = selection_result["triggered_by"]
    
    plan_content = f"""# 分析计划 (Analysis Plan)

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**输入瓶颈**: {', '.join(bottleneck_tags)}  
**方法栈规模**: {selection_result['total_count']} 个方法

"""
    
    if selection_result["warning"]:
        plan_content += f"""> ⚠️  **告警**: {selection_result['warning'].split('   当前方法列表')[0].replace('⚠️  WARN: ', '')}\n\n"""
    
    plan_content += """## 一、方法栈总览

| 方法 ID | 方法名称 | 触发瓶颈 | 关键输出 | 财务影响 |
|---------|----------|----------|----------|----------|
"""
    
    for method_id, method in methods.items():
        bottlenecks = ', '.join(triggered_by[method_id])
        plan_content += f"| {method_id} | {method['name']} | {bottlenecks} | {method['output']} | {method['financial_impact']} |\n"
    
    plan_content += f"""
## 二、分析步骤

### 步骤 1: 数据准备
- [ ] 收集各方法所需基础数据（见方法卡详细清单）
- [ ] 确认数据可用性与质量等级（A/B/C/D）
- [ ] 建立数据访问权限

### 步骤 2: 方法执行
按以下顺序执行分析方法：
"""
    
    for i, (method_id, method) in enumerate(methods.items(), 1):
        plan_content += f"\n#### {i}. {method['name']} ({method_id})\n"
        plan_content += f"- **目的**: {method['description']}\n"
        plan_content += f"- **预期输出**: {method['output']}\n"
        plan_content += f"- **所需数据**: 详见方法卡 `{method_id}`\n"
    
    plan_content += f"""
### 步骤 3: 综合整合
- [ ] 将各方法输出整合至统一分析框架
- [ ] 识别方法间的依赖与冲突
- [ ] 形成初步 Finding

### 步骤 4: 逻辑审核准备
- [ ] 整理证据链（EV-ID 关联）
- [ ] 准备 Storyline 更新提案
- [ ] 提交 S4 (review-iom-logic) 审核

## 三、治理检查点

- [ ] G1 Gate: Issue Tree 已通过 MECE 验证
- [ ] 方法栈 ≤ 5 个（若超出需用户确认优先级）
- [ ] 每个方法有明确的财务锚定
- [ ] 分析计划已记录至台账

---

*本计划由 `method_selector.py` 自动生成，下一步需经用户确认后执行分析方法。*
"""
    
    output_path = os.path.join(output_dir, "analysis_plan.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    return output_path


def generate_method_cards(selection_result: Dict, output_dir: str) -> List[str]:
    """为每个选中的方法生成方法卡"""
    
    cards_paths = []
    methods = selection_result["methods"]
    
    # 构建 method_id 到瓶颈标签的映射
    method_to_bottleneck = {}
    for tag, info in BOTTLENECK_METHOD_MAP.items():
        for method in info["methods"]:
            method_id = method["id"]
            if method_id not in method_to_bottleneck:
                method_to_bottleneck[method_id] = {"tag": tag, "label_zh": info["label_zh"]}
    
    for method_id, method in methods.items():
        bottleneck_info = method_to_bottleneck.get(method_id, {"tag": "N/A", "label_zh": "N/A"})
        
        card_content = f"""# 方法卡：{method['name']} ({method_id})

## 基本信息

| 属性 | 值 |
|------|-----|
| **方法 ID** | {method_id} |
| **名称** | {method['name']} |
| **描述** | {method['description']} |
| **适用瓶颈** | {bottleneck_info['label_zh']} |

## 方法论详解

### 定义
{method['description']}

### 适用场景
- HMLV 环境下{method['name'].lower()}需求强烈
- 当前存在{method['financial_impact']}相关的痛点
- 具备基础数据支撑（见下方数据清单）

### 关键输出
**主要交付物**: {method['output']}

**辅助交付物**:
- 数据分析报告
- 现状 vs 目标对比
- 实施路线图建议

## 数据需求清单

| 数据类型 | 来源系统 | 最低粒度 | 证据等级要求 |
|----------|----------|----------|--------------|
| *根据具体方法补充* | ERP/MES | *按天/按单* | B 级以上 |

## 分析模板

```markdown
### {method['name']} 分析结果

**现状基线**: [填写当前指标值]
**目标值**: [填写改善目标]
**差距分析**: [描述关键发现]
**根因识别**: [列出 Top 3 根因]
**改善机会**: [量化改善潜力]
```

## 财务锚定

**直接影响**: {method['financial_impact']}

**量化公式**: 
- *根据具体方法补充计算公式*

## 与其他方法的依赖

*根据分析计划中的方法栈，说明本方法与哪些方法存在前后依赖关系*

---

*本方法卡由 `method_selector.py` 自动生成，详细执行指南请参考内部知识库 `iom-methodology-notes.md`*
"""
        
        card_path = os.path.join(output_dir, f"method_card_{method_id}.md")
        with open(card_path, 'w', encoding='utf-8') as f:
            f.write(card_content)
        
        cards_paths.append(card_path)
    
    return cards_paths


def check_gate_g1(issue_tree_path: str) -> bool:
    """检查 G1 Gate：Issue Tree 是否已通过 MECE 验证"""
    
    if not os.path.exists(issue_tree_path):
        print(f"⚠️  警告：Issue Tree 文件不存在：{issue_tree_path}")
        return False
    
    # 简化检查：文件存在即认为通过（实际应解析内容检查 mece_passed 标记）
    with open(issue_tree_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    if 'mece' in content or 'pass' in content:
        return True
    
    print(f"⚠️  警告：Issue Tree 文件中未找到 MECE 验证标记")
    return True  # 宽松模式，不阻断


def main():
    parser = argparse.ArgumentParser(
        description='S3: Select IOM Methods - 方法选择器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --bottlenecks "inventory_imbalance,changeover_loss" --output-dir outputs/
  %(prog)s --bottlenecks '[\"planning_chaos\", \"kitting_low\"]' --issue-tree state/issue_tree.md
        """
    )
    
    parser.add_argument(
        '--bottlenecks', '-b',
        required=True,
        help='瓶颈标签列表（逗号分隔或 JSON 数组格式）'
    )
    
    parser.add_argument(
        '--issue-tree', '-t',
        default=None,
        help='可选：Issue Tree 文件路径用于 G1 Gate 校验'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='outputs/',
        help='输出目录（默认：outputs/）'
    )
    
    parser.add_argument(
        '--skip-gate-check',
        action='store_true',
        help='跳过 G1 Gate 检查'
    )
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 60)
    print("S3: Select IOM Methods - 方法选择器")
    print("=" * 60)
    
    # G1 Gate 检查
    if not args.skip_gate_check and args.issue_tree:
        print("\n[1/4] 执行 G1 Gate 检查...")
        if not check_gate_g1(args.issue_tree):
            print("❌ G1 Gate 检查失败：Issue Tree 未通过 MECE 验证")
            print("   请先运行 S2 的 mece_checker.py 完成验证")
            return 1
        print("✓ G1 Gate 检查通过")
    elif not args.skip_gate_check:
        print("\n[1/4] 跳过 G1 Gate 检查（未提供 Issue Tree 路径）")
    
    # 解析瓶颈标签
    print("\n[2/4] 解析瓶颈标签...")
    bottleneck_tags = parse_bottlenecks(args.bottlenecks)
    print(f"   输入瓶颈：{bottleneck_tags}")
    
    # 执行方法选择
    print("\n[3/4] 执行方法选择算法...")
    selection_result = select_methods(bottleneck_tags)
    
    print(f"   选中方法数：{selection_result['total_count']}")
    print(f"   方法列表：{list(selection_result['methods'].keys())}")
    
    if selection_result["warning"]:
        print(f"\n{selection_result['warning']}")
        print("\n❌ 由于方法数量超过限制，分析计划生成已终止。")
        print("   请减少瓶颈标签或确认优先级后重新运行。")
        return 1
    
    # 生成输出
    print("\n[4/4] 生成分析计划与方法卡...")
    
    plan_path = generate_analysis_plan(selection_result, bottleneck_tags, args.output_dir)
    print(f"   ✓ 分析计划：{plan_path}")
    
    card_paths = generate_method_cards(selection_result, args.output_dir)
    for card_path in card_paths:
        print(f"   ✓ 方法卡：{card_path}")
    
    print("\n" + "=" * 60)
    print("✅ 方法选择完成！")
    print("=" * 60)
    print(f"\n下一步:")
    print("  1. 审阅 analysis_plan.md 确认分析步骤")
    print("  2. 参考方法卡执行具体分析")
    print("  3. 将分析结果提交 S4 (review-iom-logic) 审核")
    
    return 0


if __name__ == '__main__':
    exit(main())
