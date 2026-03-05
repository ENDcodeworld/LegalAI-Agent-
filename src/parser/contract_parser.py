"""
合同解析模块
负责解析 PDF/Word 合同文件，提取条款结构
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ClauseType(Enum):
    """条款类型枚举"""
    DEFINITION = "定义条款"
    PAYMENT = "付款条款"
    DELIVERY = "交付条款"
    WARRANTY = "保证条款"
    LIABILITY = "责任条款"
    TERMINATION = "终止条款"
    CONFIDENTIALITY = "保密条款"
    DISPUTE = "争议解决"
    INTELLECTUAL_PROPERTY = "知识产权"
    FORCE_MAJEURE = "不可抗力"
    OTHER = "其他条款"


@dataclass
class Clause:
    """合同条款数据类"""
    title: str  # 条款标题
    content: str  # 条款内容
    clause_type: ClauseType  # 条款类型
    page_number: Optional[int] = None  # 页码
    risk_level: Optional[str] = None  # 风险等级（待分析）
    issues: List[str] = None  # 问题列表（待分析）
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class Contract:
    """合同数据类"""
    title: str  # 合同标题
    parties: List[str]  # 合同各方
    sign_date: Optional[str]  # 签署日期
    clauses: List[Clause]  # 条款列表
    total_pages: Optional[int] = None  # 总页数
    file_path: Optional[str] = None  # 文件路径
    
    def get_clause_by_type(self, clause_type: ClauseType) -> List[Clause]:
        """根据类型获取条款"""
        return [c for c in self.clauses if c.clause_type == clause_type]
    
    def get_risk_clauses(self) -> List[Clause]:
        """获取有风险标记的条款"""
        return [c for c in self.clauses if c.risk_level]


class ContractParser:
    """合同解析器"""
    
    def __init__(self):
        # 条款类型关键词映射
        self.clause_keywords = {
            ClauseType.DEFINITION: ["定义", "释义", "词语含义"],
            ClauseType.PAYMENT: ["付款", "支付", "价款", "费用", "金额"],
            ClauseType.DELIVERY: ["交付", "交货", "履行", "期限"],
            ClauseType.WARRANTY: ["保证", "保修", "质保", "承诺"],
            ClauseType.LIABILITY: ["责任", "赔偿", "违约", "损失"],
            ClauseType.TERMINATION: ["终止", "解除", "到期", "续约"],
            ClauseType.CONFIDENTIALITY: ["保密", "秘密", "机密"],
            ClauseType.DISPUTE: ["争议", "仲裁", "诉讼", "管辖"],
            ClauseType.INTELLECTUAL_PROPERTY: ["知识产权", "专利", "商标", "版权"],
            ClauseType.FORCE_MAJEURE: ["不可抗力", "意外事件"],
        }
    
    def parse_text(self, text: str) -> Contract:
        """
        从纯文本解析合同
        
        Args:
            text: 合同文本内容
            
        Returns:
            Contract: 解析后的合同对象
        """
        # 提取合同标题
        title = self._extract_title(text)
        
        # 提取合同各方
        parties = self._extract_parties(text)
        
        # 提取签署日期
        sign_date = self._extract_sign_date(text)
        
        # 提取条款
        clauses = self._extract_clauses(text)
        
        return Contract(
            title=title,
            parties=parties,
            sign_date=sign_date,
            clauses=clauses
        )
    
    def _extract_title(self, text: str) -> str:
        """提取合同标题"""
        # 简单实现：取第一行非空文本
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                return line
        return "未命名合同"
    
    def _extract_parties(self, text: str) -> List[str]:
        """提取合同各方"""
        parties = []
        
        # 匹配"甲方："、"乙方："等模式
        pattern = r'(?:甲方 | 乙方 | 丙方 | 甲方 \(?:|乙方 \(?:|丙方 \(?:)([^)（,\n]+)'
        matches = re.findall(pattern, text)
        parties.extend(matches)
        
        # 匹配"公司"、"有限公司"等模式
        company_pattern = r'([\u4e00-\u9fa5]+(?:公司 | 企业 | 单位 | 中心))'
        company_matches = re.findall(company_pattern, text[:1000])  # 只在前 1000 字找
        parties.extend(company_matches[:3])  # 最多取 3 个
        
        # 去重
        return list(set(parties))[:5]
    
    def _extract_sign_date(self, text: str) -> Optional[str]:
        """提取签署日期"""
        # 匹配日期模式
        patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{4}/\d{1,2}/\d{1,2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_clauses(self, text: str) -> List[Clause]:
        """提取合同条款"""
        clauses = []
        
        # 按章节分割（第 X 条、X.、(X) 等模式）
        clause_patterns = [
            r'(第 [一二三四五六七八九十百千\d]+条 [：:].*?)(?=第 [一二三四五六七八九十百千\d]+条 | $)',
            r'(\d+\.\d+.*?)(?=\d+\.\d+| $)',
            r'(\(\d+\).*?)(?=\(\d+\)| $)',
        ]
        
        for pattern in clause_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                clause = self._parse_clause(match.strip())
                if clause:
                    clauses.append(clause)
        
        # 如果没有找到结构化条款，按段落分割
        if not clauses:
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if len(para) > 50:  # 只处理有意义的段落
                    clause = self._parse_clause(para)
                    if clause:
                        clauses.append(clause)
        
        return clauses
    
    def _parse_clause(self, text: str) -> Optional[Clause]:
        """解析单个条款"""
        if not text or len(text) < 10:
            return None
        
        # 提取标题（第一行或冒号前）
        lines = text.split('\n')
        title = lines[0].strip() if lines else "未命名条款"
        
        # 如果标题太长，截取前 50 字
        if len(title) > 50:
            title = title[:50] + "..."
        
        # 内容（去掉标题后的部分）
        content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else text
        
        # 识别条款类型
        clause_type = self._identify_clause_type(title + content)
        
        return Clause(
            title=title,
            content=content if content else title,
            clause_type=clause_type
        )
    
    def _identify_clause_type(self, text: str) -> ClauseType:
        """识别条款类型"""
        text_lower = text.lower()
        
        for clause_type, keywords in self.clause_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return clause_type
        
        return ClauseType.OTHER


def parse_contract_file(file_path: str) -> Contract:
    """
    解析合同文件
    
    Args:
        file_path: 文件路径（支持.txt, .docx, .pdf）
        
    Returns:
        Contract: 解析后的合同对象
    """
    parser = ContractParser()
    
    # 读取文件
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_path.endswith('.docx'):
        # 需要安装 python-docx
        try:
            from docx import Document
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")
    elif file_path.endswith('.pdf'):
        # 需要安装 pdfplumber 或 PyPDF2
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except ImportError:
            raise ImportError("请安装 pdfplumber: pip install pdfplumber")
    else:
        raise ValueError(f"不支持的文件格式：{file_path}")
    
    return parser.parse_text(text)


# 测试代码
if __name__ == "__main__":
    # 示例合同文本
    sample_contract = """
    买卖合同
    
    甲方：北京科技有限公司
    乙方：上海贸易有限公司
    
    签订日期：2026 年 3 月 5 日
    
    第一条 定义
    本合同中下列词语含义如下：
    1.1 "产品"指本合同约定的货物
    1.2 "交付"指产品所有权转移
    
    第二条 付款条款
    乙方应在合同签订后 30 日内支付全部价款，总计人民币 100 万元。
    付款方式：银行转账
    
    第三条 交付条款
    甲方应于收到全部款项后 15 日内交付产品。
    交付地点：乙方指定仓库
    
    第四条 质量保证
    甲方保证产品质量符合国家标准，保修期 2 年。
    
    第五条 违约责任
    任何一方违约，应赔偿对方因此遭受的全部损失。
    
    第六条 争议解决
    本合同争议提交北京仲裁委员会仲裁。
    """
    
    parser = ContractParser()
    contract = parser.parse_text(sample_contract)
    
    print(f"合同标题：{contract.title}")
    print(f"合同各方：{contract.parties}")
    print(f"签署日期：{contract.sign_date}")
    print(f"条款数量：{len(contract.clauses)}")
    print("\n条款列表:")
    for i, clause in enumerate(contract.clauses, 1):
        print(f"{i}. [{clause.clause_type.value}] {clause.title[:30]}...")
