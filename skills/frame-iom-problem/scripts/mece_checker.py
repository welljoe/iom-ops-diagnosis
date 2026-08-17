#!/usr/bin/env python3
"""
mece_checker.py - Issue Tree MECE 检查

用法:
    python mece_checker.py --input <issue_tree_file>
"""

import argparse
import re
from pathlib import Path


# IOM 四模块框架 (MECE 分解基准)
IOM_MODULES = {
    "M1": {
        "name": "计划大脑",
        "keywords": ["计划", "排产", "齐套", "订单", "插单", "围栏", "S&OP", "S&OE"],
        "required_elements": ["订单准入", "时间围栏", "齐套控制"]
    },
    "M2": {
        "name": "柔性制造",
        "keywords": ["换线", "SMED", "线平衡", "cell", "U 型", "多能工", "OEE", "人均产值"],
        "required_elements": ["快速换线", "柔性布局", "人员弹性"]
    },
    "M3": {
        "name": "供应链延迟",
        "keywords": ["呆滞", "缺料", "VMI", "寄售", "延迟制造", "通用件", "解耦", "库龄"],
        "required_elements": ["差异化备料", "半成品缓冲", "延迟策略"]
    },
    "M4": {
        "name": "组织绩效",
        "keywords": ["KPI", "绩效", "部门墙", "价值流", "日会", "技能矩阵", "排班"],
        "required_elements": ["KPI 对齐", "价值流经理", "分层日会"]
    }
}


def parse_issue_tree(content: str) -> dict:
    """解析 Issue Tree 内容"""
    
    tree = {
        "root": None,
        "branches": {}
    }
    
    lines = content.split('\n')
    current_module = None
    current_branch = None
    
    for line in lines:
        # 跳过空行和注释
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # 识别模块级标题 (## M1: xxx)
        module_match = re.match(r'^##\s*(M\d+)[\s:：](.+)', line)
        if module_match:
            mod_id = module_match.group(1)
            mod_name = module_match.group(2).strip()
            current_module = mod_id
            tree["branches"][mod_id] = {
                "name": mod_name,
                "issues": []
            }
            continue
        
        # 识别问题项 (- 或 * 开头)
        issue_match = re.match(r'^[\-\*]\s*(.+)', line)
        if issue_match and current_module:
            issue_text = issue_match.group(1).strip()
            tree["branches"][current_module]["issues"].append(issue_text)
    
    return tree


def check_mece_coverage(tree: dict) -> tuple[bool, list[str]]:
    """检查 MECE 覆盖情况"""
    
    issues = []
    covered_modules = set(tree["branches"].keys())
    
    # 检查是否覆盖所有四模块
    all_modules = set(IOM_MODULES.keys())
    missing_modules = all_modules - covered_modules
    
    if missing_modules:
        for mod_id in missing_modules:
            issues.append(f"❌ 缺少模块覆盖：{mod_id} ({IOM_MODULES[mod_id]['name']})")
    
    # 检查每个模块的问题数量
    for mod_id, branch in tree["branches"].items():
        issue_count = len(branch["issues"])
        if issue_count == 0:
            issues.append(f"⚠️  {mod_id} 模块无具体问题项")
        elif issue_count < 2:
            issues.append(f"⚠️  {mod_id} 模块问题项较少 (建议≥2 个)")
        
        # 检查关键词匹配
        module_keywords = IOM_MODULES[mod_id]["keywords"]
        matched_keywords = []
        for issue in branch["issues"]:
            for kw in module_keywords:
                if kw.lower() in issue.lower():
                    matched_keywords.append(kw)
        
        if not matched_keywords:
            issues.append(f"⚠️  {mod_id} 模块问题未包含典型关键词")
    
    # 检查互斥性 (简化：检查是否有重复问题)
    all_issues = []
    for branch in tree["branches"].values():
        all_issues.extend(branch["issues"])
    
    duplicates = [i for i in all_issues if all_issues.count(i) > 1]
    if duplicates:
        issues.append(f"⚠️  发现重复问题项：{set(duplicates)}")
    
    return len(issues) == 0, issues


def generate_report(tree: dict, passed: bool, issues: list[str]) -> str:
    """生成 MECE 检查报告"""
    
    lines = [
        "# MECE Check Report",
        "",
        f"**检查结果**: {'✅ PASS' if passed else '❌ FAIL'}",
        "",
        "## 模块覆盖情况",
        ""
    ]
    
    for mod_id, module_info in IOM_MODULES.items():
        if mod_id in tree["branches"]:
            issue_count = len(tree["branches"][mod_id]["issues"])
            lines.append(f"- ✅ **{mod_id} {module_info['name']}**: {issue_count} 个问题项")
        else:
            lines.append(f"- ❌ **{mod_id} {module_info['name']}**: 未覆盖")
    
    lines.extend([
        "",
        "## 检查发现的问题",
        ""
    ])
    
    if issues:
        for issue in issues:
            lines.append(f"{issue}")
    else:
        lines.append("✅ 未发现明显问题")
    
    lines.extend([
        "",
        "## 建议",
        ""
    ])
    
    if not passed:
        lines.append("请根据上述问题补充或调整 Issue Tree，确保:")
        lines.append("1. 四个模块均有覆盖")
        lines.append("2. 每个模块有足够的问题项支撑")
        lines.append("3. 问题项之间相互独立、完全穷尽 (MECE)")
    else:
        lines.append("✅ Issue Tree 结构良好，可进入下一阶段")
    
    lines.append("")
    
    return "\n".join(lines)


def run_check(input_file: str):
    """执行 MECE 检查"""
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ 输入文件不存在：{input_file}")
        return False
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 解析 Issue Tree
    tree = parse_issue_tree(content)
    
    if not tree["branches"]:
        print("⚠️  未解析到任何模块分支")
        print("   请确保 Issue Tree 使用 ## M1: xxx 格式定义模块")
        return False
    
    print(f"✓ 解析到 {len(tree['branches'])} 个模块分支")
    
    # 执行 MECE 检查
    passed, issues = check_mece_coverage(tree)
    
    # 生成报告
    report = generate_report(tree, passed, issues)
    
    # 输出报告
    output_file = input_path.parent / "mece_check_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n{'='*50}")
    if passed:
        print("✅ MECE 检查通过 (PASS)")
    else:
        print("❌ MECE 检查未通过 (FAIL)")
        print(f"\n问题列表:")
        for issue in issues:
            print(f"  {issue}")
    
    print(f"\n详细报告：{output_file}")
    
    return passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Issue Tree MECE 检查")
    parser.add_argument("--input", type=str, required=True, help="Issue Tree 文件")
    args = parser.parse_args()
    
    success = run_check(args.input)
    exit(0 if success else 1)
