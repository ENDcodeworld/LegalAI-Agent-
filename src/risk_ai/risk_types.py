"""
风险类型定义 - 50+ 风险类型覆盖
基于中国法律实践和行业标准
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    CRITICAL = "严重风险"


class RiskCategory(Enum):
    """风险一级分类（10 大类）"""
    UNFAIR_CLAUSE = "不公平条款"
    AMBIGUOUS_TERM = "模糊表述"
    LEGAL_COMPLIANCE = "法律合规"
    FINANCIAL_RISK = "财务风险"
    PERFORMANCE_RISK = "履约风险"
    TERMINATION_RISK = "终止风险"
    INTELLECTUAL_PROPERTY = "知识产权"
    CONFIDENTIALITY = "保密条款"
    DISPUTE_RESOLUTION = "争议解决"
    DATA_COMPLIANCE = "数据合规"


class RiskType(Enum):
    """
    风险类型 - 50+ 具体风险类型
    每个类型包含：一级分类、风险名称、示例关键词、法律依据
    """
    
    # ========== 不公平条款 (10 类) ==========
    UNFAIR_UNILATERAL_CHANGE = "单方变更权"
    UNFAIR_UNILATERAL_TERMINATE = "单方解除权"
    UNFAIR_ASYMMETRIC_PENALTY = "不对等违约金"
    UNFAIR_EXEMPTION_CLAUSE = "免责条款"
    UNFAIR_FINAL_INTERPRETATION = "最终解释权"
    UNFAIR_PRICE_ADJUSTMENT = "价格调整权"
    UNFAIR_SERVICE_MODIFICATION = "服务变更权"
    UNFAIR_AUTO_RENEWAL = "自动续费陷阱"
    UNFAIR_BINDING_ARBITRATION = "强制仲裁条款"
    UNFAIR_WAIVER_RIGHTS = "权利放弃条款"
    
    # ========== 模糊表述 (8 类) ==========
    AMBIGUOUS_TIME = "时间模糊"
    AMBIGUOUS_STANDARD = "标准模糊"
    AMBIGUOUS_SCOPE = "范围模糊"
    AMBIGUOUS_AMOUNT = "金额模糊"
    AMBIGUOUS_QUALITY = "质量标准模糊"
    AMBIGUOUS_DELIVERY = "交付条件模糊"
    AMBIGUOUS_ACCEPTANCE = "验收标准模糊"
    AMBIGUOUS_NOTICE = "通知方式模糊"
    
    # ========== 法律合规 (8 类) ==========
    LEGAL_FORMAT_CLAUSE_INVALID = "格式条款无效"
    LEGAL_MANDATORY_VIOLATION = "违反强制性规定"
    LEGAL_EXCEED_AUTHORITY = "超越权限"
    LEGAL_CONSUMER_RIGHTS = "侵害消费者权益"
    LEGAL_LABOR_VIOLATION = "违反劳动法规"
    LEGAL_TAX_EVASION = "阴阳合同风险"
    LEGAL_USURY = "高利贷风险"
    LEGAL_ILLEGAL_CONTENT = "违法内容"
    
    # ========== 财务风险 (8 类) ==========
    FINANCIAL_UNLIMITED_LIABILITY = "无限责任"
    FINANCIAL_JOINT_LIABILITY = "连带责任"
    FINANCIAL_NO_COMPENSATION_CAP = "赔偿上限缺失"
    FINANCIAL_HARSH_PAYMENT = "付款条件苛刻"
    FINANCIAL_EXCESSIVE_PENALTY = "违约金过高"
    FINANCIAL_INTEREST_CLARITY = "利息约定不明"
    FINANCIAL_CURRENCY_RISK = "币种风险"
    FINANCIAL_TAX_BURDEN = "税负承担不明"
    
    # ========== 履约风险 (6 类) ==========
    PERFORMANCE_STANDARD_UNDEFINED = "履约标准不明"
    PERFORMANCE_DELIVERY_UNDEFINED = "交付条件模糊"
    PERFORMANCE_ACCEPTANCE_UNDEFINED = "验收标准缺失"
    PERFORMANCE_WARRANTY_UNDEFINED = "保修责任不明"
    PERFORMANCE_AFTER_SALES = "售后服务缺失"
    PERFORMANCE_FORCE_MAJEURE = "不可抗力滥用"
    
    # ========== 终止风险 (5 类) ==========
    TERMINATION_ASYMMETRIC = "解约条件不对等"
    TERMINATION_UNILATERAL_RENEWAL = "续约权单方"
    TERMINATION_NO_LIQUIDATION = "清算条款缺失"
    TERMINATION_NOTICE_INADEQUATE = "通知期限不足"
    TERMINATION_EFFECT_UNDEFINED = "终止效果不明"
    
    # ========== 知识产权 (5 类) ==========
    IP_OWNERSHIP_UNDEFINED = "权属约定不明"
    IP_LICENSE_TOO_BROAD = "许可范围过宽"
    IP_INFRINGEMENT_UNCLEAR = "侵权责任不清"
    IP_MORAL_RIGHTS = "精神权利侵害"
    IP_DERIVATIVE_WORKS = "衍生作品归属"
    
    # ========== 保密条款 (4 类) ==========
    CONFIDENTIALITY_TOO_BROAD = "保密范围过宽"
    CONFIDENTIALITY_PERIOD = "保密期限不合理"
    CONFIDENTIALITY_NO_EXCEPTIONS = "保密例外缺失"
    CONFIDENTIALITY_RETURN = "资料返还缺失"
    
    # ========== 争议解决 (4 类) ==========
    DISPUTE_UNFAVENIENT_FORUM = "管辖地不利"
    DISPUTE_ARBITRATION_UNDEFINED = "仲裁机构不明"
    DISPUTE_COST_ASYMMETRIC = "诉讼成本不均"
    DISPUTE_CLASS_ACTION_WAIVER = "集体诉讼放弃"
    
    # ========== 数据合规 (4 类) ==========
    DATA_OVER_COLLECTION = "个人信息收集过度"
    DATA_USAGE_UNDEFINED = "使用范围不明"
    DATA_CROSS_BORDER = "跨境传输风险"
    DATA_SECURITY_INADEQUATE = "安全措施不足"


# 风险类型详细定义
@dataclass
class RiskTypeDefinition:
    """风险类型定义"""
    risk_type: RiskType
    category: RiskCategory
    description: str
    keywords: List[str]
    legal_basis: Optional[str] = None
    example: Optional[str] = None
    default_level: RiskLevel = RiskLevel.MEDIUM


# 风险类型配置 - 50+ 风险类型详细定义
RISK_TYPE_DEFINITIONS = {
    # ========== 不公平条款 ==========
    RiskType.UNFAIR_UNILATERAL_CHANGE: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_UNILATERAL_CHANGE,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="一方有权单方面变更合同内容，无需对方同意",
        keywords=["有权变更", "单方调整", "无需协商", "自行决定", "随时修改"],
        legal_basis="《民法典》第 543 条：当事人协商一致，可以变更合同",
        example="甲方有权随时调整服务内容，无需通知乙方",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.UNFAIR_UNILATERAL_TERMINATE: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_UNILATERAL_TERMINATE,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="一方可单方面解除合同，无需合理理由",
        keywords=["随时解除", "单方终止", "无需理由", "立即解约"],
        legal_basis="《民法典》第 563 条：法定解除权情形",
        example="甲方可随时解除本合同，无需承担违约责任",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.UNFAIR_ASYMMETRIC_PENALTY: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_ASYMMETRIC_PENALTY,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="违约金约定对双方不对等",
        keywords=["乙方违约", "违约金", "赔偿", "不对等"],
        legal_basis="《民法典》第 585 条：违约金约定",
        example="乙方违约需支付 50% 违约金，甲方违约仅退还费用",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.UNFAIR_EXEMPTION_CLAUSE: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_EXEMPTION_CLAUSE,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="一方免除自身责任的条款",
        keywords=["概不负责", "不承担责任", "免除责任", "免责"],
        legal_basis="《民法典》第 497 条：格式条款无效情形",
        example="甲方对产品质量概不负责",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.UNFAIR_FINAL_INTERPRETATION: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_FINAL_INTERPRETATION,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="一方拥有合同最终解释权",
        keywords=["最终解释权", "解释权归", "以甲方解释为准"],
        legal_basis="《民法典》第 498 条：格式条款解释规则",
        example="本合同最终解释权归甲方所有",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.UNFAIR_PRICE_ADJUSTMENT: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_PRICE_ADJUSTMENT,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="一方可单方面调整价格",
        keywords=["调整价格", "价格变动", "调价权", "价格上浮"],
        legal_basis="《民法典》第 510 条：价款约定不明",
        example="甲方有权根据市场情况调整价格",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.UNFAIR_SERVICE_MODIFICATION: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_SERVICE_MODIFICATION,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="一方可单方面变更服务内容",
        keywords=["变更服务", "调整功能", "修改内容", "服务变更"],
        legal_basis="《民法典》第 543 条",
        example="甲方有权变更服务内容，乙方不得异议",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.UNFAIR_AUTO_RENEWAL: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_AUTO_RENEWAL,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="自动续费条款存在陷阱",
        keywords=["自动续费", "默认续约", "自动延期"],
        legal_basis="《消费者权益保护法》",
        example="合同到期自动续费，除非乙方提前 30 日书面通知",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.UNFAIR_BINDING_ARBITRATION: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_BINDING_ARBITRATION,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="强制仲裁条款限制诉讼权利",
        keywords=["必须仲裁", "不得诉讼", "仲裁优先"],
        legal_basis="《仲裁法》",
        example="任何争议必须提交仲裁，不得向法院起诉",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.UNFAIR_WAIVER_RIGHTS: RiskTypeDefinition(
        risk_type=RiskType.UNFAIR_WAIVER_RIGHTS,
        category=RiskCategory.UNFAIR_CLAUSE,
        description="要求一方放弃法定权利",
        keywords=["放弃权利", "不得主张", "无权要求"],
        legal_basis="《民法典》",
        example="乙方放弃追究甲方违约责任的权利",
        default_level=RiskLevel.HIGH
    ),
    
    # ========== 模糊表述 ==========
    RiskType.AMBIGUOUS_TIME: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_TIME,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="时间约定不明确",
        keywords=["及时", "尽快", "适时", "适时", "合理时间", "另行通知"],
        legal_basis="《民法典》第 510 条",
        example="甲方应及时交付产品",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.AMBIGUOUS_STANDARD: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_STANDARD,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="标准约定不明确",
        keywords=["合理", "适当", "符合要求", "满意", "认可"],
        legal_basis="《民法典》第 510 条",
        example="服务质量应符合甲方要求",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.AMBIGUOUS_SCOPE: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_SCOPE,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="范围约定不明确",
        keywords=["等相关", "及其他", "包括但不限于", "等"],
        legal_basis="《民法典》第 466 条",
        example="包括差旅费、住宿费等相关费用",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.AMBIGUOUS_AMOUNT: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_AMOUNT,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="金额约定不明确",
        keywords=["约", "左右", "大概", "预计", "暂定"],
        legal_basis="《民法典》第 510 条",
        example="合同金额约 100 万元左右",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.AMBIGUOUS_QUALITY: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_QUALITY,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="质量标准约定不明确",
        keywords=["优质", "良好", "合格", "符合要求"],
        legal_basis="《民法典》第 511 条",
        example="产品应符合质量标准",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.AMBIGUOUS_DELIVERY: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_DELIVERY,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="交付条件约定不明确",
        keywords=["指定地点", "约定方式", "相关手续"],
        legal_basis="《民法典》第 510 条",
        example="产品交付至乙方指定地点",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.AMBIGUOUS_ACCEPTANCE: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_ACCEPTANCE,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="验收标准约定不明确",
        keywords=["验收合格", "满意为准", "确认无误"],
        legal_basis="《民法典》第 620 条",
        example="产品经甲方验收合格后付款",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.AMBIGUOUS_NOTICE: RiskTypeDefinition(
        risk_type=RiskType.AMBIGUOUS_NOTICE,
        category=RiskCategory.AMBIGUOUS_TERM,
        description="通知方式约定不明确",
        keywords=["通知对方", "告知", "书面通知"],
        legal_basis="《民法典》第 140 条",
        example="应提前通知对方",
        default_level=RiskLevel.LOW
    ),
    
    # ========== 法律合规 ==========
    RiskType.LEGAL_FORMAT_CLAUSE_INVALID: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_FORMAT_CLAUSE_INVALID,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="格式条款可能被认定无效",
        keywords=["最终解释权", "概不负责", "不承担", "无效"],
        legal_basis="《民法典》第 497 条",
        example="提供格式条款一方不合理地免除或者减轻其责任",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.LEGAL_MANDATORY_VIOLATION: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_MANDATORY_VIOLATION,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="违反法律强制性规定",
        keywords=["违反", "禁止", "不得", "强制"],
        legal_basis="《民法典》第 153 条",
        example="合同内容违反法律强制性规定",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.LEGAL_EXCEED_AUTHORITY: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_EXCEED_AUTHORITY,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="超越权限签订合同",
        keywords=["超越权限", "无权代理", "未经授权"],
        legal_basis="《民法典》第 171 条",
        example="签约人超越代理权限",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.LEGAL_CONSUMER_RIGHTS: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_CONSUMER_RIGHTS,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="侵害消费者权益",
        keywords=["不退不换", "概不退换", "消费者"],
        legal_basis="《消费者权益保护法》",
        example="商品售出概不退换",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.LEGAL_LABOR_VIOLATION: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_LABOR_VIOLATION,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="违反劳动法规",
        keywords=["不缴纳社保", "无加班费", "试用期", "劳动"],
        legal_basis="《劳动合同法》",
        example="试用期内不缴纳社会保险",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.LEGAL_TAX_EVASION: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_TAX_EVASION,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="阴阳合同避税风险",
        keywords=["两份合同", "实际金额", "避税", "阴阳"],
        legal_basis="《税收征收管理法》",
        example="签订两份金额不同的合同",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.LEGAL_USURY: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_USURY,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="高利贷风险",
        keywords=["利息", "利率", "月息", "年息", "超过"],
        legal_basis="《民法典》第 680 条",
        example="借款利率超过 LPR4 倍",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.LEGAL_ILLEGAL_CONTENT: RiskTypeDefinition(
        risk_type=RiskType.LEGAL_ILLEGAL_CONTENT,
        category=RiskCategory.LEGAL_COMPLIANCE,
        description="合同内容违法",
        keywords=["违法", "禁止", "非法", "违规"],
        legal_basis="《民法典》第 153 条",
        example="合同内容违反法律法规",
        default_level=RiskLevel.CRITICAL
    ),
    
    # ========== 财务风险 ==========
    RiskType.FINANCIAL_UNLIMITED_LIABILITY: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_UNLIMITED_LIABILITY,
        category=RiskCategory.FINANCIAL_RISK,
        description="承担无限责任",
        keywords=["无限责任", "全部损失", "一切损失", "所有损失"],
        legal_basis="《民法典》第 584 条",
        example="乙方需承担无限连带责任，赔偿一切损失",
        default_level=RiskLevel.CRITICAL
    ),
    
    RiskType.FINANCIAL_JOINT_LIABILITY: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_JOINT_LIABILITY,
        category=RiskCategory.FINANCIAL_RISK,
        description="承担连带责任",
        keywords=["连带责任", "连带保证", "共同承担"],
        legal_basis="《民法典》第 178 条",
        example="乙方对甲方债务承担连带责任",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.FINANCIAL_NO_COMPENSATION_CAP: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_NO_COMPENSATION_CAP,
        category=RiskCategory.FINANCIAL_RISK,
        description="赔偿金额无上限",
        keywords=["赔偿", "损失", "无上限", "不限"],
        legal_basis="《民法典》第 584 条",
        example="违约方应赔偿对方全部损失，无上限",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.FINANCIAL_HARSH_PAYMENT: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_HARSH_PAYMENT,
        category=RiskCategory.FINANCIAL_RISK,
        description="付款条件苛刻",
        keywords=["预付", "全款", "先付款", "一次性"],
        legal_basis="《民法典》第 510 条",
        example="签约后 30 日内支付 100% 款项",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.FINANCIAL_EXCESSIVE_PENALTY: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_EXCESSIVE_PENALTY,
        category=RiskCategory.FINANCIAL_RISK,
        description="违约金过高",
        keywords=["违约金", "%", "百分之", "罚金"],
        legal_basis="《民法典》第 585 条：违约金超过损失 30% 可请求调整",
        example="违约金为合同金额的 50%",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.FINANCIAL_INTEREST_CLARITY: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_INTEREST_CLARITY,
        category=RiskCategory.FINANCIAL_RISK,
        description="利息约定不明确",
        keywords=["利息", "利率", "资金占用费"],
        legal_basis="《民法典》第 680 条",
        example="逾期付款应支付利息",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.FINANCIAL_CURRENCY_RISK: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_CURRENCY_RISK,
        category=RiskCategory.FINANCIAL_RISK,
        description="币种约定风险",
        keywords=["美元", "外币", "汇率", "币种"],
        legal_basis="《外汇管理条例》",
        example="合同金额以美元结算",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.FINANCIAL_TAX_BURDEN: RiskTypeDefinition(
        risk_type=RiskType.FINANCIAL_TAX_BURDEN,
        category=RiskCategory.FINANCIAL_RISK,
        description="税负承担不明确",
        keywords=["税费", "税金", "含税", "不含税"],
        legal_basis="《税收征收管理法》",
        example="合同金额为含税价",
        default_level=RiskLevel.LOW
    ),
    
    # ========== 履约风险 ==========
    RiskType.PERFORMANCE_STANDARD_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.PERFORMANCE_STANDARD_UNDEFINED,
        category=RiskCategory.PERFORMANCE_RISK,
        description="履约标准不明确",
        keywords=["标准", "规范", "要求", "质量"],
        legal_basis="《民法典》第 510 条",
        example="服务应符合行业标准",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.PERFORMANCE_DELIVERY_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.PERFORMANCE_DELIVERY_UNDEFINED,
        category=RiskCategory.PERFORMANCE_RISK,
        description="交付条件不明确",
        keywords=["交付", "交货", "履行", "提供"],
        legal_basis="《民法典》第 509 条",
        example="产品交付条件不明确",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.PERFORMANCE_ACCEPTANCE_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.PERFORMANCE_ACCEPTANCE_UNDEFINED,
        category=RiskCategory.PERFORMANCE_RISK,
        description="验收标准缺失",
        keywords=["验收", "检验", "检测", "确认"],
        legal_basis="《民法典》第 620 条",
        example="产品验收标准不明确",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.PERFORMANCE_WARRANTY_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.PERFORMANCE_WARRANTY_UNDEFINED,
        category=RiskCategory.PERFORMANCE_RISK,
        description="保修责任不明确",
        keywords=["保修", "质保", "售后", "维修"],
        legal_basis="《民法典》第 582 条",
        example="产品保修期不明确",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.PERFORMANCE_AFTER_SALES: RiskTypeDefinition(
        risk_type=RiskType.PERFORMANCE_AFTER_SALES,
        category=RiskCategory.PERFORMANCE_RISK,
        description="售后服务缺失",
        keywords=["售后", "服务", "支持", "维护"],
        legal_basis="《消费者权益保护法》",
        example="未约定售后服务内容",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.PERFORMANCE_FORCE_MAJEURE: RiskTypeDefinition(
        risk_type=RiskType.PERFORMANCE_FORCE_MAJEURE,
        category=RiskCategory.PERFORMANCE_RISK,
        description="不可抗力条款滥用",
        keywords=["不可抗力", "免责", "意外", "无法控制"],
        legal_basis="《民法典》第 180 条",
        example="不可抗力范围过于宽泛",
        default_level=RiskLevel.LOW
    ),
    
    # ========== 终止风险 ==========
    RiskType.TERMINATION_ASYMMETRIC: RiskTypeDefinition(
        risk_type=RiskType.TERMINATION_ASYMMETRIC,
        category=RiskCategory.TERMINATION_RISK,
        description="解约条件不对等",
        keywords=["解除", "解约", "终止", "不对等"],
        legal_basis="《民法典》第 562 条",
        example="甲方可随时解约，乙方需提前 30 日通知",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.TERMINATION_UNILATERAL_RENEWAL: RiskTypeDefinition(
        risk_type=RiskType.TERMINATION_UNILATERAL_RENEWAL,
        category=RiskCategory.TERMINATION_RISK,
        description="续约权单方控制",
        keywords=["续约", "延期", "优先权", "单方"],
        legal_basis="《民法典》",
        example="合同到期后甲方有权决定是否续约",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.TERMINATION_NO_LIQUIDATION: RiskTypeDefinition(
        risk_type=RiskType.TERMINATION_NO_LIQUIDATION,
        category=RiskCategory.TERMINATION_RISK,
        description="清算条款缺失",
        keywords=["清算", "结算", "善后", "处理"],
        legal_basis="《民法典》第 566 条",
        example="合同终止后清算方式不明确",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.TERMINATION_NOTICE_INADEQUATE: RiskTypeDefinition(
        risk_type=RiskType.TERMINATION_NOTICE_INADEQUATE,
        category=RiskCategory.TERMINATION_RISK,
        description="通知期限不足",
        keywords=["通知", "提前", "期限", "日"],
        legal_basis="《民法典》",
        example="解约仅需提前 3 日通知",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.TERMINATION_EFFECT_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.TERMINATION_EFFECT_UNDEFINED,
        category=RiskCategory.TERMINATION_RISK,
        description="终止效果不明确",
        keywords=["终止后", "解除后", "效力", "后果"],
        legal_basis="《民法典》第 566 条",
        example="合同终止后的效力不明确",
        default_level=RiskLevel.LOW
    ),
    
    # ========== 知识产权 ==========
    RiskType.IP_OWNERSHIP_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.IP_OWNERSHIP_UNDEFINED,
        category=RiskCategory.INTELLECTUAL_PROPERTY,
        description="知识产权权属约定不明",
        keywords=["知识产权", "所有权", "归属", "权利"],
        legal_basis="《著作权法》《专利法》",
        example="合作开发成果归属不明确",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.IP_LICENSE_TOO_BROAD: RiskTypeDefinition(
        risk_type=RiskType.IP_LICENSE_TOO_BROAD,
        category=RiskCategory.INTELLECTUAL_PROPERTY,
        description="许可范围过宽",
        keywords=["许可", "使用", "授权", "范围"],
        legal_basis="《著作权法》",
        example="授予甲方全球永久免费使用权",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.IP_INFRINGEMENT_UNCLEAR: RiskTypeDefinition(
        risk_type=RiskType.IP_INFRINGEMENT_UNCLEAR,
        category=RiskCategory.INTELLECTUAL_PROPERTY,
        description="侵权责任不清",
        keywords=["侵权", "索赔", "知识产权"],
        legal_basis="《民法典》",
        example="知识产权侵权责任约定不明",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.IP_MORAL_RIGHTS: RiskTypeDefinition(
        risk_type=RiskType.IP_MORAL_RIGHTS,
        category=RiskCategory.INTELLECTUAL_PROPERTY,
        description="精神权利侵害",
        keywords=["署名", "修改", "保护", "精神权利"],
        legal_basis="《著作权法》",
        example="乙方放弃署名权",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.IP_DERIVATIVE_WORKS: RiskTypeDefinition(
        risk_type=RiskType.IP_DERIVATIVE_WORKS,
        category=RiskCategory.INTELLECTUAL_PROPERTY,
        description="衍生作品归属不明",
        keywords=["衍生", "改编", "二次创作"],
        legal_basis="《著作权法》",
        example="衍生作品权利归属不明确",
        default_level=RiskLevel.LOW
    ),
    
    # ========== 保密条款 ==========
    RiskType.CONFIDENTIALITY_TOO_BROAD: RiskTypeDefinition(
        risk_type=RiskType.CONFIDENTIALITY_TOO_BROAD,
        category=RiskCategory.CONFIDENTIALITY,
        description="保密范围过宽",
        keywords=["保密", "秘密", "机密", "所有信息"],
        legal_basis="《民法典》",
        example="乙方应对所有信息保密",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.CONFIDENTIALITY_PERIOD: RiskTypeDefinition(
        risk_type=RiskType.CONFIDENTIALITY_PERIOD,
        category=RiskCategory.CONFIDENTIALITY,
        description="保密期限不合理",
        keywords=["永久", "长期", "保密期限"],
        legal_basis="《民法典》",
        example="保密义务永久有效",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.CONFIDENTIALITY_NO_EXCEPTIONS: RiskTypeDefinition(
        risk_type=RiskType.CONFIDENTIALITY_NO_EXCEPTIONS,
        category=RiskCategory.CONFIDENTIALITY,
        description="保密例外缺失",
        keywords=["例外", "公开", "法定"],
        legal_basis="《民法典》",
        example="未约定保密例外情形",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.CONFIDENTIALITY_RETURN: RiskTypeDefinition(
        risk_type=RiskType.CONFIDENTIALITY_RETURN,
        category=RiskCategory.CONFIDENTIALITY,
        description="资料返还缺失",
        keywords=["返还", "归还", "销毁", "资料"],
        legal_basis="《民法典》",
        example="合同终止后资料返还约定缺失",
        default_level=RiskLevel.LOW
    ),
    
    # ========== 争议解决 ==========
    RiskType.DISPUTE_UNFAVENIENT_FORUM: RiskTypeDefinition(
        risk_type=RiskType.DISPUTE_UNFAVENIENT_FORUM,
        category=RiskCategory.DISPUTE_RESOLUTION,
        description="管辖地对己方不利",
        keywords=["管辖", "法院", "所在地", "仲裁"],
        legal_basis="《民事诉讼法》",
        example="由甲方所在地法院管辖",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.DISPUTE_ARBITRATION_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.DISPUTE_ARBITRATION_UNDEFINED,
        category=RiskCategory.DISPUTE_RESOLUTION,
        description="仲裁机构约定不明",
        keywords=["仲裁", "委员会", "机构"],
        legal_basis="《仲裁法》",
        example="提交仲裁机构仲裁",
        default_level=RiskLevel.MEDIUM
    ),
    
    RiskType.DISPUTE_COST_ASYMMETRIC: RiskTypeDefinition(
        risk_type=RiskType.DISPUTE_COST_ASYMMETRIC,
        category=RiskCategory.DISPUTE_RESOLUTION,
        description="诉讼成本承担不均",
        keywords=["费用", "成本", "承担", "律师费"],
        legal_basis="《诉讼费用交纳办法》",
        example="诉讼费由乙方承担",
        default_level=RiskLevel.LOW
    ),
    
    RiskType.DISPUTE_CLASS_ACTION_WAIVER: RiskTypeDefinition(
        risk_type=RiskType.DISPUTE_CLASS_ACTION_WAIVER,
        category=RiskCategory.DISPUTE_RESOLUTION,
        description="集体诉讼权利放弃",
        keywords=["集体诉讼", "代表人", "放弃"],
        legal_basis="《民事诉讼法》",
        example="乙方放弃集体诉讼权利",
        default_level=RiskLevel.MEDIUM
    ),
    
    # ========== 数据合规 ==========
    RiskType.DATA_OVER_COLLECTION: RiskTypeDefinition(
        risk_type=RiskType.DATA_OVER_COLLECTION,
        category=RiskCategory.DATA_COMPLIANCE,
        description="个人信息收集过度",
        keywords=["个人信息", "数据", "收集", "全部"],
        legal_basis="《个人信息保护法》",
        example="可收集用户全部个人信息",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.DATA_USAGE_UNDEFINED: RiskTypeDefinition(
        risk_type=RiskType.DATA_USAGE_UNDEFINED,
        category=RiskCategory.DATA_COMPLIANCE,
        description="数据使用范围不明",
        keywords=["使用", "处理", "分析", "共享"],
        legal_basis="《个人信息保护法》",
        example="可将数据用于任何商业目的",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.DATA_CROSS_BORDER: RiskTypeDefinition(
        risk_type=RiskType.DATA_CROSS_BORDER,
        category=RiskCategory.DATA_COMPLIANCE,
        description="数据跨境传输风险",
        keywords=["跨境", "境外", "传输", "存储"],
        legal_basis="《个人信息保护法》《数据安全法》",
        example="数据可传输至境外存储",
        default_level=RiskLevel.HIGH
    ),
    
    RiskType.DATA_SECURITY_INADEQUATE: RiskTypeDefinition(
        risk_type=RiskType.DATA_SECURITY_INADEQUATE,
        category=RiskCategory.DATA_COMPLIANCE,
        description="数据安全措施不足",
        keywords=["安全", "保护", "措施", "加密"],
        legal_basis="《数据安全法》",
        example="未约定数据安全保障措施",
        default_level=RiskLevel.MEDIUM
    ),
}


def get_risk_type_definition(risk_type: RiskType) -> RiskTypeDefinition:
    """获取风险类型定义"""
    return RISK_TYPE_DEFINITIONS.get(risk_type)


def get_all_risk_types() -> List[RiskType]:
    """获取所有风险类型"""
    return list(RISK_TYPE_DEFINITIONS.keys())


def get_risk_types_by_category(category: RiskCategory) -> List[RiskType]:
    """根据分类获取风险类型"""
    return [
        rt for rt, defn in RISK_TYPE_DEFINITIONS.items()
        if defn.category == category
    ]


def get_risk_type_by_keyword(keyword: str) -> List[RiskType]:
    """根据关键词匹配风险类型"""
    matched = []
    for risk_type, definition in RISK_TYPE_DEFINITIONS.items():
        for kw in definition.keywords:
            if kw in keyword:
                matched.append(risk_type)
                break
    return matched
