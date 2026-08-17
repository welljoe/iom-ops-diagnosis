#!/usr/bin/env python3
"""
painpoint_mapper.py - 痛点到假设的映射

用法:
    python painpoint_mapper.py --input <painpoints_file> --output <output_file>
"""

import argparse
from pathlib import Path


# HMLV 痛点模式库 (P1-P6)
PAIN_PATTERNS = {
    "P1": {
        "name": "插单无围栏击穿计划",
        "mapped_hypotheses": ["H1"],
        "description": "紧急插单频繁，无时间围栏机制，导致计划变更率高"
    },
    "P2": {
        "name": "呆滞与缺料并存",
        "mapped_hypotheses": ["H2", "H3"],
        "description": "原材料/半成品呆滞，同时产线待料频发"
    },
    "P3": {
        "name": "齐套率低/车间待料",
        "mapped_hypotheses": ["H3"],
        "description": "排产前齐套率低，导致车间停工待料"
    },
    "P4": {
        "name": "换线损失大",
        "mapped_hypotheses": ["H4"],
        "description": "多品种小批量导致频繁换线，换线时间占比高"
    },
    "P5": {
        "name": "人海战术/人均产值低",
        "mapped_hypotheses": ["H5"],
        "description": "依赖大量人工，人均产值低于行业基准"
    },
    "P6": {
        "name": "成品呆滞高",
        "mapped_hypotheses": ["H6"],
        "description": "成品库存高企，库龄结构恶化"
    }
}

# 假设库 (H1-H8)
HYPOTHESIS_LIBRARY = {
    "H1": {
        "statement": "插单无时间围栏导致计划变更率>40%",
        "module": "M1-计划大脑",
        "validation_data": "订单变更日志、计划冻结窗口执行情况"
    },
    "H2": {
        "statement": "备料策略未差异化导致呆滞与缺料并存",
        "module": "M3-供应链延迟",
        "validation_data": "ABC-XYZ 矩阵、安全库存策略"
    },
    "H3": {
        "statement": "齐套控制缺失导致车间待料损失 OEE>15%",
        "module": "M1-计划大脑",
        "validation_data": "齐套率统计、停工待料记录"
    },
    "H4": {
        "statement": "换线时间占有效工时>25%",
        "module": "M2-柔性制造",
        "validation_data": "设备日志、换线时间记录"
    },
    "H5": {
        "statement": "线平衡率<70%，人均产值低于行业基准 30%",
        "module": "M2-柔性制造",
        "validation_data": "线平衡分析、人均产值统计"
    },
    "H6": {
        "statement": "成品呆滞中>60% 源自定制件提前生产",
        "module": "M3-供应链延迟",
        "validation_data": "库龄×BOM 分析、订单履约记录"
    },
    "H7": {
        "statement": "多能工比例<30%，调度弹性不足",
        "module": "M4-组织绩效",
        "validation_data": "技能矩阵、排班记录"
    },
    "H8": {
        "statement": "部门墙导致 OTIF 与周转 KPI 冲突",
        "module": "M4-组织绩效",
        "validation_data": "KPI 定义文档、跨部门会议记录"
    }
}

# IOM 四模块框架
MODULES = {
    "M1": "计划大脑 (Planning Brain)",
    "M2": "柔性制造 (Flexible Manufacturing)",
    "M3": "供应链延迟 (Supply Chain Postponement)",
    "M4": "组织绩效 (Organization & Performance)"
}


def map_painpoints_to_hypotheses(painpoints: list[str]) -> dict:
    """将痛点映射到假设"""
    
    mapping_result = {
        "painpoints": [],
        "hypotheses": [],
        "coverage": {}
    }
    
    for painpoint in painpoints:
        if painpoint not in PAIN_PATTERNS:
            print(f"⚠️  未知痛点：{painpoint}")
            continue
        
        pattern = PAIN_PATTERNS[painpoint]
        mapping_result["painpoints"].append({
            "id": painpoint,
            "name": pattern["name"],
            "description": pattern["description"]
        })
        
        for hyp_id in pattern["mapped_hypotheses"]:
            if hyp_id not in [h["id"] for h in mapping_result["hypotheses"]]:
                hyp = HYPOTHESIS_LIBRARY[hyp_id]
                mapping_result["hypotheses"].append({
                    "id": hyp_id,
                    "statement": hyp["statement"],
                    "module": hyp["module"],
                    "validation_data": hyp["validation_data"]
                })
            
            # 记录覆盖关系
            if hyp_id not in mapping_result["coverage"]:
                mapping_result["coverage"][hyp_id] = []
            mapping_result["coverage"][hyp_id].append(painpoint)
    
    return mapping_result


def generate_hypothesis_matrix(mapping_result: dict) -> str:
    """生成假设矩阵 Markdown"""
    
    lines = [
        "# Hypothesis Matrix",
        "",
        "## 假设清单",
        "",
        "| H-ID | 可证伪假设 | 模块 | 验证数据 | 支撑痛点 | 状态 |",
        "|------|------------|------|----------|----------|------|"
    ]
    
    for hyp in mapping_result["hypotheses"]:
        supporting_painpoints = ", ".join(
            mapping_result["coverage"].get(hyp["id"], [])
        )
        lines.append(
            f"| {hyp['id']} | {hyp['statement']} | {hyp['module']} | "
            f"{hyp['validation_data']} | {supporting_painpoints} | 待验证 |"
        )
    
    lines.extend([
        "",
        "## 模块覆盖情况",
        ""
    ])
    
    for mod_id, mod_name in MODULES.items():
        covered_hyps = [h for h in mapping_result["hypotheses"] if h["module"] == mod_id]
        if covered_hyps:
            lines.append(f"- **{mod_id}**: {len(covered_hyps)} 个假设")
        else:
            lines.append(f"- ⚠️ **{mod_id}**: 无假设覆盖 (可能需要补充)")
    
    lines.extend([
        "",
        "## 备注",
        "",
        "> 状态说明：待验证 / 支持 / 证伪 / 待补证",
        ""
    ])
    
    return "\n".join(lines)


def run_mapping(input_file: str, output_file: str):
    """执行痛点映射"""
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 输入文件不存在：{input_file}")
        return False
    
    # 读取痛点清单
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 简单解析痛点 ID (支持 P1, P2, ...格式)
    import re
    painpoints = re.findall(r'P\d+', content)
    
    if not painpoints:
        print("⚠️  未在输入文件中找到痛点 ID (P1-P6)")
        print("   请确保文件包含类似 'P1', 'P2' 的痛点标识")
        return False
    
    print(f"✓ 识别到痛点：{', '.join(set(painpoints))}")
    
    # 执行映射
    mapping_result = map_painpoints_to_hypotheses(list(set(painpoints)))
    
    # 生成假设矩阵
    matrix_md = generate_hypothesis_matrix(mapping_result)
    
    # 输出
    output_path = Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(matrix_md)
    
    print(f"✓ 假设矩阵已生成：{output_file}")
    print(f"  - 假设数量：{len(mapping_result['hypotheses'])}")
    print(f"  - 覆盖模块：{len(set(h['module'] for h in mapping_result['hypotheses']))}/4")
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="痛点到假设的映射")
    parser.add_argument("--input", type=str, required=True, help="痛点清单文件")
    parser.add_argument("--output", type=str, default="hypothesis_matrix.md", 
                        help="输出文件路径")
    args = parser.parse_args()
    
    success = run_mapping(args.input, args.output)
    exit(0 if success else 1)
