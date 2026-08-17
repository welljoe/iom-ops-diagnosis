#!/usr/bin/env python3
"""
S5: Generate IOM Visuals - 单页可视化脚本

读取 confirmed 状态的页面内容，渲染为 MBB 风格单页视觉稿。
治理强制：仅当 page_register 中状态为 confirmed 时才允许渲染。
"""

import argparse
import os
import re
from datetime import datetime
from typing import Dict, Optional


# ============================================================================
# 页面模板库
# ============================================================================

PAGE_TEMPLATES = {
    'executive_summary': '''# {page_title}

**页码**: {page_id} | **章节**: 高管摘要 | **状态**: {status}

---

## 核心 Finding
{finding}

## 关键 Insight
{insight}

## 行动 Implication
{implication}

---

*生成时间：{timestamp}*
''',
    
    'vsm_current': '''# {page_title}

**页码**: {page_id} | **章节**: 现状分析 | **状态**: {status}

---

## 价值流图 (Current State)

### 流程概览
{process_flow}

### 关键指标
| 指标 | 当前值 | 行业基准 | 差距 |
|------|--------|----------|------|
| 前置时间 (Lead Time) | {lead_time} | - | - |
| 制造周期效率 (MCE) | {mce} | >30% | {mce_gap} |
| 在制品库存 (WIP) | {wip} | - | - |

### 主要浪费点
{waste_points}

---

*生成时间：{timestamp}*
''',
    
    'matrix_page': '''# {page_title}

**页码**: {page_id} | **章节**: {chapter} | **状态**: {status}

---

## 矩阵分析

| | 高影响/高价值 | 低影响/高价值 |
|---|---------------|---------------|
| **高可行性** | {quadrant_1} | {quadrant_2} |
| **低可行性** | {quadrant_3} | {quadrant_4} |

### 优先行动项
{priority_actions}

---

*生成时间：{timestamp}*
''',
    
    'roadmap_page': '''# {page_title}

**页码**: {page_id} | **章节**: 实施规划 | **状态**: {status}

---

## 百日计划路线图

### 阶段一：诊断共识 (W1-2)
- {phase1_item1}
- {phase1_item2}

### 阶段二：灯塔试点 (W3-6)
- {phase2_item1}
- {phase2_item2}

### 阶段三：速赢验证 (W7-10)
- {phase3_item1}
- {phase3_item2}

### 阶段四：推广固化 (W11-16)
- {phase4_item1}
- {phase4_item2}

### 关键里程碑
| 里程碑 | 目标日期 | Owner | 依赖 |
|--------|----------|-------|------|
{milestones}

---

*生成时间：{timestamp}*
''',
    
    'kpi_page': '''# {page_title}

**页码**: {page_id} | **章节**: 绩效分析 | **状态**: {status}

---

## KPI 仪表盘

### OTIF (On-Time In-Full)
- 当前值：**{otif_current}%**
- 目标值：{otif_target}%
- 差距：{otif_gap}pp

### 库存周转率
- 当前值：**{turnover_current}x**
- 目标值：{turnover_target}x
- 改善空间：{turnover_upside}%

### 人均产值
- 当前值：**{productivity_current}**
- 目标值：{productivity_target}
- 行业对标：{productivity_benchmark}

### 趋势分析
{trend_analysis}

---

*生成时间：{timestamp}*
'''
}


# ============================================================================
# 台账解析
# ============================================================================

def parse_page_register(file_path: str) -> Dict[str, Dict]:
    """解析页面注册台账"""
    
    pages = {}
    
    if not os.path.exists(file_path):
        print(f"⚠️  警告：页面台账文件不存在：{file_path}")
        return pages
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试解析 Markdown 表格格式
    # 期望格式：PG-ID | 章节 | 状态 (draft/confirmed/VF) | VF 批复原文引用
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            continue
        
        # 跳过表头分隔线
        if re.match(r'^[\s|-]+$', line):
            continue
        
        # 跳过表头
        if 'PG-ID' in line and '章节' in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        
        if len(parts) >= 3:
            pg_id = parts[0].strip()
            if not pg_id.startswith('PG-'):
                continue
            
            pages[pg_id] = {
                'pg_id': pg_id,
                'chapter': parts[1] if len(parts) > 1 else '',
                'status': parts[2] if len(parts) > 2 else 'draft',
                'vf_comment': parts[3] if len(parts) > 3 else ''
            }
    
    return pages


def load_page_content(content_file: Optional[str], page_id: str) -> Dict:
    """加载页面内容"""
    
    content = {
        'page_title': f'页面 {page_id}',
        'finding': '',
        'insight': '',
        'implication': '',
        'raw_content': ''
    }
    
    if content_file and os.path.exists(content_file):
        with open(content_file, 'r', encoding='utf-8') as f:
            raw = f.read()
        content['raw_content'] = raw
        
        # 尝试提取结构化内容
        finding_match = re.search(r'(?:Finding|发现)[:：\s]*(.+?)(?=Insight|洞察|$)', raw, re.DOTALL | re.IGNORECASE)
        if finding_match:
            content['finding'] = finding_match.group(1).strip()
        
        insight_match = re.search(r'(?:Insight|洞察)[:：\s]*(.+?)(?=Implication|行动|$)', raw, re.DOTALL | re.IGNORECASE)
        if insight_match:
            content['insight'] = insight_match.group(1).strip()
        
        implication_match = re.search(r'(?:Implication|行动|建议)[:：\s]*(.+?)$', raw, re.DOTALL | re.IGNORECASE)
        if implication_match:
            content['implication'] = implication_match.group(1).strip()
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', raw, re.MULTILINE)
        if title_match:
            content['page_title'] = title_match.group(1).strip()
    
    elif not content_file:
        # 尝试从默认位置读取
        default_paths = [
            f'outputs/pages/{page_id}.md',
            f'state/confirmed_content/{page_id}.md',
            f'state/pages/{page_id}.md'
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return load_page_content(path, page_id)
    
    return content


# ============================================================================
# 渲染逻辑
# ============================================================================

class PageRenderer:
    """页面渲染器"""
    
    def __init__(self, page_register: Dict[str, Dict]):
        self.page_register = page_register
    
    def render(self, page_id: str, page_type: str, content: Dict, output_dir: str) -> Optional[str]:
        """渲染单个页面"""
        
        # 检查页面状态
        page_info = self.page_register.get(page_id, {'status': 'unknown'})
        status = page_info.get('status', 'draft')
        
        if status == 'draft':
            print(f"❌ 错误：页面 {page_id} 状态为 draft，无法渲染")
            print("   请先将页面状态更新为 confirmed（用户确认内容）")
            return None
        
        if status == 'VF':
            print(f"⚠️  警告：页面 {page_id} 已 VF 冻结")
            print("   如需修改，请先撤销 VF 状态")
            # VF 页面仍可渲染，但需要警告
        
        # 获取模板
        template = PAGE_TEMPLATES.get(page_type, PAGE_TEMPLATES['matrix_page'])
        
        # 填充模板
        render_params = {
            'page_id': page_id,
            'page_title': content.get('page_title', f'页面 {page_id}'),
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'finding': content.get('finding', '*待补充*'),
            'insight': content.get('insight', '*待补充*'),
            'implication': content.get('implication', '*待补充*'),
            'chapter': page_info.get('chapter', '未分类'),
            # VSM 参数
            'process_flow': content.get('process_flow', '*待补充流程图*'),
            'lead_time': content.get('lead_time', '-'),
            'mce': content.get('mce', '-'),
            'mce_gap': content.get('mce_gap', '-'),
            'wip': content.get('wip', '-'),
            'waste_points': content.get('waste_points', '*待补充*'),
            # 矩阵参数
            'quadrant_1': content.get('quadrant_1', '*待补充*'),
            'quadrant_2': content.get('quadrant_2', '*待补充*'),
            'quadrant_3': content.get('quadrant_3', '*待补充*'),
            'quadrant_4': content.get('quadrant_4', '*待补充*'),
            'priority_actions': content.get('priority_actions', '*待补充*'),
            # Roadmap 参数
            'phase1_item1': content.get('phase1_item1', '*待补充*'),
            'phase1_item2': content.get('phase1_item2', ''),
            'phase2_item1': content.get('phase2_item1', '*待补充*'),
            'phase2_item2': content.get('phase2_item2', ''),
            'phase3_item1': content.get('phase3_item1', '*待补充*'),
            'phase3_item2': content.get('phase3_item2', ''),
            'phase4_item1': content.get('phase4_item1', '*待补充*'),
            'phase4_item2': content.get('phase4_item2', ''),
            'milestones': content.get('milestones', '*待补充*'),
            # KPI 参数
            'otif_current': content.get('otif_current', '-'),
            'otif_target': content.get('otif_target', '-'),
            'otif_gap': content.get('otif_gap', '-'),
            'turnover_current': content.get('turnover_current', '-'),
            'turnover_target': content.get('turnover_target', '-'),
            'turnover_upside': content.get('turnover_upside', '-'),
            'productivity_current': content.get('productivity_current', '-'),
            'productivity_target': content.get('productivity_target', '-'),
            'productivity_benchmark': content.get('productivity_benchmark', '-'),
            'trend_analysis': content.get('trend_analysis', '*待补充*'),
        }
        
        rendered = template.format(**render_params)
        
        # 写入文件
        output_filename = f"{page_id}_visual.md"
        output_path = os.path.join(output_dir, output_filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)
        
        return output_path


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='S5: Generate IOM Visuals - 单页可视化渲染器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --page-id PG-03 --page-type vsm_current
  %(prog)s --page-id PG-05 --content-file state/confirmed_content/PG-05.md --page-type matrix_page
        """
    )
    
    parser.add_argument(
        '--page-id', '-p',
        required=True,
        help='页面 ID（如 PG-01, PG-02）'
    )
    
    parser.add_argument(
        '--content-file', '-c',
        default=None,
        help='可选：页面内容文件路径'
    )
    
    parser.add_argument(
        '--page-type', '-t',
        default='matrix_page',
        choices=list(PAGE_TEMPLATES.keys()),
        help='页面类型（默认：matrix_page）'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='outputs/pages/',
        help='输出目录（默认：outputs/pages/）'
    )
    
    parser.add_argument(
        '--page-register', '-r',
        default='state/page_register.md',
        help='页面台账文件路径（默认：state/page_register.md）'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("S5: Generate IOM Visuals - 单页可视化渲染器")
    print("=" * 60)
    
    # 加载台账
    print("\n[1/4] 加载页面台账...")
    page_register = parse_page_register(args.page_register)
    print(f"   ✓ 台账条目数：{len(page_register)}")
    
    if args.page_id not in page_register:
        print(f"   ⚠️  警告：页面 {args.page_id} 未在台账中注册")
        print("      将按 draft 状态处理，渲染可能被拒绝")
    
    # 加载内容
    print("\n[2/4] 加载页面内容...")
    content = load_page_content(args.content_file, args.page_id)
    
    if content['raw_content']:
        print(f"   ✓ 内容文件：{args.content_file or '默认位置'}")
    else:
        print(f"   ⚠️  警告：未找到页面内容，将使用占位符")
    
    # 创建渲染器
    print("\n[3/4] 初始化渲染器...")
    renderer = PageRenderer(page_register)
    
    # 执行渲染
    print("\n[4/4] 渲染页面...")
    print(f"   页面 ID: {args.page_id}")
    print(f"   页面类型：{args.page_type}")
    
    output_path = renderer.render(args.page_id, args.page_type, content, args.output_dir)
    
    if output_path:
        print(f"\n✅ 渲染完成！")
        print(f"   输出文件：{output_path}")
        print(f"\n下一步:")
        print(f"  1. 审阅渲染结果 {output_path}")
        print(f"  2. 如需修改，请更新内容后重新渲染")
        print(f"  3. 确认无误后，提交用户进行 VF 授权")
    else:
        print(f"\n❌ 渲染失败，请检查页面状态")
    
    print("\n" + "=" * 60)
    
    return 0 if output_path else 1


if __name__ == '__main__':
    exit(main())
