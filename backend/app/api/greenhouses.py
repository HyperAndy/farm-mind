from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import random
import uuid

from app.models.schemas import (
    Greenhouse, GreenhouseCreate, EnvironmentData,
    Alert, Suggestion, WeatherForecast, CropType
)
from app.agent.greenhoust_agent import get_agent, CROP_OPTIMAL


router = APIRouter(prefix="/api/v1", tags=["greenhouses"])

# 模拟数据库
greenhouses_db: dict[str, Greenhouse] = {}


@router.post("/greenhouses", response_model=Greenhouse)
async def create_greenhouse(gh: GreenhouseCreate):
    """创建大棚"""
    greenhouse = Greenhouse(
        id=str(uuid.uuid4()),
        org_id="org_default",
        name=gh.name,
        location=gh.location,
        area=gh.area,
        crop_type=gh.crop_type,
        status="active",
        created_at=datetime.now()
    )
    greenhouses_db[greenhouse.id] = greenhouse
    return greenhouse


@router.get("/greenhouses")
async def list_greenhouses():
    """列出所有大棚"""
    return list(greenhouses_db.values())


@router.get("/greenhouses/{greenhouse_id}")
async def get_greenhouse(greenhouse_id: str):
    """获取大棚详情"""
    if greenhouse_id not in greenhouses_db:
        raise HTTPException(status_code=404, detail="大棚不存在")
    return greenhouses_db[greenhouse_id]


@router.get("/greenhouses/{greenhouse_id}/env/current")
async def get_current_env(greenhouse_id: str):
    """获取当前环境数据（模拟）"""
    if greenhouse_id not in greenhouses_db:
        raise HTTPException(status_code=404, detail="大棚不存在")

    gh = greenhouses_db[greenhouse_id]
    optimal = CROP_OPTIMAL.get(gh.crop_type, CROP_OPTIMAL[CropType.TOMATO])

    # 生成模拟数据，围绕最佳值上下波动
    env = EnvironmentData(
        temperature=optimal["temp_min"] + random.uniform(-3, 8),
        humidity=optimal["humidity_min"] + random.uniform(5, 40),
        light=optimal["light_min"] + random.randint(-5000, 15000),
        co2=optimal["co2_min"] + random.randint(-100, 300),
        soil_ec=optimal.get("soil_ec_min", 1.5) + random.uniform(-0.3, 0.5),
        soil_pH=optimal.get("soil_pH_min", 6.0) + random.uniform(-0.5, 0.8),
        soil_temp=optimal["temp_min"] + random.uniform(-2, 5),
        soil_moisture=40 + random.randint(-15, 30)
    )
    return env


@router.get("/greenhouses/{greenhouse_id}/env/history")
async def get_env_history(
    greenhouse_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: str = "5m"
):
    """获取历史环境数据（模拟）"""
    if greenhouse_id not in greenhouses_db:
        raise HTTPException(status_code=404, detail="大棚不存在")

    gh = greenhouses_db[greenhouse_id]
    optimal = CROP_OPTIMAL.get(gh.crop_type, CROP_OPTIMAL[CropType.TOMATO])

    # 生成24小时模拟数据
    now = datetime.now()
    records = []
    for i in range(24):
        timestamp = now - timedelta(hours=24-i)
        env = EnvironmentData(
            temperature=optimal["temp_min"] + random.uniform(-2, 6),
            humidity=optimal["humidity_min"] + random.uniform(5, 35),
            light=max(5000, optimal["light_min"] + random.randint(-8000, 20000)),
            co2=optimal["co2_min"] + random.randint(-50, 200),
            soil_ec=optimal.get("soil_ec_min", 1.5) + random.uniform(-0.2, 0.4),
            soil_pH=optimal.get("soil_pH_min", 6.0) + random.uniform(-0.3, 0.5),
            soil_temp=optimal["temp_min"] + random.uniform(-1, 4),
            soil_moisture=40 + random.randint(-10, 25)
        )
        records.append({"timestamp": timestamp.isoformat(), **env.model_dump()})

    return {"records": records, "count": len(records)}


@router.get("/greenhouses/{greenhouse_id}/weather")
async def get_weather(greenhouse_id: str):
    """获取天气预报（模拟）"""
    if greenhouse_id not in greenhouses_db:
        raise HTTPException(status_code=404, detail="大棚不存在")

    # 生成3天模拟预报
    forecasts = []
    weathers = ["sunny", "cloudy", "rainy"]
    for i in range(3):
        timestamp = datetime.now() + timedelta(days=i+1)
        forecasts.append(WeatherForecast(
            timestamp=timestamp,
            temp_high=28 + random.randint(-3, 8),
            temp_low=18 + random.randint(-2, 5),
            humidity=60 + random.randint(-15, 20),
            weather=random.choice(weathers),
            precipitation=random.choice([0, 0, 0, 5, 10, 20])
        ))
    return {"forecasts": forecasts}


@router.post("/greenhouses/{greenhouse_id}/analyze")
async def analyze_environment(greenhouse_id: str):
    """分析环境并生成建议"""
    if greenhouse_id not in greenhouses_db:
        raise HTTPException(status_code=404, detail="大棚不存在")

    gh = greenhouses_db[greenhouse_id]
    try:
        agent = get_agent(greenhouse_id, gh.crop_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent初始化失败: {str(e)}")

    try:
        # 直接生成模拟数据
        import random
        optimal = CROP_OPTIMAL.get(gh.crop_type, CROP_OPTIMAL[CropType.TOMATO])
        env = EnvironmentData(
            temperature=optimal["temp_min"] + random.uniform(-3, 8),
            humidity=optimal["humidity_min"] + random.uniform(5, 40),
            light=optimal["light_min"] + random.randint(-5000, 15000),
            co2=optimal["co2_min"] + random.randint(-100, 300),
            soil_ec=optimal.get("soil_ec_min", 1.5) + random.uniform(-0.3, 0.5),
            soil_pH=optimal.get("soil_pH_min", 6.0) + random.uniform(-0.5, 0.8),
            soil_temp=optimal["temp_min"] + random.uniform(-2, 5),
            soil_moisture=40 + random.randint(-15, 30)
        )

        weather = WeatherForecast(
            timestamp=datetime.now() + timedelta(days=1),
            temp_high=28 + random.randint(-3, 8),
            temp_low=18 + random.randint(-2, 5),
            humidity=60 + random.randint(-15, 20),
            weather=random.choice(["sunny", "cloudy", "rainy"]),
            precipitation=random.choice([0, 0, 0, 5, 10, 20])
        )

        alerts, analysis = agent.analyze_environment(env, weather)
        suggestion = agent.generate_control_suggestion(env, weather, analysis)

        return {
            "analysis": analysis,
            "alerts": [alert.model_dump() for alert in alerts],
            "suggestion": suggestion.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/greenhouses/{greenhouse_id}/suggestions")
async def list_suggestions(greenhouse_id: str):
    """获取建议列表（模拟）"""
    if greenhouse_id not in greenhouses_db:
        raise HTTPException(status_code=404, detail="大棚不存在")

    # 返回一个模拟建议
    return {
        "suggestions": [
            {
                "id": str(uuid.uuid4()),
                "greenhouse_id": greenhouse_id,
                "agent_type": "control",
                "suggestion": "当前环境正常，建议保持当前状态",
                "reasoning": "各参数均在最佳范围内",
                "confidence": 0.9,
                "actions": [],
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
        ]
    }


@router.get("/alerts")
async def list_alerts(greenhouse_id: Optional[str] = None, level: Optional[str] = None):
    """获取告警列表"""
    # 模拟返回
    return {"alerts": []}