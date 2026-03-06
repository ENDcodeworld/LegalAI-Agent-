"""
智能 Redline 生成模块
实现 AI 自动生成的修改建议（红线圈注 + 修改文本 + 修改说明）

功能：
- 识别风险条款后，自动生成修改建议
- 红线圈注：标记需要修改的原文位置
- 修改文本：提供具体的修改后文本
- 修改说明：解释为什么这样修改
- 目标：L4 级自动化，80%+ 建议可直接采用
"""

from .models import (
    RedlineSuggestion,
    RedlineLevel,
    RedlineReport,
    MarketBenchmark,
    LegalBasis
)
from .redline_generator import SmartRedlineGenerator
from .report_exporter import RedlineReportExporter

__all__ = [
    'RedlineSuggestion',
    'RedlineLevel',
    'RedlineReport',
    'MarketBenchmark',
    'LegalBasis',
    'SmartRedlineGenerator',
    'RedlineReportExporter'
]

__version__ = '1.0.0'
