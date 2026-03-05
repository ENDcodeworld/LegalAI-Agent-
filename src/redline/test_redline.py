"""
智能 Redline 生成模块测试用例

测试覆盖：
1. 基础功能测试
2. 不同风险类型测试
3. 建议质量等级测试
4. 报告导出测试
5. 边界条件测试
"""

import unittest
import sys
import os
from datetime import datetime

# 添加路径
sys.path.insert(0, '/home/admin/.openclaw/workspace/LegalAI-Agent/src')

from analyzer.risk_analyzer import RiskAnalyzer, RiskPoint, RiskType, RiskLevel
from parser.contract_parser import ContractParser, Clause, ClauseType, Contract
from redline.redline_generator import SmartRedlineGenerator
from redline.models import (
    RedlineSuggestion,
    RedlineLevel,
    RedlineType,
    RedlineReport,
    MarketBenchmark,
    LegalBasis,
    RiskSeverity
)
from redline.report_exporter import RedlineReportExporter


class TestRedlineSuggestion(unittest.TestCase):
    """RedlineSuggestion 数据模型测试"""
    
    def test_create_suggestion(self):
        """测试创建建议对象"""
        suggestion = RedlineSuggestion(
            suggestion_id="test-001",
            risk_point_id="risk-001",
            original_text="甲方有权随时调整价格",
            suggested_text="价格调整需经双方协商一致",
            redline_type=RedlineType.MODIFICATION,
            level=RedlineLevel.L4_INTELLIGENT,
            rationale="原条款违反公平原则",
            confidence=0.9,
            adoption_probability=0.85,
            priority=RiskSeverity.HIGH
        )
        
        self.assertEqual(suggestion.suggestion_id, "test-001")
        self.assertEqual(suggestion.level, RedlineLevel.L4_INTELLIGENT)
        self.assertEqual(suggestion.confidence, 0.9)
        self.assertGreater(suggestion.adoption_probability, 0.8)
    
    def test_suggestion_to_dict(self):
        """测试建议对象转字典"""
        suggestion = RedlineSuggestion(
            suggestion_id="test-002",
            risk_point_id="risk-002",
            original_text="测试原文",
            suggested_text="测试建议",
            redline_type=RedlineType.MODIFICATION,
            level=RedlineLevel.L3_SPECIFIC,
            rationale="测试理由"
        )
        
        data = suggestion.to_dict()
        
        self.assertIn('suggestion_id', data)
        self.assertIn('original_text', data)
        self.assertIn('suggested_text', data)
        self.assertEqual(data['suggestion_id'], "test-002")
        self.assertEqual(data['level'], "L3-具体建议")
    
    def test_get_diff_display(self):
        """测试差异显示"""
        # 修改类型
        suggestion_mod = RedlineSuggestion(
            suggestion_id="test-003",
            risk_point_id="risk-003",
            original_text="旧文本",
            suggested_text="新文本",
            redline_type=RedlineType.MODIFICATION,
            level=RedlineLevel.L3_SPECIFIC,
            rationale="测试"
        )
        diff = suggestion_mod.get_diff_display()
        self.assertIn("~~", diff)
        self.assertIn("**", diff)
        
        # 删除类型
        suggestion_del = RedlineSuggestion(
            suggestion_id="test-004",
            risk_point_id="risk-004",
            original_text="删除文本",
            suggested_text="",
            redline_type=RedlineType.DELETION,
            level=RedlineLevel.L3_SPECIFIC,
            rationale="测试"
        )
        diff = suggestion_del.get_diff_display()
        self.assertIn("~~", diff)


class TestSmartRedlineGenerator(unittest.TestCase):
    """SmartRedlineGenerator 核心功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = SmartRedlineGenerator()
        self.parser = ContractParser()
        self.analyzer = RiskAnalyzer()
    
    def test_generate_for_single_risk(self):
        """测试为单个风险点生成建议"""
        risk_point = RiskPoint(
            risk_type=RiskType.UNFAIR_CLAUSE,
            risk_level=RiskLevel.HIGH,
            clause_title="价格条款",
            risk_content="发现单方变更权",
            original_text="甲方有权随时调整价格，无需通知乙方",
            legal_basis="《民法典》第 543 条",
            suggestion="建议修改为双方协商",
            confidence=0.85
        )
        
        suggestion = self.generator.generate(risk_point)
        
        self.assertIsInstance(suggestion, RedlineSuggestion)
        self.assertIsNotNone(suggestion.suggestion_id)
        self.assertEqual(suggestion.original_text, risk_point.original_text)
        self.assertGreater(len(suggestion.suggested_text), 0)
        self.assertGreater(suggestion.confidence, 0.5)
    
    def test_l4_level_generation(self):
        """测试 L4 级建议生成"""
        risk_point = RiskPoint(
            risk_type=RiskType.UNFAIR_CLAUSE,
            risk_level=RiskLevel.CRITICAL,
            clause_title="解释权条款",
            risk_content="最终解释权条款",
            original_text="本合同最终解释权归甲方所有",
            confidence=0.9
        )
        
        suggestion = self.generator.generate(risk_point)
        
        # L4 级建议应该有法律依据和市场基准
        self.assertEqual(suggestion.level, RedlineLevel.L4_INTELLIGENT)
        self.assertGreater(len(suggestion.legal_basis), 0)
        self.assertIsNotNone(suggestion.market_benchmark)
    
    def test_risk_type_identification(self):
        """测试风险类型识别"""
        test_cases = [
            ("甲方有权随时调整价格", "单方变更权"),
            ("最终解释权归甲方", "最终解释权"),
            ("承担无限连带责任", "无限责任"),
            ("及时交付", "模糊表述"),
        ]
        
        for text, expected_type in test_cases:
            # 使用字符串而非枚举，以便测试基于文本的识别
            risk_point = RiskPoint(
                risk_type="UNKNOWN",  # 使用字符串强制基于文本识别
                risk_level=RiskLevel.HIGH,
                clause_title="测试条款",
                risk_content="测试",
                original_text=text,
                confidence=0.8
            )
            
            identified_type = self.generator._identify_risk_type(risk_point)
            self.assertEqual(identified_type, expected_type, f"Failed for: {text}")
    
    def test_confidence_calculation(self):
        """测试置信度计算"""
        risk_point = RiskPoint(
            risk_type=RiskType.UNFAIR_CLAUSE,
            risk_level=RiskLevel.CRITICAL,
            clause_title="测试",
            risk_content="测试",
            original_text="测试文本",
            confidence=0.9
        )
        
        legal_basis = [
            LegalBasis("《民法典》", "第 543 条", "测试内容", "测试相关性")
        ]
        market_benchmark = MarketBenchmark(
            industry="通用",
            clause_type="测试",
            standard_practice="测试惯例",
            adoption_rate=0.85
        )
        
        confidence = self.generator._calculate_confidence(
            risk_point, legal_basis, market_benchmark
        )
        
        self.assertGreater(confidence, 0.7)
        self.assertLessEqual(confidence, 0.99)
    
    def test_adoption_probability_estimation(self):
        """测试采纳率估算"""
        probability = self.generator._estimate_adoption_probability(
            risk_type="单方变更权",
            priority=RiskSeverity.CRITICAL,
            confidence=0.9,
            market_benchmark=MarketBenchmark(
                industry="通用",
                clause_type="测试",
                standard_practice="测试",
                adoption_rate=0.85
            )
        )
        
        self.assertGreater(probability, 0.7)
        self.assertLessEqual(probability, 0.95)


class TestRedlineReportGeneration(unittest.TestCase):
    """Redline 报告生成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = SmartRedlineGenerator()
        self.parser = ContractParser()
        self.analyzer = RiskAnalyzer()
    
    def test_full_report_generation(self):
        """测试完整报告生成"""
        contract_text = """
        买卖合同
        
        甲方：北京科技有限公司
        乙方：上海贸易有限公司
        
        第一条 价格调整
        甲方有权随时调整产品价格，无需通知乙方。
        
        第二条 合同解除
        甲方可随时解除本合同。
        
        第三条 违约责任
        乙方违约需承担无限连带责任，赔偿一切损失。
        
        第四条 争议解决
        本合同最终解释权归甲方所有。
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        self.assertIsInstance(report, RedlineReport)
        self.assertGreater(report.total_suggestions, 0)
        self.assertIsNotNone(report.executive_summary)
        self.assertIsNotNone(report.overall_risk_assessment)
        self.assertGreater(len(report.key_recommendations), 0)
    
    def test_report_statistics(self):
        """测试报告统计信息"""
        contract_text = """
        买卖合同
        
        第一条 价格
        甲方有权随时调整价格。
        
        第二条 解释权
        最终解释权归甲方。
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        stats = report.get_statistics()
        
        self.assertIn('total_suggestions', stats)
        self.assertIn('l4_adoption_rate', stats)
        self.assertIn('avg_confidence', stats)
        self.assertGreater(stats['total_suggestions'], 0)
    
    def test_l4_adoption_rate(self):
        """测试 L4 级建议占比"""
        contract_text = """
        买卖合同
        
        第一条 甲方有权随时调整价格，无需通知乙方。
        第二条 最终解释权归甲方所有。
        第三条 乙方承担无限责任。
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        # 应该有一定比例的 L4 级建议
        l4_count = report.suggestions_by_level.get('L4-智能 Redline', 0)
        self.assertGreater(l4_count, 0)
        self.assertGreater(report.l4_adoption_rate, 0.5)


class TestReportExporter(unittest.TestCase):
    """报告导出器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = SmartRedlineGenerator()
        self.parser = ContractParser()
        self.analyzer = RiskAnalyzer()
        self.exporter = RedlineReportExporter(output_dir='./test_exports')
        
        # 生成测试报告
        contract_text = """
        买卖合同
        
        第一条 甲方有权随时调整价格。
        第二条 最终解释权归甲方。
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        self.report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
    
    def test_export_json(self):
        """测试 JSON 导出"""
        filepath = self.exporter.export(self.report, format='json', filename='test_json')
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.json'))
        
        # 验证 JSON 内容
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('report_id', data)
        self.assertIn('total_suggestions', data)
        self.assertIn('all_suggestions', data)
    
    def test_export_html(self):
        """测试 HTML 导出"""
        filepath = self.exporter.export(self.report, format='html', filename='test_html')
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.html'))
        
        # 验证 HTML 内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('<html', content)
        self.assertIn(self.report.contract_name, content)
        self.assertIn('Redline', content)
    
    def test_export_all_formats(self):
        """测试所有格式导出"""
        results = self.exporter.export_all_formats(
            self.report,
            filename='test_all'
        )
        
        # JSON 和 HTML 应该成功
        self.assertIsNotNone(results.get('json'))
        self.assertIsNotNone(results.get('html'))


class TestEdgeCases(unittest.TestCase):
    """边界条件和异常测试"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = SmartRedlineGenerator()
        self.parser = ContractParser()
        self.analyzer = RiskAnalyzer()
    
    def test_empty_contract(self):
        """测试空合同"""
        contract_text = ""
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        self.assertIsInstance(report, RedlineReport)
        self.assertEqual(report.total_suggestions, 0)
    
    def test_no_risk_contract(self):
        """测试无风险合同"""
        contract_text = """
        买卖合同
        
        第一条 双方平等协商
        第二条 价格经双方协商确定
        第三条 争议友好协商解决
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        self.assertIsInstance(report, RedlineReport)
        # 可能仍有少量建议，但应该很少
    
    def test_very_long_clause(self):
        """测试超长条款"""
        long_text = "甲方权利：" + "有权决定" * 1000
        contract_text = f"""
        买卖合同
        
        第一条 {long_text}
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        
        # 不应该崩溃
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        self.assertIsInstance(report, RedlineReport)
    
    def test_special_characters(self):
        """测试特殊字符"""
        contract_text = """
        买卖合同
        
        第一条 价格调整<>&"'
        第二条 解释权归©®™甲方
        """
        
        contract = self.parser.parse_text(contract_text)
        analysis_result = self.analyzer.analyze(contract)
        
        # 不应该崩溃
        report = self.generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        self.assertIsInstance(report, RedlineReport)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流程"""
        # 1. 准备合同
        contract_text = """
        技术服务合同
        
        甲方：北京科技有限公司
        乙方：上海技术服务中心
        
        第一条 服务内容
        乙方为甲方提供技术开发服务。
        
        第二条 费用支付
        甲方应在合同签订后 30 日内支付全部费用。
        
        第三条 价格调整
        乙方有权根据市场情况随时调整服务价格，无需通知甲方。
        
        第四条 知识产权
        服务过程中产生的所有知识产权归乙方所有。
        
        第五条 违约责任
        甲方违约需承担无限连带责任，赔偿乙方一切损失。
        
        第六条 合同解除
        乙方可随时解除本合同，无需承担任何责任。
        
        第七条 争议解决
        本合同最终解释权归乙方所有。
        """
        
        # 2. 解析合同
        parser = ContractParser()
        contract = parser.parse_text(contract_text)
        
        # 3. 分析风险
        analyzer = RiskAnalyzer()
        analysis_result = analyzer.analyze(contract)
        
        # 4. 生成 Redline
        generator = SmartRedlineGenerator()
        report = generator.generate_report(
            contract=contract,
            risk_points=analysis_result.risk_points,
            clauses=contract.clauses
        )
        
        # 5. 验证报告质量
        self.assertGreater(report.total_suggestions, 3, "应该发现多个风险点")
        self.assertGreater(report.l4_adoption_rate, 0.5, "L4 级建议占比应超过 50%")
        
        # 6. 导出报告
        exporter = RedlineReportExporter(output_dir='./test_integration')
        results = exporter.export_all_formats(report, filename='integration_test')
        
        # 7. 验证导出
        self.assertIsNotNone(results.get('json'))
        self.assertIsNotNone(results.get('html'))
        
        # 8. 打印摘要
        print("\n" + "="*60)
        print("集成测试报告摘要")
        print("="*60)
        print(f"合同：{report.contract_name}")
        print(f"总建议数：{report.total_suggestions}")
        print(f"L4 级建议：{report.suggestions_by_level.get('L4-智能 Redline', 0)}")
        print(f"L4 占比：{report.l4_adoption_rate * 100:.1f}%")
        print(f"严重风险：{report.suggestions_by_priority.get('严重', 0)}")
        print(f"高风险：{report.suggestions_by_priority.get('高', 0)}")
        print("\n关键建议:")
        for i, rec in enumerate(report.key_recommendations[:3], 1):
            print(f"{i}. {rec}")
        print("="*60)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestRedlineSuggestion))
    suite.addTests(loader.loadTestsFromTestCase(TestSmartRedlineGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestRedlineReportGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestReportExporter))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
