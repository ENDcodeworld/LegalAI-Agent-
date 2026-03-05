#!/usr/bin/env python3
"""
AI 风险识别引擎快速演示
"""

import sys
from pathlib import Path

# 添加路径
risk_ai_path = Path(__file__).parent.parent / "src" / "risk_ai"
sys.path.insert(0, str(risk_ai_path))

# 导入风险类型
try:
    from risk_types import RISK_TYPE_DEFINITIONS, RiskType, RiskLevel, RiskCategory
    from rule_engine import RuleEngine
except ImportError as e:
    print(f"导入失败：{e}")
    print(f"当前路径：{risk_ai_path}")
    import os
    print(f"文件列表：{os.listdir(risk_ai_path)}")
    sys.exit(1)

print("\n" + "="*60)
print("  AI 风险识别引擎 v2.0 - 快速演示")
print("="*60 + "\n")

# 统计信息
print("📊 风险类型统计:")
print(f"   总类型数：{len(RISK_TYPE_DEFINITIONS)}")
print(f"   分类数：{len(RiskCategory)}")

# 分类统计
category_count = {}
for risk_type, definition in RISK_TYPE_DEFINITIONS.items():
    category = definition.category.value
    category_count[category] = category_count.get(category, 0) + 1

print(f"\n📂 10 大分类:")
for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
    print(f"   • {category}: {count}种")

# 严重风险示例
print(f"\n🔴 严重风险类型示例:")
critical_types = [
    (rt, defn) for rt, defn in RISK_TYPE_DEFINITIONS.items()
    if defn.default_level == RiskLevel.CRITICAL
][:5]

for risk_type, definition in critical_types:
    print(f"\n   {risk_type.value}")
    print(f"   描述：{definition.description}")
    print(f"   关键词：{definition.keywords[:3]}")
    print(f"   法律依据：{definition.legal_basis}")

# 规则引擎演示
print("\n" + "="*60)
print("  规则引擎演示")
print("="*60 + "\n")

from rule_engine import RuleEngine
import time

engine = RuleEngine()

test_cases = [
    ("最终解释权", "本合同最终解释权归甲方所有"),
    ("无限责任", "乙方需承担无限连带责任，赔偿一切损失"),
    ("单方解除", "甲方可随时解除本合同"),
    ("免责条款", "甲方对产品质量概不负责"),
]

for name, text in test_cases:
    start = time.time()
    risks = engine.scan(text, "测试条款")
    elapsed = (time.time() - start) * 1000
    
    if risks:
        risk = risks[0]
        print(f"✅ {name}:")
        print(f"   风险类型：{risk.risk_type.value}")
        print(f"   风险等级：{risk.risk_level.value}")
        print(f"   置信度：{risk.confidence:.2f}")
        print(f"   扫描时间：{elapsed:.2f}ms")
    else:
        print(f"❌ {name}: 未识别到风险")
    print()

print("="*60)
print("  演示完成！")
print("="*60)
print("\n📖 更多信息:")
print("   - 技术文档：docs/AI_RISK_ENGINE.md")
print("   - 实现总结：docs/IMPLEMENTATION_SUMMARY.md")
print("   - 运行完整测试：cd src/risk_ai && python test_risk_ai.py")
print("\n")
