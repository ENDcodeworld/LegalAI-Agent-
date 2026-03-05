"""
风险分类器
基于规则和模式的条款风险分类
支持 50+ 风险类型的自动分类
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    from .risk_types import RiskType, RiskLevel, RiskCategory, RISK_TYPE_DEFINITIONS, get_risk_type_definition
    from .models import RiskPoint
except ImportError:
    from risk_types import RiskType, RiskLevel, RiskCategory, RISK_TYPE_DEFINITIONS, get_risk_type_definition
    from models import RiskPoint


@dataclass
class ClassificationResult:
    """分类结果"""
    risk_type: RiskType
    confidence: float
    matched_keywords: List[str]
    category: RiskCategory


class RiskClassifier:
    """
    风险分类器
    将合同条款文本分类到 50+ 风险类型
    
    特点：
    - 多关键词匹配
    - 上下文感知
    - 置信度评分
    """
    
    def __init__(self):
        self.keyword_index = self._build_keyword_index()
    
    def _build_keyword_index(self) -> Dict[str, List[RiskType]]:
        """构建关键词索引"""
        index = {}
        
        for risk_type, definition in RISK_TYPE_DEFINITIONS.items():
            for keyword in definition.keywords:
                if keyword not in index:
                    index[keyword] = []
                index[keyword].append(risk_type)
        
        return index
    
    def classify(
        self,
        text: str,
        title: str = ""
    ) -> List[ClassificationResult]:
        """
        分类文本风险类型
        
        Args:
            text: 条款文本
            title: 条款标题
            
        Returns:
            List[ClassificationResult]: 分类结果列表
        """
        full_text = f"{title} {text}".lower()
        results = []
        matched_risk_types = set()
        
        # 关键词匹配
        for keyword, risk_types in self.keyword_index.items():
            if keyword.lower() in full_text:
                for risk_type in risk_types:
                    if risk_type in matched_risk_types:
                        continue
                    
                    definition = get_risk_type_definition(risk_type)
                    if not definition:
                        continue
                    
                    # 计算置信度
                    confidence = self._calculate_confidence(
                        risk_type=risk_type,
                        keyword=keyword,
                        text=full_text,
                        definition=definition
                    )
                    
                    if confidence > 0.5:  # 置信度阈值
                        results.append(ClassificationResult(
                            risk_type=risk_type,
                            confidence=confidence,
                            matched_keywords=[keyword],
                            category=definition.category
                        ))
                        matched_risk_types.add(risk_type)
        
        # 按置信度排序
        results.sort(key=lambda x: -x.confidence)
        
        return results
    
    def _calculate_confidence(
        self,
        risk_type: RiskType,
        keyword: str,
        text: str,
        definition
    ) -> float:
        """计算分类置信度"""
        base_confidence = 0.6
        
        # 关键词匹配数量
        match_count = sum(1 for kw in definition.keywords if kw.lower() in text)
        keyword_bonus = min(0.1 * match_count, 0.2)
        
        # 风险等级加成
        level_bonus = {
            RiskLevel.CRITICAL: 0.1,
            RiskLevel.HIGH: 0.05,
            RiskLevel.MEDIUM: 0.0,
            RiskLevel.LOW: -0.05,
        }.get(definition.default_level, 0.0)
        
        # 上下文增强
        context_bonus = self._check_context(risk_type, text)
        
        confidence = base_confidence + keyword_bonus + level_bonus + context_bonus
        return min(confidence, 0.99)
    
    def _check_context(self, risk_type: RiskType, text: str) -> float:
        """检查上下文增强置信度"""
        bonus = 0.0
        
        # 特定风险类型的上下文检查
        if risk_type == RiskType.UNFAIR_FINAL_INTERPRETATION:
            if re.search(r"最终解释权.*归.*所有", text):
                bonus += 0.2
        
        elif risk_type == RiskType.FINANCIAL_UNLIMITED_LIABILITY:
            if re.search(r"无限.*责任 | 一切.*损失", text):
                bonus += 0.15
        
        elif risk_type == RiskType.UNFAIR_UNILATERAL_TERMINATE:
            if re.search(r"随时.*解除 | 无需.*理由", text):
                bonus += 0.15
        
        elif risk_type == RiskType.AMBIGUOUS_TIME:
            if re.search(r"及时 | 尽快 | 适时", text):
                bonus += 0.1
        
        return bonus
    
    def classify_to_risk_point(
        self,
        text: str,
        title: str = "",
        clause_title: str = ""
    ) -> List[RiskPoint]:
        """
        分类并转换为风险点
        
        Args:
            text: 条款文本
            title: 条款标题
            clause_title: 条款名称
            
        Returns:
            List[RiskPoint]: 风险点列表
        """
        classification_results = self.classify(text, title)
        
        risk_points = []
        for result in classification_results:
            definition = get_risk_type_definition(result.risk_type)
            if not definition:
                continue
            
            risk_point = RiskPoint(
                risk_type=result.risk_type,
                risk_level=definition.default_level,
                clause_title=clause_title or title or "未命名条款",
                risk_content=f"发现{definition.description}，匹配关键词：{', '.join(result.matched_keywords)}",
                original_text=self._extract_original_text(text, result.matched_keywords),
                confidence=result.confidence,
                legal_basis=definition.legal_basis,
                suggestion=self._generate_suggestion(result.risk_type),
                category=result.category,
                analysis_source="classifier"
            )
            
            risk_points.append(risk_point)
        
        return risk_points
    
    def _extract_original_text(self, text: str, keywords: List[str]) -> str:
        """提取原文片段"""
        for keyword in keywords:
            if keyword in text:
                # 提取包含关键词的句子
                start = max(0, text.find(keyword) - 20)
                end = min(len(text), text.find(keyword) + len(keyword) + 20)
                return text[start:end].strip()
        
        return text[:100] if len(text) > 100 else text
    
    def _generate_suggestion(self, risk_type: RiskType) -> str:
        """生成修改建议"""
        suggestions = {
            RiskType.UNFAIR_FINAL_INTERPRETATION: "建议删除'最终解释权'条款，或修改为'本合同解释权由双方共同协商'",
            RiskType.UNFAIR_EXEMPTION_CLAUSE: "建议修改为双方对等的责任承担表述",
            RiskType.FINANCIAL_UNLIMITED_LIABILITY: "建议修改为有限责任，上限为合同金额",
            RiskType.UNFAIR_UNILATERAL_CHANGE: "建议修改为'经双方协商一致后变更'",
            RiskType.AMBIGUOUS_TIME: "建议用具体时间节点替代模糊表述",
        }
        
        return suggestions.get(risk_type, "建议进一步审查该条款")
    
    def get_supported_risk_types(self) -> List[RiskType]:
        """获取支持的风险类型"""
        return list(RISK_TYPE_DEFINITIONS.keys())
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_risk_types": len(RISK_TYPE_DEFINITIONS),
            "total_keywords": len(self.keyword_index),
            "categories": len(RiskCategory),
        }
