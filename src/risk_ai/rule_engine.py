"""
规则引擎 - 快速初筛
基于关键词和规则模式进行风险识别
召回率优先，速度优先（毫秒级）
"""

import re
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    from .risk_types import RiskType, RiskLevel, RiskCategory, RISK_TYPE_DEFINITIONS, get_risk_type_definition
    from .models import RiskPoint, AnalysisResult
except ImportError:
    from risk_types import RiskType, RiskLevel, RiskCategory, RISK_TYPE_DEFINITIONS, get_risk_type_definition
    from models import RiskPoint, AnalysisResult


@dataclass
class RulePattern:
    """规则模式"""
    pattern: str  # 正则表达式或关键词
    risk_type: RiskType
    priority: int = 1  # 优先级
    flags: int = 0  # 正则标志


class RuleEngine:
    """
    规则引擎
    快速扫描合同文本，识别明显风险点
    特点：超快速（毫秒级）、高召回率、中等准确率
    """
    
    def __init__(self):
        self.patterns: List[RulePattern] = []
        self._build_patterns()
    
    def _build_patterns(self):
        """构建规则模式库"""
        # 从风险类型定义中自动生成规则
        for risk_type, definition in RISK_TYPE_DEFINITIONS.items():
            for keyword in definition.keywords:
                # 将关键词转换为正则模式
                pattern = self._keyword_to_pattern(keyword)
                self.patterns.append(RulePattern(
                    pattern=pattern,
                    risk_type=risk_type,
                    priority=self._get_priority(risk_type, definition.default_level),
                    flags=re.IGNORECASE
                ))
        
        # 添加特殊规则模式
        self._add_special_patterns()
    
    def _keyword_to_pattern(self, keyword: str) -> str:
        """将关键词转换为正则模式"""
        # 简单实现：直接匹配关键词
        # 可以扩展为更复杂的模式
        return re.escape(keyword)
    
    def _get_priority(self, risk_type: RiskType, level: RiskLevel) -> int:
        """根据风险等级获取优先级"""
        priority_map = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1,
        }
        return priority_map.get(level, 1)
    
    def _add_special_patterns(self):
        """添加特殊规则模式"""
        # 最终解释权模式
        self.patterns.append(RulePattern(
            pattern=r"最终解释权\s*(归 | 属于 | 由).*(所有 | 享有)",
            risk_type=RiskType.UNFAIR_FINAL_INTERPRETATION,
            priority=4,
            flags=re.IGNORECASE
        ))
        
        # 概不负责模式
        self.patterns.append(RulePattern(
            pattern=r"概不\s*(负责 | 承担 | 退换)",
            risk_type=RiskType.UNFAIR_EXEMPTION_CLAUSE,
            priority=4,
            flags=re.IGNORECASE
        ))
        
        # 无限责任模式
        self.patterns.append(RulePattern(
            pattern=r"无限\s*(责任 | 连带)",
            risk_type=RiskType.FINANCIAL_UNLIMITED_LIABILITY,
            priority=4,
            flags=re.IGNORECASE
        ))
        
        # 随时解除模式
        self.patterns.append(RulePattern(
            pattern=r"(有权 | 可以)\s*随时\s*(解除 | 终止 | 变更 | 调整)",
            risk_type=RiskType.UNFAIR_UNILATERAL_TERMINATE,
            priority=3,
            flags=re.IGNORECASE
        ))
        
        # 模糊时间模式
        self.patterns.append(RulePattern(
            pattern=r"(及时 | 尽快 | 适时 | 及时)",
            risk_type=RiskType.AMBIGUOUS_TIME,
            priority=1,
            flags=re.IGNORECASE
        ))
    
    def scan(self, text: str, clause_title: str = "") -> List[RiskPoint]:
        """
        扫描文本，识别风险点
        
        Args:
            text: 合同条款文本
            clause_title: 条款标题
            
        Returns:
            List[RiskPoint]: 识别的风险点列表
        """
        start_time = time.time()
        risk_points = []
        matched_patterns = set()  # 避免重复匹配
        
        # 合并标题和正文
        full_text = f"{clause_title} {text}"
        
        for pattern_obj in sorted(self.patterns, key=lambda p: -p.priority):
            # 跳过已匹配的风险类型（每个风险类型只报告一次）
            if pattern_obj.risk_type in matched_patterns:
                continue
            
            # 执行匹配
            matches = re.finditer(pattern_obj.pattern, full_text, pattern_obj.flags)
            
            for match in matches:
                matched_text = match.group(0)
                
                # 获取风险类型定义
                definition = get_risk_type_definition(pattern_obj.risk_type)
                if not definition:
                    continue
                
                # 创建风险点
                risk_point = self._create_risk_point(
                    risk_type=pattern_obj.risk_type,
                    definition=definition,
                    clause_title=clause_title,
                    original_text=matched_text,
                    matched_text=full_text
                )
                
                risk_points.append(risk_point)
                matched_patterns.add(pattern_obj.risk_type)
                break  # 每个模式只取第一个匹配
        
        # 记录分析时间
        analysis_time = (time.time() - start_time) * 1000
        for rp in risk_points:
            rp.analysis_time_ms = analysis_time
            rp.analysis_source = "rule"
        
        return risk_points
    
    def _create_risk_point(
        self,
        risk_type: RiskType,
        definition,
        clause_title: str,
        original_text: str,
        matched_text: str
    ) -> RiskPoint:
        """创建风险点对象"""
        # 确定风险等级
        risk_level = definition.default_level
        
        # 生成风险描述
        risk_content = f"发现{definition.description}，关键词：'{original_text}'"
        
        # 生成修改建议
        suggestion = self._generate_suggestion(risk_type, original_text)
        
        return RiskPoint(
            risk_type=risk_type,
            risk_level=risk_level,
            clause_title=clause_title or "未命名条款",
            risk_content=risk_content,
            original_text=original_text,
            confidence=0.75,  # 规则引擎基础置信度
            legal_basis=definition.legal_basis,
            suggestion=suggestion,
            category=definition.category,
        )
    
    def _generate_suggestion(self, risk_type: RiskType, original_text: str) -> str:
        """生成修改建议"""
        suggestions = {
            RiskType.UNFAIR_FINAL_INTERPRETATION: "建议删除'最终解释权'条款，或修改为'本合同解释权由双方共同协商'",
            RiskType.UNFAIR_EXEMPTION_CLAUSE: "建议修改为双方对等的责任承担表述，明确各自责任范围",
            RiskType.FINANCIAL_UNLIMITED_LIABILITY: "建议修改为有限责任，上限为合同金额或实际损失",
            RiskType.UNFAIR_UNILATERAL_TERMINATE: "建议修改为双方平等的解除权，或设定合理的解除条件",
            RiskType.AMBIGUOUS_TIME: "建议用具体时间节点替代模糊表述，如'3 个工作日内'",
        }
        
        default_suggestion = "建议进一步审查该条款，确保权利义务对等"
        return suggestions.get(risk_type, default_suggestion)
    
    def scan_full_contract(self, clauses: List) -> List[RiskPoint]:
        """
        扫描完整合同
        
        Args:
            clauses: 条款列表（来自 ContractParser）
            
        Returns:
            List[RiskPoint]: 所有风险点
        """
        all_risks = []
        
        for clause in clauses:
            clause_risks = self.scan(
                text=clause.content,
                clause_title=clause.title
            )
            all_risks.extend(clause_risks)
        
        return all_risks
    
    def get_stats(self) -> Dict:
        """获取引擎统计信息"""
        return {
            "total_patterns": len(self.patterns),
            "risk_types_covered": len(set(p.risk_type for p in self.patterns)),
        }
