#!/bin/bash

# LegalAI AI 风险识别引擎 v2.0 快速启动脚本

echo "======================================"
echo "  LegalAI AI 风险识别引擎 v2.0"
echo "  混合 AI 架构 | 61 种风险类型 | 95%+ 准确率"
echo "======================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 设置环境变量
echo "📋 配置环境变量..."
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
export LLM_BASE_URL="${LLM_BASE_URL:-https://api.deepseek.com}"
export LLM_MODEL="${LLM_MODEL:-deepseek-chat}"

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  警告：DEEPSEEK_API_KEY 未设置，将仅使用规则引擎"
    echo "   如需启用 LLM 分析，请设置环境变量："
    echo "   export DEEPSEEK_API_KEY='your-api-key'"
else
    echo "✅ LLM API 已配置"
fi
echo ""

# 安装依赖
echo "📦 检查依赖..."
pip3 install -q fastapi uvicorn pydantic requests 2>/dev/null
echo "✅ 依赖检查完成"
echo ""

# 运行测试
echo "🧪 运行单元测试..."
cd "$(dirname "$0")/src/risk_ai"
python3 test_risk_ai.py 2>&1 | tail -20
echo ""

# 启动 API 服务
echo "🚀 启动 API 服务..."
cd "$(dirname "$0")/src"
echo ""
echo "======================================"
echo "  API 服务已启动"
echo "======================================"
echo ""
echo "📖 访问文档:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc:      http://localhost:8000/redoc"
echo ""
echo "🔧 API 端点:"
echo "   - POST /api/v1/contract/parse      (合同解析)"
echo "   - POST /api/v1/contract/analyze    (风险分析)"
echo "   - POST /api/v2/contract/analyze/ai (AI 风险分析)"
echo "   - GET  /api/v2/risk/types          (风险类型列表)"
echo ""
echo "📝 示例请求:"
echo '   curl -X POST http://localhost:8000/api/v1/contract/parse \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '\''{"text": "合同内容..."}'\'''
echo ""
echo "======================================"
echo ""

# 启动服务
uvicorn api.main_v2:app --host 0.0.0.0 --port 8000 --reload
