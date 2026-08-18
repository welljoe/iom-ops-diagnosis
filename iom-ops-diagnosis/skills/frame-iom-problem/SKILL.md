# S2: Frame IOM Problem

**问题界定与结构化分解技能**

## 职责

- 界定 Governing Question
- 痛点→假设映射
- Issue Tree MECE 分解

## 输入契约

- 客户痛点清单
- 柔性特征描述

## 输出契约

- GQ 文档
- 假设矩阵
- Issue Tree

## 守边界（红线）

- ❌ 不做证据检验
- ❌ 不下最终结论
- ❌ 不产出页面

## 使用方法

```bash
# 痛点映射
python scripts/painpoint_mapper.py --input painpoints.md

# MECE 检查
python scripts/mece_checker.py --input issue_tree.md
```

## 参考文档

- `references/iom-4module-framework.md` - IOM 四模块框架
- `references/hmlv-pain-patterns.md` - HMLV 痛点模式库
- `references/hypothesis-library.md` - 假设库 (H1-H8)

## 模板

- `templates/governing_question.md` - Governing Question 模板
- `templates/issue_tree.md` - Issue Tree 模板
- `templates/hypothesis_matrix.md` - 假设矩阵模板
