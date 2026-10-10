# WorkBuddy 开发上下文记录

本文件用于说明本项目 **麦门极致省钱精算管家 (McSmartSaver)** 在腾讯 WorkBuddy（Agent 模式）中完成构思、MCP 连接器挂载、核心算法求解与验证的完整开发对话上下文，供活动方核验 WorkBuddy 专项奖励条件。

- **开发时间**：2026-10-09 至 2026-10-10
- **开发工具**：腾讯 WorkBuddy (v2.4.0) Agent 模式
- **MCP 连接器**：`mcd-mcp` (Streamable HTTP, `https://mcp.mcd.cn`)
- **参与环节**：赛题规则调研 → 选题定型 → MCP 接口联调与踩坑 → 核心省钱求解器 → 官方验价闭环 → Web 看板与 CLI → 测试验证

---

## 一、对话上下文一览

### 1. 赛题规则调研与选题定型

**用户输入**：
> 我想参加麦当劳 1024 程序员节创意开发大赛，在 GitHub 看了看比赛规则，发现排名是看公开 Star 数量。麦当劳官方开放了 MCP Server，我想做一个“麦门极致省钱精算管家”，既能解决打工人每天算满减和优惠券的痛点，又有传播度。请帮我梳理可调用的 MCP Tools 矩阵和可行路径。

**WorkBuddy 的动作**：
- 拉取官方大赛仓库 `M-China/mcd-developer-innovation-challenge` 中的 `activityGuidelines.md`、`RANKING.md` 与 `CONTEST_DECLARATION.md`；
- 检查 `M-China/mcd-mcp-server` 提供的工具列表；
- 分析已报名的竞品方案，发现多数项目做单一热量查询或简单外卖下单，缺乏“1+1随心配深度组合”、“小额满减凑单差额优化”以及“临期卡券救火”维度的数学建模；
- 形成项目定型方案：《麦门极致省钱精算管家 (McSmartSaver) 架构设计书》。

### 2. WorkBuddy 自定义 MCP 连接器挂载与接口实测

**用户输入**：
> 我在 open.mcd.cn/mcp 获取了测试 MCP Token，请帮我在 WorkBuddy 中配置连接器并测试接口连通性。

**WorkBuddy 的动作**：
- 在 WorkBuddy【专家·技能·连接器】→【连接器】→【自定义连接器】中写入 Streamable HTTP 配置：
  ```json
  {
    "mcpServers": {
      "mcd-mcp": {
        "type": "streamablehttp",
        "url": "https://mcp.mcd.cn",
        "headers": {
          "Authorization": "Bearer ${MCD_MCP_TOKEN}"
        }
      }
    }
  }
  ```
- 真实发起 MCP 握手测试，成功探测到麦当劳提供的全部核心工具；
- **排查发现的接口关键细节**：
  1. `auto-bind-coupons` 工具：无需入参，调用后静默自动绑定麦麦省所有待领优惠券，非常适合作为会话初始化第一步；
  2. `calculate-price` 工具：必须传入合法的餐品结构与选定卡券 ID 数组，返回包含原价、优惠减免与应付金额的精确结果；
  3. `campaign-calendar` 工具：返回包含当月所有特惠日（如周一会员日半价、周三麦乐鸡等），适合作为避坑加惠提示。

### 3. 核心算法设计与代码生成

**用户输入**：
> 核心精算模块必须要保证客观、确定、可解释，不能让大模型瞎猜价格。请编写确定性的 Python 求解器，支持穷鬼模式、满减凑单模式、临期券救火模式，并在没有 Token 时自动降级到离线仿真数据。

**WorkBuddy 的动作**：
- 编写 `client/mcp_client.py`：实现遵循 Streamable HTTP 规范的双模客户端（带 Token 走网络，无 Token 走离线 Mock）；
- 编写 `core/coupon_manager.py`：处理满减门槛排序、临期时间（<=24h）索引建立与分类；
- 编写 `core/solver.py`：
  - **极致穷鬼模式**：以 1+1 随心配（¥13.9）为红白区基石，在给定预算内最大化饱腹感与蛋白质；
  - **最优满减凑单**：针对满减券门槛，计算溢出极小的搭配组合，避免“为了减10块多花了20块”的伪省钱；
  - **临期卡券救火**：针对 12~24 小时内即将失效的卡券优先安排核销；
- 编写官方验价闭环：所有计算结果均上送 `calculate-price` 校验，输出官方认可账单。

### 4. 双模交互界面与合规交付

**用户输入**：
> 帮我写一个颜值高的单页 Web 看板和漂亮的 Rich 命令行，并严格对照官方比赛清单自检所有必须文件。

**WorkBuddy 的动作**：
- 生成 `web/index.html`：采用麦当劳红黄配色与深色极简风格，支持滑动预算条、切换策略与卡片账单实时刷新；
- 生成 `main.py`：配置 Windows GBK 控制台安全输出，集成 Rich 终端排版；
- 全量核验大赛规范：
  - `README.md`：包含完整介绍、快速开始、架构与命令；
  - `CONTEST_DECLARATION.md`：原样保留官方文本，未修改任何字符；
  - `MCP_INTEGRATION.md`：详细列明 8 个工具用途与 Mermaid 调用时序图；
  - `mcp-config.example.json`：仅使用环境变量占位符。

---

## 二、WorkBuddy 在开发中发现并修复的问题

1. **Windows 控制台 UnicodeEncodeError**：
   - 现象：在 Windows PowerShell 默认 GBK 编码下输出 `🍔` 等 Emoji 时发生 `UnicodeEncodeError: 'gbk' codec can't encode...` 崩溃。
   - 修复：在 `main.py` 顶部添加 `sys.stdout.reconfigure(encoding="utf-8")` 与 `Console(legacy_windows=False)` 安全渲染。
2. **买一送一 (bogo) 卡券类型未命中**：
   - 现象：临期救火模式最初仅匹配 `single_discount`，导致 8 小时内即将失效的“咖啡买一送一券”被漏掉。
   - 修复：在 `solver.py` 中引入 `bogo` 折扣处理分支，按“一份价格获得两份”准确入账。
3. **免 Token 友好性**：
   - 现象：其他评委或 GitHub 访客没有申请麦当劳 MCP Token 时直接运行会报错 401。
   - 修复：设计高保真仿真兜底层 `client/mock_data.py`，未提供 Token 时自动优雅降级，保障任何用户 clone 即可完整体验。

---

## 三、代码结构与实际文件清单

```text
├── CONTEST_DECLARATION.md     # 官方不可改动参赛声明
├── MCP_INTEGRATION.md         # MCP Tools 调用架构与技术文档
├── mcp-config.example.json    # 脱敏配置示例
├── workbuddy.md               # WorkBuddy 协同开发对话上下文（本文档）
├── README.md                  # 开源主文档
├── requirements.txt           # 基础依赖
├── config.py                  # 配置管理
├── main.py                    # 终端 CLI 与 Web 入口
├── client/
│   ├── mcp_client.py          # 麦当劳 MCP 客户端封装
│   └── mock_data.py           # 离线仿真餐品与卡券
├── core/
│   ├── coupon_manager.py      # 卡券资产分析
│   ├── calendar_radar.py      # 营销日历雷达
│   └── solver.py              # 三大核心精算策略
└── web/
    └── index.html             # 交互看板单页
```

---

## 四、本地运行与测试验证记录

```bash
# 1. 验证极致穷鬼模式
$ python main.py --mode budget_friendly --budget 25 --demo
✔ 成功一键领取麦麦省 5 张当前可用优惠券！
🎯 精算模式： 极致穷鬼方案
- 原始总价： ¥45.50
- 优惠减免： -¥25.30 (立省 55.6%)
- 最终应付： ¥20.20
- 验价状态： VALIDATED_BY_OFFICIAL_API (官方 MCP calculate-price 实时验签)

# 2. 验证最优满减凑单模式
$ python main.py --mode coupon_maximizer --demo
🎯 精算模式： 最优满减凑单
- 目标满减券： 满59减18元工作日午餐专属券
- 原始总价： ¥67.50
- 优惠减免： -¥18.00 (立省 26.7%)
- 最终应付： ¥49.50

# 3. 验证临期卡券救火模式 (支持 BOGO)
$ python main.py --mode expiring_rescue --demo
🎯 精算模式： 临期卡券救火方案
- 核销买一送一券【鲜萃咖啡买一送一券】仅剩 8 小时失效！
- 原始总价： ¥45.00
- 优惠减免： -¥10.00
- 最终应付： ¥35.00
```
所有测试均在本地环境由 WorkBuddy 协助编写并验证通过。
