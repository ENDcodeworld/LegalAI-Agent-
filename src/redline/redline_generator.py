"""
智能 Redline 生成器

实现 LawGeex 专利级智能修改建议，达到 L4 级自动化水平
目标：80%+ 建议可直接采用
"""

import uuid
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .models import (
    RedlineSuggestion,
    RedlineLevel,
    RedlineType,
    RedlineReport,
    ClauseRedline,
    MarketBenchmark,
    LegalBasis,
    RedlineAnnotation,
    RiskSeverity,
    RedlineConfig
)


class SmartRedlineGenerator:
    """
    智能 Redline 生成器
    
    核心功能：
    1. 识别风险条款后，自动生成修改建议
    2. 红线圈注：标记需要修改的原文位置
    3. 修改文本：提供具体的修改后文本
    4. 修改说明：解释为什么这样修改
    5. 法律依据：引用相关法律法规
    6. 市场基准：提供行业惯例参考
    """
    
    def __init__(self, llm_client=None, market_db=None, legal_db=None):
        """
        初始化 Redline 生成器
        
        Args:
            llm_client: 大语言模型客户端（用于生成修改建议）
            market_db: 市场条款数据库（用于检索行业惯例）
            legal_db: 法律法规数据库（用于检索法律依据）
        """
        self.llm_client = llm_client
        self.market_db = market_db or self._init_default_market_db()
        self.legal_db = legal_db or self._init_default_legal_db()
        self.config = RedlineConfig()
        
        # 风险类型到修改策略的映射
        self.risk_strategies = self._init_risk_strategies()
    
    def _init_default_market_db(self) -> Dict:
        """初始化默认市场基准数据库"""
        return {
            "价格调整条款": {
                "industry": "通用",
                "standard_practice": "价格调整需经双方书面协商一致，并提前 30 日通知对方",
                "adoption_rate": 0.85,
                "sample_clauses": [
                    "价格调整需经双方书面协商一致，并提前 30 日通知对方。未经协商一致，任何一方不得单方变更。",
                    "合同价格在本合同有效期内保持不变。如需调整，应由双方协商并签订补充协议。"
                ]
            },
            "单方解除权": {
                "industry": "通用",
                "standard_practice": "合同解除需经双方协商一致，或符合法定解除条件",
                "adoption_rate": 0.90,
                "sample_clauses": [
                    "任何一方欲解除本合同，应提前 30 日书面通知对方，经双方协商一致后方可解除。",
                    "除本合同另有约定或法律规定外，任何一方不得单方解除合同。"
                ]
            },
            "违约责任": {
                "industry": "通用",
                "standard_practice": "违约金不超过造成损失的 30%，且应有明确上限",
                "adoption_rate": 0.88,
                "sample_clauses": [
                    "违约方应赔偿守约方因此遭受的实际损失，但赔偿总额不超过合同总金额的 30%。",
                    "违约金约定为合同总金额的 20%，如实际损失超过违约金，守约方可就超出部分继续追偿。"
                ]
            },
            "争议解决": {
                "industry": "通用",
                "standard_practice": "优先选择原告所在地或合同履行地法院/仲裁机构",
                "adoption_rate": 0.75,
                "sample_clauses": [
                    "因本合同引起的争议，双方应友好协商解决；协商不成的，提交原告所在地人民法院诉讼解决。",
                    "因本合同引起的争议，提交合同履行地仲裁委员会按照其仲裁规则进行仲裁。"
                ]
            },
            "最终解释权": {
                "industry": "通用",
                "standard_practice": "合同解释权应由双方共同享有，或按照法律规定进行解释",
                "adoption_rate": 0.95,
                "sample_clauses": [
                    "本合同的解释权由甲乙双方共同享有。",
                    "对本合同条款的理解有争议的，应当按照合同所使用的词句、合同的有关条款、合同的目的、交易习惯以及诚实信用原则，确定该条款的真实意思。"
                ]
            },
            "保密条款": {
                "industry": "通用",
                "standard_practice": "保密期限通常为 2-5 年，不应永久保密",
                "adoption_rate": 0.82,
                "sample_clauses": [
                    "保密义务自本合同生效之日起至合同终止后 3 年内有效。",
                    "本保密条款的有效期为合同期限及合同终止后 2 年。"
                ]
            },
            "知识产权": {
                "industry": "技术服务",
                "standard_practice": "背景知识产权归各自所有，新产生知识产权协商约定",
                "adoption_rate": 0.80,
                "sample_clauses": [
                    "双方在合作前已有的知识产权归各自所有。合作期间新产生的知识产权，由双方另行协商约定归属。",
                    "乙方为履行本合同所创作的成果，知识产权归乙方所有，甲方享有永久使用权。"
                ]
            },
            "不可抗力": {
                "industry": "通用",
                "standard_practice": "不可抗力事件发生后应及时通知，并提供证明",
                "adoption_rate": 0.92,
                "sample_clauses": [
                    "因不可抗力导致无法履行合同的，受影响方应在 5 日内通知对方，并在 15 日内提供相关证明文件。",
                    "不可抗力事件持续超过 30 日的，任何一方有权解除合同。"
                ]
            },
            "付款条款": {
                "industry": "通用",
                "standard_practice": "分期付款，保留质保金",
                "adoption_rate": 0.85,
                "sample_clauses": [
                    "签约后 7 日内支付 30% 预付款，交付验收后 15 日内支付 60%，质保期满后支付 10% 质保金。",
                    "货款分三期支付：合同签订后支付 30%，货到验收后支付 60%，质保期届满后支付 10%。"
                ]
            }
        }
    
    def _init_default_legal_db(self) -> Dict:
        """初始化默认法律法规数据库"""
        return {
            "单方变更权": [
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 543 条",
                    content="当事人协商一致，可以变更合同。",
                    relevance="合同变更需经双方协商一致，单方变更权违反该规定"
                ),
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 496 条",
                    content="格式条款是当事人为了重复使用而预先拟定，并在订立合同时未与对方协商的条款。",
                    relevance="单方变更权条款可能构成无效格式条款"
                )
            ],
            "单方解除权": [
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 562 条",
                    content="当事人协商一致，可以解除合同。当事人可以约定一方解除合同的事由。解除合同的事由发生时，解除权人可以解除合同。",
                    relevance="合同解除应遵循约定或法定条件，不得随意单方解除"
                ),
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 563 条",
                    content="有下列情形之一的，当事人可以解除合同：（一）因不可抗力致使不能实现合同目的；（二）在履行期限届满前，当事人一方明确表示或者以自己的行为表明不履行主要债务...",
                    relevance="法定解除权有明确限定条件"
                )
            ],
            "无限责任": [
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 584 条",
                    content="当事人一方不履行合同义务或者履行合同义务不符合约定，造成对方损失的，损失赔偿额应当相当于因违约所造成的损失，包括合同履行后可以获得的利益；但是，不得超过违约一方订立合同时预见到或者应当预见到的因违约可能造成的损失。",
                    relevance="损害赔偿应以可预见为限，不应承担无限责任"
                ),
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 585 条",
                    content="当事人可以约定一方违约时应当根据违约情况向对方支付一定数额的违约金，也可以约定因违约产生的损失赔偿额的计算方法。约定的违约金过分高于造成的损失的，人民法院或者仲裁机构可以根据当事人的请求予以适当减少。",
                    relevance="违约金过高可请求调整"
                )
            ],
            "最终解释权": [
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 497 条",
                    content="有下列情形之一的，该格式条款无效：...（二）提供格式条款一方不合理地免除或者减轻其责任、加重对方责任、限制对方主要权利；（三）提供格式条款一方排除对方主要权利。",
                    relevance="'最终解释权'条款排除对方权利，属于无效格式条款"
                ),
                LegalBasis(
                    law_name="《中华人民共和国消费者权益保护法》",
                    article="第 26 条",
                    content="经营者不得以格式条款、通知、声明、店堂告示等方式，作出排除或者限制消费者权利、减轻或者免除经营者责任、加重消费者责任等对消费者不公平、不合理的规定，不得利用格式条款并借助技术手段强制交易。格式条款、通知、声明、店堂告示等含有前款所列内容的，其内容无效。",
                    relevance="最终解释权条款对消费者不公平，属于无效条款"
                )
            ],
            "模糊表述": [
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 466 条",
                    content="当事人对合同条款的理解有争议的，应当依据本法第一百四十二条第一款的规定，确定争议条款的含义。合同文本采用两种以上文字订立并约定具有同等效力的，对各文本使用的词句推定具有相同含义。各文本使用的词句不一致的，应当根据合同的相关条款、性质、目的以及诚信原则等予以解释。",
                    relevance="模糊表述易引发争议，应按合同解释规则处理"
                )
            ],
            "违约金过高": [
                LegalBasis(
                    law_name="《中华人民共和国民法典》",
                    article="第 585 条",
                    content="约定的违约金过分高于造成的损失的，人民法院或者仲裁机构可以根据当事人的请求予以适当减少。",
                    relevance="违约金超过损失 30% 一般可认定为过分高于"
                ),
                LegalBasis(
                    law_name="《最高人民法院关于适用<中华人民共和国合同法>若干问题的解释（二）》",
                    article="第 29 条",
                    content="当事人主张约定的违约金过高请求予以适当减少的，人民法院应当以实际损失为基础，兼顾合同的履行情况、当事人的过错程度以及预期利益等综合因素，根据公平原则和诚实信用原则予以衡量，并作出裁决。当事人约定的违约金超过造成损失的百分之三十的，一般可以认定为合同法第一百一十四条第二款规定的'过分高于造成的损失'。",
                    relevance="明确违约金超过损失 30% 为过高标准"
                )
            ]
        }
    
    def _init_risk_strategies(self) -> Dict:
        """初始化风险类型到修改策略的映射"""
        return {
            "单方变更权": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.HIGH,
                "template": "建议修改为：价格/条款调整需经双方书面协商一致，并提前 {notice_days} 日通知对方。未经协商一致，任何一方不得单方变更。"
            },
            "单方解除权": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.HIGH,
                "template": "建议修改为：任何一方欲解除本合同，应提前 {notice_days} 日书面通知对方，经双方协商一致后方可解除。除本合同另有约定或法律规定外，任何一方不得单方解除合同。"
            },
            "无限责任": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.CRITICAL,
                "template": "建议修改为：违约方应赔偿守约方因此遭受的实际损失，但赔偿总额不超过合同总金额的 {liability_cap}%。"
            },
            "最终解释权": {
                "redline_type": RedlineType.DELETION,
                "priority": RiskSeverity.CRITICAL,
                "template": "建议删除该条款。'最终解释权'属于无效格式条款，违反《民法典》第 497 条。"
            },
            "模糊表述": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.MEDIUM,
                "template": "建议将'{vague_term}'修改为具体明确的表述，如：{specific_term}"
            },
            "违约金过高": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.HIGH,
                "template": "建议修改为：违约金为合同总金额的 {penalty_rate}%，如实际损失超过违约金，守约方可就超出部分继续追偿。"
            },
            "保密期限过长": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.MEDIUM,
                "template": "建议修改为：保密义务自本合同生效之日起至合同终止后 {confidentiality_years} 年内有效。"
            },
            "付款条件苛刻": {
                "redline_type": RedlineType.MODIFICATION,
                "priority": RiskSeverity.HIGH,
                "template": "建议修改为：签约后 7 日内支付 30% 预付款，交付验收后 15 日内支付 60%，质保期满后支付 10% 质保金。"
            }
        }
    
    def generate(self, risk_point) -> RedlineSuggestion:
        """
        为单个风险点生成 Redline 建议
        
        Args:
            risk_point: 风险点对象（来自 RiskAnalyzer）
            
        Returns:
            RedlineSuggestion: 生成的修改建议
        """
        # 1. 识别风险类型
        risk_type = self._identify_risk_type(risk_point)
        
        # 2. 检索市场基准
        market_benchmark = self._search_market_benchmark(risk_type, risk_point.original_text)
        
        # 3. 检索法律依据
        legal_basis_list = self._search_legal_basis(risk_type)
        
        # 4. 生成修改建议文本
        suggested_text, rationale = self._generate_suggestion_text(
            risk_point=risk_point,
            risk_type=risk_type,
            market_benchmark=market_benchmark,
            legal_basis=legal_basis_list
        )
        
        # 5. 确定修改类型和优先级
        strategy = self.risk_strategies.get(risk_type, {})
        redline_type = strategy.get("redline_type", RedlineType.MODIFICATION)
        priority = strategy.get("priority", RiskSeverity.MEDIUM)
        
        # 6. 生成红线圈注
        annotations = self._generate_annotations(risk_point.original_text, suggested_text, redline_type)
        
        # 7. 计算置信度和采纳率
        confidence = self._calculate_confidence(risk_point, legal_basis_list, market_benchmark)
        adoption_probability = self._estimate_adoption_probability(
            risk_type, priority, confidence, market_benchmark
        )
        
        # 8. 确定建议等级
        level = self._determine_level(legal_basis_list, market_benchmark, suggested_text)
        
        # 9. 创建建议对象
        suggestion = RedlineSuggestion(
            suggestion_id=str(uuid.uuid4())[:8],
            risk_point_id=getattr(risk_point, 'id', str(uuid.uuid4())[:8]),
            original_text=risk_point.original_text,
            suggested_text=suggested_text,
            redline_type=redline_type,
            level=level,
            rationale=rationale,
            legal_basis=legal_basis_list,
            market_benchmark=market_benchmark,
            annotations=annotations,
            confidence=confidence,
            adoption_probability=adoption_probability,
            priority=priority,
            tags=[risk_type]
        )
        
        return suggestion
    
    def _identify_risk_type(self, risk_point) -> str:
        """识别风险类型"""
        # 从风险内容中推断（优先基于文本识别）
        text = risk_point.original_text + " " + getattr(risk_point, 'risk_content', '')
        
        # 单方变更权：包含"单方"、"随时"、"任意"、"无需通知"、"保留变更"等
        if any(kw in text for kw in ["单方", "随时", "任意", "无需通知", "保留变更", "有权随时"]):
            return "单方变更权"
        elif any(kw in text for kw in ["最终解释权", "解释权归"]):
            return "最终解释权"
        elif any(kw in text for kw in ["无限责任", "一切损失", "全部损失", "连带责任"]):
            return "无限责任"
        elif any(kw in text for kw in ["适当", "合理", "及时", "相关"]):
            return "模糊表述"
        elif any(kw in text for kw in ["违约金", "赔偿"]):
            return "违约金过高"
        elif any(kw in text for kw in ["永久", "长期"]):
            return "保密期限过长"
        elif any(kw in text for kw in ["单方解除", "随时解除", "随时解除"]):
            return "单方解除权"
        
        # 如果没有从文本中识别出具体类型，再使用 risk_type 属性
        if hasattr(risk_point, 'risk_type'):
            risk_type = risk_point.risk_type
            if hasattr(risk_type, 'value'):
                rt_value = risk_type.value
                # 如果是具体的风险类型，返回它
                if rt_value not in ["其他", "未知", "UNKNOWN"]:
                    return rt_value
        
        return "其他风险"
    
    def _search_market_benchmark(self, risk_type: str, original_text: str) -> Optional[MarketBenchmark]:
        """检索市场基准数据"""
        # 遍历市场数据库，找到最匹配的基准
        for key, data in self.market_db.items():
            if key in risk_type or risk_type in key:
                return MarketBenchmark(
                    industry=data["industry"],
                    clause_type=key,
                    standard_practice=data["standard_practice"],
                    adoption_rate=data["adoption_rate"],
                    sample_clauses=data["sample_clauses"]
                )
        
        # 如果没有精确匹配，返回通用基准
        return MarketBenchmark(
            industry="通用",
            clause_type=risk_type,
            standard_practice="遵循公平原则，保障双方合法权益",
            adoption_rate=0.75,
            sample_clauses=[]
        )
    
    def _search_legal_basis(self, risk_type: str) -> List[LegalBasis]:
        """检索法律依据"""
        # 直接匹配
        if risk_type in self.legal_db:
            return self.legal_db[risk_type]
        
        # 模糊匹配
        for key, laws in self.legal_db.items():
            if key in risk_type or risk_type in key:
                return laws
        
        # 默认返回
        return [
            LegalBasis(
                law_name="《中华人民共和国民法典》",
                article="第 6 条",
                content="民事主体从事民事活动，应当遵循公平原则，合理确定各方的权利和义务。",
                relevance="合同条款应遵循公平原则"
            )
        ]
    
    def _generate_suggestion_text(
        self,
        risk_point,
        risk_type: str,
        market_benchmark: Optional[MarketBenchmark],
        legal_basis: List[LegalBasis]
    ) -> Tuple[str, str]:
        """
        生成修改建议文本和理由
        
        Returns:
            (suggested_text, rationale)
        """
        original_text = risk_point.original_text
        
        # 使用预设模板生成建议
        strategy = self.risk_strategies.get(risk_type)
        
        if strategy and "template" in strategy:
            template = strategy["template"]
            
            # 根据风险类型填充模板参数
            if risk_type == "单方变更权":
                suggested_text = template.format(notice_days=30)
                rationale = f"原条款赋予一方单方变更权，违反《民法典》第 543 条关于合同变更需协商一致的规定。{market_benchmark.standard_practice if market_benchmark else ''}"
            
            elif risk_type == "单方解除权":
                suggested_text = template.format(notice_days=30)
                rationale = f"原条款赋予一方单方解除权，可能导致合同不稳定。{market_benchmark.standard_practice if market_benchmark else ''}"
            
            elif risk_type == "无限责任":
                suggested_text = template.format(liability_cap=30)
                rationale = f"原条款要求承担无限责任，违反《民法典》第 584 条关于可预见损失的规定。建议设置合理赔偿上限。"
            
            elif risk_type == "最终解释权":
                suggested_text = "建议删除该条款，或修改为：本合同的解释权由甲乙双方共同享有，对合同条款的理解有争议的，应当按照合同所使用的词句、合同的有关条款、合同的目的、交易习惯以及诚实信用原则，确定该条款的真实意思。"
                rationale = f"'最终解释权归甲方所有'属于无效格式条款，违反《民法典》第 497 条和《消费者权益保护法》第 26 条。{market_benchmark.standard_practice if market_benchmark else ''}"
            
            elif risk_type == "模糊表述":
                # 提取模糊词
                vague_terms = ["适当", "合理", "及时", "相关"]
                found_vague = next((t for t in vague_terms if t in original_text), None)
                if found_vague:
                    specific_map = {
                        "适当": "经双方协商确定的合理",
                        "合理": "符合行业标准的",
                        "及时": "在 3 个工作日内",
                        "相关": "与本合同直接相关的"
                    }
                    suggested_text = template.format(
                        vague_term=found_vague,
                        specific_term=specific_map.get(found_vague, "明确具体的")
                    )
                else:
                    suggested_text = "建议用具体数值或明确标准替代模糊表述"
                rationale = f"模糊表述易引发理解分歧，根据《民法典》第 466 条，应使用明确具体的表述。"
            
            elif risk_type == "违约金过高":
                suggested_text = template.format(penalty_rate=20)
                rationale = f"根据《民法典》第 585 条及相关司法解释，违约金超过造成损失 30% 的，可认定为过分高于。建议调整为合同金额的 20%。"
            
            else:
                suggested_text = template
                rationale = f"原条款存在{risk_type}风险，建议按市场惯例修改。"
        else:
            # 通用建议
            suggested_text = f"建议修改为公平合理的表述，保障双方合法权益"
            rationale = f"原条款存在{risk_type}风险，建议参考行业惯例进行修改。"
        
        return suggested_text, rationale
    
    def _generate_annotations(
        self,
        original_text: str,
        suggested_text: str,
        redline_type: RedlineType
    ) -> List[RedlineAnnotation]:
        """生成红线圈注信息"""
        annotations = []
        
        if redline_type == RedlineType.DELETION:
            # 整段删除
            annotations.append(RedlineAnnotation(
                start_pos=0,
                end_pos=len(original_text),
                annotation_type="strikethrough",
                color="red",
                comment="建议删除"
            ))
        elif redline_type == RedlineType.MODIFICATION:
            # 标记修改区域（简化实现：标记整段）
            annotations.append(RedlineAnnotation(
                start_pos=0,
                end_pos=len(original_text),
                annotation_type="highlight",
                color="yellow",
                comment="建议修改"
            ))
        elif redline_type == RedlineType.ADDITION:
            # 新增内容
            annotations.append(RedlineAnnotation(
                start_pos=len(original_text),
                end_pos=len(original_text),
                annotation_type="underline",
                color="green",
                comment="建议新增"
            ))
        
        return annotations
    
    def _calculate_confidence(
        self,
        risk_point,
        legal_basis: List[LegalBasis],
        market_benchmark: Optional[MarketBenchmark]
    ) -> float:
        """计算建议置信度"""
        confidence = 0.5  # 基础置信度
        
        # 有法律依据加分
        if legal_basis:
            confidence += 0.2
        
        # 有市场基准加分
        if market_benchmark and market_benchmark.adoption_rate > 0.8:
            confidence += 0.2
        
        # 风险等级高加分（更确定是风险）
        if hasattr(risk_point, 'risk_level'):
            level = risk_point.risk_level
            if hasattr(level, 'value'):
                if "严重" in str(level.value) or "CRITICAL" in str(level.value):
                    confidence += 0.1
                elif "高" in str(level.value) or "HIGH" in str(level.value):
                    confidence += 0.05
        
        return min(confidence, 0.99)
    
    def _estimate_adoption_probability(
        self,
        risk_type: str,
        priority: RiskSeverity,
        confidence: float,
        market_benchmark: Optional[MarketBenchmark]
    ) -> float:
        """估算建议采纳率"""
        probability = 0.5  # 基础采纳率
        
        # 优先级高，采纳率更高
        if priority == RiskSeverity.CRITICAL:
            probability += 0.3
        elif priority == RiskSeverity.HIGH:
            probability += 0.2
        elif priority == RiskSeverity.MEDIUM:
            probability += 0.1
        
        # 置信度高，采纳率更高
        probability += confidence * 0.2
        
        # 市场基准采用率高，采纳率更高
        if market_benchmark and market_benchmark.adoption_rate > 0.8:
            probability += 0.1
        
        return min(probability, 0.95)
    
    def _determine_level(
        self,
        legal_basis: List[LegalBasis],
        market_benchmark: Optional[MarketBenchmark],
        suggested_text: str
    ) -> RedlineLevel:
        """确定建议质量等级"""
        # L4: 有法律依据 + 有市场基准 + 有具体文本
        if legal_basis and market_benchmark and len(suggested_text) > 20:
            return RedlineLevel.L4_INTELLIGENT
        
        # L3: 有具体修改文本
        if len(suggested_text) > 20 and "建议" not in suggested_text:
            return RedlineLevel.L3_SPECIFIC
        
        # L2: 有修改方向
        if len(suggested_text) > 10:
            return RedlineLevel.L2_DIRECTION
        
        # L1: 通用建议
        return RedlineLevel.L1_GENERIC
    
    def generate_for_clauses(
        self,
        risk_points: List,
        clauses: List
    ) -> List[ClauseRedline]:
        """
        为多个条款生成 Redline 建议
        
        Args:
            risk_points: 风险点列表
            clauses: 条款列表
            
        Returns:
            List[ClauseRedline]: 条款 Redline 列表
        """
        clause_redlines = []
        
        # 按条款分组风险点
        clause_risks = {}
        for risk in risk_points:
            clause_title = getattr(risk, 'clause_title', '其他条款')
            if clause_title not in clause_risks:
                clause_risks[clause_title] = []
            clause_risks[clause_title].append(risk)
        
        # 为每个条款生成 Redline
        for clause in clauses:
            risks = clause_risks.get(clause.title, [])
            
            if not risks:
                continue
            
            # 为每个风险点生成建议
            suggestions = []
            for risk in risks:
                suggestion = self.generate(risk)
                suggestions.append(suggestion)
            
            # 确定条款风险等级
            max_priority = RiskSeverity.LOW
            for s in suggestions:
                if s.priority == RiskSeverity.CRITICAL:
                    max_priority = RiskSeverity.CRITICAL
                    break
                elif s.priority == RiskSeverity.HIGH and max_priority != RiskSeverity.CRITICAL:
                    max_priority = RiskSeverity.HIGH
                elif s.priority == RiskSeverity.MEDIUM and max_priority == RiskSeverity.LOW:
                    max_priority = RiskSeverity.MEDIUM
            
            # 生成整体修改建议（合并所有建议）
            overall_suggestion = self._merge_suggestions(clause.content, suggestions)
            
            clause_redlines.append(ClauseRedline(
                clause_id=str(uuid.uuid4())[:8],
                clause_title=clause.title,
                clause_content=clause.content,
                suggestions=suggestions,
                risk_level=max_priority,
                overall_suggestion=overall_suggestion
            ))
        
        return clause_redlines
    
    def _merge_suggestions(
        self,
        original_content: str,
        suggestions: List[RedlineSuggestion]
    ) -> str:
        """合并多个建议，生成完整的修改后文本"""
        # 简化实现：如果有删除建议，直接标记删除；否则逐条应用修改
        result = original_content
        
        for suggestion in suggestions:
            if suggestion.redline_type == RedlineType.DELETION:
                result = result.replace(suggestion.original_text, f"[删除：{suggestion.original_text}]")
            elif suggestion.redline_type == RedlineType.MODIFICATION:
                result = result.replace(suggestion.original_text, f"[修改为：{suggestion.suggested_text}]")
        
        return result
    
    def generate_report(
        self,
        contract,
        risk_points: List,
        clauses: List
    ) -> RedlineReport:
        """
        生成完整的 Redline 报告
        
        Args:
            contract: 合同对象
            risk_points: 风险点列表
            clauses: 条款列表
            
        Returns:
            RedlineReport: 完整的 Redline 报告
        """
        # 生成条款级别的 Redline
        clause_redlines = self.generate_for_clauses(risk_points, clauses)
        
        # 收集所有建议
        all_suggestions = []
        for cr in clause_redlines:
            all_suggestions.extend(cr.suggestions)
        
        # 统计信息
        suggestions_by_level = {}
        suggestions_by_priority = {}
        
        for s in all_suggestions:
            level_key = s.level.value
            suggestions_by_level[level_key] = suggestions_by_level.get(level_key, 0) + 1
            
            priority_key = s.priority.value
            suggestions_by_priority[priority_key] = suggestions_by_priority.get(priority_key, 0) + 1
        
        # 计算 L4 采纳率
        l4_count = suggestions_by_level.get('L4-智能 Redline', 0)
        l4_adoption_rate = l4_count / len(all_suggestions) if all_suggestions else 0
        
        # 生成执行摘要
        executive_summary = self._generate_executive_summary(all_suggestions, contract)
        
        # 生成整体风险评估
        overall_risk = self._generate_overall_risk_assessment(all_suggestions)
        
        # 生成关键建议（Top 5）
        key_recommendations = self._generate_key_recommendations(all_suggestions)
        
        return RedlineReport(
            report_id=str(uuid.uuid4())[:12],
            contract_id=getattr(contract, 'id', str(uuid.uuid4())[:12]),
            contract_name=getattr(contract, 'title', '未命名合同'),
            generated_at=datetime.now(),
            total_suggestions=len(all_suggestions),
            suggestions_by_level=suggestions_by_level,
            suggestions_by_priority=suggestions_by_priority,
            clause_redlines=clause_redlines,
            executive_summary=executive_summary,
            overall_risk_assessment=overall_risk,
            key_recommendations=key_recommendations,
            l4_adoption_rate=l4_adoption_rate,
            all_suggestions=all_suggestions
        )
    
    def _generate_executive_summary(self, suggestions: List[RedlineSuggestion], contract) -> str:
        """生成执行摘要"""
        if not suggestions:
            return "合同整体风险较低，未发现重大风险条款。"
        
        critical_count = sum(1 for s in suggestions if s.priority == RiskSeverity.CRITICAL)
        high_count = sum(1 for s in suggestions if s.priority == RiskSeverity.HIGH)
        l4_count = sum(1 for s in suggestions if s.level == RedlineLevel.L4_INTELLIGENT)
        
        summary = f"本合同共发现 {len(suggestions)} 处风险点，"
        
        if critical_count > 0:
            summary += f"其中 {critical_count} 处为严重风险（必须修改），"
        if high_count > 0:
            summary += f"{high_count} 处为高风险（强烈建议修改）。"
        
        if l4_count > 0:
            summary += f" 已生成 {l4_count} 条 L4 级智能修改建议（含法律依据和市场基准），可直接采用。"
        
        return summary
    
    def _generate_overall_risk_assessment(self, suggestions: List[RedlineSuggestion]) -> str:
        """生成整体风险评估"""
        if not suggestions:
            return "低风险：合同条款整体公平合理，可正常签署。"
        
        critical_count = sum(1 for s in suggestions if s.priority == RiskSeverity.CRITICAL)
        high_count = sum(1 for s in suggestions if s.priority == RiskSeverity.HIGH)
        
        if critical_count > 0:
            return f"严重风险：发现 {critical_count} 处严重风险条款，建议必须修改后再签署，否则可能面临重大法律风险。"
        elif high_count >= 3:
            return f"高风险：发现 {high_count} 处高风险条款，建议与对方协商修改后再签署。"
        elif high_count >= 1:
            return "中风险：发现少量高风险条款，建议关注并酌情修改。"
        else:
            return "低风险：合同整体风险可控，建议关注低风险条款的优化。"
    
    def _generate_key_recommendations(self, suggestions: List[RedlineSuggestion]) -> List[str]:
        """生成关键建议（Top 5）"""
        # 按优先级和置信度排序
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (
                {'严重': 4, '高': 3, '中': 2, '低': 1}.get(s.priority.value, 0),
                -s.confidence
            ),
            reverse=True
        )
        
        recommendations = []
        for s in sorted_suggestions[:5]:
            rec = f"【{s.priority.value}】{s.rationale[:100]}..."
            recommendations.append(rec)
        
        if not recommendations:
            recommendations.append("合同整体良好，无需特别修改。")
        
        return recommendations


# 测试代码
if __name__ == "__main__":
    # 导入必要的模块
    import sys
    sys.path.insert(0, '/home/admin/.openclaw/workspace/LegalAI-Agent/src')
    
    from analyzer.risk_analyzer import RiskAnalyzer, RiskPoint, RiskType, RiskLevel
    from parser.contract_parser import ContractParser, Clause, ClauseType, Contract
    
    # 示例合同
    sample_contract = """
    买卖合同
    
    甲方：北京科技有限公司
    乙方：上海贸易有限公司
    
    第一条 价格调整
    甲方有权随时调整产品价格，无需通知乙方。
    
    第二条 合同解除
    甲方可随时解除本合同，无需承担任何责任。
    
    第三条 违约责任
    乙方违约需承担无限连带责任，赔偿甲方一切损失。
    
    第四条 争议解决
    本合同最终解释权归甲方所有。
    
    第五条 交付时间
    甲方应及时交付产品。
    """
    
    # 解析合同
    parser = ContractParser()
    contract = parser.parse_text(sample_contract)
    
    # 分析风险
    analyzer = RiskAnalyzer()
    analysis_result = analyzer.analyze(contract)
    
    # 生成 Redline
    generator = SmartRedlineGenerator()
    report = generator.generate_report(
        contract=contract,
        risk_points=analysis_result.risk_points,
        clauses=contract.clauses
    )
    
    # 输出报告
    print("=" * 60)
    print(f"Redline 报告：{report.contract_name}")
    print(f"生成时间：{report.generated_at}")
    print(f"总建议数：{report.total_suggestions}")
    print(f"L4 级建议占比：{report.l4_adoption_rate * 100:.1f}%")
    print("=" * 60)
    print("\n执行摘要:")
    print(report.executive_summary)
    print("\n整体风险评估:")
    print(report.overall_risk_assessment)
    print("\n关键建议:")
    for i, rec in enumerate(report.key_recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 60)
    print("条款级 Redline 详情:")
    print("=" * 60)
    
    for cr in report.clause_redlines:
        print(f"\n【{cr.clause_title}】")
        print(f"风险等级：{cr.risk_level.value}")
        print(f"原文：{cr.clause_content[:100]}...")
        print(f"修改后：{cr.overall_suggestion[:100]}...")
        
        for s in cr.suggestions:
            print(f"\n  📝 建议 {s.suggestion_id}:")
            print(f"     类型：{s.redline_type.value}")
            print(f"     等级：{s.level.value}")
            print(f"     原文：{s.original_text[:50]}...")
            print(f"     建议：{s.suggested_text[:50]}...")
            print(f"     理由：{s.rationale[:80]}...")
            print(f"     置信度：{s.confidence:.2f}")
            print(f"     采纳率：{s.adoption_probability:.2f}")
            
            if s.legal_basis:
                print(f"     法律依据:")
                for lb in s.legal_basis[:2]:
                    print(f"       - {lb.law_name}{lb.article}: {lb.content[:30]}...")
            
            if s.market_benchmark:
                print(f"     市场基准：{s.market_benchmark.standard_practice[:50]}...")
