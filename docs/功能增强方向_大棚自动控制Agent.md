# 大棚自动控制 Agent 功能增强方向

> 脑暴日期：2026-05-03

---

## 一、功能增强方向总览

| 序号 | 方向 | 优先级 | 说明 |
|------|------|--------|------|
| 1 | 作物知识库 | **MVP** | 作物环境参数、生长周期、病虫害知识图谱 |
| 2 | 环境预测与自适应 | **MVP** | 病虫害预警、采收预测、极端天气应急 |
| 3 | 水肥一体化 | P1 | EC/pH调节、施肥策略 |
| 4 | 生长追踪与成像 | P1 | 多光谱成像、成熟度识别 |
| 5 | 作业自动化 | P2 | 自动灌溉、农机协作 |
| 6 | 数据分析增强 | P2 | 投入产出、茬口优化 |
| 7 | 多棚协同管理 | P2 | 棚间对比、最优实践 |
| 8 | 告警与应急 | **MVP** | 多级告警、智能去重、应急策略 |
| 9 | 报表与决策支持 | P1 | 日周月报、产量预测 |
| 10 | 第三方集成 | P2 | 农机、电商、气象接入 |

---

## 二、MVP 优先级方向详解

### 1. 作物知识库

**目标**：为 Agent 提供决策依据，实现"基于作物特性的智能调控"

#### 核心功能

1. **作物环境参数库**
   - 存储各作物最佳环境范围（温度/湿度/光照/CO2）
   - 支持不同生长阶段的差异化参数
   - 示例：

   | 作物 | 阶段 | 温度(°C) | 湿度(%) | 光照(lux) | CO2(ppm) |
   |------|------|----------|---------|-----------|----------|
   | 番茄 | 开花结果期 | 20-28 | 60-80 | 30000-50000 | 800-1000 |
   | 草莓 | 育苗期 | 15-22 | 70-85 | 15000-25000 | 400-600 |
   | 番茄 | 幼苗期 | 18-25 | 70-85 | 20000-35000 | 600-800 |

2. **生长周期模型**
   - 记录播种→开花→结果→采收的时间线
   - 根据积温推算生长阶段
   - 提供采收时机建议

3. **病虫害知识图谱**
   - 症状→作物→环境条件→防治方案
   - 基于当前环境数据预测发病风险
   - 提供图文对照诊断

4. **水肥策略库**
   - 不同作物、不同阶段的施肥配方
   - EC/pH 阈值配置
   - 轮作配套建议

#### 数据结构设计

```python
class CropKnowledge:
    crop_type: str
    growth_stages: list[GrowthStage]
    optimal_env: EnvironmentParams
    disease_risks: list[DiseaseRisk]
    fertilizer_strategies: list[FertilizerStrategy]

class GrowthStage:
    name: str  # 幼苗期/开花期/结果期/采收期
    duration_days: int
    temp_range: tuple[float, float]
    humidity_range: tuple[float, float]
    light_requirement: int  # lux
    co2_requirement: int  # ppm
```

#### 价值
- 替代人工经验，实现标准化调控
- 新手也能管理大棚
- 为后续 AI 学习提供基础数据

---

### 2. 环境预测与自适应

**目标**：从"被动告警"升级为"主动预防"

#### 核心功能

1. **病虫害预警**
   - 基于温湿度趋势预测发病风险
   - 触发条件示例：
     - 连续3天湿度>85% + 温度22-28°C → 灰霉病高风险
     - 土壤EC值持续升高 → 盐分积累风险
   - 提前24-48小时预警

2. **采收时机预测**
   - 积温模型：统计每日有效积温
   - 光照积累：计算累计光照值
   - 到达阈值时提醒采收

3. **极端天气应急**
   - 对接天气预报数据
   - 自动生成应急策略：
     - 大风天气：关闭通风口、固定遮阳帘
     - 暴雨天气：检查排水系统
     - 高温预警：提前开启湿帘/喷雾
   - 支持策略模板自定义

#### 技术实现

```python
class EnvironmentPredictor:
    def predict_disease_risk(self, env_history: list[EnvironmentData]) -> list[Alert]:
        """分析历史环境数据，预测病虫害风险"""
        # 分析温湿度曲线
        # 匹配病虫害模型
        # 返回预警列表

    def predict_harvest_time(self, crop_type: str, env_accumulated: dict) -> datetime:
        """基于积温和光照积累预测采收时间"""

    def generate_emergency_strategy(self, weather: WeatherForecast) -> list[ControlAction]:
        """根据天气预报生成应急控制策略"""
```

#### 价值
- 把问题消灭在萌芽状态
- 减少损失、提升品质
- 体现 AI 主动性

---

### 8. 告警与应急

**目标**：建立完善的告警体系，确保问题及时处理

#### 核心功能

1. **多级告警机制**

   | 级别 | 条件 | 通知方式 | 处理方式 |
   |------|------|----------|----------|
   | 提醒 | 参数接近阈值 | APP推送 | 可忽略 |
   | 警告 | 参数超出阈值 | APP推送+短信 | 建议处理 |
   | 紧急 | 参数严重超标/设备故障 | APP推送+短信+电话 | 立即处理 |
   | 临界 | 预测即将超标 | APP推送 | 预防措施 |

2. **智能告警聚合**
   - 同一大棚短时间内多条告警 → 合并为一条
   - 多棚同一告警 → 批量通知
   - 避免告警风暴

3. **告警升级机制**
   - 警告未处理 → 自动升级为紧急
   - 紧急告警 → 自动通知上级联系人

4. **应急策略库**
   - 预置常见场景的应急方案
   - 支持自动执行（可配置）
   - 执行记录审计

5. **告警统计分析**
   - 告警频率统计
   - 高频问题识别
   - 设备故障率

#### 数据结构

```python
class AlertRule:
    id: str
    name: str
    metric: str  # temperature/humidity/...
    condition: str  # >/< / range
    threshold: float
    level: str  # reminder/warning/urgent/critical
    actions: list[ControlAction]  # 自动执行的动作
    notify_users: list[str]

class Alert:
    id: str
    greenhouse_id: str
    rule_id: str
    level: str
    message: str
    value: float
    threshold: float
    status: str  # pending/acknowledged/resolved
    created_at: datetime
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime]
```

#### 价值
- 保障大棚安全
- 减少人工巡查成本
- 问题追溯有据可查

---

## 三、MVP 功能清单

| 模块 | 功能点 | 描述 |
|------|--------|------|
| 作物知识库 | 作物参数配置 | 支持常见作物（番茄/草莓/黄瓜/辣椒）的环境参数 |
| 作物知识库 | 生长阶段管理 | 定义各作物的生长阶段及参数 |
| 作物知识库 | 病虫害知识 | 内置常见病虫害及防治方案 |
| 环境预测 | 病虫害预警 | 基于环境趋势预测发病风险 |
| 环境预测 | 天气预报接入 | 对接外部天气 API |
| 环境预测 | 应急策略生成 | 根据天气自动生成控制建议 |
| 告警系统 | 多级告警 | reminder/warning/urgent 三级 |
| 告警系统 | 告警聚合 | 减少重复告警 |
| 告警系统 | 告警统计 | 告警次数/类型统计 |
| 告警系统 | 应急策略库 | 预置应急方案，支持自动执行 |

---

## 四、技术实现建议

### 数据层
- 作物知识库：JSON 文件或 SQLite 存储
- 告警规则：数据库存储，支持动态配置
- 历史告警：数据库存储

### 服务层
- `CropKnowledgeService`：作物知识查询
- `EnvironmentPredictionService`：预测分析
- `AlertService`：告警管理

### 触发机制
- 定时任务：检查环境数据，触发预测
- 事件驱动：数据更新时触发告警检查

### 扩展性
- 作物知识库支持用户自定义
- 告警规则支持动态配置
- 预测模型可迭代优化

---

## 五、后续扩展方向

MVP 完成后，可逐步扩展：

1. **水肥一体化** → 根据土壤数据自动调控施肥
2. **生长追踪** → 接入摄像头，实现视觉分析
3. **多棚协同** → 区域级优化建议
4. **报表生成** → 日周月报自动推送