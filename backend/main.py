import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from manager import AgentManager
from config import setup_api

class UserQuery(BaseModel):
    message: str
    user_id: str
    device_info: Optional[Dict] = None

class EducationLink(BaseModel):
    title: str
    url: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    is_fraud: bool
    confidence: float
    explanation: str
    recommendations: List[str]
    education_links: List[EducationLink]
    educational_text: str
    education_tips: List[str]

class Feedback(BaseModel):
    analysis_id: str
    feedback_type: str
    comment: Optional[str] = None

setup_api()

app = FastAPI(
    title="API Detector de Golpes",
    description="Backend para o sistema de detecção de golpes usando Agentes de IA",
    version="1.0.0",
)

origins = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_message_endpoint(query: UserQuery):
    print(f"Recebida solicitação de análise para user_id: {query.user_id}")
    try:
        result = await agent_manager.process_user_query(query.dict())
        return AnalysisResponse(**result)
    except Exception as e:
        print(f"Erro na análise: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao processar sua solicitação.")

@app.post("/feedback")
async def submit_feedback_endpoint(feedback_data: Feedback):
    print(f"Feedback recebido: {feedback_data.dict()}")
    return {"status": "success", "message": "Feedback recebido. Obrigado!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)