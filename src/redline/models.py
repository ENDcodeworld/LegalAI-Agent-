"""
Redline 模块数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


class RedlineLevel(Enum):
    """
    Redline 建议质量分级
    
    L1 - 通用建议：泛化建议，无具体文本
    L2 - 方向建议：指出修改方向
    L3 - 具体建议：提供具体修改文本
    L4 - 智能 Redline：具体文本 + 法律依据 + 市场基准
    """
    L1_GENERIC = "L1-通用建议"
    L2_DIRECTION = "L2-方向建议"
    L3_SPECIFIC = "L3-具体建议"
    L4_INTELLIGENT = "L4-智能 Redline"


class RedlineType(Enum):
    """Redline 修改类型"""
    ADDITION = "新增"  # 添加内容
    DELETION = "删除"  # 删除内容
    MODIFICATION = "修改"  # 修改内容
    RELOCATION = "调整位置"  # 调整条款位置


class RiskSeverity(Enum):
    """风险严重程度"""
    CRITICAL = "严重"  # 必须修改，否则合同不可签署
    HIGH = "高"  # 强烈建议修改
    MEDIUM = "中"  # 建议修改
    LOW = "低"  # 可选修改


@dataclass
class LegalBasis:
    """
    法律依据
    
    Attributes:
        law_name: 法律法规名称
        article: 具体条款号
        content: 条款内容
        relevance: 相关性说明
    """
    law_name: str  # 如 "《中华人民共和国民法典》"
    article: str  # 如 "第 543 条"
    content: str  # 条款具体内容
    relevance: str  # 与当前风险的关联性说明


@dataclass
class MarketBenchmark:
    """
    市场基准数据
    
    Attributes:
        industry: 所属行业
        clause_type: 条款类型
        standard_practice: 行业惯例描述
        adoption_rate: 采用率（0-1）
        sample_clauses: 示例条款列表
    """
    industry: str  # 如 "互联网 SaaS"
    clause_type: str  # 如 "价格调整条款"
    standard_practice: str  # 行业惯例描述
    adoption_rate: float  # 市场采用率，0-1 之间
    sample_clauses: List[str] = field(default_factory=list)  # 市场常见条款示例


@dataclass
class RedlineAnnotation:
    """
    红线圈注信息
    
    Attributes:
        start_pos: 原文起始位置（字符索引）
        end_pos: 原文结束位置（字符索引）
        annotation_type: 圈注类型（高亮/删除线/下划线等）
        color: 圈注颜色
        comment: 圈注说明
    """
    start_pos: int
    end_pos: int
    annotation_type: str  # "highlight", "strikethrough", "underline"
    color: str  # "red", "yellow", "green"
    comment: str


@dataclass
class RedlineSuggestion:
    """
    Redline 修改建议
    
    核心数据结构，包含完整的修改建议信息
    
    Attributes:
        suggestion_id: 建议唯一标识
        risk_point_id: 关联的风险点 ID
        original_text: 原文内容
        suggested_text: 建议修改后的文本
        redline_type: 修改类型（新增/删除/修改）
        level: 建议质量等级（L1-L4）
        rationale: 修改理由说明
        legal_basis: 法律依据列表
        market_benchmark: 市场基准数据
        annotations: 红线圈注信息
        confidence: 置信度（0-1）
        adoption_probability: 预计采纳率（0-1）
        priority: 修改优先级
        tags: 标签列表
    """
    suggestion_id: str
    risk_point_id: str
    original_text: str
    suggested_text: str
    redline_type: RedlineType
    level: RedlineLevel
    rationale: str  # 修改理由
    legal_basis: List[LegalBasis] = field(default_factory=list)
    market_benchmark: Optional[MarketBenchmark] = None
    annotations: List[RedlineAnnotation] = field(default_factory=list)
    confidence: float = 0.0  # 置信度
    adoption_probability: float = 0.0  # 预计采纳率
    priority: RiskSeverity = RiskSeverity.MEDIUM
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'suggestion_id': self.suggestion_id,
            'risk_point_id': self.risk_point_id,
            'original_text': self.original_text,
            'suggested_text': self.suggested_text,
            'redline_type': self.redline_type.value,
            'level': self.level.value,
            'rationale': self.rationale,
            'legal_basis': [
                {
                    'law_name': lb.law_name,
                    'article': lb.article,
                    'content': lb.content,
                    'relevance': lb.relevance
                }
                for lb in self.legal_basis
            ],
            'market_benchmark': {
                'industry': self.market_benchmark.industry,
                'clause_type': self.market_benchmark.clause_type,
                'standard_practice': self.market_benchmark.standard_practice,
                'adoption_rate': self.market_benchmark.adoption_rate,
                'sample_clauses': self.market_benchmark.sample_clauses
            } if self.market_benchmark else None,
            'annotations': [
                {
                    'start_pos': a.start_pos,
                    'end_pos': a.end_pos,
                    'annotation_type': a.annotation_type,
                    'color': a.color,
                    'comment': a.comment
                }
                for a in self.annotations
            ],
            'confidence': self.confidence,
            'adoption_probability': self.adoption_probability,
            'priority': self.priority.value,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }
    
    def get_diff_display(self) -> str:
        """
        获取差异显示文本（用于 UI 展示）
        
        Returns:
            带有标记的差异文本
        """
        # 简单实现：使用标记符号
        if self.redline_type == RedlineType.DELETION:
            return f"~~{self.original_text}~~ → {self.suggested_text}"
        elif self.redline_type == RedlineType.ADDITION:
            return f"{self.original_text} → **{self.suggested_text}**"
        else:  # MODIFICATION
            return f"~~{self.original_text}~~ → **{self.suggested_text}**"


@dataclass
class ClauseRedline:
    """
    条款级别的 Redline 汇总
    
    Attributes:
        clause_id: 条款 ID
        clause_title: 条款标题
        clause_content: 条款原文
        suggestions: 该条款的所有修改建议
        risk_level: 风险等级
        overall_suggestion: 整体修改建议（合并所有建议后的完整条款）
    """
    clause_id: str
    clause_title: str
    clause_content: str
    suggestions: List[RedlineSuggestion]
    risk_level: RiskSeverity
    overall_suggestion: str = ""  # 合并后的完整条款文本


@dataclass
class RedlineReport:
    """
    Redline 报告
    
    完整的合同审阅报告，包含所有修改建议
    
    Attributes:
        report_id: 报告唯一标识
        contract_id: 合同 ID
        contract_name: 合同名称
        generated_at: 生成时间
        total_suggestions: 建议总数
        suggestions_by_level: 按等级分类的建议数量
        suggestions_by_priority: 按优先级分类的建议数量
        clause_redlines: 各条款的 Redline 详情
        executive_summary: 执行摘要
        overall_risk_assessment: 整体风险评估
        key_recommendations: 关键建议（Top 5）
        l4_adoption_rate: L4 级建议占比
    """
    report_id: str
    contract_id: str
    contract_name: str
    generated_at: datetime
    total_suggestions: int
    suggestions_by_level: Dict[str, int]
    suggestions_by_priority: Dict[str, int]
    clause_redlines: List[ClauseRedline]
    executive_summary: str
    overall_risk_assessment: str
    key_recommendations: List[str]
    l4_adoption_rate: float = 0.0  # L4 级建议占比
    all_suggestions: List[RedlineSuggestion] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'report_id': self.report_id,
            'contract_id': self.contract_id,
            'contract_name': self.contract_name,
            'generated_at': self.generated_at.isoformat(),
            'total_suggestions': self.total_suggestions,
            'suggestions_by_level': self.suggestions_by_level,
            'suggestions_by_priority': self.suggestions_by_priority,
            'clause_redlines': [
                {
                    'clause_id': cr.clause_id,
                    'clause_title': cr.clause_title,
                    'clause_content': cr.clause_content,
                    'suggestions': [s.to_dict() for s in cr.suggestions],
                    'risk_level': cr.risk_level.value,
                    'overall_suggestion': cr.overall_suggestion
                }
                for cr in self.clause_redlines
            ],
            'executive_summary': self.executive_summary,
            'overall_risk_assessment': self.overall_risk_assessment,
            'key_recommendations': self.key_recommendations,
            'l4_adoption_rate': self.l4_adoption_rate,
            'all_suggestions': [s.to_dict() for s in self.all_suggestions]
        }
    
    def get_statistics(self) -> Dict:
        """获取报告统计信息"""
        return {
            'total_suggestions': self.total_suggestions,
            'l4_suggestions': self.suggestions_by_level.get('L4-智能 Redline', 0),
            'l4_adoption_rate': f"{self.l4_adoption_rate * 100:.1f}%",
            'critical_count': self.suggestions_by_priority.get('严重', 0),
            'high_count': self.suggestions_by_priority.get('高', 0),
            'medium_count': self.suggestions_by_priority.get('中', 0),
            'low_count': self.suggestions_by_priority.get('低', 0),
            'avg_confidence': sum(s.confidence for s in self.all_suggestions) / len(self.all_suggestions) if self.all_suggestions else 0,
            'avg_adoption_prob': sum(s.adoption_probability for s in self.all_suggestions) / len(self.all_suggestions) if self.all_suggestions else 0
        }


@dataclass
class RedlineConfig:
    """
    Redline 生成配置
    
    Attributes:
        target_level: 目标建议等级（默认 L4）
        include_legal_basis: 是否包含法律依据
        include_market_benchmark: 是否包含市场基准
        min_confidence: 最小置信度阈值
        max_suggestions_per_clause: 每条条款最大建议数
        output_format: 输出格式
    """
    target_level: RedlineLevel = RedlineLevel.L4_INTELLIGENT
    include_legal_basis: bool = True
    include_market_benchmark: bool = True
    min_confidence: float = 0.6
    max_suggestions_per_clause: int = 5
    output_format: str = "json"  # json, pdf, word, html
