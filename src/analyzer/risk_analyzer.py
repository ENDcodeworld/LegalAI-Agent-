"""
合同风险分析模块
基于规则 + AI 识别合同风险点
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    CRITICAL = "严重风险"


class RiskType(Enum):
    """风险类型"""
    UNFAIR_CLAUSE = "不公平条款"
    MISSING_CLAUSE = "缺失关键条款"
    AMBIGUOUS_TERM = "模糊表述"
    LEGAL_ISSUE = "法律合规问题"
    FINANCIAL_RISK = "财务风险"
    PERFORMANCE_RISK = "履约风险"
    TERMINATION_RISK = "终止风险"


@dataclass
class RiskPoint:
    """风险点数据类"""
    risk_type: RiskType  # 风险类型
    risk_level: RiskLevel  # 风险等级
    clause_title: str  # 相关条款标题
    risk_content: str  # 风险内容描述
    original_text: str  # 原文引用
    legal_basis: Optional[str] = None  # 法律依据
    suggestion: Optional[str] = None  # 修改建议
    confidence: float = 0.0  # 置信度 (0-1)


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    contract_title: str
    total_clauses: int
    risk_count: int
    risk_points: List[RiskPoint]
    risk_summary: Dict[str, int]  # 各等级风险数量
    overall_risk_level: RiskLevel
    recommendations: List[str]  # 总体建议


class RiskAnalyzer:
    """合同风险分析器"""
    
    def __init__(self):
        # 高风险关键词列表
        self.high_risk_keywords = {
            RiskType.UNFAIR_CLAUSE: [
                "单方面", "任意", "无需通知", "概不负责", "不承担责任",
                "最终解释权", "保留变更权利", "无需承担", "免除责任"
            ],
            RiskType.AMBIGUOUS_TERM: [
                "适当", "合理", "及时", "相关", "等", "约", "左右",
                "原则上", "一般情况下", "视情况而定"
            ],
            RiskType.FINANCIAL_RISK: [
                "无限责任", "连带责任", "全额赔偿", "一切损失",
                "违约金 %", "滞纳金", "利息"
            ],
            RiskType.PERFORMANCE_RISK: [
                "不可抗力", "免责", "延期", "无法保证", "不承诺",
                "不保证", "可能", "有权变更"
            ],
        }
        
        # 缺失条款检查清单
        self.required_clauses = {
            "买卖合同": ["付款方式", "交付时间", "质量标准", "验收标准", "违约责任"],
            "租赁合同": ["租金", "租期", "押金", "维修责任", "提前解约"],
            "劳动合同": ["工作内容", "工作地点", "工资", "工时", "社保"],
            "合作协议": ["合作内容", "出资方式", "利润分配", "决策机制", "退出机制"],
        }
    
    def analyze(self, contract) -> AnalysisResult:
        """
        分析合同风险
        
        Args:
            contract: ContractParser 解析后的合同对象
            
        Returns:
            AnalysisResult: 分析结果
        """
        risk_points = []
        
        # 1. 逐条分析风险
        for clause in contract.clauses:
            clause_risks = self._analyze_clause(clause)
            risk_points.extend(clause_risks)
        
        # 2. 检查缺失条款
        missing_risks = self._check_missing_clauses(contract)
        risk_points.extend(missing_risks)
        
        # 3. 计算总体风险等级
        overall_risk = self._calculate_overall_risk(risk_points)
        
        # 4. 生成风险汇总
        risk_summary = {
            "严重风险": sum(1 for r in risk_points if r.risk_level == RiskLevel.CRITICAL),
            "高风险": sum(1 for r in risk_points if r.risk_level == RiskLevel.HIGH),
            "中风险": sum(1 for r in risk_points if r.risk_level == RiskLevel.MEDIUM),
            "低风险": sum(1 for r in risk_points if r.risk_level == RiskLevel.LOW),
        }
        
        # 5. 生成总体建议
        recommendations = self._generate_recommendations(risk_points, contract)
        
        return AnalysisResult(
            contract_title=contract.title,
            total_clauses=len(contract.clauses),
            risk_count=len(risk_points),
            risk_points=risk_points,
            risk_summary=risk_summary,
            overall_risk_level=overall_risk,
            recommendations=recommendations
        )
    
    def _analyze_clause(self, clause) -> List[RiskPoint]:
        """分析单个条款的风险"""
        risk_points = []
        text = clause.title + " " + clause.content
        
        # 检查高风险关键词
        for risk_type, keywords in self.high_risk_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # 找到包含关键词的句子
                    sentences = re.split(r'[,.!.!?]', text)
                    for sentence in sentences:
                        if keyword in sentence and len(sentence.strip()) > 5:
                            risk_point = self._create_risk_point(
                                risk_type=risk_type,
                                clause=clause,
                                keyword=keyword,
                                original_text=sentence.strip()
                            )
                            risk_points.append(risk_point)
                            break  # 每个关键词只报告一次
        
        return risk_points
    
    def _check_missing_clauses(self, contract) -> List[RiskPoint]:
        """检查缺失的关键条款"""
        risk_points = []
        
        # 识别合同类型
        contract_type = self._identify_contract_type(contract)
        
        # 获取该类型合同的必备条款
        required = self.required_clauses.get(contract_type, [])
        
        # 检查是否缺失
        existing_clauses = " ".join([c.title + c.content for c in contract.clauses])
        
        for req_clause in required:
            if req_clause not in existing_clauses:
                risk_points.append(RiskPoint(
                    risk_type=RiskType.MISSING_CLAUSE,
                    risk_level=RiskLevel.MEDIUM,
                    clause_title="整体结构",
                    risk_content=f"合同可能缺少'{req_clause}'相关条款",
                    original_text="",
                    legal_basis="根据《民法典》相关规定，该条款对保障双方权益至关重要",
                    suggestion=f"建议添加'{req_clause}'相关条款，明确双方权利义务",
                    confidence=0.7
                ))
        
        return risk_points
    
    def _identify_contract_type(self, contract) -> str:
        """识别合同类型"""
        title = contract.title.lower()
        
        if "买卖" in title:
            return "买卖合同"
        elif "租赁" in title:
            return "租赁合同"
        elif "劳动" in title or "雇佣" in title:
            return "劳动合同"
        elif "合作" in title or "合伙" in title:
            return "合作协议"
        elif "借款" in title or "借贷" in title:
            return "借款合同"
        else:
            return "其他合同"
    
    def _create_risk_point(self, risk_type: RiskType, clause, 
                          keyword: str, original_text: str) -> RiskPoint:
        """创建风险点对象"""
        # 根据风险类型和关键词确定风险等级
        risk_level = self._determine_risk_level(risk_type, keyword)
        
        # 生成风险描述
        risk_content = self._generate_risk_description(risk_type, keyword)
        
        # 生成修改建议
        suggestion = self._generate_suggestion(risk_type, keyword, original_text)
        
        # 法律依据
        legal_basis = self._get_legal_basis(risk_type)
        
        return RiskPoint(
            risk_type=risk_type,
            risk_level=risk_level,
            clause_title=clause.title,
            risk_content=risk_content,
            original_text=original_text,
            legal_basis=legal_basis,
            suggestion=suggestion,
            confidence=0.8
        )
    
    def _determine_risk_level(self, risk_type: RiskType, keyword: str) -> RiskLevel:
        """确定风险等级"""
        critical_keywords = ["概不负责", "不承担责任", "无限责任", "最终解释权"]
        high_keywords = ["单方面", "任意", "无需通知", "免除责任"]
        
        if keyword in critical_keywords:
            return RiskLevel.CRITICAL
        elif keyword in high_keywords:
            return RiskLevel.HIGH
        elif risk_type == RiskType.FINANCIAL_RISK:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_risk_description(self, risk_type: RiskType, keyword: str) -> str:
        """生成风险描述"""
        descriptions = {
            RiskType.UNFAIR_CLAUSE: f"发现不公平条款关键词'{keyword}'，可能导致权利义务不对等",
            RiskType.AMBIGUOUS_TERM: f"发现模糊表述'{keyword}'，可能引发理解分歧",
            RiskType.FINANCIAL_RISK: f"发现财务风险关键词'{keyword}'，可能增加经济负担",
            RiskType.PERFORMANCE_RISK: f"发现履约风险关键词'{keyword}'，可能影响合同执行",
            RiskType.MISSING_CLAUSE: "缺失关键条款，可能导致权益保障不足",
            RiskType.LEGAL_ISSUE: "可能存在法律合规问题",
            RiskType.TERMINATION_RISK: "终止条款可能存在风险",
        }
        return descriptions.get(risk_type, "发现潜在风险")
    
    def _generate_suggestion(self, risk_type: RiskType, keyword: str, 
                            original_text: str) -> str:
        """生成修改建议"""
        suggestions = {
            RiskType.UNFAIR_CLAUSE: "建议修改为双方对等的权利义务表述，明确各自责任范围",
            RiskType.AMBIGUOUS_TERM: "建议用具体数值或明确标准替代模糊表述",
            RiskType.FINANCIAL_RISK: "建议明确赔偿上限，避免无限责任",
            RiskType.PERFORMANCE_RISK: "建议明确履约标准和违约责任",
            RiskType.MISSING_CLAUSE: "建议补充相关条款，完善合同内容",
            RiskType.LEGAL_ISSUE: "建议咨询专业律师，确保合规",
            RiskType.TERMINATION_RISK: "建议明确终止条件和后续处理",
        }
        return suggestions.get(risk_type, "建议进一步审查该条款")
    
    def _get_legal_basis(self, risk_type: RiskType) -> Optional[str]:
        """获取法律依据"""
        legal_basis = {
            RiskType.UNFAIR_CLAUSE: "《民法典》第四百九十七条：格式条款无效的情形",
            RiskType.AMBIGUOUS_TERM: "《民法典》第四百六十六条：合同解释规则",
            RiskType.FINANCIAL_RISK: "《民法典》第五百八十五条：违约金约定",
            RiskType.PERFORMANCE_RISK: "《民法典》第五百七十七条：违约责任",
            RiskType.MISSING_CLAUSE: "《民法典》第四百七十条：合同一般条款",
        }
        return legal_basis.get(risk_type)
    
    def _calculate_overall_risk(self, risk_points: List[RiskPoint]) -> RiskLevel:
        """计算总体风险等级"""
        if not risk_points:
            return RiskLevel.LOW
        
        critical_count = sum(1 for r in risk_points if r.risk_level == RiskLevel.CRITICAL)
        high_count = sum(1 for r in risk_points if r.risk_level == RiskLevel.HIGH)
        
        if critical_count > 0:
            return RiskLevel.CRITICAL
        elif high_count >= 3:
            return RiskLevel.HIGH
        elif high_count >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(self, risk_points: List[RiskPoint], 
                                  contract) -> List[str]:
        """生成总体建议"""
        recommendations = []
        
        # 按风险等级排序
        critical_risks = [r for r in risk_points if r.risk_level == RiskLevel.CRITICAL]
        high_risks = [r for r in risk_points if r.risk_level == RiskLevel.HIGH]
        
        if critical_risks:
            recommendations.append("⚠️ 发现严重风险条款，建议优先修改后再签署")
        
        if high_risks:
            recommendations.append("⚠️ 发现多个高风险条款，建议与对方协商修改")
        
        # 检查缺失条款
        missing = [r for r in risk_points if r.risk_type == RiskType.MISSING_CLAUSE]
        if missing:
            recommendations.append("📋 合同缺少部分关键条款，建议补充完善")
        
        # 通用建议
        if len(risk_points) > 5:
            recommendations.append("💡 建议聘请专业律师进行全面审查")
        
        if not recommendations:
            recommendations.append("✅ 合同整体风险较低，可正常签署")
        
        return recommendations


# 测试代码
if __name__ == "__main__":
    # 导入 parser 模块
    from parser.contract_parser import ContractParser, Clause, ClauseType, Contract
    
    # 示例合同
    sample_contract = """
    买卖合同
    
    甲方：北京科技有限公司
    乙方：上海贸易有限公司
    
    第一条 付款条款
    乙方应在合同签订后 30 日内支付全部价款。甲方保留随时变更价格的权利。
    
    第二条 交付条款
    甲方应于收到款项后及时交付产品，具体时间另行通知。
    
    第三条 质量保证
    甲方对产品质量概不负责，乙方自行承担使用风险。
    
    第四条 违约责任
    乙方违约需承担无限连带责任，赔偿甲方一切损失。
    
    第五条 争议解决
    本合同最终解释权归甲方所有。
    """
    
    # 解析合同
    parser = ContractParser()
    contract = parser.parse_text(sample_contract)
    
    # 分析风险
    analyzer = RiskAnalyzer()
    result = analyzer.analyze(contract)
    
    # 输出结果
    print(f"合同：{result.contract_title}")
    print(f"条款数：{result.total_clauses}")
    print(f"风险点：{result.risk_count}")
    print(f"总体风险：{result.overall_risk_level.value}")
    print("\n风险汇总:")
    for level, count in result.risk_summary.items():
        if count > 0:
            print(f"  {level}: {count}")
    print("\n风险详情:")
    for i, risk in enumerate(result.risk_points[:5], 1):
        print(f"{i}. [{risk.risk_level.value}] {risk.risk_content}")
        print(f"   原文：{risk.original_text[:50]}...")
        print(f"   建议：{risk.suggestion}")
        print()
    print("总体建议:")
    for rec in result.recommendations:
        print(f"  {rec}")
