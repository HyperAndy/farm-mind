# FarmMind

Smart greenhouse environment monitoring system, providing precise environmental control recommendations for growers through AI Agent.

[English](./README.md) | [中文](./README_zh.md)

---

## Features

- Real-time environment monitoring (temperature/humidity/light/CO2/soil EC-pH)
- AI intelligent recommendations (control suggestions based on environmental data + weather forecast)
- Real-time alerts (immediate notifications for environmental anomalies)
- Device control (fan/sunshade/supplementary lighting/drip irrigation)
- Historical data chart analysis with ECharts

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: HTML/CSS/JavaScript + ECharts + Remix Icon
- **Agent**: Rule-based greenhouse environment analysis

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Visit http://localhost:3000

## Project Structure

```
├── backend/              # Backend service
│   ├── app/
│   │   ├── agent/       # Agent decision logic
│   │   ├── api/         # API routes
│   │   ├── models/      # Data models
│   │   └── main.py      # FastAPI entry
│   └── requirements.txt
└── frontend/            # Frontend
    └── index.html
```

## License

MIT