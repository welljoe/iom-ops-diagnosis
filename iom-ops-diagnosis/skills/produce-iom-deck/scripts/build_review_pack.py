#!/usr/bin/env python3
"""
S6: Produce IOM Deck - 交付生产脚本（审阅包生成器）

生成完整的审阅包文档，包含执行摘要、Storyline、证据台账摘要、决策日志等。
治理强制：必须包含完整的证据链追溯和用户 VF 批复原文。
"""

import argparse
import os
import re
from datetime import datetime
from typing import Dict, List


# ============================================================================
# 台账解析函数
# ============================================================================

def parse_markdown_table(file_path: str) -> List[Dict]:
    """解析 Markdown 表格文件"""
    
    if not os.path.exists(file_path):
        return []
    
    records = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    headers = None
    
    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            continue
        
        # 跳过表头分隔线
        if re.match(r'^[\s|-]+$', line):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        
        # 检测表头
        if headers is None:
            if any(kw in line for kw in ['PG-ID', 'EV-ID', 'Gate', '版本']):
                headers = parts
            continue
        
        if len(parts) >= len(headers):
            record = {}
            for i, header in enumerate(headers):
                record[header.strip()] = parts[i] if i < len(parts) else ''
            records.append(record)
    
    return records


def load_file_content(file_path: str) -> str:
    """加载文件内容"""
    
    if not os.path.exists(file_path):
        return ""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# ============================================================================
# 审阅包生成
# ============================================================================

class ReviewPackBuilder:
    """审阅包构建器"""
    
    def __init__(self, state_dir: str):
        self.state_dir = state_dir
        self.page_register = []
        self.evidence_register = []
        self.gate_log = []
        self.storyline = ""
    
    def load_state_files(self):
        """加载 State 目录下的所有台账文件"""
        
        print("  加载台账文件...")
        
        # 加载页面台账
        page_reg_path = os.path.join(self.state_dir, 'page_register.md')
        self.page_register = parse_markdown_table(page_reg_path)
        print(f"    ✓ page_register: {len(self.page_register)} 页")
        
        # 加载证据台账
        ev_reg_path = os.path.join(self.state_dir, 'evidence_register.md')
        self.evidence_register = parse_markdown_table(ev_reg_path)
        print(f"    ✓ evidence_register: {len(self.evidence_register)} 条证据")
        
        # 加载 Gate 日志
        gate_log_path = os.path.join(self.state_dir, 'gate_log.md')
        self.gate_log = parse_markdown_table(gate_log_path)
        print(f"    ✓ gate_log: {len(self.gate_log)} 条记录")
        
        # 加载 Storyline
        storyline_path = os.path.join(self.state_dir, 'storyline.md')
        self.storyline = load_file_content(storyline_path)
        if self.storyline:
            print(f"    ✓ storyline: {len(self.storyline)} 字符")
    
    def generate_executive_summary(self) -> str:
        """生成执行摘要"""
        
        vf_pages = [p for p in self.page_register if p.get('状态', '').strip() == 'VF']
        total_pages = len(self.page_register)
        completion_rate = len(vf_pages)/total_pages*100 if total_pages > 0 else 0
        
        summary = f"""# 执行摘要 (Executive Summary)

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**项目状态**: {'✅ G5 交付完成' if len(vf_pages) > 0 else '⚠️ 进行中'}

---

## 项目目标达成情况

*根据 Storyline 版本与 VF 页面数量评估*

- **VF 授权页面数**: {len(vf_pages)} 页
- **总页面数**: {total_pages} 页
- **完成率**: {completion_rate:.1f}%

## 核心建议摘要

{self._extract_key_insights()}

## 关键财务影响量化

{self._extract_financial_impact()}

---

*本摘要由 `build_review_pack.py` 自动生成*
"""
        
        return summary
    
    def _extract_key_insights(self) -> str:
        """从 Storyline 中提取关键 Insight"""
        
        if not self.storyline:
            return "*Storyline 内容为空*"
        
        # 尝试提取 Insight
        insight_matches = re.findall(
            r'(?:Insight|洞察)[:：\s]*(.+?)(?=Implication|行动|$)',
            self.storyline,
            re.DOTALL | re.IGNORECASE
        )
        
        if insight_matches:
            insights = "• " + "\n• ".join([m.strip()[:200] for m in insight_matches[:3]])
            return insights
        else:
            return "*未检测到结构化的 Insight，请参见完整 Storyline*"
    
    def _extract_financial_impact(self) -> str:
        """从 Storyline 中提取财务影响"""
        
        if not self.storyline:
            return "*Storyline 内容为空*"
        
        financial_keywords = ['OTIF', '周转', '人均产值', '利润', '成本', '%', '+', '-']
        
        # 简单提取包含财务关键词的句子
        sentences = re.split(r'[.!?。！？]', self.storyline)
        financial_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(kw in sentence for kw in financial_keywords):
                financial_sentences.append(sentence[:150])
        
        if financial_sentences:
            return "• " + "\n• ".join(financial_sentences[:3])
        else:
            return "*未在 Storyline 中检测到明显的财务影响量化表述*"
    
    def generate_storyline_section(self) -> str:
        """生成 Storyline 章节"""
        
        section = """# 完整 Storyline

---

## 版本历史

*见 state/storyline.md 完整版本*

"""
        
        if self.storyline:
            section += self.storyline
        else:
            section += "*Storyline 内容为空，请补充*"
        
        section += "\n\n---\n\n"
        
        return section
    
    def generate_evidence_summary(self) -> str:
        """生成证据台账摘要"""
        
        # 按证据等级统计
        grade_counts = {}
        for ev in self.evidence_register:
            grade = ev.get('分级', 'D').strip()
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # A/B 级证据清单
        ab_evidences = [ev for ev in self.evidence_register 
                        if ev.get('分级', 'D').strip() in ['A', 'B']]
        
        summary = f"""# 证据台账摘要 (Evidence Summary)

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 证据分级统计

| 等级 | 数量 | 定义 |
|------|------|------|
| A | {grade_counts.get('A', 0)} | 客户系统统计数据 |
| B | {grade_counts.get('B', 0)} | 多源交叉访谈 |
| C | {grade_counts.get('C', 0)} | 单源或外部对标 |
| D | {grade_counts.get('D', 0)} | 假设待补证 |
| **总计** | **{len(self.evidence_register)}** | - |

## A/B 级证据清单

"""
        
        if ab_evidences:
            summary += "| EV-ID | 来源 | 分级 | 支撑假设 |\n"
            summary += "|-------|------|------|----------|\n"
            
            for ev in ab_evidences[:10]:  # 最多显示 10 条
                summary += f"| {ev.get('EV-ID', '-')} | {ev.get('来源', '-')} | {ev.get('分级', '-')} | {ev.get('支撑假设', '-')} |\n"
            
            if len(ab_evidences) > 10:
                summary += f"\n*共 {len(ab_evidences)} 条，此处显示前 10 条*\n"
        else:
            summary += "*暂无 A/B 级证据，请补充高质量证据*\n"
        
        summary += """
## 未决假设与风险

"""
        
        # D 级证据（待补证假设）
        d_evidences = [ev for ev in self.evidence_register 
                       if ev.get('分级', 'D').strip() == 'D']
        
        if d_evidences:
            summary += "以下假设尚待进一步验证：\n\n"
            for ev in d_evidences:
                summary += f"- **{ev.get('EV-ID', 'Unknown')}**: {ev.get('支撑假设', 'N/A')}\n"
        else:
            summary += "*无未决假设，所有假设已完成验证*\n"
        
        summary += "\n---\n\n"
        
        return summary
    
    def generate_decision_log(self) -> str:
        """生成决策日志"""
        
        log = f"""# 决策日志 (Decision Log)

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Gate 通过记录

"""
        
        if self.gate_log:
            log += "| Gate | 时间 | 状态 | 缺失项 | 操作者 |\n"
            log += "|------|------|------|--------|--------|\n"
            
            for gate in self.gate_log:
                log += f"| {gate.get('Gate', '-')} | {gate.get('时间', '-')} | {gate.get('PASS/FAIL', '-')} | {gate.get('缺失项', '-')} | {gate.get('操作者', '-')} |\n"
        else:
            log += "*暂无 Gate 记录*\n"
        
        log += """
## 方案取舍记录

*根据项目实际情况补充关键决策点*

### 决策点 1: [决策主题]
- **选项 A**: ...
- **选项 B**: ...
- **最终选择**: ...
- **决策依据**: ...

## 用户 VF 批复原文引用

"""
        
        # 从 page_register 中提取 VF 批复
        vf_pages_with_comments = [p for p in self.page_register 
                                   if p.get('状态', '').strip() == 'VF' and p.get('VF 批复原文引用', '')]
        
        if vf_pages_with_comments:
            for page in vf_pages_with_comments[:5]:  # 最多显示 5 条
                log += f"**{page.get('PG-ID', 'Unknown')}** ({page.get('章节', 'N/A')}):\n"
                log += f"> {page.get('VF 批复原文引用', 'N/A')}\n\n"
        else:
            log += "*暂无 VF 批复记录*\n"
        
        log += "\n---\n\n"
        
        return log
    
    def generate_roadmap_section(self) -> str:
        """实施路线图章节"""
        
        roadmap = """# 实施路线图 (Implementation Roadmap)

---

## 百日计划里程碑

| 阶段 | 时间窗口 | 关键里程碑 | Owner |
|------|----------|------------|-------|
| 诊断共识 | W1-2 | VSM 基线 + 章程签核 | 项目组 |
| 灯塔试点 | W3-6 | 首条柔性 Cell+ 齐套控制塔 | 生产总监 |
| 速赢验证 | W7-10 | 齐套≥95%、换线−50%、OTIF≥98% | 运营 VP |
| 推广固化 | W11-16 | SOP+ 技能矩阵 + 分层日会 | CEO |

## 速赢项标识

- ✅ **齐套率提升**: T-3 齐套规则 → 减少车间等待
- ✅ **换线时间降低**: SMED 快速换模 → 小单边际成本下降
- ✅ **OTIF 改善**: 订单围栏机制 → 紧急插单减少

---

*本路线图基于 IOM 标准百日计划模板，具体 Owner 需与客户确认*

"""
        
        return roadmap
    
    def build_full_pack(self) -> str:
        """构建完整审阅包"""
        
        pack = f"""# IOM 诊断项目审阅包 (Review Pack)

**项目名称**: iom-ops-diagnosis  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**文档版本**: v1.0

---

"""
        
        pack += self.generate_executive_summary()
        pack += self.generate_storyline_section()
        pack += self.generate_evidence_summary()
        pack += self.generate_decision_log()
        pack += self.generate_roadmap_section()
        
        pack += """---

## 附录：全链路留痕索引

| 台账类型 | 文件路径 | 说明 |
|----------|----------|------|
| 页面台账 | state/page_register.md | 所有页面状态追踪 |
| 证据台账 | state/evidence_register.md | 证据分级与关联 |
| Gate 日志 | state/gate_log.md | 阶段门通过记录 |
| Storyline | state/storyline.md | 动态推理主线 |

---

*本审阅包由 `build_review_pack.py` 自动生成，包含项目全链路留痕*
"""
        
        return pack


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='S6: Produce IOM Deck - 审阅包生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --state-dir state/ --output-dir outputs/review/
        """
    )
    
    parser.add_argument(
        '--state-dir', '-s',
        default='state/',
        help='State 目录路径（默认：state/）'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='outputs/review/',
        help='输出目录（默认：outputs/review/）'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("S6: Produce IOM Deck - 审阅包生成器")
    print("=" * 60)
    
    # 创建审阅包构建器
    print("\n[1/3] 初始化审阅包构建器...")
    builder = ReviewPackBuilder(args.state_dir)
    
    # 加载 State 文件
    print("\n[2/3] 加载 State 文件...")
    builder.load_state_files()
    
    # 生成审阅包
    print("\n[3/3] 生成审阅包...")
    
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成完整审阅包
    full_pack = builder.build_full_pack()
    pack_path = os.path.join(output_dir, 'review_pack.md')
    
    with open(pack_path, 'w', encoding='utf-8') as f:
        f.write(full_pack)
    
    print(f"   ✓ 完整审阅包：{pack_path}")
    
    # 单独生成证据摘要
    evidence_summary = builder.generate_evidence_summary()
    evidence_path = os.path.join(output_dir, 'evidence_summary.md')
    
    with open(evidence_path, 'w', encoding='utf-8') as f:
        f.write(evidence_summary)
    
    print(f"   ✓ 证据摘要：{evidence_path}")
    
    # 单独生成决策日志
    decision_log = builder.generate_decision_log()
    decision_path = os.path.join(output_dir, 'decision_log.md')
    
    with open(decision_path, 'w', encoding='utf-8') as f:
        f.write(decision_log)
    
    print(f"   ✓ 决策日志：{decision_path}")
    
    print("\n" + "=" * 60)
    print("✅ 审阅包生成完成！")
    print("=" * 60)
    print(f"\n输出文件:")
    print(f"  - review_pack.md: 完整审阅包")
    print(f"  - evidence_summary.md: 证据台账摘要")
    print(f"  - decision_log.md: 决策日志")
    print(f"\n下一步:")
    print(f"  1. 审阅 review_pack.md 确认内容完整")
    print(f"  2. 可将 Markdown 转换为 PDF 交付客户")
    print(f"  3. 配合 PPT deck 一起提交 G5 Gate 检查")
    
    return 0


if __name__ == '__main__':
    exit(main())
