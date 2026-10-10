<p align="center">
  <h1 align="center">🍔 麦门极致省钱精算管家 (McSmartSaver)</h1>
  <p align="center">
    <strong>吃得饱、省到老！基于麦当劳官方 MCP 开放能力 · 拒绝被刺，科学吃堡</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/McDonald's-MCP%20Enabled-DA291C?style=flat-square&logo=mcdonalds" alt="MCP">
    <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/1024-Programmers'%20Day-FFC72C?style=flat-square" alt="1024">
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
    <img src="https://img.shields.io/badge/WorkBuddy-Supported-0052D9?style=flat-square" alt="WorkBuddy">
  </p>
</p>

---

## 📖 项目简介

**麦门极致省钱精算管家 (McSmartSaver)** 是面向广大麦当劳爱好者与打工人的智能餐饮精算决策 Agent。

过去在麦当劳点餐，消费者常常陷入困境：
- ❌ **满减陷阱**：为了凑满 40 减 10，盲目加购高价单品，结果“为了省10块，多花了20块”；
- ❌ **优惠券遗漏与浪费**：卡券分散在各处，大量单品半价券、买一送一券因遗忘而在 24 小时内悄然失效；
- ❌ **价格算不明白**：“1+1随心配”、特惠券、会员日加成到底怎么组合性价比最高？

本项目通过深度集成麦当劳官方开放平台提供的 **Model Context Protocol（MCP）远程服务**，构建了一套自动化卡券收割、动态规划凑单、活动日历雷达与官方验价闭环的省钱引擎！

---

## ✨ 核心特性

- 🤖 **全网卡券一键收割**：自动调用 `auto-bind-coupons` 领取麦麦省全部可用优惠券，并调用 `query-my-coupons` 清点全部折扣资产。
- 🎯 **三大智能精算模式**：
  1. **🍔 极致穷鬼模式 (Budget-Friendly)**：以经典『1+1 随心配』(¥13.9) 为坚实基石，在 ¥15~¥30 超低预算下最大化卡路里与高蛋白质，拒绝溢价诱导。
  2. **💰 最优满减凑单 (Coupon-Maximizer)**：针对满 40 减 10、满 59 减 18 等大额券，采用贪心剪枝算法寻找溢出差额极小的小食/饮品精准补齐门槛，榨干折扣率。
  3. **⏳ 临期卡券救火 (Expiring-Rescue)**：优先识别 12~24 小时内即将失效的半价券、买一送一券，反向生成最佳核销方案，绝不浪费任何权益。
- 📊 **官方验价闭环 (calculate-price)**：直接由麦当劳官方 MCP 接口进行金额计算，确保原价、实付金额、满减优惠及配送费 100% 真实准确。
- 📅 **麦麦活动雷达 (campaign-calendar)**：动态提示周一会员日半价、周三麦乐鸡节及 1024 程序员节专属特惠，科学避开溢价时段。
- 💻 **双模交互呈现**：
  - 🎨 **炫酷终端 CLI**：基于 Rich 打造现代化终端报表，自带餐品营养/卡路里热量计算与决策依据解释。
  - 🌐 **沉浸式 Web 演示面板**：内置极简高颜值前端单页（一键滑块调整预算、动态切换策略、官方结算单卡片实时更新）。

---

## 🏗️ 架构与 MCP 工具链路

系统通过 Streamable HTTP 协议与麦当劳官方 MCP Server (`https://mcp.mcd.cn`) 建立通信：

```text
[ 用户输入 / 预算偏好 ] 
         │
         ▼
 1. 资产收割层: auto-bind-coupons (一键领券) ──> query-my-coupons (卡券盘点)
         │
 2. 供给感知层: query-meals (在售菜单) ──> campaign-calendar (活动日历) ──> now-time-info (时段)
         │
 3. 精算求解层: SmartSaverSolver ──> [穷鬼模式 / 满减凑单 / 临期救火]
         │
 4. 官方验价层: calculate-price (官方服务端验价与结算核验)
         │
         ▼
[ 最终省钱报告 + 官方验签账单 + Web/CLI 可视化展示 ]
```

关于所调用的各 Tool 详细入参与返回结构，详见 [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)。

---

## 🚀 快速上手

### 1. 环境准备
本项目兼容 Python 3.9+ 环境。

```bash
# 克隆仓库
git clone https://github.com/your-username/mcd-smart-saver.git
cd mcd-smart-saver

# 安装必要依赖
pip install -r requirements.txt
```

### 2. 配置 MCP Token (可选)
- 前往 [麦当劳开放平台](https://open.mcd.cn/mcp) 使用手机号登录，点击右上角【控制台】并激活申请个人 MCP Token。
- 方式一：设置环境变量：
  ```bash
  export MCD_MCP_TOKEN="YOUR_ACTUAL_TOKEN"     # Linux / macOS
  $env:MCD_MCP_TOKEN="YOUR_ACTUAL_TOKEN"       # Windows PowerShell
  ```
- 方式二：复制配置模板：
  ```bash
  cp mcp-config.example.json mcp-config.json
  # 在 mcp-config.json 中填入你的 Token
  ```
> 💡 **免 Token 体验模式**：若暂无 Token，项目内置了全套高保真离线 Mock 数据与仿真验价逻辑，任何人 clone 下来均可直接运行体验！

---

## 💻 运行与使用示例

### 1. 命令行交互 (CLI)

```bash
# 模式 1：极致穷鬼模式 (指定预算 25 元)
python main.py --mode budget_friendly --budget 25

# 模式 2：最优满减门槛凑单
python main.py --mode coupon_maximizer

# 模式 3：临期卡券救火
python main.py --mode expiring_rescue

# 强制使用离线仿真演示数据
python main.py --demo
```

**运行效果示例**：
```text
🎯 精算模式： 极致穷鬼方案
                              🛒 智能搭配点餐清单                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃ 餐品 / 组合名称                ┃ 数量 ┃   原价 ┃ 实付估… ┃  (kcal) ┃     (g) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ 1+1随心配：双层吉士堡 + 美式   │  1   │ ¥32.00 │  ¥13.90 │     455 │      25 │
│ 麦乐鸡(5块) [券后加购]         │  1   │ ¥13.50 │   ¥9.90 │     230 │      13 │
└────────────────────────────────┴──────┴────────┴─────────┴─────────┴─────────┘
╭───────────────────────────── 📊 官方结算核验单 ──────────────────────────────╮
│     💰 账单总览与官方验价：                                                  │
│     • 原始总价： ¥45.50                                                      │
│     • 优惠减免： -¥25.30 (立省 55.6%)                                        │
│     • 最终应付： ¥20.20                                                      │
│     • 验价状态： VALIDATED_BY_OFFICIAL_API                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 2. 启动可视化 Web 演示看板

```bash
python main.py --web
```
控制台将自动输出本地访问链接（默认 `http://localhost:8080`），并在浏览器中打开麦当劳黄金拱门配色的现代交互看板！

---

## 📂 项目结构规范

本项目严格依照大赛规范要求组织目录结构：

```text
├── CONTEST_DECLARATION.md     # 官方不可改动参赛声明 (包含原创性、合规与敏感信息声明)
├── MCP_INTEGRATION.md         # 麦当劳官方 MCP Tools 调用流程、架构与业务价值详述
├── mcp-config.example.json    # 脱敏 MCP 配置示例 (仅保留环境变量占位符)
├── workbuddy.md               # 腾讯 WorkBuddy 智能体对话上下文导出记录 (用于申报联动奖励)
├── requirements.txt           # 项目运行基础依赖
├── config.py                  # 配置解析与环境变量读取
├── main.py                    # 统一 CLI 与 Web 服务入口
├── client/
│   ├── mcp_client.py          # 麦当劳 MCP Streamable HTTP 协议交互封装
│   └── mock_data.py           # 离线高保真餐品、卡券与日历数据
├── core/
│   ├── coupon_manager.py      # 卡券分类、门槛索引与临期紧急度判定
│   ├── calendar_radar.py      # 麦麦活动日历雷达与消费避坑提示
│   └── solver.py              # 核心精算求解器 (穷鬼方案 / 最优满减 / 临期救火)
└── web/
    └── index.html             # 现代化交互看板单页
```

---

## 🎯 目标用户

- **打工人与学生党**：每天为午餐/晚餐发愁，追求极致性价比，用最少的预算吃饱吃好。
- **麦当劳深度会员与麦门信徒**：账户中积攒了大量优惠券与积分，希望自动最大化利用权益，拒绝任何卡券临期浪费。
- **开发者与极客群体**：学习 Model Context Protocol（MCP）技术如何与真实餐饮商业闭环落地的参考范例。

---

## 📜 参赛与开源声明

- 参赛项目声明详见 [CONTEST_DECLARATION.md](./CONTEST_DECLARATION.md)。
- 本项目遵循 MIT 开源协议。
- 项目为麦当劳程序员节创意开发大赛参赛作品，由开发者独立研发，非麦当劳官方商业产品。
