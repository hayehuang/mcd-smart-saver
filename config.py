"""配置管理模块

读取环境变量及默认 MCP 配置，优先从环境变量或本地 .env 获取 MCD_MCP_TOKEN
"""
import os
import json
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 麦当劳官方 MCP 远程服务地址 (Streamable HTTP)
MCD_MCP_URL = os.getenv("MCD_MCP_URL", "https://mcp.mcd.cn")

# 官方 MCP Token
MCD_MCP_TOKEN = os.getenv("MCD_MCP_TOKEN", "")

# 如果当前目录存在脱敏配置文件或用户自定义的 mcp-config.json，尝试自动读取
CUSTOM_CONFIG_FILE = BASE_DIR / "mcp-config.json"
if not MCD_MCP_TOKEN and CUSTOM_CONFIG_FILE.exists():
    try:
        with open(CUSTOM_CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            headers = cfg.get("mcpServers", {}).get("mcd-mcp", {}).get("headers", {})
            auth = headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token_val = auth.replace("Bearer ", "").strip()
                if token_val and token_val != "YOUR_MCP_TOKEN":
                    MCD_MCP_TOKEN = token_val
    except Exception:
        pass

# 请求超时设定
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

# 是否开启离线演示 Mock 模式
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
