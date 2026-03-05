"""
LegalAI 法律文书生成模块
根据案情自动生成起诉状、律师函、仲裁申请书等模板
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class CaseInfo:
    """案件信息数据类"""
    case_type: str  # 案件类型：民事/刑事/行政
    dispute_type: str  # 纠纷类型：合同/侵权/劳动/婚姻等
    plaintiff: str  # 原告/申请人
    defendant: str  # 被告/被申请人
    claims: List[str]  # 诉讼请求
    facts: str  # 事实与理由
    evidence: List[str]  # 证据清单
    court: Optional[str] = None  # 管辖法院
    amount: Optional[str] = None  # 标的金额


@dataclass
class LegalDocument:
    """法律文书数据类"""
    doc_type: str  # 文书类型
    title: str  # 文书标题
    content: str  # 文书内容
    created_at: str  # 生成时间
    template_version: str  # 模板版本


class DocumentGenerator:
    """法律文书生成器"""
    
    def __init__(self):
        self.template_version = "v1.0-2026"
    
    def generate_complaint(self, case: CaseInfo) -> LegalDocument:
        """生成起诉状"""
        
        template = f"""
民事起诉状

原告：{case.plaintiff}
被告：{case.defendant}

诉讼请求：
"""
        for i, claim in enumerate(case.claims, 1):
            template += f"{i}. {claim}\n"
        
        template += f"""
事实与理由：
{case.facts}

证据和证据来源：
"""
        for i, evidence in enumerate(case.evidence, 1):
            template += f"{i}. {evidence}\n"
        
        template += f"""
此致
{case.court or '有管辖权的人民法院'}

具状人：{case.plaintiff}
{datetime.now().strftime('%Y年%m月%d日')}

附：
1. 本起诉状副本{len(case.defendant.split('、'))}份
2. 证据材料清单
"""
        
        return LegalDocument(
            doc_type="起诉状",
            title=f"民事起诉状 - {case.dispute_type}纠纷",
            content=template.strip(),
            created_at=datetime.now().isoformat(),
            template_version=self.template_version
        )
    
    def generate_lawyer_letter(self, case: CaseInfo) -> LegalDocument:
        """生成律师函"""
        
        template = f"""
律 师 函

{case.defendant}：

{case.plaintiff}（以下简称"委托人"）委托本律师就贵方与委托人之间的{case.dispute_type}纠纷一案，郑重致函如下：

一、事实概要
{case.facts}

二、法律分析
根据《中华人民共和国民法典》及相关法律法规，贵方的行为已构成违约/侵权，应承担相应的法律责任。

三、律师意见
本律师代表委托人郑重函告贵方：
"""
        for i, claim in enumerate(case.claims, 1):
            template += f"{i}. {claim}\n"
        
        template += f"""
请贵方在收到本函之日起 7 日内予以回复并履行上述义务。如逾期不予理会，委托人将依法采取诉讼/仲裁等法律措施，届时贵方将承担由此产生的一切法律后果。

特此函告！

{case.plaintiff}代理律师：[律师姓名]
[律师事务所名称]
{datetime.now().strftime('%Y年%m月%d日')}

联系方式：[电话/邮箱]
"""
        
        return LegalDocument(
            doc_type="律师函",
            title=f"律师函 - {case.dispute_type}纠纷",
            content=template.strip(),
            created_at=datetime.now().isoformat(),
            template_version=self.template_version
        )
    
    def generate_arbitration_application(self, case: CaseInfo) -> LegalDocument:
        """生成仲裁申请书"""
        
        template = f"""
仲裁申请书

申请人：{case.plaintiff}
被申请人：{case.defendant}

仲裁请求：
"""
        for i, claim in enumerate(case.claims, 1):
            template += f"{i}. {claim}\n"
        
        template += f"""
事实与理由：
{case.facts}

根据申请人与被申请人签订的《合同》中的仲裁条款，现向贵会提起仲裁申请，请求依法裁决。

证据清单：
"""
        for i, evidence in enumerate(case.evidence, 1):
            template += f"{i}. {evidence}\n"
        
        template += f"""
此致
[仲裁委员会名称]

申请人：{case.plaintiff}
{datetime.now().strftime('%Y年%m月%d日')}

附：
1. 本申请书副本{len(case.defendant.split('、'))}份
2. 证据材料
3. 仲裁协议复印件
"""
        
        return LegalDocument(
            doc_type="仲裁申请书",
            title=f"仲裁申请书 - {case.dispute_type}纠纷",
            content=template.strip(),
            created_at=datetime.now().isoformat(),
            template_version=self.template_version
        )
    
    def get_template_list(self) -> List[Dict]:
        """获取可用模板列表"""
        return [
            {
                "type": "起诉状",
                "name": "民事起诉状",
                "description": "适用于民事案件起诉",
                "fields": ["原告", "被告", "诉讼请求", "事实与理由", "证据", "管辖法院"]
            },
            {
                "type": "律师函",
                "name": "律师函",
                "description": "适用于诉前警告、催告履行",
                "fields": ["收件方", "委托人", "事实概要", "法律分析", "律师意见"]
            },
            {
                "type": "仲裁申请书",
                "name": "仲裁申请书",
                "description": "适用于仲裁案件申请",
                "fields": ["申请人", "被申请人", "仲裁请求", "事实与理由", "证据", "仲裁委员会"]
            },
            {
                "type": "答辩状",
                "name": "民事答辩状",
                "description": "适用于被告答辩",
                "fields": ["答辩人", "被答辩人", "答辩请求", "事实与理由"]
            },
            {
                "type": "保全申请书",
                "name": "财产保全申请书",
                "description": "适用于诉前/诉中财产保全",
                "fields": ["申请人", "被申请人", "保全请求", "事实与理由", "担保方式"]
            }
        ]


# 测试代码
if __name__ == "__main__":
    generator = DocumentGenerator()
    
    # 测试案件
    case = CaseInfo(
        case_type="民事",
        dispute_type="合同",
        plaintiff="张三",
        defendant="李四",
        claims=[
            "请求判令被告支付货款人民币 100,000 元",
            "请求判令被告支付逾期利息（以 100,000 元为基数，按 LPR 计算）",
            "请求判令被告承担本案诉讼费用"
        ],
        facts="2025 年 1 月 1 日，原告与被告签订《买卖合同》，约定被告向原告购买货物一批，总价款 100,000 元。原告已按约交付货物，但被告至今未支付货款。经多次催讨，被告仍拒不履行付款义务。",
        evidence=[
            "《买卖合同》复印件一份",
            "送货单复印件一份",
            "催款函复印件一份",
            "微信聊天记录截图"
        ],
        court="北京市朝阳区人民法院"
    )
    
    # 生成起诉状
    complaint = generator.generate_complaint(case)
    print("=== 起诉状 ===")
    print(complaint.content)
    print()
    
    # 生成律师函
    letter = generator.generate_lawyer_letter(case)
    print("=== 律师函 ===")
    print(letter.content)
    print()
    
    # 获取模板列表
    templates = generator.get_template_list()
    print("=== 可用模板 ===")
    for t in templates:
        print(f"- {t['name']}: {t['description']}")
