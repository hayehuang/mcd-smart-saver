<p align="center">
  <h1 align="center">🍔 麦门极致省钱精算管家 (McSmartSaver Skill)</h1>
  <p align="center">
    <strong>基于麦当劳官方 MCP 开放能力 · 面向腾讯 WorkBuddy 与 AI Agent 的餐饮省钱精算 Skill</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/McDonald's-MCP%20Skill-DA291C?style=flat-square&logo=mcdonalds" alt="MCP">
    <img src="https://img.shields.io/badge/Agent-WorkBuddy%20Skill-0052D9?style=flat-square&logo=tencentqq" alt="WorkBuddy">
    <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/1024-Programmers'%20Day-FFC72C?style=flat-square" alt="1024">
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  </p>
</p>

---

## 📖 Skill 简介

**麦门极致省钱精算管家 (McSmartSaver)** 是面向腾讯 WorkBuddy、Cursor、Claude 及多智能体生态的**餐饮省钱精算 Agent Skill**。

### 为什么需要这个 Skill？
过去在麦当劳点餐，消费者常常陷入痛点：
- ❌ **满减陷阱**：为了凑够满 40 减 10，盲目加购高价单品，结果“为了省10块，多花了20块”；
- ❌ **优惠券遗漏与浪费**：卡券分散在各处，大量单品半价券、买一送一券因遗忘而在 24 小时内悄然失效；
- ❌ **大模型口算幻觉**：通用 LLM 缺乏实时菜单与优惠规则，容易胡编乱造不存在的套餐价格。

本 Skill 遵循 **「数值不进 LLM 猜测，数学由确定性求解器完成，最终金额官方验签」** 的严谨架构，通过深度集成麦当劳中国官方 MCP（Model Context Protocol）能力，为智能体赋予自动领券、科学算法凑单、临期救火与官方验价的全闭环能力！

---

## ✨ 核心能力与精算场景

本 Skill 在智能体感知到用户意图时，可自动激活三大精算策略：

1. **🍔 极致穷鬼模式 (Budget-Friendly)**：以经典『1+1 随心配』(¥13.9) 为坚实基石，在 ¥15~¥30 超低预算下最大化卡路里与高蛋白质，拒绝溢价诱导。
2. **💰 最优满减凑单 (Coupon-Maximizer)**：针对满 40 减 10、满 59 减 18 等大额券，采用贪心剪枝算法寻找溢出差额极小的小食/饮品精准补齐门槛，榨干折扣率。
3. **⏳ 临期卡券救火 (Expiring-Rescue)**：优先识别 12~24 小时内即将失效的半价券、买一送一券，反向生成最佳核销方案，绝不浪费任何权益。
4. **📅 麦麦活动雷达 (campaign-calendar)**：动态感知周一会员日半价、周三麦乐鸡节及 1024 程序员节专属特惠，科学避开溢价时段。
5. **📊 官方验价闭环 (calculate-price)**：直接由麦当劳官方 MCP 接口进行金额计算，确保原价、实付金额、满减优惠及配送费 100% 真实准确。

---

## 🧭 在智能体平台中使用本 Skill

### 1. 在腾讯 WorkBuddy 中挂载使用
1. 打开 WorkBuddy，在左侧导航栏【专家·技能·连接器】→ 切换至【连接器】；
2. 点击右上角【自定义连接器】→【配置 MCP】，按如下配置连接麦当劳官方服务：
   ```json
   {
     "mcpServers": {
       "mcd-mcp": {
         "type": "streamablehttp",
         "url": "https://mcp.mcd.cn",
         "headers": {
           "Authorization": "Bearer YOUR_MCP_TOKEN"
         }
       }
     }
   }
   ```
3. 在对话框中即可通过自然语言直接调用本 Skill，例如：
   - *“今天中午只有 25 块钱预算，帮我用麦当劳 1+1 随心配搭配一个蛋白质最高、最划算的方案！”*
   - *“我有一张满 40 减 10 的券，想吃巨无霸，怎么凑单最划算？”*
   - *“帮我查查卡包里有没有快过期的半价券，推荐怎么花掉它。”*

### 2. 规范定义文件
本 Skill 遵循标准 Agent Skill 规范，规范说明与 Prompt 指引详见：
- [SKILL.md](./SKILL.md) / [skills/mcd-smart-saver/SKILL.md](./skills/mcd-smart-saver/SKILL.md)

---

## 🏗️ 架构与 MCP 链路

```text
[ 用户自然语言请求: 预算/偏好/想省钱 ] 
                  │
                  ▼
         [ McSmartSaver Skill ] (意图分流与工作流编排)
                  │
  ┌───────────────┴────────────────────────┐
  ▼                                        ▼
1. 资产全自动收割与盘点                   2. 供给与时空感知
  • auto-bind-coupons (一键自动领券)       • query-meals (实时在售菜单)
  • query-my-coupons (全量卡券盘点)        • campaign-calendar (营销活动日历)
  │                                        • now-time-info (早餐/正餐时段)
  └───────────────┬────────────────────────┘
                  ▼
3. 确定性求解器: core/solver.py (背包剪枝、穷鬼方案、最优凑单)
                  │
                  ▼
4. 官方验价闭环: calculate-price (提交候选商品清单 + 抵扣券至官方验证)
                  │
                  ▼
[ 结构化人话省钱报告 + 官方验签账单卡片 + 营养热量分析 ]
```

详尽的 MCP 工具入参说明与业务价值见 [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)。

---

## 🚀 本地运行与演示体验

本仓库除提供完整的 Skill 定义外，还内置了**确定性本地引擎**与**可视化交互面板**：

```bash
# 1. 克隆仓库与安装依赖
git clone https://github.com/hayehuang/mcd-smart-saver.git
cd mcd-smart-saver
pip install -r requirements.txt

# 2. 命令行直接精算演示 (支持免 Token 离线仿真体验)
python main.py --mode budget_friendly --budget 25 --demo
python main.py --mode coupon_maximizer --demo
python main.py --mode expiring_rescue --demo

# 3. 启动高颜值 Web 交互面板
python main.py --web
```

---

## 📂 仓库文件组织

```text
├── SKILL.md                   # Agent Skill 核心规范、Prompt 与工作流定义
├── skills/mcd-smart-saver/    # 标准 Skill 模块包目录
│   └── SKILL.md               # 模块级规范文档
├── CONTEST_DECLARATION.md     # 官方不可改动参赛声明 (含原创性、合规与安全声明)
├── MCP_INTEGRATION.md         # MCP Tools 调用架构、时序图与业务价值详述
├── mcp-config.example.json    # 脱敏配置示例 (仅保留环境变量占位符)
├── workbuddy.md               # 腾讯 WorkBuddy 协同开发对话上下文记录
├── requirements.txt           # 基础依赖
├── config.py                  # 配置管理
├── main.py                    # 终端 CLI 与 Web 演示看板入口
├── client/
│   ├── mcp_client.py          # 麦当劳 MCP Streamable HTTP 协议交互封装
│   └── mock_data.py           # 离线高保真餐品、卡券与日历数据
├── core/
│   ├── coupon_manager.py      # 卡券资产分析、门槛排序与临期紧急度判定
│   ├── calendar_radar.py      # 营销日历雷达与消费避坑提示
│   └── solver.py              # 三大核心确定性精算策略
└── web/
    └── index.html             # 交互看板单页
```

---

## 🎯 目标用户

- **打工人与学生党**：每天为午餐/晚餐发愁，追求极致性价比，用最少的预算吃饱吃好。
- **麦当劳深度会员与麦门信徒**：账户中积攒了大量优惠券与积分，希望自动最大化利用权益，拒绝任何卡券临期浪费。
- **智能体开发者与极客群体**：学习 Model Context Protocol（MCP）技术如何与真实餐饮商业闭环落地的标准范例。

---

## 📜 参赛与开源声明

- 参赛项目声明详见 [CONTEST_DECLARATION.md](./CONTEST_DECLARATION.md)。
- 本项目遵循 MIT 开源协议。
- 项目为麦当劳程序员节创意开发大赛参赛作品，由开发者独立研发，非麦当劳官方商业产品。
