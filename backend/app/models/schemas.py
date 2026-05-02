from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class CropType(str, Enum):
    TOMATO = "tomato"
    STRAWBERRY = "strawberry"
    MUSHROOM = "mushroom"
    FLOWER = "flower"
    VEGETABLE = "vegetable"


class GreenhouseBase(BaseModel):
    name: str
    location: str
    area: float  # 亩
    crop_type: CropType


class GreenhouseCreate(GreenhouseBase):
    pass


class Greenhouse(GreenhouseBase):
    id: str
    org_id: str
    status: str = "active"
    created_at: datetime

    class Config:
        from_attributes = True


class EnvironmentData(BaseModel):
    temperature: float  # ℃
    humidity: float  # %
    light: int  # lux
    co2: int  # ppm
    soil_ec: Optional[float] = None  # mS/cm
    soil_pH: Optional[float] = None
    soil_temp: Optional[float] = None
    soil_moisture: Optional[float] = None


class ControlAction(BaseModel):
    device_type: str  # fan/curtain/light/irrigation/co2
    action: str  # turn_on/turn_off/set_value
    value: Optional[str] = None


class Suggestion(BaseModel):
    id: str
    greenhouse_id: str
    agent_type: str  # environment/control/water_fert
    suggestion: str
    reasoning: str
    confidence: float
    actions: list[ControlAction]
    status: str = "pending"  # pending/accepted/rejected/expired
    created_at: datetime


class Alert(BaseModel):
    id: str
    greenhouse_id: str
    alert_type: str  # temperature/humidity/light/co2/soil
    level: str  # urgent/warning/info
    threshold_value: float
    actual_value: float
    message: str
    status: str = "pending"  # pending/acknowledged/resolved
    created_at: datetime


class WeatherForecast(BaseModel):
    timestamp: datetime
    temp_high: float
    temp_low: float
    humidity: int
    weather: str  # sunny/cloudy/rainy/stormy
    precipitation: float  # mm