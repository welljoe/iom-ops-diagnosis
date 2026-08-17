#!/usr/bin/env python3
"""
S4: Review IOM Logic - 逻辑审核器脚本

对 Storyline 和证据台账进行逻辑审核，生成审核报告与补证计划。
治理强制：关键结论无 A/B 证据时，审核结果自动标记为 FAIL。
"""

import argparse
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# ============================================================================
# 证据分级定义
# ============================================================================

EVIDENCE_GRADES = {
    'A': {'weight': 1.0, 'description': '客户系统统计数据', 'examples': ['ERP 出库记录', 'MES 设备日志']},
    'B': {'weight': 0.8, 'description': '多源交叉访谈', 'examples': ['≥3 人独立陈述一致']},
    'C': {'weight': 0.5, 'description': '单源或外部对标', 'examples': ['单人访谈', '行业报告']},
    'D': {'weight': 0.2, 'description': '假设待补证', 'examples': ['未验证的推测']}
}

MIN_EVIDENCE_FOR_KEY_FINDING = 0.8  # 关键结论最低证据权重（A 级或 2 条 B 级）


# ============================================================================
# 解析函数
# ============================================================================

def parse_evidence_register(file_path: str) -> List[Dict]:
    """解析证据台账文件"""
    
    if not os.path.exists(file_path):
        print(f"⚠️  警告：证据台账文件不存在：{file_path}")
        return []
    
    evidences = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试解析 Markdown 表格格式
    # 期望格式：EV-ID | 来源 | 分级 | 支撑假设 | 时间戳
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            continue
        
        # 跳过表头分隔线
        if re.match(r'^[\s|-]+$', line):
            continue
        
        # 跳过表头
        if 'EV-ID' in line and '来源' in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        
        if len(parts) >= 4:
            ev_id = parts[0].strip()
            if not ev_id.startswith('EV-'):
                continue
            
            evidence = {
                'ev_id': ev_id,
                'source': parts[1] if len(parts) > 1 else '',
                'grade': parts[2] if len(parts) > 2 else 'D',
                'hypothesis': parts[3] if len(parts) > 3 else '',
                'timestamp': parts[4] if len(parts) > 4 else '',
                'weight': EVIDENCE_GRADES.get(parts[2] if len(parts) > 2 else 'D', {}).get('weight', 0.2)
            }
            evidences.append(evidence)
    
    return evidences


def parse_storyline(file_path: str) -> Dict:
    """解析 Storyline 文件，提取 Finding/Insight/Implication 结构"""
    
    if not os.path.exists(file_path):
        print(f"⚠️  警告：Storyline 文件不存在：{file_path}")
        return {'findings': [], 'insights': [], 'implications': [], 'raw_content': ''}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    storyline = {
        'findings': [],
        'insights': [],
        'implications': [],
        'raw_content': content,
        'version': 'unknown'
    }
    
    # 提取版本号
    version_match = re.search(r'版本 [:：]?\s*v?(\d+\.\d+)', content, re.IGNORECASE)
    if version_match:
        storyline['version'] = version_match.group(1)
    
    # 提取 Finding（支持多种标记方式）
    finding_patterns = [
        r'(?:^|\n)\s*[*#-]\s*Finding\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
        r'(?:^|\n)\s*[*#-]\s*\*\*Finding\*\*\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
        r'(?:^|\n)\s*F\d+[:．]\s*(.+?)(?=\n\s*[FI]|\Z)',
    ]
    
    for pattern in finding_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            finding_text = match.strip()
            if finding_text and len(finding_text) > 10:  # 过滤太短的匹配
                storyline['findings'].append({
                    'text': finding_text,
                    'evidence_refs': extract_evidence_refs(finding_text),
                    'has_financial_impact': has_financial_language(finding_text)
                })
    
    # 提取 Insight
    insight_patterns = [
        r'(?:^|\n)\s*[*#-]\s*Insight\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
        r'(?:^|\n)\s*[*#-]\s*\*\*Insight\*\*\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
        r'(?:^|\n)\s*I\d+[:．]\s*(.+?)(?=\n\s*[FI]|\Z)',
    ]
    
    for pattern in insight_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            insight_text = match.strip()
            if insight_text and len(insight_text) > 10:
                storyline['insights'].append({
                    'text': insight_text,
                    'linked_finding': None,  # 需要更复杂的关联逻辑
                    'leads_to_action': has_action_language(insight_text)
                })
    
    # 提取 Implication
    implication_patterns = [
        r'(?:^|\n)\s*[*#-]\s*Implication\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
        r'(?:^|\n)\s*[*#-]\s*\*\*Implication\*\*\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
        r'(?:^|\n)\s*(?:行动 | 建议|Action)\s*[:：]?\s*(.+?)(?=\n\s*[*#-]|\Z)',
    ]
    
    for pattern in implication_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            imp_text = match.strip()
            if imp_text and len(imp_text) > 10:
                storyline['implications'].append({
                    'text': imp_text,
                    'is_actionable': has_action_language(imp_text),
                    'has_owner': has_owner_assignment(imp_text)
                })
    
    # 如果没有找到结构化标记，尝试按段落提取
    if not storyline['findings'] and content.strip():
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 20]
        if paragraphs:
            # 将第一段作为主要 Finding
            storyline['findings'].append({
                'text': paragraphs[0],
                'evidence_refs': extract_evidence_refs(paragraphs[0]),
                'has_financial_impact': has_financial_language(paragraphs[0])
            })
    
    return storyline


def extract_evidence_refs(text: str) -> List[str]:
    """从文本中提取证据引用（如 EV-01, EV-03 等）"""
    refs = re.findall(r'EV-\d+[A-Z]?', text, re.IGNORECASE)
    return list(set(refs))  # 去重


def has_financial_language(text: str) -> bool:
    """检查是否包含财务语言（OTIF、周转、人均产值、利润等）"""
    financial_keywords = [
        'otif', '周转', '库存', '人均产值', '利润', '成本', '现金流',
        'roi', 'npv', 'ebitda', '毛利率', '营运资本', 'ccc',
        '+%', '-%', '改善', '下降', '提升', '释放', '增厚'
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in financial_keywords)


def has_action_language(text: str) -> bool:
    """检查是否包含行动导向语言"""
    action_keywords = [
        '应', '需', '要', '建议', '行动', '实施', '建立', '优化',
        'should', 'must', 'need to', 'action', 'implement', 'establish'
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in action_keywords)


def has_owner_assignment(text: str) -> bool:
    """检查是否有责任人指派"""
    owner_patterns = [
        r'owner\s*[:：]',
        r'责任 [人人]',
        r'负责.*部门',
        r'by\s+\w+',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in owner_patterns)


# ============================================================================
# 审核逻辑
# ============================================================================

class LogicAuditor:
    """逻辑审核器核心类"""
    
    def __init__(self, storyline: Dict, evidences: List[Dict], hypothesis_matrix_path: Optional[str] = None):
        self.storyline = storyline
        self.evidences = evidences
        self.hypothesis_matrix_path = hypothesis_matrix_path
        self.issues = []
        self.warnings = []
        self.pass_count = 0
        self.fail_count = 0
    
    def audit(self) -> Dict:
        """执行完整审核流程"""
        
        print("  [1/4] 审核证据链完整性...")
        self._audit_evidence_chain()
        
        print("  [2/4] 审核 So-What 逻辑链...")
        self._audit_logical_flow()
        
        print("  [3/4] 审核 IOM 特化要求...")
        self._audit_iom_specific()
        
        print("  [4/4] 审核 MECE 原则...")
        self._audit_mece()
        
        # 计算总体结果
        total_checks = self.pass_count + self.fail_count
        pass_rate = self.pass_count / total_checks if total_checks > 0 else 0
        
        overall_result = "PASS" if (self.fail_count == 0 and pass_rate >= 0.8) else "FAIL"
        
        return {
            'result': overall_result,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'pass_rate': pass_rate,
            'issues': self.issues,
            'warnings': self.warnings,
            'evidence_gap_plan': self._generate_evidence_gap_plan()
        }
    
    def _add_issue(self, category: str, severity: str, description: str, suggestion: str, related_item: str = ''):
        """添加审核问题"""
        self.issues.append({
            'category': category,
            'severity': severity,  # CRITICAL, MAJOR, MINOR
            'description': description,
            'suggestion': suggestion,
            'related_item': related_item
        })
        if severity in ['CRITICAL', 'MAJOR']:
            self.fail_count += 1
        else:
            self.pass_count += 1
    
    def _add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def _audit_evidence_chain(self):
        """审核证据链完整性"""
        
        findings = self.storyline.get('findings', [])
        
        if not findings:
            self._add_issue(
                '证据链', 'CRITICAL',
                'Storyline 中未找到任何 Finding',
                '请补充至少一个基于证据的 Finding',
                'storyline'
            )
            return
        
        for i, finding in enumerate(findings, 1):
            ev_refs = finding.get('evidence_refs', [])
            
            if not ev_refs:
                self._add_issue(
                    '证据链', 'CRITICAL',
                    f'Finding #{i} 没有引用任何证据',
                    '请补充证据引用（如 EV-01, EV-02），或标注为"待验证假设"',
                    finding['text'][:50]
                )
                continue
            
            # 检查证据是否存在于台账
            evidence_weights = []
            for ev_ref in ev_refs:
                matching_evidence = [e for e in self.evidences if e['ev_id'].upper() == ev_ref.upper()]
                
                if not matching_evidence:
                    self._add_warning(f'证据引用 {ev_ref} 在台账中未找到，请确认编号正确')
                    continue
                
                evidence_weights.append(matching_evidence[0]['weight'])
            
            # 检查是否有足够的 A/B 级证据
            if evidence_weights:
                max_weight = max(evidence_weights)
                avg_weight = sum(evidence_weights) / len(evidence_weights)
                
                if max_weight < MIN_EVIDENCE_FOR_KEY_FINDING:
                    self._add_issue(
                        '证据链', 'MAJOR',
                        f'Finding #{i} 缺乏 A/B 级证据支撑（最高权重：{max_weight}）',
                        '请补充更高质量的证据（A 级系统数据或 B 级交叉访谈）',
                        finding['text'][:50]
                    )
                else:
                    self.pass_count += 1
            else:
                self._add_issue(
                    '证据链', 'MAJOR',
                    f'Finding #{i} 引用的证据在台账中找不到',
                    '请更新证据台账或修正引用编号',
                    finding['text'][:50]
                )
    
    def _audit_logical_flow(self):
        """审核 So-What 逻辑链"""
        
        findings = self.storyline.get('findings', [])
        insights = self.storyline.get('insights', [])
        implications = self.storyline.get('implications', [])
        
        # 检查 Finding → Insight 推导
        if findings and not insights:
            self._add_issue(
                '逻辑链', 'MAJOR',
                '有 Finding 但缺少 Insight',
                '请补充"So-What"分析：这个 Finding 意味着什么？',
                'storyline structure'
            )
        elif findings and insights:
            self.pass_count += 1
        
        # 检查 Insight → Implication 推导
        if insights and not implications:
            self._add_issue(
                '逻辑链', 'MAJOR',
                '有 Insight 但缺少 Implication/行动建议',
                '请补充"That-So"分析：因此我们应该采取什么行动？',
                'storyline structure'
            )
        elif insights and implications:
            self.pass_count += 1
        
        # 检查 Implication 是否可执行
        for i, imp in enumerate(implications, 1):
            if not imp.get('is_actionable', False):
                self._add_issue(
                    '逻辑链', 'MINOR',
                    f'Implication #{i} 缺乏明确的行动导向',
                    '使用行动性语言（应、需、建议、实施等）重写',
                    imp['text'][:50]
                )
            else:
                self.pass_count += 1
            
            if not imp.get('has_owner', False):
                self._add_warning(f'Implication #{i} 未指定责任人 (Owner)，建议补充')
    
    def _audit_iom_specific(self):
        """审核 IOM 特化要求"""
        
        findings = self.storyline.get('findings', [])
        implications = self.storyline.get('implications', [])
        
        # 检查财务语言
        financial_findings_count = sum(1 for f in findings if f.get('has_financial_impact', False))
        
        if findings and financial_findings_count == 0:
            self._add_issue(
                'IOM 特化', 'MAJOR',
                '所有 Finding 都未折算为财务语言',
                '将发现转化为 OTIF、库存周转、人均产值、利润等财务指标',
                'financial anchoring'
            )
        elif findings:
            ratio = financial_findings_count / len(findings)
            if ratio >= 0.5:
                self.pass_count += 1
            else:
                self._add_issue(
                    'IOM 特化', 'MINOR',
                    f'仅 {ratio*100:.0f}% 的 Finding 包含财务语言',
                    '建议将所有发现都与财务影响挂钩',
                    'financial anchoring'
                )
        else:
            self.pass_count += 1  # 无 Finding 时不扣分
        
        # 检查端到端视角
        e2e_keywords = ['端到端', 'end-to-end', '全链路', 'concept-to-cash', '从...到...', '价值流']
        full_content = self.storyline.get('raw_content', '')
        
        if not any(kw.lower() in full_content.lower() for kw in e2e_keywords):
            self._add_warning('未检测到明显的端到端视角描述，建议补充全价值链分析')
        else:
            self.pass_count += 1
    
    def _audit_mece(self):
        """审核 MECE 原则（简化版）"""
        
        findings = self.storyline.get('findings', [])
        
        if len(findings) <= 1:
            self._add_warning('Finding 数量≤1，无法有效检查 MECE 原则')
            self.pass_count += 1
            return
        
        # 简单检查：多个 Finding 之间是否有明显重复
        finding_texts = [f['text'].lower() for f in findings]
        
        # 计算文本相似度（简化：检查是否有大量共同词汇）
        for i in range(len(finding_texts)):
            for j in range(i + 1, len(finding_texts)):
                words_i = set(finding_texts[i].split())
                words_j = set(finding_texts[j].split())
                
                if len(words_i) > 5 and len(words_j) > 5:
                    overlap = len(words_i & words_j) / min(len(words_i), len(words_j))
                    
                    if overlap > 0.6:  # 60% 以上重叠视为可能不互斥
                        self._add_warning(
                            f'Finding #{i+1} 和 #{j+1} 可能存在内容重叠（相似度：{overlap*100:.0f}%）'
                        )
        
        self.pass_count += 1
    
    def _generate_evidence_gap_plan(self) -> List[Dict]:
        """生成证据缺口补证计划"""
        
        gap_plan = []
        
        for issue in self.issues:
            if issue['category'] == '证据链' and '缺乏' in issue['description']:
                gap_plan.append({
                    'gap_type': 'evidence_missing',
                    'related_finding': issue['related_item'],
                    'required_grade': 'A 或 B',
                    'suggested_source': 'ERP/MES系统数据 或 多源交叉访谈',
                    'priority': 'HIGH' if issue['severity'] == 'CRITICAL' else 'MEDIUM'
                })
        
        return gap_plan


# ============================================================================
# 报告生成
# ============================================================================

def generate_audit_report(audit_result: Dict, output_dir: str) -> str:
    """生成逻辑审核报告"""
    
    result_emoji = '✅' if audit_result['result'] == 'PASS' else '❌'
    
    report_content = f"""# 逻辑审核报告 (Logic Audit Report)

**审核时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审核结果**: {result_emoji} {audit_result['result']}  
**通过率**: {audit_result['pass_rate']*100:.1f}% ({audit_result['pass_count']}/{audit_result['pass_count'] + audit_result['fail_count']})

---

## 一、审核概览

| 维度 | 通过数 | 失败数 | 状态 |
|------|--------|--------|------|
| 证据链完整性 | - | - | {'✅' if all(i['category'] != '证据链' or i['severity'] == 'MINOR' for i in audit_result['issues']) else '❌'} |
| So-What 逻辑链 | - | - | {'✅' if all(i['category'] != '逻辑链' or i['severity'] == 'MINOR' for i in audit_result['issues']) else '❌'} |
| IOM 特化要求 | - | - | {'✅' if all(i['category'] != 'IOM 特化' or i['severity'] == 'MINOR' for i in audit_result['issues']) else '❌'} |
| MECE 原则 | - | - | {'✅' if all(i['category'] != 'MECE' or i['severity'] != 'MAJOR' for i in audit_result['issues']) else '⚠️'} |

---

## 二、问题清单

"""
    
    if not audit_result['issues']:
        report_content += "*恭喜！未发现重大问题。*\n\n"
    else:
        # 按严重程度排序
        severity_order = {'CRITICAL': 0, 'MAJOR': 1, 'MINOR': 2}
        sorted_issues = sorted(audit_result['issues'], key=lambda x: severity_order.get(x['severity'], 3))
        
        for i, issue in enumerate(sorted_issues, 1):
            severity_emoji = {'CRITICAL': '🔴', 'MAJOR': '🟠', 'MINOR': '🟡'}.get(issue['severity'], '⚪')
            
            report_content += f"""### 问题 #{i}: {issue['category']} - {issue['severity']}

- **描述**: {issue['description']}
- **建议**: {issue['suggestion']}
- **相关项**: `{issue['related_item'][:80]}`

"""
    
    report_content += """---

## 三、警告事项

"""
    
    if audit_result['warnings']:
        for warning in audit_result['warnings']:
            report_content += f"- ⚠️  {warning}\n"
    else:
        report_content += "*无警告事项。*\n"
    
    report_content += f"""
---

## 四、下一步行动

"""
    
    if audit_result['result'] == 'PASS':
        report_content += """✅ **审核通过**，可以进入下一阶段：

1. 将 Storyline 状态更新为 `confirmed`
2. 提交 S5 (generate-iom-visuals) 进行页面渲染
3. 准备章节 Review 会议

"""
    else:
        report_content += """❌ **审核未通过**，需要先解决以下问题：

### 必须修复 (CRITICAL/MAJOR)
"""
        critical_issues = [i for i in audit_result['issues'] if i['severity'] in ['CRITICAL', 'MAJOR']]
        for issue in critical_issues:
            report_content += f"- [ ] {issue['description']}\n"
        
        report_content += """
### 建议优化 (MINOR)
"""
        minor_issues = [i for i in audit_result['issues'] if i['severity'] == 'MINOR']
        for issue in minor_issues:
            report_content += f"- [ ] {issue['description']}\n"
        
        report_content += """
**修复后请重新运行本审核脚本**。

"""
    
    report_content += """---

*本报告由 `logic_audit.py` 自动生成，审核标准基于 MBB 问题解决方法论与 IOM 特化要求。*
"""
    
    output_path = os.path.join(output_dir, "logic_audit_report.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return output_path


def generate_evidence_plan(gap_plan: List[Dict], output_dir: str) -> str:
    """生成补证计划"""
    
    plan_content = f"""# 补证计划 (Evidence Gap Plan)

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**缺口数量**: {len(gap_plan)}

---

## 证据缺口清单

"""
    
    if not gap_plan:
        plan_content += "*恭喜！未发现明显的证据缺口。*\n\n"
    else:
        for i, gap in enumerate(gap_plan, 1):
            plan_content += f"""### 缺口 #{i}

| 属性 | 值 |
|------|-----|
| **类型** | {gap['gap_type']} |
| **优先级** | {gap['priority']} |
| **相关 Finding** | `{gap['related_finding'][:60]}` |
| **所需证据等级** | {gap['required_grade']} |
| **建议来源** | {gap['suggested_source']} |

**行动计划**:
- [ ] 确定具体数据来源/访谈对象
- [ ] 收集证据并记录至 evidence_register.md
- [ ] 更新 Storyline 引用新证据 EV-ID
- [ ] 重新运行逻辑审核

---

"""
    
    plan_content += """---

*本计划由 `logic_audit.py` 自动生成，请优先处理 HIGH 优先级缺口。*
"""
    
    output_path = os.path.join(output_dir, "evidence_plan.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    return output_path


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='S4: Review IOM Logic - 逻辑审核器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --storyline state/storyline.md --evidence-register state/evidence_register.md
  %(prog)s --storyline state/storyline.md --evidence-register state/evidence_register.md --hypothesis-matrix state/hypothesis_matrix.md
        """
    )
    
    parser.add_argument(
        '--storyline', '-s',
        required=True,
        help='Storyline 文件路径（state/storyline.md）'
    )
    
    parser.add_argument(
        '--evidence-register', '-e',
        required=True,
        help='证据台账文件路径（state/evidence_register.md）'
    )
    
    parser.add_argument(
        '--hypothesis-matrix', '-h',
        default=None,
        help='可选：假设矩阵文件路径'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='outputs/review/',
        help='输出目录（默认：outputs/review/）'
    )
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 60)
    print("S4: Review IOM Logic - 逻辑审核器")
    print("=" * 60)
    
    # 解析输入
    print("\n[1/5] 解析输入文件...")
    evidences = parse_evidence_register(args.evidence_register)
    print(f"   ✓ 证据台账：{len(evidences)} 条证据")
    
    storyline = parse_storyline(args.storyline)
    print(f"   ✓ Storyline: v{storyline['version']}, {len(storyline['findings'])} Findings, "
          f"{len(storyline['insights'])} Insights, {len(storyline['implications'])} Implications")
    
    if not storyline['findings']:
        print("   ⚠️  警告：未能从 Storyline 中提取到结构化的 Finding")
        print("      请确保 Storyline 包含清晰的 Finding/Insight/Implication 标记")
    
    # 创建审核器
    print("\n[2/5] 初始化逻辑审核器...")
    auditor = LogicAuditor(storyline, evidences, args.hypothesis_matrix)
    
    # 执行审核
    print("\n[3/5] 执行审核流程...")
    audit_result = auditor.audit()
    
    # 显示摘要
    print("\n[4/5] 审核结果摘要:")
    result_emoji = '✅' if audit_result['result'] == 'PASS' else '❌'
    print(f"   总体结果：{result_emoji} {audit_result['result']}")
    print(f"   通过率：{audit_result['pass_rate']*100:.1f}%")
    print(f"   问题数：{len(audit_result['issues'])} (Critical: {sum(1 for i in audit_result['issues'] if i['severity']=='CRITICAL')}, "
          f"Major: {sum(1 for i in audit_result['issues'] if i['severity']=='MAJOR')})")
    print(f"   警告数：{len(audit_result['warnings'])}")
    
    # 生成报告
    print("\n[5/5] 生成报告...")
    report_path = generate_audit_report(audit_result, args.output_dir)
    print(f"   ✓ 审核报告：{report_path}")
    
    plan_path = generate_evidence_plan(audit_result['evidence_gap_plan'], args.output_dir)
    print(f"   ✓ 补证计划：{plan_path}")
    
    print("\n" + "=" * 60)
    
    if audit_result['result'] == 'PASS':
        print("✅ 逻辑审核通过！可以进入 S5 页面渲染阶段。")
    else:
        print("❌ 逻辑审核未通过。请先修复 Critical/Major 问题后重新审核。")
        print("\n需优先解决的问题:")
        for issue in audit_result['issues']:
            if issue['severity'] in ['CRITICAL', 'MAJOR']:
                print(f"  - {issue['description']}")
    
    print("=" * 60)
    
    return 0 if audit_result['result'] == 'PASS' else 1


if __name__ == '__main__':
    exit(main())
