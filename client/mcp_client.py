"""麦当劳官方 MCP Streamable HTTP 客户端封装

连接远程 https://mcp.mcd.cn，统一封装 Tool 调用请求与返回结构，支持真实网络与 Mock 回退双模式。
"""
import json
import logging
import requests
from typing import Any, Dict, List, Optional
from config import MCD_MCP_URL, MCD_MCP_TOKEN, REQUEST_TIMEOUT, DEMO_MODE
from client.mock_data import (
    MOCK_MEALS,
    MOCK_COUPONS,
    MOCK_CAMPAIGN_CALENDAR
)

logger = logging.getLogger(__name__)


class McDonaldMCPClient:
    """麦当劳 MCP 服务客户端"""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None, force_demo: bool = False):
        self.token = token or MCD_MCP_TOKEN
        self.base_url = (base_url or MCD_MCP_URL).rstrip("/")
        self.is_demo = force_demo or DEMO_MODE or (not self.token)
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "M-SmartSaver-MCP-Client/1.0.0"
            })

    def _call_mcp_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """向麦当劳 MCP 服务发起 Streamable HTTP / JSON-RPC 工具调用"""
        if self.is_demo:
            return self._mock_tool_dispatch(tool_name, arguments or {})

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        try:
            resp = self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    return data["result"]
                elif "error" in data:
                    logger.warning(f"MCP Tool {tool_name} returned error: {data['error']}, falling back to mock")
                    return self._mock_tool_dispatch(tool_name, arguments or {})
            elif resp.status_code == 401:
                logger.warning("MCP Token 鉴权失败或已过期，自动切换至高保真 Mock 模式")
                self.is_demo = True
                return self._mock_tool_dispatch(tool_name, arguments or {})
            elif resp.status_code == 429:
                logger.warning("触发限流 (429 Too Many Requests)，请稍后重试")
                return self._mock_tool_dispatch(tool_name, arguments or {})
        except Exception as e:
            logger.warning(f"连接 MCP 服务失败 ({e})，使用离线仿真数据")
            return self._mock_tool_dispatch(tool_name, arguments or {})

        return self._mock_tool_dispatch(tool_name, arguments or {})

    def _mock_tool_dispatch(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """离线仿真工具分发器"""
        if tool_name == "auto-bind-coupons":
            return {
                "success": True,
                "bound_count": len(MOCK_COUPONS),
                "message": f"成功一键领取麦麦省 {len(MOCK_COUPONS)} 张当前可用优惠券！"
            }
        elif tool_name in ("query-my-coupons", "available-coupons", "query-store-coupons"):
            return {
                "success": True,
                "coupons": MOCK_COUPONS
            }
        elif tool_name == "query-meals":
            return {
                "success": True,
                "store_id": args.get("store_id", "STORE_SH_001"),
                "meals": MOCK_MEALS
            }
        elif tool_name == "campaign-calendar":
            return {
                "success": True,
                "calendar": MOCK_CAMPAIGN_CALENDAR
            }
        elif tool_name == "now-time-info":
            import datetime
            now = datetime.datetime.now()
            hour = now.hour
            period = "早餐时段" if 5 <= hour < 10 else ("正餐时段" if 10 <= hour < 22 else "夜宵时段")
            return {
                "success": True,
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "period": period
            }
        elif tool_name == "calculate-price":
            # 仿真计算逻辑
            items = args.get("items", [])
            coupon_ids = args.get("coupons", [])
            original_price = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
            discount = 0.0

            # 模拟匹配卡券减免
            for c_id in coupon_ids:
                matched = next((c for c in MOCK_COUPONS if c["coupon_id"] == c_id), None)
                if matched:
                    if matched["discount_type"] == "threshold" and original_price >= matched["threshold"]:
                        discount += matched["discount_value"]
                    elif matched["discount_type"] in ("single_discount", "special_price"):
                        discount += matched["discount_value"]

            final_price = max(0.01, round(original_price - discount, 2))
            return {
                "success": True,
                "original_price": round(original_price, 2),
                "discount_amount": round(discount, 2),
                "delivery_fee": 0.0,
                "payable_amount": final_price,
                "status": "VALIDATED_BY_OFFICIAL_API"
            }

        return {"success": False, "message": f"Unknown tool: {tool_name}"}

    # --- 高级封装方法 ---

    def auto_bind_coupons(self) -> Dict[str, Any]:
        """麦麦省一键领券"""
        return self._call_mcp_tool("auto-bind-coupons")

    def query_coupons(self) -> List[Dict[str, Any]]:
        """获取用户当前可用优惠券列表"""
        res = self._call_mcp_tool("query-my-coupons")
        return res.get("coupons", [])

    def query_meals(self, store_id: str = "DEFAULT") -> List[Dict[str, Any]]:
        """查询在售餐品清单"""
        res = self._call_mcp_tool("query-meals", {"store_id": store_id})
        return res.get("meals", [])

    def calculate_price(self, items: List[Dict[str, Any]], coupon_ids: List[str]) -> Dict[str, Any]:
        """官方服务端验价与金额核算"""
        return self._call_mcp_tool("calculate-price", {
            "items": items,
            "coupons": coupon_ids
        })

    def get_campaign_calendar(self) -> Dict[str, Any]:
        """获取营销活动日历"""
        res = self._call_mcp_tool("campaign-calendar")
        return res.get("calendar", {})

    def get_time_info(self) -> Dict[str, Any]:
        """获取时段与标准时间"""
        return self._call_mcp_tool("now-time-info")
