"""
AI 风险识别引擎 v2.0
混合 AI 架构：规则引擎 + 轻量模型 + 大语言模型
目标：95%+ 风险识别准确率
"""

from .risk_types import RiskType, RiskLevel, RiskCategory
from .models import RiskPoint, AnalysisResult, AIAnalysisConfig
from .rule_engine import RuleEngine
from .confidence_fusion import ConfidenceFusion
from .llm_analyzer import LLMAnalyzer
from .hybrid_router import HybridAIRouter
from .risk_classifier import RiskClassifier

__version__ = "2.0.0"
__all__ = [
    "RiskType",
    "RiskLevel", 
    "RiskCategory",
    "RiskPoint",
    "AnalysisResult",
    "AIAnalysisConfig",
    "RuleEngine",
    "ConfidenceFusion",
    "LLMAnalyzer",
    "HybridAIRouter",
    "RiskClassifier",
]
