# iom-ops-diagnosis Agent

**基于 MBB 问题解决方法论 × "端到端敏捷运营体系重构"的集成运营管理（IOM）咨询诊断 Agent**

## 定位与适用场景

面向 **"多品种小批量（HMLV）、插单多、小单多"** 制造企业，以 CEO 视角执行端到端 IOM 咨询诊断：从痛点界定 → 假设分解 → 证据检验 → 方案选择 → 页面确认 → 交付生产，全程受治理、可追溯。

## 快速开始

```bash
# 初始化项目工作空间
python skills/manage-iom-engagement/scripts/init_workspace.py --project-name my-iom-project

# 运行阶段门检查
python skills/manage-iom-engagement/scripts/gate_check.py --gate G0
```

## 目录结构

```
iom-ops-diagnosis/
├── .codex-plugin/          # 插件元数据
├── skills/                 # 六大技能模块
│   ├── manage-iom-engagement/   # S1: 项目编排与状态治理
│   ├── frame-iom-problem/       # S2: 问题界定与结构化分解
│   ├── select-iom-methods/      # S3: 方法选择器
│   ├── review-iom-logic/        # S4: 逻辑审核器
│   ├── generate-iom-visuals/    # S5: 单页可视化
│   └── produce-iom-deck/        # S6: 交付生产
├── knowledge/              # 知识底座
├── state/                  # 运行时台账
└── outputs/                # 输出产物
```

## 核心原则

| 类别 | 原则 | 说明 |
|------|------|------|
| 继承 | 流程驱动 | G0–G5 阶段门 + 主线流程脚本化检查 |
| 继承 | 治理为先 | Stage Gate 不通过不进入下一阶段 |
| 继承 | 用户决策 | 用户是唯一 VF（Verified & Frozen）授权者 |
| IOM | 柔性约束 | 所有方案必须满足"设备 + 人员 + 产线"三柔性特征 |
| IOM | 财务锚定 | 所有 Finding 必须折算为 OTIF/周转/人均产值/利润语言 |

## 使用方法

详见各 Skill 的 `SKILL.md` 文档。
