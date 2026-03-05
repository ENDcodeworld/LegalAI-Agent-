"""
LegalAI-Agent FastAPI 接口 v2.0
提供合同解析、风险分析、文书生成、司法解释查询等服务
"""

import os
import sys
import uuid
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# 添加项目根目录到路径（使用绝对路径）
LEGALAI_ROOT = Path('/home/admin/.openclaw/workspace/LegalAI-Agent/src')
sys.path.insert(0, str(LEGALAI_ROOT))

# 导入模块
try:
    from parser.contract_parser import ContractParser, Contract, parse_contract_file
    from analyzer.risk_analyzer import RiskAnalyzer, AnalysisResult, RiskLevel
    from generator.document_generator import DocumentGenerator, CaseInfo, LegalDocument
    from generator.court_crawler import SupremeCourtCrawler, JudicialInterpretation, create_sample_data
    print("✅ 模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败：{e}")
    raise


# ==================== 应用初始化 ====================

app = FastAPI(
    title="LegalAI-Agent API",
    description="""
    ## 法律 AI 合同分析服务
    
    提供智能合同解析、风险分析、文书生成、司法解释查询等功能：
    
    ### 核心功能
    - **合同解析**: 支持 PDF/Word/TXT 格式合同文件解析
    - **风险分析**: 基于规则和 AI 识别合同风险点
    - **文书生成**: 自动生成起诉状、律师函、仲裁申请书
    - **司法解释**: 查询最高人民法院最新司法解释
    
    ### 技术特性
    - 支持 CORS 跨域访问
    - Swagger 自动文档
    - 完善的错误处理
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据存储 ====================

contract_storage: Dict[str, Dict[str, Any]] = {}


# ==================== Pydantic 模型 ====================

class ContractParseRequest(BaseModel):
    text: str = Field(..., description="合同文本内容", min_length=1)


class ContractAnalyzeRequest(BaseModel):
    contract_id: str = Field(..., description="合同 ID")


class CaseInfoRequest(BaseModel):
    """案件信息请求"""
    case_type: str = Field(..., description="案件类型：民事/刑事/行政")
    dispute_type: str = Field(..., description="纠纷类型：合同/侵权/劳动/婚姻等")
    plaintiff: str = Field(..., description="原告/申请人")
    defendant: str = Field(..., description="被告/被申请人")
    claims: List[str] = Field(..., description="诉讼请求列表")
    facts: str = Field(..., description="事实与理由")
    evidence: List[str] = Field(default=[], description="证据清单")
    court: Optional[str] = Field(None, description="管辖法院")
    amount: Optional[str] = Field(None, description="标的金额")


class DocumentGenerateRequest(BaseModel):
    """文书生成请求"""
    doc_type: str = Field(..., description="文书类型：起诉状/律师函/仲裁申请书")
    case_info: CaseInfoRequest


# ==================== 健康检查 ====================

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "parser": "✅",
            "analyzer": "✅",
            "generator": "✅",
            "crawler": "✅"
        }
    }


# ==================== 合同解析 API ====================

@app.post("/api/v1/contract/parse", tags=["合同解析"])
async def parse_contract(request: ContractParseRequest):
    """
    解析合同文本，提取条款结构
    """
    try:
        parser = ContractParser()
        contract = parser.parse_text(request.text)
        
        contract_id = str(uuid.uuid4())
        contract_storage[contract_id] = {
            "contract": contract,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "contract_id": contract_id,
            "title": contract.title,
            "parties": contract.parties,
            "sign_date": contract.sign_date,
            "total_clauses": len(contract.clauses),
            "clauses": [
                {
                    "title": c.title,
                    "type": c.clause_type.value,
                    "content_preview": c.content[:100] + "..." if len(c.content) > 100 else c.content
                }
                for c in contract.clauses[:10]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/contract/analyze", tags=["合同解析"])
async def analyze_contract(request: ContractAnalyzeRequest):
    """
    分析合同风险
    """
    try:
        if request.contract_id not in contract_storage:
            raise HTTPException(status_code=404, detail="合同不存在")
        
        data = contract_storage[request.contract_id]
        contract = data["contract"]
        
        analyzer = RiskAnalyzer()
        result = analyzer.analyze(contract)
        
        return {
            "success": True,
            "contract_id": request.contract_id,
            "risk_count": result.risk_count,
            "overall_risk_level": result.overall_risk_level.value,
            "risk_summary": result.risk_summary,
            "risk_points": [
                {
                    "risk_type": r.risk_type.value,
                    "risk_level": r.risk_level.value,
                    "clause_title": r.clause_title,
                    "risk_content": r.risk_content,
                    "original_text": r.original_text[:100] + "..." if len(r.original_text) > 100 else r.original_text,
                    "suggestion": r.suggestion
                }
                for r in result.risk_points
            ],
            "recommendations": result.recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 文书生成 API ====================

@app.post("/api/v1/document/generate", tags=["文书生成"])
async def generate_document(request: DocumentGenerateRequest):
    """
    根据案情生成法律文书
    """
    try:
        generator = DocumentGenerator()
        
        case_info = CaseInfo(
            case_type=request.case_info.case_type,
            dispute_type=request.case_info.dispute_type,
            plaintiff=request.case_info.plaintiff,
            defendant=request.case_info.defendant,
            claims=request.case_info.claims,
            facts=request.case_info.facts,
            evidence=request.case_info.evidence,
            court=request.case_info.court,
            amount=request.case_info.amount
        )
        
        if request.doc_type == "起诉状":
            doc = generator.generate_complaint(case_info)
        elif request.doc_type == "律师函":
            doc = generator.generate_lawyer_letter(case_info)
        elif request.doc_type == "仲裁申请书":
            doc = generator.generate_arbitration_application(case_info)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文书类型：{request.doc_type}")
        
        return {
            "success": True,
            "doc_type": doc.doc_type,
            "title": doc.title,
            "content": doc.content,
            "created_at": doc.created_at,
            "template_version": doc.template_version
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/document/templates", tags=["文书生成"])
async def get_templates():
    """
    获取可用文书模板列表
    """
    generator = DocumentGenerator()
    return {
        "success": True,
        "templates": generator.get_template_list()
    }


# ==================== 司法解释 API ====================

@app.get("/api/v1/interpretations", tags=["司法解释"])
async def get_interpretations(
    days: int = Query(30, description="最近多少天"),
    category: Optional[str] = Query(None, description="分类筛选")
):
    """
    获取最新司法解释
    """
    try:
        crawler = SupremeCourtCrawler()
        
        # 加载示例数据（实际使用需要真实爬取）
        interpretations = create_sample_data()
        
        # 分类筛选
        if category:
            interpretations = [i for i in interpretations if i.category == category]
        
        return {
            "success": True,
            "count": len(interpretations),
            "interpretations": [
                {
                    "title": i.title,
                    "doc_number": i.doc_number,
                    "publish_date": i.publish_date,
                    "effective_date": i.effective_date,
                    "department": i.department,
                    "category": i.category,
                    "summary": i.summary
                }
                for i in interpretations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/interpretations/weekly", tags=["司法解释"])
async def get_weekly_update():
    """
    获取本周司法解释更新摘要
    """
    try:
        crawler = SupremeCourtCrawler()
        summary = crawler.get_weekly_update()
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 启动应用 ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
