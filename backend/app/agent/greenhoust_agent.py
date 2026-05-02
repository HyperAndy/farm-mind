import uuid
from datetime import datetime
from app.models.schemas import (
    EnvironmentData, ControlAction, Suggestion, Alert,
    WeatherForecast, CropType
)


# 作物最佳环境参数
CROP_OPTIMAL = {
    CropType.TOMATO: {
        "temp_min": 18, "temp_max": 28,
        "humidity_min": 50, "humidity_max": 80,
        "light_min": 20000, "light_max": 50000,
        "co2_min": 400, "co2_max": 1000,
        "soil_ec_min": 1.5, "soil_ec_max": 2.5,
        "soil_pH_min": 6.0, "soil_pH_max": 7.0,
    },
    CropType.STRAWBERRY: {
        "temp_min": 15, "temp_max": 25,
        "humidity_min": 60, "humidity_max": 85,
        "light_min": 15000, "light_max": 40000,
        "co2_min": 350, "co2_max": 800,
        "soil_ec_min": 1.2, "soil_ec_max": 2.0,
        "soil_pH_min": 5.5, "soil_pH_max": 6.5,
    },
    CropType.MUSHROOM: {
        "temp_min": 15, "temp_max": 24,
        "humidity_min": 75, "humidity_max": 95,
        "light_min": 0, "light_max": 5000,
        "co2_min": 800, "co2_max": 2000,
        "soil_ec_min": 1.0, "soil_ec_max": 1.8,
        "soil_pH_min": 5.5, "soil_pH_max": 7.0,
    },
    CropType.FLOWER: {
        "temp_min": 18, "temp_max": 30,
        "humidity_min": 50, "humidity_max": 80,
        "light_min": 25000, "light_max": 60000,
        "co2_min": 350, "co2_max": 800,
        "soil_ec_min": 1.5, "soil_ec_max": 2.5,
        "soil_pH_min": 6.0, "soil_pH_max": 7.0,
    },
    CropType.VEGETABLE: {
        "temp_min": 18, "temp_max": 30,
        "humidity_min": 60, "humidity_max": 85,
        "light_min": 20000, "light_max": 50000,
        "co2_min": 400, "co2_max": 1000,
        "soil_ec_min": 1.5, "soil_ec_max": 2.5,
        "soil_pH_min": 6.0, "soil_pH_max": 7.0,
    },
}


class GreenhouseAgent:
    """设施大棚智能管控 Agent"""

    def __init__(self, greenhouse_id: str, crop_type: CropType):
        self.greenhouse_id = greenhouse_id
        self.crop_type = crop_type
        self.optimal = CROP_OPTIMAL.get(crop_type, CROP_OPTIMAL[CropType.TOMATO])

    def analyze_environment(
        self, env: EnvironmentData, weather: WeatherForecast
    ) -> tuple[list[Alert], str]:
        """分析环境数据，生成告警"""
        alerts = []
        analysis_parts = []

        # 温度分析
        if env.temperature > self.optimal["temp_max"]:
            level = "urgent" if env.temperature > self.optimal["temp_max"] + 5 else "warning"
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="temperature",
                level=level,
                threshold_value=self.optimal["temp_max"],
                actual_value=env.temperature,
                message=f"温度过高：{env.temperature}℃（建议保持在{self.optimal['temp_max']}℃以下）",
                created_at=datetime.now()
            ))
            analysis_parts.append(f"温度{env.temperature}℃偏高")
        elif env.temperature < self.optimal["temp_min"]:
            level = "urgent" if env.temperature < self.optimal["temp_min"] - 5 else "warning"
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="temperature",
                level=level,
                threshold_value=self.optimal["temp_min"],
                actual_value=env.temperature,
                message=f"温度过低：{env.temperature}℃（建议保持在{self.optimal['temp_min']}℃以上）",
                created_at=datetime.now()
            ))
            analysis_parts.append(f"温度{env.temperature}℃偏低")
        elif env.humidity > self.optimal["humidity_max"]:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="humidity",
                level="warning",
                threshold_value=self.optimal["humidity_max"],
                actual_value=env.humidity,
                message=f"湿度过高：{env.humidity}%（可能导致病害）",
                created_at=datetime.now()
            ))
            analysis_parts.append(f"湿度{env.humidity}%偏高")
        elif env.humidity < self.optimal["humidity_min"]:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="humidity",
                level="warning",
                threshold_value=self.optimal["humidity_min"],
                actual_value=env.humidity,
                message=f"湿度过低：{env.humidity}%（需注意补水）",
                created_at=datetime.now()
            ))
            analysis_parts.append(f"湿度{env.humidity}%偏低")
        # 光照分析
        if env.light > self.optimal["light_max"]:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="light",
                level="info",
                threshold_value=self.optimal["light_max"],
                actual_value=env.light,
                message=f"光照过强：{env.light}lux（需遮阳）",
                created_at=datetime.now()
            ))
            analysis_parts.append(f"光照{env.light}lux过强")
        elif env.light < self.optimal["light_min"]:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="light",
                level="warning",
                threshold_value=self.optimal["light_min"],
                actual_value=env.light,
                message=f"光照不足：{env.light}lux（需补光）",
                created_at=datetime.now()
            ))
            analysis_parts.append(f"光照{env.light}lux不足")

        # CO2分析
        if env.co2 < self.optimal["co2_min"]:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                greenhouse_id=self.greenhouse_id,
                alert_type="co2",
                level="info",
                threshold_value=self.optimal["co2_min"],
                actual_value=env.co2,
                message=f"CO2不足：{env.co2}ppm（需补充）",
                created_at=datetime.now()
            ))

        analysis = "当前环境：" + "，".join(analysis_parts) if analysis_parts else "当前环境正常"
        return alerts, analysis

    def generate_control_suggestion(
        self, env: EnvironmentData, weather: WeatherForecast, analysis: str
    ) -> Suggestion:
        """生成控制建议"""
        actions = []
        reasoning_parts = [analysis]

        # 温度处理
        if env.temperature > self.optimal["temp_max"] + 2:
            actions.append(ControlAction(device_type="fan", action="turn_on", value="high"))
            reasoning_parts.append("温度偏高，建议开启风机降温")
        elif env.temperature > self.optimal["temp_max"]:
            actions.append(ControlAction(device_type="fan", action="turn_on", value="low"))
            reasoning_parts.append("温度略高，建议开启风机低档")
        elif env.temperature < self.optimal["temp_min"] - 2:
            actions.append(ControlAction(device_type="curtain", action="turn_on", value="close"))
            reasoning_parts.append("温度过低，建议关闭通风")

        # 湿度处理
        if env.humidity > self.optimal["humidity_max"] + 5:
            actions.append(ControlAction(device_type="fan", action="turn_on", value="high"))
            reasoning_parts.append("湿度过高，建议加强通风")
        elif env.humidity < self.optimal["humidity_min"] - 5:
            actions.append(ControlAction(device_type="irrigation", action="turn_on", value="10min"))
            reasoning_parts.append("湿度过低，建议启动滴灌")

        # 光照处理
        if env.light > self.optimal["light_max"]:
            actions.append(ControlAction(device_type="curtain", action="set_value", value="50"))
            reasoning_parts.append("光照过强，建议降下遮阳帘50%")
        elif env.light < self.optimal["light_min"]:
            actions.append(ControlAction(device_type="light", action="turn_on"))
            reasoning_parts.append("光照不足，建议开启补光灯")

        # CO2处理
        if env.co2 < self.optimal["co2_min"] and self.crop_type in [CropType.TOMATO, CropType.VEGETABLE]:
            actions.append(ControlAction(device_type="co2", action="turn_on"))
            reasoning_parts.append("CO2不足，建议开启CO2补充")

        # 结合天气预报
        if weather.weather == "sunny" and weather.temp_high > self.optimal["temp_max"] + 3:
            # 添加遮阳建议
            curtain_action = next((a for a in actions if a.device_type == "curtain"), None)
            if not curtain_action:
                actions.append(ControlAction(device_type="curtain", action="set_value", value="30"))
                reasoning_parts.append(f"天气预报明天高温{weather.temp_high}℃，建议提前遮阳")

        if not actions:
            reasoning_parts.append("当前环境无需特殊调控")

        suggestion_text = "；".join(reasoning_parts)
        reasoning_text = f"基于{self.crop_type.value}作物的最佳环境参数和当前传感器数据：\n" + "\n".join(f"- {r}" for r in reasoning_parts)

        return Suggestion(
            id=str(uuid.uuid4()),
            greenhouse_id=self.greenhouse_id,
            agent_type="control",
            suggestion=suggestion_text,
            reasoning=reasoning_text,
            confidence=0.85,
            actions=actions,
            created_at=datetime.now()
        )

    def generate_water_fert_suggestion(self, env: EnvironmentData) -> str:
        """生成水肥建议"""
        suggestions = []

        if env.soil_ec and env.soil_ec > self.optimal["soil_ec_max"] + 0.3:
            suggestions.append("土壤EC值偏高，建议减少施肥浓度或增加清水灌溉")
        elif env.soil_ec and env.soil_ec < self.optimal["soil_ec_min"] - 0.2:
            suggestions.append("土壤EC值偏低，建议适当增加肥料浓度")

        if env.soil_pH and env.soil_pH < self.optimal["soil_pH_min"]:
            suggestions.append(f"土壤pH偏酸({env.soil_pH})，建议使用碱性肥料调整")
        elif env.soil_pH and env.soil_pH > self.optimal["soil_pH_max"]:
            suggestions.append(f"土壤pH偏碱({env.soil_pH})，建议使用酸性肥料调整")

        if env.soil_moisture and env.soil_moisture < 30:
            suggestions.append("土壤含水率过低(<30%)，建议启动滴灌补水")

        return "；".join(suggestions) if suggestions else "水肥状态正常，无需调整"


# 全局Agent实例缓存
_agents: dict[str, GreenhouseAgent] = {}


def get_agent(greenhouse_id: str, crop_type: CropType) -> GreenhouseAgent:
    key = f"{greenhouse_id}_{crop_type.value}"
    if key not in _agents:
        _agents[key] = GreenhouseAgent(greenhouse_id, crop_type)
    return _agents[key]