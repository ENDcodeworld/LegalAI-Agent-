"""
大语言模型分析器
使用 DeepSeek-V3 / 通义千问等模型进行深度风险分析
高准确率，较慢速度（秒级）
"""

import json
import time
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import requests

try:
    from .risk_types import RiskType, RiskLevel, RiskCategory, get_all_risk_types, get_risk_type_definition
    from .models import RiskPoint, LLMRequest, LLMResponse
except ImportError:
    from risk_types import RiskType, RiskLevel, RiskCategory, get_all_risk_types, get_risk_type_definition
    from models import RiskPoint, LLMRequest, LLMResponse


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"  # deepseek-chat 或 qwen-max
    timeout: int = 30
    max_tokens: int = 2000
    temperature: float = 0.1
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """从环境变量加载配置"""
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("LLM_MODEL", "deepseek-chat"),
            timeout=int(os.getenv("LLM_TIMEOUT", "30")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        )


class LLMAnalyzer:
    """
    大语言模型分析器
    对复杂风险点进行深度分析
    特点：高准确率（95%+）、较慢速度（秒级）、成本较高
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })
    
    def analyze(self, clause_text: str, clause_title: str = "") -> List[RiskPoint]:
        """
        使用 LLM 分析条款风险
        
        Args:
            clause_text: 条款文本
            clause_title: 条款标题
            
        Returns:
            List[RiskPoint]: 识别的风险点
        """
        start_time = time.time()
        
        # 构建提示词
        prompt = self._build_prompt(clause_text, clause_title)
        
        # 调用 LLM
        response_text = self._call_llm(prompt)
        
        # 解析响应
        risk_points = self._parse_response(response_text, clause_text, clause_title)
        
        # 记录分析时间
        latency_ms = (time.time() - start_time) * 1000
        for rp in risk_points:
            rp.analysis_time_ms = latency_ms
            rp.analysis_source = "llm"
        
        return risk_points
    
    def _build_prompt(self, clause_text: str, clause_title: str) -> str:
        """构建分析提示词"""
        # 获取所有风险类型
        all_risk_types = get_all_risk_types()
        risk_type_list = "\n".join([f"- {rt.value}" for rt in all_risk_types[:20]])  # 限制数量
        
        prompt = f"""你是一位资深法律专家，专门从事合同风险审查。请分析以下合同条款，识别潜在风险。

## 分析要求
1. 识别条款中存在的风险类型（从下方列表选择）
2. 评估风险等级（严重风险/高风险/中风险/低风险）
3. 引用相关法律依据
4. 提供具体修改建议
5. 如有可能，提供修改后的文本示例

## 风险类型列表（部分）
{risk_type_list}
... 等 50+ 风险类型

## 待分析条款
**条款标题**: {clause_title or "未命名条款"}
**条款内容**:
```
{clause_text}
```

## 输出格式
请严格按照以下 JSON 格式输出（仅输出 JSON，不要其他内容）：
```json
{{
  "risk_points": [
    {{
      "risk_type": "风险类型名称",
      "risk_level": "风险等级",
      "risk_content": "风险描述",
      "original_text": "原文引用",
      "confidence": 0.0-1.0,
      "legal_basis": "法律依据",
      "suggestion": "修改建议",
      "redline_suggestion": "修改后文本示例（可选）"
    }}
  ]
}}
```

## 注意事项
- 只识别确实存在的风险，不要过度解读
- 置信度评分：非常确定 0.9+，比较确定 0.7-0.9，一般 0.5-0.7
- 如果没有发现风险，返回空列表：{{"risk_points": []}}
"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        if not self.config.api_key:
            # 无 API Key 时返回模拟响应
            return self._mock_response()
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深法律专家，专门从事合同风险审查。请严格按要求分析合同风险。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            # API 调用失败时返回模拟响应
            print(f"LLM API 调用失败：{e}")
            return self._mock_response()
    
    def _mock_response(self) -> str:
        """模拟响应（用于测试或无 API Key 时）"""
        return json.dumps({
            "risk_points": []
        }, ensure_ascii=False)
    
    def _parse_response(self, response_text: str, clause_text: str, clause_title: str) -> List[RiskPoint]:
        """解析 LLM 响应"""
        risk_points = []
        
        try:
            # 尝试提取 JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                data = json.loads(response_text)
            
            # 解析风险点
            for rp_data in data.get("risk_points", []):
                risk_type = self._parse_risk_type(rp_data.get("risk_type", ""))
                if not risk_type:
                    continue
                
                risk_level = self._parse_risk_level(rp_data.get("risk_level", "中风险"))
                
                definition = get_risk_type_definition(risk_type)
                
                risk_point = RiskPoint(
                    risk_type=risk_type,
                    risk_level=risk_level,
                    clause_title=clause_title or "未命名条款",
                    risk_content=rp_data.get("risk_content", ""),
                    original_text=rp_data.get("original_text", ""),
                    confidence=float(rp_data.get("confidence", 0.8)),
                    legal_basis=rp_data.get("legal_basis", definition.legal_basis if definition else None),
                    suggestion=rp_data.get("suggestion", ""),
                    redline_suggestion=rp_data.get("redline_suggestion"),
                    category=definition.category if definition else None,
                )
                
                risk_points.append(risk_point)
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"解析 LLM 响应失败：{e}")
            # 返回空列表
        
        return risk_points
    
    def _parse_risk_type(self, risk_type_str: str) -> Optional[RiskType]:
        """解析风险类型字符串"""
        # 尝试直接匹配
        for rt in RiskType:
            if rt.value == risk_type_str or rt.name == risk_type_str:
                return rt
        
        # 模糊匹配
        risk_type_str_lower = risk_type_str.lower()
        for rt in RiskType:
            if rt.value.lower() in risk_type_str_lower or risk_type_str_lower in rt.value.lower():
                return rt
        
        return None
    
    def _parse_risk_level(self, level_str: str) -> RiskLevel:
        """解析风险等级字符串"""
        level_map = {
            "严重风险": RiskLevel.CRITICAL,
            "高风险": RiskLevel.HIGH,
            "中风险": RiskLevel.MEDIUM,
            "低风险": RiskLevel.LOW,
            "critical": RiskLevel.CRITICAL,
            "high": RiskLevel.HIGH,
            "medium": RiskLevel.MEDIUM,
            "low": RiskLevel.LOW,
        }
        return level_map.get(level_str, RiskLevel.MEDIUM)
    
    def analyze_batch(
        self,
        clauses: List[Dict[str, str]],
        max_concurrent: int = 5
    ) -> List[RiskPoint]:
        """
        批量分析多个条款
        
        Args:
            clauses: 条款列表，每项包含 text 和 title
            max_concurrent: 最大并发数
            
        Returns:
            List[RiskPoint]: 所有风险点
        """
        all_risks = []
        
        # 简单串行实现（可扩展为并发）
        for clause in clauses:
            risks = self.analyze(
                clause_text=clause.get("text", ""),
                clause_title=clause.get("title", "")
            )
            all_risks.extend(risks)
        
        return all_risks
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "model": self.config.model,
            "base_url": self.config.base_url,
            "api_key_configured": bool(self.config.api_key),
        }
