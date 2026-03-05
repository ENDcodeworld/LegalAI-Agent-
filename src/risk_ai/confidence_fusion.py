"""
置信度融合模块
融合规则引擎、轻量模型、大语言模型的分析结果
实现置信度校准和最终决策
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

try:
    from .risk_types import RiskType, RiskLevel
    from .models import RiskPoint
except ImportError:
    from risk_types import RiskType, RiskLevel
    from models import RiskPoint


class FusionStrategy(Enum):
    """融合策略"""
    MAX_CONFIDENCE = "max"  # 取最高置信度
    WEIGHTED_AVERAGE = "weighted"  # 加权平均
    BAYESIAN = "bayesian"  # 贝叶斯融合
    VOTING = "voting"  # 投票机制


@dataclass
class FusedRiskPoint:
    """融合后的风险点"""
    risk_point: RiskPoint
    fused_confidence: float
    sources: List[str]  # 分析来源列表
    confidence_scores: Dict[str, float]  # 各来源置信度


class ConfidenceFusion:
    """
    置信度融合器
    融合多模型分析结果，输出最终置信度
    """
    
    def __init__(self, strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE):
        self.strategy = strategy
        
        # 模型权重（可根据历史准确率调整）
        self.weights = {
            "rule": 0.3,    # 规则引擎权重
            "slm": 0.4,     # 轻量模型权重
            "llm": 0.3,     # 大语言模型权重
        }
        
        # 模型基础可信度
        self.base_reliability = {
            "rule": 0.75,   # 规则引擎基础可信度
            "slm": 0.85,    # 轻量模型基础可信度
            "llm": 0.95,    # 大语言模型基础可信度
        }
    
    def fuse(self, risk_points: List[RiskPoint]) -> List[FusedRiskPoint]:
        """
        融合多个风险点
        
        Args:
            risk_points: 来自不同模型的风险点列表
            
        Returns:
            List[FusedRiskPoint]: 融合后的风险点
        """
        # 按风险类型分组
        grouped = self._group_by_risk_type(risk_points)
        
        fused_results = []
        for risk_type, points in grouped.items():
            if len(points) == 1:
                # 单一来源，直接校准
                fused = self._calibrate_single(points[0])
            else:
                # 多来源，进行融合
                fused = self._fuse_multiple(points)
            
            fused_results.append(fused)
        
        # 按置信度排序
        fused_results.sort(key=lambda x: -x.fused_confidence)
        
        return fused_results
    
    def _group_by_risk_type(self, risk_points: List[RiskPoint]) -> Dict[RiskType, List[RiskPoint]]:
        """按风险类型分组"""
        grouped = {}
        for rp in risk_points:
            if rp.risk_type not in grouped:
                grouped[rp.risk_type] = []
            grouped[rp.risk_type].append(rp)
        return grouped
    
    def _calibrate_single(self, risk_point: RiskPoint) -> FusedRiskPoint:
        """校准单一来源的风险点"""
        source = risk_point.analysis_source
        
        # 根据来源调整置信度
        base_confidence = risk_point.confidence
        reliability = self.base_reliability.get(source, 0.8)
        
        # 校准后的置信度
        calibrated_confidence = base_confidence * reliability
        
        return FusedRiskPoint(
            risk_point=risk_point,
            fused_confidence=calibrated_confidence,
            sources=[source],
            confidence_scores={source: base_confidence}
        )
    
    def _fuse_multiple(self, risk_points: List[RiskPoint]) -> FusedRiskPoint:
        """融合多个来源的风险点"""
        # 选择置信度最高的作为基础
        best_point = max(risk_points, key=lambda p: p.confidence)
        
        # 收集所有置信度
        confidence_scores = {}
        for rp in risk_points:
            source = rp.analysis_source
            confidence_scores[source] = rp.confidence
        
        # 根据策略计算融合置信度
        if self.strategy == FusionStrategy.MAX_CONFIDENCE:
            fused_confidence = max(rp.confidence for rp in risk_points)
        
        elif self.strategy == FusionStrategy.WEIGHTED_AVERAGE:
            fused_confidence = self._weighted_average(risk_points)
        
        elif self.strategy == FusionStrategy.BAYESIAN:
            fused_confidence = self._bayesian_fusion(risk_points)
        
        elif self.strategy == FusionStrategy.VOTING:
            fused_confidence = self._voting_fusion(risk_points)
        
        else:
            fused_confidence = best_point.confidence
        
        # 更新最佳风险点的置信度
        best_point.confidence = fused_confidence
        
        return FusedRiskPoint(
            risk_point=best_point,
            fused_confidence=fused_confidence,
            sources=list(confidence_scores.keys()),
            confidence_scores=confidence_scores
        )
    
    def _weighted_average(self, risk_points: List[RiskPoint]) -> float:
        """加权平均融合"""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for rp in risk_points:
            source = rp.analysis_source
            weight = self.weights.get(source, 0.3)
            weighted_sum += rp.confidence * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _bayesian_fusion(self, risk_points: List[RiskPoint]) -> float:
        """贝叶斯融合"""
        # 简化贝叶斯融合
        # P(Risk|Evidence) = P(Evidence|Risk) * P(Risk) / P(Evidence)
        
        prior = 0.5  # 先验概率
        
        likelihood_product = 1.0
        for rp in risk_points:
            # 将置信度转换为似然比
            likelihood = rp.confidence
            likelihood_product *= likelihood
        
        # 后验概率
        posterior = (likelihood_product * prior) / (likelihood_product * prior + (1 - prior))
        
        return min(posterior, 0.99)  # 上限 0.99
    
    def _voting_fusion(self, risk_points: List[RiskPoint]) -> float:
        """投票融合"""
        # 每个来源一票，加权投票
        total_votes = 0.0
        positive_votes = 0.0
        
        for rp in risk_points:
            source = rp.analysis_source
            weight = self.weights.get(source, 0.3)
            total_votes += weight
            
            # 置信度超过阈值算正票
            if rp.confidence > 0.6:
                positive_votes += weight * rp.confidence
        
        if total_votes == 0:
            return 0.0
        
        return positive_votes / total_votes
    
    def calibrate(self, risk_points: List[RiskPoint]) -> List[RiskPoint]:
        """
        校准风险点置信度（简化接口）
        
        Args:
            risk_points: 风险点列表
            
        Returns:
            List[RiskPoint]: 校准后的风险点
        """
        fused_results = self.fuse(risk_points)
        
        # 转换回 RiskPoint 列表
        calibrated = []
        for fused in fused_results:
            rp = fused.risk_point
            rp.confidence = fused.fused_confidence
            calibrated.append(rp)
        
        return calibrated
    
    def filter_by_confidence(
        self,
        risk_points: List[RiskPoint],
        threshold: float = 0.6
    ) -> List[RiskPoint]:
        """按置信度过滤风险点"""
        return [rp for rp in risk_points if rp.confidence >= threshold]
    
    def filter_by_risk_level(
        self,
        risk_points: List[RiskPoint],
        min_level: RiskLevel = RiskLevel.LOW
    ) -> List[RiskPoint]:
        """按风险等级过滤"""
        level_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3,
        }
        
        min_order = level_order.get(min_level, 0)
        
        return [
            rp for rp in risk_points
            if level_order.get(rp.risk_level, 0) >= min_order
        ]
    
    def deduplicate(
        self,
        risk_points: List[RiskPoint],
        similarity_threshold: float = 0.8
    ) -> List[RiskPoint]:
        """
        去重风险点
        
        Args:
            risk_points: 风险点列表
            similarity_threshold: 相似度阈值
            
        Returns:
            List[RiskPoint]: 去重后的风险点
        """
        if not risk_points:
            return []
        
        # 按风险类型和原文分组
        grouped = {}
        for rp in risk_points:
            key = (rp.risk_type, rp.original_text[:50])  # 简化去重
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(rp)
        
        # 每组取置信度最高的
        deduplicated = []
        for key, points in grouped.items():
            best = max(points, key=lambda p: p.confidence)
            deduplicated.append(best)
        
        return deduplicated
