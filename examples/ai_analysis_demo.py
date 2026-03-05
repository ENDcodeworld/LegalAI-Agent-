#!/usr/bin/env python3
"""
AI 风险识别引擎使用示例
演示如何使用 v2.0 AI 混合架构进行合同风险分析
"""

import sys
from pathlib import Path

# 添加路径
LEGALAI_ROOT = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(LEGALAI_ROOT))

from parser.contract_parser import ContractParser
from risk_ai.hybrid_router import HybridAIRouter, RouterConfig
from risk_ai.models import AIAnalysisConfig


def demo_simple_contract():
    """示例 1: 简单合同分析"""
    print("="*60)
    print("示例 1: 简单买卖合同分析")
    print("="*60)
    
    contract_text = """
    买卖合同
    
    甲方：北京科技有限公司
    乙方：上海贸易有限公司
    
    第一条 价格调整
    甲方有权随时调整价格，无需通知乙方。
    
    第二条 最终解释权
    本合同最终解释权归甲方所有。
    
    第三条 责任限制
    甲方对产品质量概不负责。
    """
    
    # 解析合同
    parser = ContractParser()
    contract = parser.parse_text(contract_text)
    
    # AI 风险分析
    router = HybridAIRouter()
    result = router.analyze(contract.clauses)
    
    # 输出结果
    print(f"\n📄 合同：{result.contract_title}")
    print(f"📊 条款数：{result.total_clauses}")
    print(f"⚠️  风险点：{result.risk_count}")
    print(f"🚨 总体风险：{result.overall_risk_level.value}")
    
    print(f"\n📈 风险汇总:")
    for level, count in result.risk_summary.items():
        if count > 0:
            emoji = {"严重风险": "🔴", "高风险": "🟠", "中风险": "🟡", "低风险": "🟢"}.get(level, "⚪")
            print(f"   {emoji} {level}: {count}")
    
    print(f"\n🎯 Top 风险点:")
    for i, risk in enumerate(result.risk_points[:3], 1):
        print(f"\n   {i}. {risk.risk_type.value}")
        print(f"      等级：{risk.risk_level.value}")
        print(f"      原文：{risk.original_text[:50]}...")
        print(f"      置信度：{risk.confidence:.2f}")
        print(f"      建议：{risk.suggestion[:50]}...")
    
    print(f"\n💡 总体建议:")
    for rec in result.recommendations:
        print(f"   {rec}")
    
    print()


def demo_complex_contract():
    """示例 2: 复杂合作协议分析"""
    print("="*60)
    print("示例 2: 复杂合作协议分析")
    print("="*60)
    
    contract_text = """
    技术合作协议
    
    甲方：北京科技有限公司
    乙方：上海创新研发中心
    
    第一条 合作内容
    乙方应及时提供技术开发服务，具体标准由甲方确定。
    甲方有权根据业务需要调整合作内容。
    
    第二条 知识产权
    合作期间产生的所有知识产权归甲方所有。
    乙方不得主张任何权利，包括但不限于专利权、著作权。
    
    第三条 保密义务
    乙方应对所有信息永久保密，不得向任何第三方披露。
    保密期限不受合同终止影响。
    
    第四条 付款条款
    乙方应在签约后 30 日内支付全部合作费用。
    甲方收到款项后及时提供技术支持。
    
    第五条 违约责任
    乙方违约需承担无限连带责任，赔偿甲方一切损失。
    甲方违约仅退还已收取费用，不承担其他责任。
    
    第六条 合同解除
    甲方可随时解除本合同，无需提前通知。
    乙方解除合同需提前 30 日书面通知，并支付违约金。
    
    第七条 争议解决
    本合同最终解释权归甲方所有。
    争议由甲方所在地人民法院管辖。
    """
    
    # 解析合同
    parser = ContractParser()
    contract = parser.parse_text(contract_text)
    
    # AI 风险分析（配置 LLM）
    config = RouterConfig(
        rule_high_confidence=0.7,
        max_llm_calls=5,
        budget_per_contract=1.0,
    )
    router = HybridAIRouter(config=config)
    
    result = router.analyze(contract.clauses)
    
    # 输出结果
    print(f"\n📄 合同：{result.contract_title}")
    print(f"📊 条款数：{result.total_clauses}")
    print(f"⚠️  风险点：{result.risk_count}")
    print(f"🚨 总体风险：{result.overall_risk_level.value}")
    
    print(f"\n📈 风险汇总:")
    for level, count in result.risk_summary.items():
        if count > 0:
            emoji = {"严重风险": "🔴", "高风险": "🟠", "中风险": "🟡", "低风险": "🟢"}.get(level, "⚪")
            print(f"   {emoji} {level}: {count}")
    
    print(f"\n📂 分类汇总:")
    for category, count in result.category_summary.items():
        if count > 0:
            print(f"   {category}: {count}")
    
    print(f"\n🎯 严重风险点:")
    critical_risks = [r for r in result.risk_points if r.risk_level.value == "严重风险"]
    for i, risk in enumerate(critical_risks[:3], 1):
        print(f"\n   {i}. {risk.risk_type.value}")
        print(f"      条款：{risk.clause_title}")
        print(f"      原文：{risk.original_text[:60]}...")
        print(f"      法律依据：{risk.legal_basis}")
        print(f"      建议：{risk.suggestion}")
    
    print(f"\n📊 分析统计:")
    stats = result.analysis_metadata.get("stats", {})
    print(f"   总耗时：{stats.get('total_time_ms', 0):.2f}ms")
    print(f"   规则引擎命中：{stats.get('rule_engine_hits', 0)}")
    print(f"   预估成本：¥{stats.get('estimated_cost', 0):.2f}")
    
    print(f"\n💡 总体建议:")
    for rec in result.recommendations:
        print(f"   {rec}")
    
    print()


def demo_api_usage():
    """示例 3: API 调用示例"""
    print("="*60)
    print("示例 3: API 调用示例")
    print("="*60)
    
    print("""
# 1. 启动 API 服务
cd /home/admin/.openclaw/workspace/LegalAI-Agent/src
uvicorn api.main_v2:app --host 0.0.0.0 --port 8000

# 2. 解析合同
curl -X POST http://localhost:8000/api/v1/contract/parse \\
  -H "Content-Type: application/json" \\
  -d '{"text": "合同内容..."}'

# 3. AI 风险分析
curl -X POST http://localhost:8000/api/v1/contract/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"contract_id": "uuid", "use_ai_engine": true}'

# 4. 获取风险类型列表
curl http://localhost:8000/api/v2/risk/types

# 5. 访问 Swagger 文档
浏览器打开：http://localhost:8000/docs
    """)
    print()


def demo_risk_types():
    """示例 4: 查看风险类型"""
    print("="*60)
    print("示例 4: 风险类型体系")
    print("="*60)
    
    from risk_ai.risk_types import RISK_TYPE_DEFINITIONS, RiskCategory
    
    print(f"\n📊 风险类型统计:")
    print(f"   总类型数：{len(RISK_TYPE_DEFINITIONS)}")
    print(f"   分类数：{len(RiskCategory)}")
    
    print(f"\n📂 10 大分类:")
    category_count = {}
    for risk_type, definition in RISK_TYPE_DEFINITIONS.items():
        category = definition.category.value
        category_count[category] = category_count.get(category, 0) + 1
    
    for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
        print(f"   {category}: {count}种")
    
    print(f"\n🎯 严重风险类型:")
    critical_types = [
        (rt, defn) for rt, defn in RISK_TYPE_DEFINITIONS.items()
        if defn.default_level.value == "严重风险"
    ]
    for risk_type, definition in critical_types[:5]:
        print(f"   • {risk_type.value}")
        print(f"     关键词：{definition.keywords[:3]}")
        print(f"     法律依据：{definition.legal_basis}")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "AI 风险识别引擎演示" + " "*19 + "║")
    print("║" + " "*10 + "LegalAI v2.0 - 混合 AI 架构" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    # 运行示例
    demo_simple_contract()
    demo_complex_contract()
    demo_api_usage()
    demo_risk_types()
    
    print("="*60)
    print("演示完成！")
    print("="*60)
    print("\n📖 更多信息:")
    print("   - 技术文档：docs/AI_RISK_ENGINE.md")
    print("   - 实现总结：docs/IMPLEMENTATION_SUMMARY.md")
    print("   - API 文档：http://localhost:8000/docs")
    print("\n")
