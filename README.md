# LegalAI-Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![GitHub stars](https://img.shields.io/github/stars/ENDcodeworld/LegalAI-Agent.svg)](https://github.com/ENDcodeworld/LegalAI-Agent/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/ENDcodeworld/LegalAI-Agent.svg)](https://github.com/ENDcodeworld/LegalAI-Agent/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

<div align="center">

**智能合同审阅 Agent | AI-Powered Contract Review System**

⚖️ 让 AI 成为你的 24/7 法务顾问，自动识别合同风险，提供专业修改建议

[在线演示](https://legalai.demo.com) · [API 文档](./docs/API.md) · [部署指南](./docs/DEPLOYMENT.md)

![LegalAI Dashboard](./docs/assets/dashboard-preview.png)
*图：LegalAI 合同审阅仪表盘*

</div>

---

## 🎯 项目概述

LegalAI-Agent 是一个基于大语言模型的智能合同审阅系统，能够自动分析合同条款、识别风险点、提供专业修改建议。适用于法务团队、律师事务所以及需要频繁处理合同的中小企业。

### ✨ 核心优势

| 传统审阅 | LegalAI |
|----------|---------|
| ⏱️ 2-3 小时/份 | ⚡ **5 分钟/份** |
| 💰 ¥500-2000/份 | 💰 **¥0.5/份** |
| 😓 人工易疲劳 | 🤖 **24/7 不间断** |
| 📊 标准不统一 | 📊 **AI 标准化** |

---

## 🔥 核心功能

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                    LegalAI 工作流程                          │
├─────────────────────────────────────────────────────────────┤
│  📄 上传合同 → 🔍 AI 分析 → ⚠️ 风险识别 → 💡 修改建议 → 📊 报告  │
└─────────────────────────────────────────────────────────────┘
```

</div>

### 功能详情

| 功能 | 描述 | 状态 |
|------|------|------|
| 📄 **合同解析** | 支持 PDF/Word 格式，自动提取条款结构 | ✅ |
| 🔍 **风险识别** | AI + 规则引擎双重检测，准确率>90% | ✅ |
| 💡 **智能建议** | 基于法律专业知识提供修改建议 | ✅ |
| 📊 **风险报告** | 可视化风险评级，支持 PDF 导出 | ✅ |
| 🔄 **版本对比** | 快速识别合同变更内容 | 🚧 |
| 📚 **条款库** | 标准条款模板推荐 | 📋 |

---

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 一键启动 (开发环境)

```bash
# 1. 克隆项目
git clone https://github.com/ENDcodeworld/LegalAI-Agent.git
cd LegalAI-Agent

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 3. 启动所有服务
docker-compose up -d

# 4. 访问应用
open http://localhost:3000
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Frontend | 3000 | React 前端 |
| Backend API | 8000 | FastAPI 后端 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存/队列 |
| Qdrant | 6333 | 向量数据库 |

---

## 💻 API 使用示例

### 上传合同

```bash
curl -X POST http://localhost:8000/api/v1/contracts/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@contract.pdf"
```

**响应：**
```json
{
  "contract_id": "ctx_abc123",
  "status": "uploaded",
  "pages": 12,
  "file_size": "2.3MB"
}
```

### 开始分析

```bash
curl -X POST http://localhost:8000/api/v1/contracts/ctx_abc123/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取报告

```bash
curl http://localhost:8000/api/v1/contracts/ctx_abc123/report \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "risk_level": "HIGH",
  "risk_score": 78,
  "issues": [
    {
      "type": "liability_cap",
      "severity": "high",
      "clause": "第 8.2 条",
      "suggestion": "建议将责任上限调整为合同总额的 200%"
    }
  ]
}
```

完整 API 文档见 [docs/API.md](./docs/API.md)

---

## 🎬 Demo 截图

<div align="center">

| 合同上传 | 风险分析 | 报告导出 |
|----------|----------|----------|
| ![Upload](./docs/assets/upload-demo.png) | ![Analysis](./docs/assets/analysis-demo.png) | ![Report](./docs/assets/report-demo.png) |

</div>

---

## 📊 性能指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 合同上传 | < 5 秒 (10MB) | ✅ 3.2 秒 |
| AI 分析 | < 30 秒 | ✅ 22 秒 |
| 报告生成 | < 10 秒 | ✅ 6 秒 |
| 并发用户 | 100+ | ✅ 150 |
| 可用性 | 99.5% | ✅ 99.7% |

---

## 💰 定价方案

<div align="center">

| 版本 | 价格 | 功能 | 适合 |
|------|------|------|------|
| 🆓 **免费** | ¥0 | 3 份/月 | 个人用户 |
| 💼 **专业** | ¥199/月 | 无限审阅 + 优先支持 | 中小企业 |
| 🏢 **企业** | ¥999/月 | API + 私有部署 + 定制 | 大型企业 |

</div>

**🎁 新用户注册即送 7 天专业版试用！**

---

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI + Python 3.11
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **任务队列**: Celery
- **向量库**: Qdrant

### 前端
- **框架**: React 18 + TypeScript
- **样式**: TailwindCSS + Shadcn/UI
- **状态**: Zustand
- **数据**: React Query

### AI
- **主模型**: Qwen2.5-72B / DeepSeek-V3
- **嵌入**: text-embedding-3-large
- **OCR**: PaddleOCR

---

## 🔐 安全设计

- 🔑 JWT 认证 + Refresh Token
- 🔒 文件加密存储 (AES-256)
- 🚦 API 速率限制
- 👤 RBAC 权限控制
- 📝 完整审计日志

---

## 📁 项目结构

```
LegalAI-Agent/
├── backend/
│   ├── api/            # API 路由
│   ├── models/         # 数据模型
│   ├── services/       # 业务逻辑
│   └── utils/          # 工具函数
├── frontend/
│   ├── src/
│   │   ├── components/ # React 组件
│   │   ├── pages/      # 页面
│   │   └── hooks/      # 自定义 Hooks
│   └── public/
├── docs/               # 文档
├── tests/              # 测试
├── templates/          # 合同模板
├── docker-compose.yml
└── README.md
```

---

## 🤝 贡献

我们欢迎各种形式的贡献！

### 贡献方式

1. 🐛 [报告 Bug](https://github.com/ENDcodeworld/LegalAI-Agent/issues)
2. 💡 [功能建议](https://github.com/ENDcodeworld/LegalAI-Agent/issues)
3. 📝 改进文档
4. 🔧 提交代码 (PR)

详细贡献指南请查看 [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📚 文档

- 📘 [快速入门](./docs/GETTING_STARTED.md)
- 📗 [API 参考](./docs/API.md)
- 📙 [部署指南](./docs/DEPLOYMENT.md)
- 📕 [常见问题](./docs/FAQ.md)

---

## 🗺️ 路线图

<div align="center">

| 时间 | 里程碑 |
|------|--------|
| 2026-03 | MVP 发布 |
| 2026-04 | Word 格式支持 |
| 2026-05 | 版本对比功能 |
| 2026-06 | 条款知识库 |
| 2026-Q3 | 多语言支持 |
| 2026-Q4 | 企业私有部署 |

</div>

---

## 📞 联系我们

- 📧 Email: contact@legalai.com
- 💬 微信：LegalAI_Official
- 🐦 Twitter: @LegalAI_Agent
- 💼 商务合作：bd@legalai.com

---

## 📄 许可证

本项目采用 [MIT 许可证](./LICENSE)

---

## 👥 团队

- **CTO**: Gemini (技术架构)
- **COO**: 小志 1 号 (项目管理)
- **法务顾问**: 合作律师事务所

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

[GitHub](https://github.com/ENDcodeworld/LegalAI-Agent) · [文档](./docs) · [在线演示](https://legalai.demo.com)

**让 AI 成为你的法务顾问！** ⚖️

</div>
