"""
数据模型定义
风险点、分析结果等核心数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json

try:
    from .risk_types import RiskType, RiskLevel, RiskCategory
except ImportError:
    from risk_types import RiskType, RiskLevel, RiskCategory


@dataclass
class RiskPoint:
    """
    风险点数据类
    单个风险点的完整信息
    """
    risk_type: RiskType  # 风险类型
    risk_level: RiskLevel  # 风险等级
    clause_title: str  # 相关条款标题
    risk_content: str  # 风险内容描述
    original_text: str  # 原文引用
    confidence: float = 0.0  # 置信度 (0-1)
    
    # 可选字段
    legal_basis: Optional[str] = None  # 法律依据
    suggestion: Optional[str] = None  # 修改建议
    redline_suggestion: Optional[str] = None  # 具体修改文本（智能 Redline）
    market_standard: Optional[str] = None  # 市场基准
    category: Optional[RiskCategory] = None  # 风险分类
    
    # AI 分析元数据
    analysis_source: str = "rule"  # 分析来源：rule/slm/llm
    analysis_time_ms: float = 0.0  # 分析耗时（毫秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "risk_type": self.risk_type.value,
            "risk_level": self.risk_level.value,
            "clause_title": self.clause_title,
            "risk_content": self.risk_content,
            "original_text": self.original_text,
            "confidence": self.confidence,
            "legal_basis": self.legal_basis,
            "suggestion": self.suggestion,
            "redline_suggestion": self.redline_suggestion,
            "market_standard": self.market_standard,
            "category": self.category.value if self.category else None,
            "analysis_source": self.analysis_source,
            "analysis_time_ms": self.analysis_time_ms,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskPoint":
        """从字典创建"""
        return cls(
            risk_type=RiskType(data["risk_type"]),
            risk_level=RiskLevel(data["risk_level"]),
            clause_title=data["clause_title"],
            risk_content=data["risk_content"],
            original_text=data["original_text"],
            confidence=data.get("confidence", 0.0),
            legal_basis=data.get("legal_basis"),
            suggestion=data.get("suggestion"),
            redline_suggestion=data.get("redline_suggestion"),
            market_standard=data.get("market_standard"),
            category=RiskCategory(data["category"]) if data.get("category") else None,
            analysis_source=data.get("analysis_source", "rule"),
            analysis_time_ms=data.get("analysis_time_ms", 0.0),
        )


@dataclass
class AnalysisResult:
    """
    分析结果数据类
    完整合同风险分析结果
    """
    contract_title: str
    total_clauses: int
    risk_count: int
    risk_points: List[RiskPoint]
    risk_summary: Dict[str, int]  # 各等级风险数量
    overall_risk_level: RiskLevel
    recommendations: List[str]  # 总体建议
    
    # 扩展字段
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    category_summary: Dict[str, int] = field(default_factory=dict)  # 各分类风险数量
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "contract_title": self.contract_title,
            "total_clauses": self.total_clauses,
            "risk_count": self.risk_count,
            "risk_points": [rp.to_dict() for rp in self.risk_points],
            "risk_summary": self.risk_summary,
            "overall_risk_level": self.overall_risk_level.value,
            "recommendations": self.recommendations,
            "analysis_metadata": self.analysis_metadata,
            "category_summary": self.category_summary,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """从字典创建"""
        return cls(
            contract_title=data["contract_title"],
            total_clauses=data["total_clauses"],
            risk_count=data["risk_count"],
            risk_points=[RiskPoint.from_dict(rp) for rp in data["risk_points"]],
            risk_summary=data["risk_summary"],
            overall_risk_level=RiskLevel(data["overall_risk_level"]),
            recommendations=data["recommendations"],
            analysis_metadata=data.get("analysis_metadata", {}),
            category_summary=data.get("category_summary", {}),
        )
    
    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass
class AIAnalysisConfig:
    """
    AI 分析配置
    控制混合 AI 架构的行为
    """
    # 置信度阈值
    rule_confidence_threshold: float = 0.9  # 规则引擎高置信度阈值
    slm_confidence_threshold: float = 0.85  # 轻量模型高置信度阈值
    
    # 模型选择
    enable_rule_engine: bool = True  # 启用规则引擎
    enable_slm: bool = True  # 启用轻量模型
    enable_llm: bool = True  # 启用大语言模型
    
    # 性能控制
    max_llm_calls: int = 10  # 最大 LLM 调用次数
    timeout_seconds: float = 30.0  # 总超时时间
    parallel_analysis: bool = True  # 并行分析
    
    # 成本优化
    cost_budget: float = 1.0  # 成本预算（元）
    prefer_fast: bool = False  # 优先快速（降低准确率）
    
    # 风险类型过滤
    enabled_risk_types: Optional[List[RiskType]] = None  # 启用的风险类型
    min_risk_level: RiskLevel = RiskLevel.LOW  # 最低风险等级
    
    # 输出控制
    include_legal_basis: bool = True  # 包含法律依据
    include_suggestions: bool = True  # 包含修改建议
    include_redline: bool = False  # 包含智能 Redline（需要 LLM）
    include_market_standard: bool = False  # 包含市场基准
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_confidence_threshold": self.rule_confidence_threshold,
            "slm_confidence_threshold": self.slm_confidence_threshold,
            "enable_rule_engine": self.enable_rule_engine,
            "enable_slm": self.enable_slm,
            "enable_llm": self.enable_llm,
            "max_llm_calls": self.max_llm_calls,
            "timeout_seconds": self.timeout_seconds,
            "parallel_analysis": self.parallel_analysis,
            "cost_budget": self.cost_budget,
            "prefer_fast": self.prefer_fast,
            "enabled_risk_types": [rt.value for rt in self.enabled_risk_types] if self.enabled_risk_types else None,
            "min_risk_level": self.min_risk_level.value,
            "include_legal_basis": self.include_legal_basis,
            "include_suggestions": self.include_suggestions,
            "include_redline": self.include_redline,
            "include_market_standard": self.include_market_standard,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIAnalysisConfig":
        """从字典创建"""
        enabled_types = None
        if data.get("enabled_risk_types"):
            enabled_types = [RiskType(rt) for rt in data["enabled_risk_types"]]
        
        return cls(
            rule_confidence_threshold=data.get("rule_confidence_threshold", 0.9),
            slm_confidence_threshold=data.get("slm_confidence_threshold", 0.85),
            enable_rule_engine=data.get("enable_rule_engine", True),
            enable_slm=data.get("enable_slm", True),
            enable_llm=data.get("enable_llm", True),
            max_llm_calls=data.get("max_llm_calls", 10),
            timeout_seconds=data.get("timeout_seconds", 30.0),
            parallel_analysis=data.get("parallel_analysis", True),
            cost_budget=data.get("cost_budget", 1.0),
            prefer_fast=data.get("prefer_fast", False),
            enabled_risk_types=enabled_types,
            min_risk_level=RiskLevel(data.get("min_risk_level", "低风险")),
            include_legal_basis=data.get("include_legal_basis", True),
            include_suggestions=data.get("include_suggestions", True),
            include_redline=data.get("include_redline", False),
            include_market_standard=data.get("include_market_standard", False),
        )


@dataclass
class AnalysisStats:
    """分析统计信息"""
    total_clauses: int = 0
    analyzed_clauses: int = 0
    rule_engine_hits: int = 0
    slm_hits: int = 0
    llm_hits: int = 0
    total_time_ms: float = 0.0
    rule_engine_time_ms: float = 0.0
    slm_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    estimated_cost: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_clauses": self.total_clauses,
            "analyzed_clauses": self.analyzed_clauses,
            "rule_engine_hits": self.rule_engine_hits,
            "slm_hits": self.slm_hits,
            "llm_hits": self.llm_hits,
            "total_time_ms": self.total_time_ms,
            "rule_engine_time_ms": self.rule_engine_time_ms,
            "slm_time_ms": self.slm_time_ms,
            "llm_time_ms": self.llm_time_ms,
            "estimated_cost": self.estimated_cost,
        }


@dataclass
class LLMRequest:
    """LLM 请求数据类"""
    prompt: str
    risk_types: Optional[List[RiskType]] = None
    context: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "prompt": self.prompt,
            "risk_types": [rt.value for rt in self.risk_types] if self.risk_types else None,
            "context": self.context,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


@dataclass
class LLMResponse:
    """LLM 响应数据类"""
    risk_points: List[RiskPoint]
    raw_response: str
    model_name: str
    usage: Dict[str, int]  # token 使用量
    latency_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "risk_points": [rp.to_dict() for rp in self.risk_points],
            "raw_response": self.raw_response,
            "model_name": self.model_name,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
        }
