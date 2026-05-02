# 设施大棚智能管控 Agent - 技术方案设计

**版本：v1.0**
**日期：2026年5月**

---

## 一、系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户层                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │  APP Web │  │  APP iOS │  │ APP Andr │  │   微信小程序     │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘     │
└───────┼────────────┼────────────┼─────────────────┼────────────────┘
        │            │            │                 │
        └────────────┴────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           网关层                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     API Gateway (Kong/Nginx)                  │   │
│  │              认证、限流、日志、路由                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                   ┌───────────────────────────┐
│    业务服务层      │                   │       Agent 服务层         │
│  ┌─────────────┐  │                   │  ┌─────────────────────┐  │
│  │  用户服务   │  │                   │  │   Environment Agent │  │
│  │  (认证/权限)│  │                   │  │   (核心决策引擎)    │  │
│  └─────────────┘  │                   │  └─────────────────────┘  │
│  ┌─────────────┐  │                   │  ┌─────────────────────┐  │
│  │  大棚管理   │  │                   │  │   Control Agent     │  │
│  │  (CRUD)    │  │                   │  │   (设备控制建议)    │  │
│  └─────────────┘  │                   │  └─────────────────────┘  │
│  ┌─────────────┐  │                   │  ┌─────────────────────┐  │
│  │  告警服务   │  │                   │  │   WaterFert Agent   │  │
│  │  (通知)    │  │                   │  │   (水肥一体化)      │  │
│  └─────────────┘  │                   │  └─────────────────────┘  │
└───────────────────┘                   └───────────────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          数据层                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │ PostgreSQL│  │ TimescaleDB│  │  Redis   │  │   文件存储       │     │
│  │(业务数据) │  │(时序数据) │  │(缓存)    │  │   (MinIO/S3)    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        设备接入层                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │  传感器   │  │  控制器   │  │  网关设备 │  │   第三方平台     │     │
│  │ (温度/湿度│  │ (风机/阀门│  │ (边缘网关)│  │   (气象/灌溉)   │     │
│  │  光照...) │  │  遮阳...) │  │          │  │                 │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈选型

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **前端** | React/Vue3 + TypeScript | 跨平台，组件化 |
| **移动端** | UniApp / React Native | 一套代码，iOS+Android |
| **后端框架** | FastAPI / NestJS | Python/Node.js，生态成熟 |
| **Agent引擎** | LangChain + RAG | LLM调用、工具编排、RAG知识库 |
| **数据库** | PostgreSQL + TimescaleDB | 业务数据+时序数据分离 |
| **缓存** | Redis Cluster | 会话缓存、数据缓存 |
| **消息队列** | RabbitMQ / Kafka | 设备数据 ingestion、异步任务 |
| **时序数据** | InfluxDB / TimescaleDB | 高频传感器数据存储 |
| **文件存储** | MinIO (S3兼容) | 照片、日志、报表存储 |
| **容器化** | Docker + K8s | 微服务编排 |
| **CI/CD** | GitHub Actions / GitLab CI | 自动化构建部署 |
| **监控** | Prometheus + Grafana | 指标监控、日志聚合 |
| **日志** | ELK Stack (Elasticsearch/Loki) | 日志收集分析 |

### 1.3 部署架构

```
                    ┌─────────────────┐
                    │   Nginx/LB     │
                    │   (HTTPS)      │
                    └────────┬───────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │  API Pod x3  │ │ Agent Pod x3│ │ WS Pod x3   │
     │  (无状态)    │ │  (无状态)    │ │  (WebSocket)│
     └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
            │                │                │
     ┌──────┴────────────────┴────────────────┴──────┐
     │                  Service Mesh (Istio)           │
     └────────────────────────┬───────────────────────┘
                              │
     ┌────────────────────────┴───────────────────────┐
     │              Storage Layer (分布式)              │
     │  PostgreSQL(主从) │ TimescaleDB │ Redis │ MinIO │
     └─────────────────────────────────────────────────┘
```

---

## 二、数据模型

### 2.1 核心实体

```
用户 (User)
├── id: UUID (PK)
├── phone: VARCHAR(11) UNIQUE
├── name: VARCHAR(50)
├── role: ENUM('admin', 'operator', 'viewer')
├── organization_id: FK
└── created_at: TIMESTAMP

组织 (Organization)
├── id: UUID (PK)
├── name: VARCHAR(100)
├── type: ENUM('enterprise', 'cooperative', 'individual')
└── plan: ENUM('free', 'basic', 'pro', 'enterprise')

大棚 (Greenhouse)
├── id: UUID (PK)
├── org_id: FK → Organization
├── name: VARCHAR(50)
├── location: VARCHAR(200)
├── area: DECIMAL(10,2) -- 面积（亩）
├── crop_type: ENUM('tomato', 'strawberry', 'mushroom', 'flower', 'vegetable')
└── status: ENUM('active', 'inactive', 'maintenance')

设备 (Device)
├── id: UUID (PK)
├── greenhouse_id: FK → Greenhouse
├── device_type: ENUM('sensor', 'controller')
├── vendor: VARCHAR(50)
├── model: VARCHAR(50)
├── serial_number: VARCHAR(100)
├── config: JSON -- 厂商特定配置
└── status: ENUM('online', 'offline', 'error')

作物阶段 (CropStage)
├── id: UUID (PK)
├── greenhouse_id: FK → Greenhouse
├── stage: ENUM('seedling', 'vegetative', 'flowering', 'fruiting', 'harvest')
├── start_date: DATE
├── end_date: DATE (nullable)
└── notes: TEXT

环境记录 (EnvironmentLog)
├── time: TIMESTAMP
├── greenhouse_id: FK → Greenhouse
├── device_id: FK → Device
├── temperature: DECIMAL(5,2) -- ℃
├── humidity: DECIMAL(5,2) -- %
├── light: INT -- lux
├── co2: INT -- ppm
├── soil_ec: DECIMAL(6,3) -- mS/cm
├── soil_pH: DECIMAL(4,2)
└── soil_temp: DECIMAL(5,2) -- ℃
└── soil_moisture: DECIMAL(5,2) -- %
(TimescaleDB 自动分区，按 greenhouse_id + time分区)

控制记录 (ControlLog)
├── id: UUID (PK)
├── greenhouse_id: FK → Greenhouse
├── device_id: FK → Device
├── action: ENUM('turn_on', 'turn_off', 'set_value')
├── value: VARCHAR(50)
├── trigger_type: ENUM('manual', 'auto', 'agent_suggestion')
├── agent_id: UUID (nullable)
├── operator_id: FK → User (nullable)
└── executed_at: TIMESTAMP

告警记录 (Alert)
├── id: UUID (PK)
├── greenhouse_id: FK → Greenhouse
├── alert_type: ENUM('temperature', 'humidity', 'light', 'co2', 'soil')
├── level: ENUM('urgent', 'warning', 'info')
├── threshold_value: DECIMAL(10,2)
├── actual_value: DECIMAL(10,2)
├── status: ENUM('pending', 'acknowledged', 'resolved')
├── acknowledged_by: FK → User (nullable)
└── created_at: TIMESTAMP

建议记录 (Suggestion)
├── id: UUID (PK)
├── greenhouse_id: FK → Greenhouse
├── agent_type: ENUM('environment', 'control', 'water_fert')
├── suggestion: TEXT
├── reasoning: TEXT -- LLM 推理过程
├──采纳状态: ENUM('pending', 'accepted', 'rejected', 'expired')
├── user_id: FK → User
└── created_at: TIMESTAMP
```

---

## 三、Agent 设计

### 3.1 Agent 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Orchestrator                     │
│                    (LangChain AgentExecutor)                │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Environment   │    │   Control     │    │  WaterFert    │
│   Agent       │    │   Agent       │    │   Agent       │
│               │    │               │    │               │
│ 职责:         │    │ 职责:         │    │ 职责:         │
│ - 分析环境数据│    │ - 生成控制建议│    │ - 水肥配比    │
│ - 异常检测   │    │ - 评估设备状态│    │ - 施肥计划    │
│ - 趋势预测   │    │ - 安全校验   │    │ - EC/pH调整   │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │  Tool Router  │
                    │   (ReAct)     │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────┐      ┌────────────┐      ┌────────────┐
│  数据库    │      │  气象API   │      │  知识库    │
│  (查询)    │      │  (天气)    │      │  (RAG)     │
└────────────┘      └────────────┘      └────────────┘
```

### 3.2 核心 Agent Prompt 设计

#### Environment Agent

```
你是设施大棚环境分析专家。你的职责：
1. 分析当前环境数据是否正常
2. 检测异常情况并评估风险等级
3. 预测未来24-72小时环境趋势
4. 结合天气预报评估对作物的影响

输入数据：
- 当前环境指标（温度/湿度/光照/CO2/土壤EC/pH）
- 未来72小时天气预报
- 作物当前生育期阶段
- 历史环境数据趋势

输出格式：
{
  "status": "normal|warning|danger",
  "risk_level": 1-10,
  "analysis": "详细分析文本",
  "predictions": [
    {"time": "24h后", "temperature": "32℃", "risk": "中"},
    {"time": "48h后", "temperature": "35℃", "risk": "高"}
  ],
  "recommendations": ["建议1", "建议2"]
}
```

#### Control Agent

```
你是温室设备控制专家。你的职责：
1. 根据环境状态生成设备控制建议
2. 确保控制动作安全（防止设备损坏、作物损伤）
3. 考虑能耗和成本优化
4. 遵守用户配置的自动化规则

决策逻辑：
IF 温度 > 32℃ AND 湿度 < 60%:
  → 开启风机 (转速50%)
  → 启动滴灌 (10分钟)
  → 降下遮阳帘 (30%)

IF 光照 > 50000 lux AND 作物阶段 in [苗期, 开花期]:
  → 升起遮阳帘 (50%)

IF CO2 < 350ppm AND 作物阶段 == 结果期:
  → 开启CO2补充设备

安全约束：
- 每次最多同时控制3个设备
- 设备连续运行超过2小时需重新评估
- 紧急告警时优先响应
```

#### WaterFert Agent

```
你是水肥一体化管理专家。你的职责：
1. 根据作物需肥规律制定施肥计划
2. 根据土壤EC/pH动态调整水肥配方
3. 结合天气情况调整灌溉策略
4. 记录水肥执行过程

作物需肥规律（番茄为例）：
- 苗期: EC目标 1.2-1.8, 每日滴灌 2-3次
- 开花期: EC目标 1.8-2.2, 每日滴灌 3-4次
- 结果期: EC目标 2.2-2.8, 每日滴灌 4-6次

决策逻辑：
IF 土壤EC > 目标EC + 0.5:
  → 减少肥料浓度50%
  → 增加清水灌溉冲洗

IF 土壤pH < 5.5:
  → 添加石灰水或其他碱性肥料

IF 天气预报显示连续阴雨:
  → 减少当日灌溉量30%
  → 增加磷钾肥比例
```

### 3.3 RAG 知识库

```
知识库内容：
1. 作物生长模型
   - 各作物的温度/湿度/光照最佳范围
   - 各生育期的水肥需求
   - 常见病虫害识别

2. 设备操作手册
   - 各品牌风机的控制参数
   - 滴灌系统的维护要点
   - 传感器校准方法

3. 农业技术规程
   - 国家设施农业标准
   - 各省份补贴政策
   - 安全操作规范

4. 历史案例
   - 异常情况处理经验
   - 用户采纳建议的效果追踪

检索增强：
- 向量数据库：Milvus / Qdrant / Weaviate
- Embedding模型：text-embedding-3-small
- Chunk大小：512 tokens
- Top-K：5
```

---

## 四、API 设计

### 4.1 REST API

#### 认证

```
POST /api/v1/auth/login
Request: { "phone": "13800138000", "code": "123456" }
Response: { "token": "jwt...", "expires_in": 7200 }

POST /api/v1/auth/refresh
Request: { "refresh_token": "..." }
Response: { "token": "jwt..." }
```

#### 大棚管理

```
GET    /api/v1/greenhouses                    # 列表
POST   /api/v1/greenhouses                    # 创建
GET    /api/v1/greenhouses/{id}               # 详情
PUT    /api/v1/greenhouses/{id}               # 更新
DELETE /api/v1/greenhouses/{id}               # 删除

GET    /api/v1/greenhouses/{id}/devices       # 大棚设备列表
POST   /api/v1/greenhouses/{id}/devices       # 添加设备
```

#### 环境数据

```
GET    /api/v1/greenhouses/{id}/env/current  # 当前环境
GET    /api/v1/greenhouses/{id}/env/history   # 历史数据
Query: ?start=2026-05-01&end=2026-05-02&interval=5m

WebSocket /ws/greenhouses/{id}/env          # 实时推送
```

#### 控制

```
POST   /api/v1/devices/{id}/control           # 控制设备
Body: { "action": "turn_on", "value": null }

GET    /api/v1/greenhouses/{id}/controls      # 控制历史
Query: ?start=...&end=...&trigger_type=agent
```

#### 告警

```
GET    /api/v1/alerts                         # 告警列表
GET    /api/v1/alerts/{id}                     # 告警详情
PUT    /api/v1/alerts/{id}/acknowledge         # 确认告警

WebSocket /ws/alerts                           # 实时告警推送
```

#### 建议

```
GET    /api/v1/greenhouses/{id}/suggestions   # 建议列表
POST   /api/v1/suggestions/{id}/accept         # 采纳建议
POST   /api/v1/suggestions/{id}/reject         # 拒绝建议
```

### 4.2 Agent API (内部)

```
POST /api/v1/agent/analyze
Body: {
  "greenhouse_id": "uuid",
  "data_type": "environment|control|water_fert",
  "context": {
    "current_env": {...},
    "weather": {...},
    "crop_stage": "fruiting",
    "history": [...]
  }
}
Response: {
  "suggestion": "...",
  "reasoning": "...",
  "confidence": 0.85,
  "actions": [{"device": "...", "action": "..."}]
}
```

### 4.3 设备接入 API

```
# 传感器数据上报
POST /api/v1/device/{device_id}/data
Body: {
  "timestamp": "2026-05-02T10:00:00Z",
  "values": {
    "temperature": 25.5,
    "humidity": 65.2,
    "light": 25000
  }
}

# 设备状态上报
POST /api/v1/device/{device_id}/status
Body: { "status": "online", "battery": 85, "signal": -65 }
```

---

## 五、数据流设计

### 5.1 实时数据流

```
传感器 → 边缘网关 → MQTT Broker → Kafka → TimescaleDB
                                    ↓
                              Agent服务 ← 实时分析
                                    ↓
                              WebSocket → APP推送
```

### 5.2 控制指令流

```
APP用户 → API Gateway → Agent服务 → 指令验证 → 设备下发
                                    ↓
                              ControlLog记录
                                    ↓
                              执行结果确认 → 用户反馈
```

### 5.3 批处理数据流

```
TimescaleDB → 数据清洗 → 特征工程 → 模型预测 → 产量预测
                                    ↓
                              报表生成 → 存储
```

---

## 六、安全设计

### 6.1 认证与授权

```
认证：
- 手机号+验证码登录
- JWT Token (2小时有效期)
- Refresh Token (30天)

授权：
- RBAC (Role-Based Access Control)
- 组织隔离 (Organization数据隔离)
- 设备操作权限分级

API安全：
- HTTPS (TLS 1.3)
- 请求签名 (HMAC-SHA256)
- 限流 (1000请求/分钟)
```

### 6.2 数据安全

```
传输加密：
- 设备→服务端：TLS + 设备证书
- APP→服务端：HTTPS + Certificate Pinning

存储加密：
- 数据库：列级加密（敏感字段）
- 文件存储：服务端加密

备份策略：
- 全量备份：每日
- 增量备份：每小时
- 异地容灾：跨区域备份
```

---

## 七、性能设计

### 7.1 性能指标

| 场景 | 指标 |
|------|------|
| 环境数据写入 | 10,000条/秒 |
| 实时告警延迟 | <100ms |
| 建议生成延迟 | <3秒 |
| API响应时间(P99) | <200ms |
| 系统可用性 | 99.5% |

### 7.2 扩展策略

```
水平扩展：
- API服务无状态，可随时扩容
- Agent服务支持多实例负载均衡
- Kafka/TimescaleDB 支持分区扩展

垂直扩展：
- TimescaleDB 按时间分区，自动清理冷数据
- Redis Cluster 支持数据分片

边缘计算：
- 边缘网关预处理数据，减少云端压力
- 本地策略执行（断网自控）
```

---

## 八、监控与运维

### 8.1 监控指标

```
应用层：
- API请求量、响应时间、错误率
- Agent建议采纳率
- 用户活跃度

系统层：
- CPU/内存/磁盘使用率
- 网络流量
- Pod重启次数

业务层：
- 设备在线率
- 告警数量
- 水肥执行次数
```

### 8.2 日志设计

```
结构化日志：
{
  "timestamp": "2026-05-02T10:00:00Z",
  "level": "INFO",
  "service": "agent-control",
  "trace_id": "uuid",
  "user_id": "uuid",
  "action": "suggestion_generated",
  "greenhouse_id": "uuid",
  "suggestion": "开启风机",
  "latency_ms": 250
}

日志级别：
- ERROR: 系统异常
- WARN: 业务警告（如建议被拒绝）
- INFO: 关键业务操作
- DEBUG: 开发调试
```

---

## 九、技术选型总结

| 模块 | 选型 | 理由 |
|------|------|------|
| 编程语言 | Python + TypeScript | Python用于AI/Agent，TypeScript用于业务服务 |
| Agent框架 | LangChain + RAG | 成熟生态，支持工具调用和知识库 |
| 数据库 | PostgreSQL + TimescaleDB | 业务+时序分离，支持SQL |
| 消息队列 | Kafka | 高吞吐，支持设备数据 ingestion |
| 缓存 | Redis | 会话缓存，高性能 |
| 搜索 | Qdrant/Milvus | 向量数据库，支持RAG |
| 部署 | Kubernetes | 容器编排，自动扩缩容 |
| 监控 | Prometheus + Grafana | 成熟开源方案 |

---

*文档版本：v1.0，最后更新：2026年5月*
*下一步：原型开发（MVP）*