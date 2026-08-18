# IOM Operations Diagnosis Agent 使用指南

## 快速开始

### 1. 安装 CLI 工具

```bash
# 克隆项目
git clone https://github.com/welljoe/iom-ops-diagnosis.git
cd iom-ops-diagnosis/iom-ops-cli

# 安装
pip install -e .
```

### 2. 验证安装

```bash
iom-ops --version
iom-ops --help
```

### 3. 初始化项目

```bash
# 创建新项目
iom-ops init --project-name my-project

# 查看项目状态
iom-ops status
```

### 4. 执行阶段门检查

```bash
# 检查 G0 门
iom-ops check --gate G0

# 检查所有门
iom-ops check --all-gates
```

### 5. 痛点分析与假设映射

```bash
# 准备痛点文件 pains.md
iom-ops map-painpoints --input pains.md --output hypotheses.md
```

### 6. MECE 检查

```bash
iom-ops check-mece --tree issue_tree.md
```

### 7. 方法选择

```bash
iom-ops select-methods --bottleneck-tags OTD_delay,quality_issue --output plan.md
```

### 8. 页面渲染

```bash
iom-ops render --page-register page_register.md --output outputs/pages
```

### 9. 构建审阅包

```bash
iom-ops build-pack --project-dir . --output outputs/review
```

## 完整工作流示例

```bash
# 1. 初始化项目
iom-ops init --project-name demo

# 2. G0 检查 (需要完成项目章程)
iom-ops check --gate G0

# 3. 痛点映射
echo "# 痛点清单\n- OTD 延迟严重\n- 库存周转慢" > pains.md
iom-ops map-painpoints --input pains.md --output hypotheses.md

# 4. 方法选择
iom-ops select-methods --bottleneck-tags OTD_delay --output analysis_plan.md

# 5. 查看所有可用命令
iom-ops --help
```

## 命令参考

| 命令 | 描述 | 主要参数 |
|------|------|----------|
| `init` | 初始化项目 | `--project-name`, `--output-dir` |
| `check` | 阶段门检查 | `--gate G0-G5`, `--all-gates` |
| `map-painpoints` | 痛点→假设映射 | `--input`, `--output` |
| `check-mece` | MECE 合规检查 | `--tree` |
| `select-methods` | 方法推荐 | `--bottleneck-tags`, `--output` |
| `render` | 页面渲染 | `--page-register`, `--output-dir` |
| `build-pack` | 构建审阅包 | `--project-dir`, `--output-dir` |
| `status` | 项目状态 | 无 |

## 故障排除

**问题**: 命令未找到
**解决**: 确保已运行 `pip install -e .` 且 Python 脚本路径在 PATH 中

**问题**: 阶段门检查失败
**解决**: 根据错误提示补充缺失的文件或内容

**问题**: 权限错误
**解决**: 使用 `--user` 标志或在虚拟环境中安装

## 开发模式

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/

# Lint 检查
flake8 src/
```

## 版本信息

当前版本：v1.1.0
- 支持 G0-G5 全阶段门治理
- 集成三大错位诊断透镜
- 支持呆滞清理 PMO 行动卡
- 高管汇报页模板
