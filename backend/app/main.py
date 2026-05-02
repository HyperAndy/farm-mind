from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.greenhouses import router as greenhouse_router


app = FastAPI(
    title="设施大棚智能管控 Agent - API",
    version="1.0.0",
    description="温室环境监控、告警和智能控制建议API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(greenhouse_router)


@app.get("/")
async def root():
    return {"message": "设施大棚智能管控 Agent API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)