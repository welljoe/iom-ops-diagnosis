#!/usr/bin/env python3
"""
gate_check.py - 执行阶段门检查

用法:
    python gate_check.py --gate G0
    python gate_check.py --all
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def load_project_state():
    """加载项目状态"""
    state_dir = Path(__file__).resolve().parent.parent.parent.parent / "state"
    state_file = state_dir / "project_state.json"
    
    if not state_file.exists():
        raise FileNotFoundError("项目未初始化，请先运行 init_workspace.py")
    
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def check_gate_g0() -> tuple[bool, list[str]]:
    """
    检查 G0 阶段门：界定
    准入条件：Governing Question + 章程量化目标获用户确认
    v1.1 补丁：增加 KPI 完整性检查（客户投诉率 -80%、人均产值 +20%）
    """
    issues = []
    
    # 获取项目根目录
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    
    # 检查项目章程是否存在
    templates_dir = base_dir / "skills" / "manage-iom-engagement" / "templates"
    charter_file = templates_dir / "project_charter.md"
    
    # 注意：实际项目中章程应由用户确认，这里仅检查文件是否存在
    # 在真实场景中，应检查用户确认标记
    if not charter_file.exists():
        issues.append("项目章程 (project_charter.md) 尚未创建")
    
    # 检查 storyline 是否已初始化
    state_dir = base_dir / "state"
    storyline_file = state_dir / "storyline.md"
    
    if not storyline_file.exists():
        issues.append("Storyline 尚未初始化")
    else:
        with open(storyline_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "待界定 Governing Question" in content:
                issues.append("Governing Question 尚未界定")
    
    # v1.1 补丁：检查高管汇报页模板中的 KPI 是否已定义
    visuals_templates_dir = base_dir / "skills" / "generate-iom-visuals" / "templates"
    exec_summary_file = visuals_templates_dir / "exec_summary_page.md"
    
    if exec_summary_file.exists():
        with open(exec_summary_file, "r", encoding="utf-8") as f:
            content = f.read()
            # 检查关键 KPI 是否在模板中被明确提及
            if "客户投诉率" not in content or "-80%" not in content:
                issues.append("G0 准入条件缺失：客户投诉率 -80% 目标未定义")
            if "人均产值" not in content or "+20%" not in content:
                issues.append("G0 准入条件缺失：人均产值 +20% 目标未定义")
    else:
        issues.append("高管汇报页模板 (exec_summary_page.md) 尚未创建，无法验证 KPI 完整性")
    
    return len(issues) == 0, issues


def check_gate_g1() -> tuple[bool, list[str]]:
    """
    检查 G1 阶段门：分解
    准入条件：Issue Tree 通过 MECE 检查；假设矩阵覆盖四模块
    """
    issues = []
    
    templates_dir = Path(__file__).parent.parent / "templates"
    
    # 检查 Issue Tree
    issue_tree_file = templates_dir / "issue_tree.md"
    if not issue_tree_file.exists():
        issues.append("Issue Tree 尚未创建")
    
    # 检查假设矩阵
    hypothesis_matrix_file = templates_dir / "hypothesis_matrix.md"
    if not hypothesis_matrix_file.exists():
        issues.append("假设矩阵 (hypothesis_matrix.md) 尚未创建")
    
    return len(issues) == 0, issues


def check_gate_g2() -> tuple[bool, list[str]]:
    """
    检查 G2 阶段门：证据
    准入条件：证据台账无 D 级关键证据；每个假设≥1 条 A/B 级证据或补证计划
    """
    issues = []
    
    state_dir = Path(__file__).parent.parent.parent / "state"
    evidence_register_file = state_dir / "evidence_register.md"
    
    if not evidence_register_file.exists():
        issues.append("证据台账 (evidence_register.md) 尚未创建")
        return len(issues) == 0, issues
    
    # 简单检查：统计证据分级
    with open(evidence_register_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 检查是否有 D 级关键证据（简化检查）
    if "| D |" in content or "|D|" in content:
        issues.append("证据台账中存在 D 级证据（假设待补证），需要补证计划")
    
    return len(issues) == 0, issues


def check_gate_g3() -> tuple[bool, list[str]]:
    """
    检查 G3 阶段门：综合
    准入条件：逻辑审核 PASS；Finding→Insight→Implication 链完整
    """
    issues = []
    
    # 检查逻辑审核报告
    outputs_dir = Path(__file__).parent.parent.parent / "outputs"
    review_dir = outputs_dir / "review"
    
    audit_report = review_dir / "logic_audit_report.md"
    if not audit_report.exists():
        issues.append("逻辑审核报告 (logic_audit_report.md) 尚未创建")
    
    return len(issues) == 0, issues


def check_gate_g4() -> tuple[bool, list[str]]:
    """
    检查 G4 阶段门：页面
    准入条件：章节 Review 通过；用户对页面显式批复 VF
    """
    issues = []
    
    state_dir = Path(__file__).parent.parent.parent / "state"
    page_register_file = state_dir / "page_register.md"
    
    if not page_register_file.exists():
        issues.append("页面台账 (page_register.md) 尚未创建")
        return len(issues) == 0, issues
    
    # 检查是否有 VF 页面
    with open(page_register_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "| VF |" not in content and "|VF|" not in content:
        issues.append("尚无页面获得 VF 授权")
    
    return len(issues) == 0, issues


def check_gate_g5() -> tuple[bool, list[str]]:
    """
    检查 G5 阶段门：交付
    准入条件：deck 仅含 VF 页；review pack 含全链路留痕
    """
    issues = []
    
    outputs_dir = Path(__file__).parent.parent.parent / "outputs"
    decks_dir = outputs_dir / "decks"
    review_dir = outputs_dir / "review"
    
    # 检查是否有交付物
    deck_files = list(decks_dir.glob("*.pptx")) + list(decks_dir.glob("*.md"))
    if not deck_files:
        issues.append("尚未生成交付 deck")
    
    review_pack = review_dir / "review_pack.md"
    if not review_pack.exists():
        issues.append("审阅包 (review_pack.md) 尚未生成")
    
    return len(issues) == 0, issues


def run_gate_check(gate: str) -> bool:
    """执行指定阶段门检查"""
    
    gate_checks = {
        "G0": check_gate_g0,
        "G1": check_gate_g1,
        "G2": check_gate_g2,
        "G3": check_gate_g3,
        "G4": check_gate_g4,
        "G5": check_gate_g5
    }
    
    if gate not in gate_checks:
        print(f"❌ 无效的阶段门：{gate}")
        print("有效的阶段门：G0, G1, G2, G3, G4, G5")
        return False
    
    print(f"\n{'='*50}")
    print(f"执行 {gate} 阶段门检查")
    print(f"{'='*50}\n")
    
    check_func = gate_checks[gate]
    passed, issues = check_func()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if passed:
        print(f"✅ {gate} 阶段门检查通过 (PASS)")
        print(f"   时间：{timestamp}")
    else:
        print(f"❌ {gate} 阶段门检查未通过 (FAIL)")
        print(f"   时间：{timestamp}")
        print(f"\n缺失项:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    # 记录到 gate_log
    log_gate_result(gate, passed, issues, timestamp)
    
    return passed


def log_gate_result(gate: str, passed: bool, issues: list[str], timestamp: str):
    """记录阶段门检查结果到日志"""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    state_dir = base_dir / "state"
    gate_log_file = state_dir / "gate_log.md"
    
    result = "PASS" if passed else "FAIL"
    missing_items = "; ".join(issues) if issues else "-"
    
    # 追加到日志
    with open(gate_log_file, "a", encoding="utf-8") as f:
        f.write(f"| {gate} | {timestamp} | {result} | {missing_items} | system |\n")


def run_all_gates():
    """执行所有阶段门检查"""
    
    print("\n" + "="*60)
    print("执行全部阶段门检查 (G0-G5)")
    print("="*60)
    
    gates = ["G0", "G1", "G2", "G3", "G4", "G5"]
    results = {}
    
    for gate in gates:
        try:
            passed = run_gate_check(gate)
            results[gate] = passed
        except Exception as e:
            print(f"⚠️  {gate} 检查异常：{str(e)}")
            results[gate] = False
    
    print("\n" + "="*60)
    print("检查汇总")
    print("="*60)
    
    for gate, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {gate}: {status}")
    
    # 找出当前可通过的最高阶段门
    max_passed_gate = None
    for gate in gates:
        if results[gate]:
            max_passed_gate = gate
        else:
            break
    
    if max_passed_gate:
        print(f"\n当前可通过的最高阶段门：{max_passed_gate}")
    else:
        print("\n暂无阶段门通过，请从 G0 开始")
    
    return all(results.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="执行阶段门检查")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--gate", type=str, help="指定阶段门 (G0-G5)")
    group.add_argument("--all", action="store_true", help="检查所有阶段门")
    args = parser.parse_args()
    
    try:
        if args.all:
            success = run_all_gates()
        else:
            success = run_gate_check(args.gate.upper())
        
        exit(0 if success else 1)
    except FileNotFoundError as e:
        print(f"❌ 错误：{e}")
        print("请先运行：python scripts/init_workspace.py --project-name <project_name>")
        exit(1)
    except Exception as e:
        print(f"❌ 检查过程出错：{e}")
        exit(1)
