# 贡献指南 | Contributing to LegalAI-Agent

首先，感谢你考虑为 LegalAI-Agent 做出贡献！🎉

本指南将帮助你开始为项目做贡献。请花几分钟阅读以下内容。

## 📋 目录

- [行为准则](#行为准则)
- [我能如何贡献？](#我能如何贡献)
- [开发环境设置](#开发环境设置)
- [提交代码流程](#提交代码流程)
- [代码风格](#代码风格)
- [测试](#测试)
- [提交信息规范](#提交信息规范)
- [常见问题](#常见问题)

---

## 行为准则

本项目采用 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。

简而言之：
- 保持开放和包容
- 尊重不同观点
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 我能如何贡献？

### 🐛 报告 Bug

发现 Bug？请创建 Issue 并提供：
- 清晰的标题和描述
- 复现步骤
- 预期行为和实际行为
- 环境信息（OS、浏览器版本等）
- 相关日志或截图

### 💡 提出功能建议

有好想法？欢迎提交 Feature Request：
- 描述功能和使用场景
- 说明为什么需要这个功能
- 如果可能，提供实现建议

### 📝 改进文档

文档同样重要！你可以帮助：
- 修正拼写和语法错误
- 补充缺失的说明
- 添加示例代码
- 翻译文档

### 🔧 提交代码

准备好贡献代码？请遵循以下流程。

---

## 开发环境设置

### 前置要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 安装步骤

```bash
# 1. Fork 项目
# 在 GitHub 上点击 Fork 按钮

# 2. 克隆你的 Fork
git clone https://github.com/YOUR_USERNAME/LegalAI-Agent.git
cd LegalAI-Agent

# 3. 添加上游远程仓库
git remote add upstream https://github.com/ENDcodeworld/LegalAI-Agent.git

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 5. 启动开发环境
docker-compose up -d

# 6. 验证服务
curl http://localhost:8000/api/health
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 后端开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements-dev.txt

# 启动后端服务
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 提交代码流程

### 1. 创建分支

```bash
# 确保基于最新的主分支
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/amazing-feature
# 或修复分支
git checkout -b fix/bug-description
```

### 2. 进行更改

- 保持代码整洁
- 添加必要的注释
- 更新相关文档
- 编写测试用例

### 3. 运行测试

```bash
# 后端测试
pytest backend/tests/

# 前端测试
cd frontend && npm test

# 代码检查
# 后端
flake8 backend/
black --check backend/
# 前端
cd frontend && npm run lint
```

### 4. 提交更改

```bash
# 添加更改的文件
git add .

# 提交（遵循提交信息规范）
git commit -m "feat: add contract analysis feature"
```

### 5. 推送到 GitHub

```bash
git push origin feature/amazing-feature
```

### 6. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "Compare & pull request"
3. 填写 PR 描述
4. 等待 CI 检查通过
5. 等待维护者审核

---

## 代码风格

### Python 代码 (后端)

- 遵循 [PEP 8](https://pep8.org/) 风格指南
- 使用 [Black](https://black.readthedocs.io/) 格式化代码
- 使用 [isort](https://pycqa.github.io/isort/) 排序导入
- 使用类型注解 (Type Hints)

```python
# ✅ 好的示例
from typing import List, Optional
from fastapi import APIRouter

router = APIRouter()

async def analyze_contract(
    contract_id: str,
    user_id: Optional[str] = None
) -> dict:
    """分析合同并返回风险报告。
    
    Args:
        contract_id: 合同 ID
        user_id: 可选的用户 ID
        
    Returns:
        包含风险分析结果的字典
        
    Raises:
        ValueError: 当合同不存在时
    """
    pass
```

### TypeScript 代码 (前端)

- 遵循 TypeScript 严格模式
- 使用 ESLint + Prettier
- 使用函数组件和 Hooks

```typescript
// ✅ 好的示例
import React, { useState, useEffect } from 'react';

interface ContractProps {
  id: string;
  name: string;
  onAnalyze?: (id: string) => void;
}

const ContractCard: React.FC<ContractProps> = ({ 
  id, 
  name, 
  onAnalyze 
}) => {
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    await onAnalyze?.(id);
    setLoading(false);
  };

  return (
    <div className="contract-card">
      <h3>{name}</h3>
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? '分析中...' : '开始分析'}
      </button>
    </div>
  );
};
```

---

## 测试

### 后端测试

```python
# backend/tests/test_contracts.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_upload_contract():
    """测试合同上传"""
    with open("tests/test_contract.pdf", "rb") as f:
        response = client.post(
            "/api/v1/contracts/upload",
            files={"file": f},
            headers={"Authorization": "Bearer test_token"}
        )
    assert response.status_code == 200
    assert "contract_id" in response.json()
```

### 前端测试

```typescript
// frontend/src/components/__tests__/ContractCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import ContractCard from '../ContractCard';

test('renders contract name', () => {
  render(<ContractCard id="1" name="Test Contract" />);
  expect(screen.getByText('Test Contract')).toBeInTheDocument();
});

test('calls onAnalyze when button clicked', () => {
  const onAnalyze = jest.fn();
  render(<ContractCard id="1" name="Test" onAnalyze={onAnalyze} />);
  fireEvent.click(screen.getByText('开始分析'));
  expect(onAnalyze).toHaveBeenCalledWith('1');
});
```

### 运行测试

```bash
# 后端
pytest backend/tests/ -v --cov=backend

# 前端
cd frontend && npm test -- --coverage
```

---

## 提交信息规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (Type)

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 示例

```bash
feat(analysis): add risk level classification

- Implement high/medium/low risk levels
- Add color coding in UI
- Update API response format

Closes #78
```

```bash
fix(api): resolve timeout issue in contract upload

- Increase upload timeout from 30s to 60s
- Add progress indicator for large files

Fixes #123
```

---

## 常见问题

### Q: 我的 PR 多久会被审核？

A: 我们会尽力在 48 小时内审核。如果超过一周没有回应，可以 @ 维护者。

### Q: 我可以一次提交多个功能吗？

A: 建议一个 PR 只做一件事。多个功能请分成多个 PR。

### Q: 如何测试 AI 分析功能？

A: 使用 `tests/sample_contracts/` 中的测试合同文件。

### Q: 如何联系维护者？

A: 可以通过 Issue、Discord 或邮件联系我们。

---

## 🎉 感谢你的贡献！

每一个贡献，无论大小，都让 LegalAI-Agent 变得更好。

如果你有任何问题，欢迎随时提出！

---

**Happy Coding!** 🚀
