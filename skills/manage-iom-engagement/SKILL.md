# S1: Manage IOM Engagement

**项目编排与状态治理技能**

## 职责

- 编排问题/Storyline/台账
- 维护端到端状态
- 执行阶段门检查

## 输入契约

- 用户指令
- 各 Skill 状态变更请求

## 输出契约

- 项目章程
- 台账更新
- Gate 报告

## 守边界（红线）

- ❌ 不生成结论
- ❌ 不修改证据
- ❌ 不生成正式页面

## 使用方法

```bash
# 初始化工作空间
python scripts/init_workspace.py --project-name my-project

# 更新台账
python scripts/update_register.py --type evidence --action add

# 执行阶段门检查
python scripts/gate_check.py --gate G0
```

## 参考文档

- `references/engagement-playbook.md` - 项目编排手册
- `references/stage-gates.md` - 阶段门定义
- `references/ledger-spec.md` - 台账规范

## 模板

- `templates/project_charter.md` - 项目章程模板
- `templates/storyline_ledger.md` - Storyline 台账模板
- `templates/registers.md` - 台账模板
