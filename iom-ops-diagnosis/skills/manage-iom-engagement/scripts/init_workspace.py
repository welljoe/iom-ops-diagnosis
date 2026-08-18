#!/usr/bin/env python3
"""
init_workspace.py - 初始化 IOM 诊断项目工作空间

用法:
    python init_workspace.py --project-name <project_name>
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path


def init_workspace(project_name: str):
    """初始化项目工作空间"""
    
    # 获取项目根目录 (相对于脚本位置：skills/manage-iom-engagement/scripts)
    # 向上三级回到项目根目录
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    state_dir = base_dir / "state"
    outputs_dir = base_dir / "outputs"
    
    # 创建目录 (使用 parents=True 确保父目录存在)
    state_dir.mkdir(exist_ok=True)
    (outputs_dir / "pages").mkdir(parents=True, exist_ok=True)
    (outputs_dir / "decks").mkdir(parents=True, exist_ok=True)
    (outputs_dir / "review").mkdir(parents=True, exist_ok=True)
    
    # 初始化 project_state.json
    project_state = {
        "project_name": project_name,
        "created_at": datetime.now().isoformat(),
        "current_gate": "G0",
        "gate_status": {
            "G0": "pending",
            "G1": "not_started",
            "G2": "not_started",
            "G3": "not_started",
            "G4": "not_started",
            "G5": "not_started"
        },
        "storyline_version": "v0.1",
        "vf_pages_count": 0
    }
    
    with open(state_dir / "project_state.json", "w", encoding="utf-8") as f:
        json.dump(project_state, f, indent=2, ensure_ascii=False)
    
    # 初始化 storyline.md
    storyline_content = f"""# Storyline Ledger - {project_name}

## 版本历史

| 版本 | 时间 | 变更描述 | 触发证据 |
|------|------|----------|----------|
| v0.1 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | 初始 Storyline | - |

## 当前 Storyline

待界定 Governing Question...
"""
    
    with open(state_dir / "storyline.md", "w", encoding="utf-8") as f:
        f.write(storyline_content)
    
    # 初始化 evidence_register.md
    evidence_register = """# Evidence Register

| EV-ID | 来源 | 分级 | 支撑假设 | 时间戳 |
|-------|------|------|----------|--------|
| - | - | - | - | - |

**证据分级说明:**
- A: 客户系统统计数据
- B: 多源交叉访谈
- C: 单源或外部对标
- D: 假设待补证
"""
    
    with open(state_dir / "evidence_register.md", "w", encoding="utf-8") as f:
        f.write(evidence_register)
    
    # 初始化 page_register.md
    page_register = """# Page Register

| PG-ID | 章节 | 状态 | VF 批复原文引用 |
|-------|------|------|-----------------|
| - | - | - | - |

**页面状态说明:**
- draft: 初始草稿
- confirmed: 已确认，等待 VF
- VF: 已冻结 (Verified & Frozen)
"""
    
    with open(state_dir / "page_register.md", "w", encoding="utf-8") as f:
        f.write(page_register)
    
    # 初始化 gate_log.md
    gate_log = f"""# Gate Log - {project_name}

| Gate | 时间 | 结果 | 缺失项 | 操作者 |
|------|------|------|--------|--------|
| G0 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | pending | - | system |

**阶段门说明:**
- G0: 界定 - Governing Question + 章程量化目标获用户确认
- G1: 分解 - Issue Tree 通过 MECE 检查；假设矩阵覆盖四模块
- G2: 证据 - 证据台账无 D 级关键证据
- G3: 综合 - 逻辑审核 PASS；Finding→Insight→Implication 链完整
- G4: 页面 - 章节 Review 通过；用户对页面显式批复 VF
- G5: 交付 - deck 仅含 VF 页；review pack 含全链路留痕
"""
    
    with open(state_dir / "gate_log.md", "w", encoding="utf-8") as f:
        f.write(gate_log)
    
    print(f"✓ 项目工作空间初始化完成：{project_name}")
    print(f"  - State directory: {state_dir}")
    print(f"  - Outputs directory: {outputs_dir}")
    print(f"  - 当前阶段门：G0 (pending)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化 IOM 诊断项目工作空间")
    parser.add_argument("--project-name", required=True, help="项目名称")
    args = parser.parse_args()
    
    init_workspace(args.project_name)
