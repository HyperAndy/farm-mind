# FarmMind

智能温室大棚环境监控系统，基于 AI Agent 为种植户提供精准的环境控制建议。

[English](./README.md) | [中文](./README_zh.md)

---

## 功能

- 实时环境监控（温度/湿度/光照/CO2/土壤EC-pH）
- AI 智能建议（基于环境数据+天气预报生成控制建议）
- 实时告警（环境异常即时通知）
- 设备控制（风机/遮阳帘/补光灯/滴灌）
- 历史数据图表分析（ECharts）

## 技术栈

- **后端**: FastAPI + Python
- **前端**: HTML/CSS/JavaScript + ECharts + Remix Icon
- **Agent**: 基于规则引擎的温室环境分析

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
python -m http.server 3000
```

访问 http://localhost:3000

## 项目结构

```
├── backend/              # 后端服务
│   ├── app/
│   │   ├── agent/       # Agent 决策逻辑
│   │   ├── api/         # API 路由
│   │   ├── models/      # 数据模型
│   │   └── main.py      # FastAPI 入口
│   └── requirements.txt
└── frontend/            # 前端页面
    └── index.html
```

## License

MIT