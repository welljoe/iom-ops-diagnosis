#!/usr/bin/env python3
"""
update_register.py - 更新台账记录

用法:
    python update_register.py --type evidence --action add --data '{"ev_id": "EV-001", ...}'
    python update_register.py --type page --action update --pg-id PG-001 --status confirmed
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def load_register(register_type: str):
    """加载指定台账"""
    state_dir = Path(__file__).parent.parent.parent / "state"
    
    register_files = {
        "evidence": state_dir / "evidence_register.md",
        "page": state_dir / "page_register.md",
        "gate_log": state_dir / "gate_log.md",
        "storyline": state_dir / "storyline.md"
    }
    
    if register_type not in register_files:
        raise ValueError(f"无效的台账类型：{register_type}")
    
    return register_files[register_type]


def parse_evidence_register(content: str) -> list[dict]:
    """解析证据台账 Markdown 为列表"""
    lines = content.strip().split('\n')
    entries = []
    
    # 跳过标题和表头
    data_start = False
    for line in lines:
        if line.startswith('| EV-ID'):
            data_start = True
            continue
        if not data_start or line.startswith('|---'):
            continue
        if line.strip() == '' or line.startswith('#'):
            continue
        
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 5 and parts[0] != '-':
            entries.append({
                'ev_id': parts[0],
                'source': parts[1],
                'grade': parts[2],
                'hypothesis': parts[3],
                'timestamp': parts[4]
            })
    
    return entries


def add_evidence_entry(data: dict):
    """添加证据条目"""
    register_file = load_register("evidence")
    
    if not register_file.exists():
        # 创建初始台账
        content = """# Evidence Register

| EV-ID | 来源 | 分级 | 支撑假设 | 时间戳 |
|-------|------|------|----------|--------|
"""
    else:
        with open(register_file, "r", encoding="utf-8") as f:
            content = f.read()
    
    # 生成新条目
    ev_id = data.get('ev_id', f"EV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    source = data.get('source', 'unknown')
    grade = data.get('grade', 'D')
    hypothesis = data.get('hypothesis', '-')
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    new_line = f"| {ev_id} | {source} | {grade} | {hypothesis} | {timestamp} |\n"
    
    # 追加到表格
    if "| - | - | - | - | - |" in content:
        content = content.replace("| - | - | - | - | - |\n", new_line)
    else:
        content += new_line
    
    with open(register_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ 证据条目已添加：{ev_id}")
    return ev_id


def update_page_status(pg_id: str, status: str, vf_comment: str = ""):
    """更新页面状态"""
    register_file = load_register("page")
    
    if not register_file.exists():
        print(f"❌ 页面台账不存在，请先初始化项目")
        return False
    
    with open(register_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 验证状态转换合法性
    valid_transitions = {
        'draft': ['confirmed'],
        'confirmed': ['VF'],
        'VF': []  # VF 后不可修改
    }
    
    # 查找现有条目
    lines = content.split('\n')
    found = False
    new_lines = []
    
    for line in lines:
        if pg_id in line and line.startswith('|'):
            found = True
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 3:
                current_status = parts[2]
                
                # 检查状态转换
                if current_status == 'VF' and status != 'VF':
                    print(f"❌ 错误：页面 {pg_id} 已处于 VF 状态，不可修改 (治理红线)")
                    return False
                
                if current_status in valid_transitions and status not in valid_transitions[current_status]:
                    print(f"⚠️  警告：状态转换 {current_status} → {status} 不符合规范")
                
                # 更新行
                vf_ref = vf_comment if status == 'VF' else (parts[3] if len(parts) > 3 else '-')
                new_line = f"| {pg_id} | {parts[1]} | {status} | {vf_ref} |"
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if not found:
        # 添加新条目
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f"| {pg_id} | unknown | {status} | {vf_comment} |"
        if "| - | - | - | - |" in content:
            new_content = content.replace("| - | - | - | - |", new_entry)
        else:
            new_content = content + "\n" + new_entry
        new_lines = new_content.split('\n')
    
    with open(register_file, "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines))
    
    print(f"✓ 页面 {pg_id} 状态已更新为：{status}")
    return True


def run_update(args):
    """执行台账更新"""
    
    if args.action == "add" and args.type == "evidence":
        if args.data:
            data = json.loads(args.data)
        else:
            data = {}
        add_evidence_entry(data)
    
    elif args.action == "update" and args.type == "page":
        if not args.pg_id:
            print("❌ 错误：--pg-id 参数必填")
            return False
        update_page_status(args.pg_id, args.status, args.vf_comment or "")
    
    else:
        print(f"⚠️  未实现的操作：{args.type} / {args.action}")
        return False
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="更新台账记录")
    parser.add_argument("--type", type=str, required=True, 
                        choices=['evidence', 'page', 'gate_log', 'storyline'],
                        help="台账类型")
    parser.add_argument("--action", type=str, required=True,
                        choices=['add', 'update', 'delete'],
                        help="操作类型")
    parser.add_argument("--data", type=str, help="JSON 格式的数据 (用于 add 操作)")
    parser.add_argument("--pg-id", type=str, help="页面 ID (用于 page 操作)")
    parser.add_argument("--status", type=str, 
                        choices=['draft', 'confirmed', 'VF'],
                        help="页面状态")
    parser.add_argument("--vf-comment", type=str, help="VF 批复注释")
    
    args = parser.parse_args()
    
    try:
        success = run_update(args)
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 更新失败：{e}")
        exit(1)
