"""
AI 风险识别引擎单元测试
测试 50+ 风险类型的识别准确率
"""

import unittest
import sys
from pathlib import Path

# 添加路径
LEGALAI_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(LEGALAI_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from risk_types import RiskType, RiskLevel, RiskCategory, RISK_TYPE_DEFINITIONS
from models import RiskPoint, AnalysisResult, AIAnalysisConfig
from rule_engine import RuleEngine
from confidence_fusion import ConfidenceFusion
from risk_classifier import RiskClassifier
from hybrid_router import HybridAIRouter, RouterConfig


class TestRiskTypes(unittest.TestCase):
    """测试风险类型定义"""
    
    def test_risk_type_count(self):
        """测试风险类型数量（50+）"""
        risk_types = list(RISK_TYPE_DEFINITIONS.keys())
        self.assertGreaterEqual(len(risk_types), 50, "风险类型应达到 50+")
        print(f"✅ 风险类型数量：{len(risk_types)}")
    
    def test_risk_categories(self):
        """测试风险分类（10 大类）"""
        categories = set()
        for definition in RISK_TYPE_DEFINITIONS.values():
            categories.add(definition.category)
        
        self.assertGreaterEqual(len(categories), 10, "风险分类应达到 10 大类")
        print(f"✅ 风险分类数量：{len(categories)}")
    
    def test_risk_type_keywords(self):
        """测试每个风险有关键词"""
        for risk_type, definition in RISK_TYPE_DEFINITIONS.items():
            self.assertGreater(
                len(definition.keywords), 0,
                f"{risk_type.value} 应至少有一个关键词"
            )
    
    def test_risk_type_legal_basis(self):
        """测试关键风险有法律依据"""
        critical_risks = [
            rt for rt, defn in RISK_TYPE_DEFINITIONS.items()
            if defn.default_level == RiskLevel.CRITICAL
        ]
        
        for risk_type in critical_risks:
            definition = RISK_TYPE_DEFINITIONS[risk_type]
            self.assertIsNotNone(
                definition.legal_basis,
                f"{risk_type.value} 应有法律依据"
            )


class TestRuleEngine(unittest.TestCase):
    """测试规则引擎"""
    
    def setUp(self):
        self.engine = RuleEngine()
    
    def test_scan_final_interpretation(self):
        """测试最终解释权识别"""
        text = "本合同最终解释权归甲方所有"
        risks = self.engine.scan(text, "争议解决")
        
        self.assertGreater(len(risks), 0)
        self.assertEqual(risks[0].risk_type, RiskType.UNFAIR_FINAL_INTERPRETATION)
        self.assertEqual(risks[0].risk_level, RiskLevel.CRITICAL)
        print(f"✅ 最终解释权识别：{risks[0].risk_content}")
    
    def test_scan_unlimited_liability(self):
        """测试无限责任识别"""
        text = "乙方需承担无限连带责任，赔偿甲方一切损失"
        risks = self.engine.scan(text, "违约责任")
        
        self.assertGreater(len(risks), 0)
        self.assertEqual(risks[0].risk_type, RiskType.FINANCIAL_UNLIMITED_LIABILITY)
        print(f"✅ 无限责任识别：{risks[0].risk_content}")
    
    def test_scan_unilateral_terminate(self):
        """测试单方解除权识别"""
        text = "甲方可随时解除本合同，无需承担违约责任"
        risks = self.engine.scan(text, "合同终止")
        
        self.assertGreater(len(risks), 0)
        self.assertIn(risks[0].risk_type, [
            RiskType.UNFAIR_UNILATERAL_TERMINATE,
            RiskType.UNFAIR_UNILATERAL_CHANGE
        ])
        print(f"✅ 单方解除权识别：{risks[0].risk_content}")
    
    def test_scan_ambiguous_time(self):
        """测试模糊时间识别"""
        text = "甲方应及时交付产品，具体时间另行通知"
        risks = self.engine.scan(text, "交付条款")
        
        self.assertGreater(len(risks), 0)
        self.assertEqual(risks[0].risk_type, RiskType.AMBIGUOUS_TIME)
        print(f"✅ 模糊时间识别：{risks[0].risk_content}")
    
    def test_scan_exemption_clause(self):
        """测试免责条款识别"""
        text = "甲方对产品质量概不负责，乙方自行承担使用风险"
        risks = self.engine.scan(text, "质量保证")
        
        self.assertGreater(len(risks), 0)
        self.assertEqual(risks[0].risk_type, RiskType.UNFAIR_EXEMPTION_CLAUSE)
        self.assertEqual(risks[0].risk_level, RiskLevel.CRITICAL)
        print(f"✅ 免责条款识别：{risks[0].risk_content}")
    
    def test_scan_multiple_risks(self):
        """测试多风险识别"""
        text = """
        甲方有权随时调整价格，无需通知乙方。
        本合同最终解释权归甲方所有。
        乙方违约需承担无限责任，赔偿一切损失。
        """
        risks = self.engine.scan(text, "综合条款")
        
        self.assertGreaterEqual(len(risks), 3)
        print(f"✅ 多风险识别：共识别{len(risks)}个风险点")
    
    def test_scan_speed(self):
        """测试扫描速度（毫秒级）"""
        import time
        
        text = "本合同最终解释权归甲方所有" * 10
        
        start = time.time()
        for _ in range(100):
            self.engine.scan(text, "测试条款")
        elapsed = (time.time() - start) * 1000
        
        avg_time = elapsed / 100
        self.assertLess(avg_time, 10, "平均扫描时间应小于 10ms")
        print(f"✅ 扫描速度：平均{avg_time:.2f}ms/次")


class TestRiskClassifier(unittest.TestCase):
    """测试风险分类器"""
    
    def setUp(self):
        self.classifier = RiskClassifier()
    
    def test_classify_final_interpretation(self):
        """测试最终解释权分类"""
        text = "本合同最终解释权归甲方所有"
        results = self.classifier.classify(text)
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].risk_type, RiskType.UNFAIR_FINAL_INTERPRETATION)
        self.assertGreater(results[0].confidence, 0.7)
        print(f"✅ 最终解释权分类：置信度{results[0].confidence:.2f}")
    
    def test_classify_unlimited_liability(self):
        """测试无限责任分类"""
        text = "乙方需承担无限连带责任，赔偿一切损失"
        results = self.classifier.classify(text)
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].risk_type, RiskType.FINANCIAL_UNLIMITED_LIABILITY)
        print(f"✅ 无限责任分类：置信度{results[0].confidence:.2f}")
    
    def test_classify_to_risk_point(self):
        """测试转换为风险点"""
        text = "甲方有权随时解除合同"
        risk_points = self.classifier.classify_to_risk_point(text, "合同终止")
        
        self.assertGreater(len(risk_points), 0)
        self.assertIsInstance(risk_points[0], RiskPoint)
        self.assertIsNotNone(risk_points[0].suggestion)
        print(f"✅ 风险点生成：{risk_points[0].risk_content}")


class TestConfidenceFusion(unittest.TestCase):
    """测试置信度融合"""
    
    def setUp(self):
        self.fusion = ConfidenceFusion()
    
    def test_calibrate_single(self):
        """测试单一来源校准"""
        risk_point = RiskPoint(
            risk_type=RiskType.UNFAIR_FINAL_INTERPRETATION,
            risk_level=RiskLevel.CRITICAL,
            clause_title="测试条款",
            risk_content="测试风险",
            original_text="原文",
            confidence=0.8,
            analysis_source="rule"
        )
        
        calibrated = self.fusion.calibrate([risk_point])
        
        self.assertEqual(len(calibrated), 1)
        self.assertLessEqual(calibrated[0].confidence, 0.8 * 0.75)  # 规则引擎可信度 0.75
        print(f"✅ 单一校准：{risk_point.confidence:.2f} → {calibrated[0].confidence:.2f}")
    
    def test_fuse_multiple(self):
        """测试多来源融合"""
        risk_points = [
            RiskPoint(
                risk_type=RiskType.UNFAIR_FINAL_INTERPRETATION,
                risk_level=RiskLevel.CRITICAL,
                clause_title="测试条款",
                risk_content="测试风险",
                original_text="原文",
                confidence=0.75,
                analysis_source="rule"
            ),
            RiskPoint(
                risk_type=RiskType.UNFAIR_FINAL_INTERPRETATION,
                risk_level=RiskLevel.CRITICAL,
                clause_title="测试条款",
                risk_content="测试风险",
                original_text="原文",
                confidence=0.95,
                analysis_source="llm"
            ),
        ]
        
        fused = self.fusion.fuse(risk_points)
        
        self.assertEqual(len(fused), 1)
        self.assertGreater(fused[0].fused_confidence, 0.8)
        print(f"✅ 多源融合：置信度{fused[0].fused_confidence:.2f}")
    
    def test_filter_by_confidence(self):
        """测试置信度过滤"""
        risk_points = [
            RiskPoint(
                risk_type=RiskType.UNFAIR_FINAL_INTERPRETATION,
                risk_level=RiskLevel.CRITICAL,
                clause_title="测试",
                risk_content="测试",
                original_text="原文",
                confidence=0.5
            ),
            RiskPoint(
                risk_type=RiskType.FINANCIAL_UNLIMITED_LIABILITY,
                risk_level=RiskLevel.CRITICAL,
                clause_title="测试",
                risk_content="测试",
                original_text="原文",
                confidence=0.9
            ),
        ]
        
        filtered = self.fusion.filter_by_confidence(risk_points, 0.7)
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].confidence, 0.9)
        print(f"✅ 置信度过滤：{len(risk_points)} → {len(filtered)}")


class TestHybridRouter(unittest.TestCase):
    """测试混合 AI 路由器"""
    
    def setUp(self):
        config = RouterConfig(
            rule_high_confidence=0.7,
            max_llm_calls=5,
            budget_per_contract=1.0,
        )
        self.router = HybridAIRouter(config=config)
    
    def test_analyze_simple_contract(self):
        """测试简单合同分析"""
        sys.path.insert(0, str(LEGALAI_ROOT))
        from parser.contract_parser import ContractParser
        
        contract_text = """
        买卖合同
        
        甲方：北京科技有限公司
        乙方：上海贸易有限公司
        
        第一条 价格调整
        甲方有权随时调整价格，无需通知乙方。
        
        第二条 最终解释权
        本合同最终解释权归甲方所有。
        
        第三条 责任限制
        甲方对产品质量概不负责。
        """
        
        parser = ContractParser()
        contract = parser.parse_text(contract_text)
        
        result = self.router.analyze(contract.clauses)
        
        self.assertGreater(result.risk_count, 0)
        self.assertEqual(result.contract_title, "买卖合同")
        print(f"✅ 简单合同分析：识别{result.risk_count}个风险点")
        print(f"   总体风险：{result.overall_risk_level.value}")
    
    def test_analyze_complex_contract(self):
        """测试复杂合同分析"""
        sys.path.insert(0, str(LEGALAI_ROOT))
        from parser.contract_parser import ContractParser
        
        contract_text = """
        合作协议
        
        甲方：北京科技有限公司
        乙方：上海贸易有限公司
        
        第一条 合作内容
        乙方应及时提供所需服务，具体标准由甲方确定。
        
        第二条 付款条款
        乙方应在签约后 30 日内支付全部价款。
        
        第三条 违约责任
        乙方违约需承担无限连带责任，赔偿甲方一切损失。
        甲方违约仅退还已收取费用。
        
        第四条 合同解除
        甲方可随时解除本合同，无需承担任何责任。
        
        第五条 知识产权
        合作期间产生的所有知识产权归甲方所有。
        
        第六条 保密条款
        乙方应对所有信息永久保密，不得向任何第三方披露。
        
        第七条 争议解决
        本合同最终解释权归甲方所有，争议由甲方所在地法院管辖。
        """
        
        parser = ContractParser()
        contract = parser.parse_text(contract_text)
        
        result = self.router.analyze(contract.clauses)
        
        self.assertGreaterEqual(result.risk_count, 5)
        print(f"✅ 复杂合同分析：识别{result.risk_count}个风险点")
        print(f"   总体风险：{result.overall_risk_level.value}")
        print(f"   风险汇总：{result.risk_summary}")
    
    def test_router_stats(self):
        """测试路由统计"""
        sys.path.insert(0, str(LEGALAI_ROOT))
        from parser.contract_parser import ContractParser
        
        contract_text = """
        测试合同
        
        第一条 甲方有权随时解除合同。
        第二条 本合同最终解释权归甲方所有。
        """
        
        parser = ContractParser()
        contract = parser.parse_text(contract_text)
        
        self.router.analyze(contract.clauses)
        stats = self.router.get_stats()
        
        self.assertIn("total_clauses", stats)
        self.assertIn("rule_engine_hits", stats)
        self.assertIn("total_time_ms", stats)
        print(f"✅ 路由统计：{stats}")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        sys.path.insert(0, str(LEGALAI_ROOT))
        from parser.contract_parser import ContractParser
        from hybrid_router import HybridAIRouter
        
        # 示例合同
        contract_text = """
        技术服务合同
        
        甲方：北京科技有限公司
        乙方：张三个人
        
        第一条 服务内容
        乙方应及时提供技术开发服务，具体标准由甲方确定。
        
        第二条 知识产权
        乙方开发的所有成果归甲方所有，乙方不得主张任何权利。
        
        第三条 保密义务
        乙方应对所有信息永久保密，保密期限不受合同终止影响。
        
        第四条 违约责任
        乙方违约需赔偿甲方一切损失，包括但不限于直接损失、间接损失。
        甲方违约仅退还已支付费用。
        
        第五条 合同解除
        甲方可随时解除合同，无需提前通知。
        乙方解除合同需提前 30 日书面通知，并支付违约金。
        
        第六条 争议解决
        本合同最终解释权归甲方所有。
        """
        
        # 解析合同
        parser = ContractParser()
        contract = parser.parse_text(contract_text)
        
        # AI 风险分析
        router = HybridAIRouter()
        result = router.analyze(contract.clauses)
        
        # 验证结果
        self.assertGreater(result.risk_count, 0)
        self.assertIn("严重风险", result.risk_summary)
        
        # 输出报告
        print("\n" + "="*60)
        print("AI 风险分析报告")
        print("="*60)
        print(f"合同：{result.contract_title}")
        print(f"条款数：{result.total_clauses}")
        print(f"风险点：{result.risk_count}")
        print(f"总体风险：{result.overall_risk_level.value}")
        print(f"\n风险汇总:")
        for level, count in result.risk_summary.items():
            if count > 0:
                print(f"  {level}: {count}")
        
        print(f"\n分类汇总:")
        for category, count in result.category_summary.items():
            if count > 0:
                print(f"  {category}: {count}")
        
        print(f"\nTop 风险点:")
        for i, risk in enumerate(result.risk_points[:5], 1):
            print(f"{i}. [{risk.risk_level.value}] {risk.risk_type.value}")
            print(f"   原文：{risk.original_text[:50]}...")
            print(f"   置信度：{risk.confidence:.2f}")
            print(f"   建议：{risk.suggestion[:50]}...")
        
        print(f"\n总体建议:")
        for rec in result.recommendations:
            print(f"  {rec}")
        
        print(f"\n分析统计:")
        stats = result.analysis_metadata.get("stats", {})
        print(f"  总耗时：{stats.get('total_time_ms', 0):.2f}ms")
        print(f"  规则引擎命中：{stats.get('rule_engine_hits', 0)}")
        print(f"  LLM 调用：{stats.get('llm_hits', 0)}")
        print(f"  预估成本：¥{stats.get('estimated_cost', 0):.2f}")
        print("="*60)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestRiskTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceFusion))
    suite.addTests(loader.loadTestsFromTestCase(TestHybridRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
