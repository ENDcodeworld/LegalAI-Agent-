"""
最高人民法院司法解释抓取模块
每周自动抓取最新司法解释，整理成知识库
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class JudicialInterpretation:
    """司法解释数据类"""
    title: str  # 标题
    doc_number: str  # 文号
    publish_date: str  # 发布日期
    effective_date: str  # 生效日期
    department: str  # 发布部门
    category: str  # 分类
    summary: str  # 摘要
    content: str  # 全文内容
    source_url: str  # 来源 URL
    crawled_at: str  # 抓取时间


class SupremeCourtCrawler:
    """最高法司法解释抓取器"""
    
    def __init__(self, data_dir: str = "/home/admin/.openclaw/workspace/LegalAI-Agent/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://www.court.gov.cn"
        self.interpretation_url = "https://www.court.gov.cn/fabu-xiangqing"
        
        # 分类映射
        self.category_map = {
            "民事": "民事",
            "刑事": "刑事",
            "行政": "行政",
            "执行": "执行",
            "国家赔偿": "国家赔偿",
            "司法解释": "司法解释"
        }
    
    def crawl_latest(self, days: int = 30) -> List[JudicialInterpretation]:
        """
        抓取最近 N 天的司法解释
        
        Args:
            days: 抓取最近多少天的数据
            
        Returns:
            司法解释列表
        """
        print(f"🕵️ 开始抓取最近{days}天的司法解释...")
        
        # 注意：这是示例代码，实际需要适配最高法官网的真实结构
        # 由于最高法官网可能有反爬措施，建议使用官方 API 或 RSS
        
        interpretations = []
        
        try:
            # 模拟抓取（实际使用需要真实爬取逻辑）
            # headers = {
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            # }
            # response = requests.get(self.interpretation_url, headers=headers)
            # response.raise_for_status()
            # soup = BeautifulSoup(response.text, 'html.parser')
            # ... 解析逻辑
            
            print("⚠️  注意：实际爬取需要适配最高法官网结构")
            print("   建议使用官方 API 或手动导入")
            
        except Exception as e:
            print(f"❌ 抓取失败：{e}")
        
        return interpretations
    
    def save_to_json(self, interpretations: List[JudicialInterpretation], filename: Optional[str] = None):
        """保存到 JSON 文件"""
        if filename is None:
            filename = f"judicial_interpretations_{datetime.now().strftime('%Y%m%d')}.json"
        
        filepath = self.data_dir / filename
        
        data = [asdict(i) for i in interpretations]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到：{filepath}")
        return filepath
    
    def load_from_json(self, filename: str) -> List[JudicialInterpretation]:
        """从 JSON 文件加载"""
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [JudicialInterpretation(**i) for i in data]
    
    def export_to_markdown(self, interpretations: List[JudicialInterpretation], filename: Optional[str] = None):
        """导出为 Markdown 表格"""
        if filename is None:
            filename = f"司法解释汇总_{datetime.now().strftime('%Y%m%d')}.md"
        
        filepath = self.data_dir / filename
        
        md_content = f"# 最高人民法院司法解释汇总\n\n"
        md_content += f"**更新时间**: {datetime.now().strftime('%Y年%m月%d日')}\n\n"
        md_content += f"**共收录**: {len(interpretations)} 条\n\n"
        
        md_content += "## 目录\n\n"
        md_content += "| 序号 | 标题 | 文号 | 发布日期 | 分类 |\n"
        md_content += "|------|------|------|----------|------|\n"
        
        for i, interp in enumerate(interpretations, 1):
            title_short = interp.title[:30] + "..." if len(interp.title) > 30 else interp.title
            md_content += f"| {i} | {title_short} | {interp.doc_number} | {interp.publish_date} | {interp.category} |\n"
        
        md_content += "\n## 详细内容\n\n"
        
        for i, interp in enumerate(interpretations, 1):
            md_content += f"### {i}. {interp.title}\n\n"
            md_content += f"**文号**: {interp.doc_number}\n\n"
            md_content += f"**发布日期**: {interp.publish_date}\n\n"
            md_content += f"**生效日期**: {interp.effective_date}\n\n"
            md_content += f"**发布部门**: {interp.department}\n\n"
            md_content += f"**分类**: {interp.category}\n\n"
            md_content += f"**摘要**: {interp.summary}\n\n"
            md_content += f"**全文**:\n\n```\n{interp.content[:500]}...\n```\n\n"
            md_content += f"**来源**: [{interp.source_url}]({interp.source_url})\n\n"
            md_content += "---\n\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown 已保存到：{filepath}")
        return filepath
    
    def get_weekly_update(self) -> Dict:
        """获取本周更新摘要"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        print(f"📊 生成本周更新摘要（{week_start.strftime('%m.%d')} - {today.strftime('%m.%d')}）...")
        
        # 加载已有数据
        interpretations = []
        for file in self.data_dir.glob("judicial_interpretations_*.json"):
            interpretations.extend(self.load_from_json(file.name))
        
        # 筛选本周数据
        week_interpretations = []
        for interp in interpretations:
            try:
                pub_date = datetime.strptime(interp.publish_date, '%Y-%m-%d')
                if pub_date >= week_start:
                    week_interpretations.append(interp)
            except:
                pass
        
        # 生成摘要
        summary = {
            "week_start": week_start.strftime('%Y-%m-%d'),
            "week_end": today.strftime('%Y-%m-%d'),
            "total_count": len(week_interpretations),
            "by_category": {},
            "latest": [asdict(i) for i in week_interpretations[:5]]
        }
        
        # 按分类统计
        for interp in week_interpretations:
            cat = interp.category
            summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1
        
        return summary


# 手动导入模板（用于测试）
def create_sample_data() -> List[JudicialInterpretation]:
    """创建示例数据"""
    return [
        JudicialInterpretation(
            title="最高人民法院关于适用《中华人民共和国民法典》合同编通则若干问题的解释",
            doc_number="法释〔2023〕12 号",
            publish_date="2023-12-05",
            effective_date="2023-12-05",
            department="最高人民法院",
            category="民事",
            summary="明确合同订立、效力、履行、保全、转让、解除等法律适用问题",
            content="为正确审理合同纠纷案件...（全文略）",
            source_url="https://www.court.gov.cn/fabu-xiangqing/xxx.html",
            crawled_at=datetime.now().isoformat()
        ),
        JudicialInterpretation(
            title="最高人民法院关于办理合同纠纷案件若干问题的规定",
            doc_number="法释〔2024〕1 号",
            publish_date="2024-01-15",
            effective_date="2024-02-01",
            department="最高人民法院",
            category="民事",
            summary="规范合同纠纷案件审理，统一裁判尺度",
            content="为依法公正审理合同纠纷案件...（全文略）",
            source_url="https://www.court.gov.cn/fabu-xiangqing/yyy.html",
            crawled_at=datetime.now().isoformat()
        )
    ]


# 测试代码
if __name__ == "__main__":
    crawler = SupremeCourtCrawler()
    
    # 创建示例数据
    sample_data = create_sample_data()
    
    # 保存到 JSON
    crawler.save_to_json(sample_data)
    
    # 导出 Markdown
    crawler.export_to_markdown(sample_data)
    
    # 获取本周摘要
    summary = crawler.get_weekly_update()
    print("\n=== 本周更新摘要 ===")
    print(f"时间：{summary['week_start']} ~ {summary['week_end']}")
    print(f"总数：{summary['total_count']}")
    print(f"分类：{summary['by_category']}")
