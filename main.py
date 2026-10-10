#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦门极致省钱精算管家 (McSmartSaver)

主入口文件：提供命令行交互式体验、一键精算以及轻量 Web 演示服务器。
"""
import sys
import argparse
import http.server
import socketserver
import webbrowser
from pathlib import Path

# 确保在 Windows 控制台环境下输出 UTF-8 编码，防止 emoji 引发 gbk 编码错误
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from client.mcp_client import McDonaldMCPClient
from core.solver import SmartSaverSolver
from core.calendar_radar import CalendarRadar

console = Console(highlight=False, legacy_windows=False)
BASE_DIR = Path(__file__).resolve().parent


def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════════════════════╗
    ║      🍔 麦门极致省钱精算管家 (McSmartSaver) 🍟                    ║
    ║      基于麦当劳官方 MCP 开放能力 · 拒绝被刺，科学吃堡！             ║
    ╚════════════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(Text(banner, style="bold yellow on dark_red"), expand=False))


def display_result(res: dict, radar: CalendarRadar):
    console.print(f"\n[bold green]🎯 精算模式：[/bold green] [bold cyan]{res['mode']}[/bold cyan]")
    
    # 餐品组合表格
    table = Table(title="🛒 智能搭配点餐清单", show_header=True, header_style="bold magenta")
    table.add_column("餐品 / 组合名称", style="cyan", width=30)
    table.add_column("数量", justify="center")
    table.add_column("原价", justify="right")
    table.add_column("实付估算", justify="right", style="green")
    table.add_column("能量 (kcal)", justify="right")
    table.add_column("蛋白质 (g)", justify="right")

    for item in res["items"]:
        table.add_row(
            item["name"],
            str(item["quantity"]),
            f"¥{item['original_price']:.2f}",
            f"¥{item['price']:.2f}",
            str(item.get("calories", "-")),
            str(item.get("protein", "-"))
        )
    console.print(table)

    # 结算面板
    official_check = res.get("official_verification", {})
    summary_text = f"""
    [bold yellow]💰 账单总览与官方验价：[/bold yellow]
    • 原始总价： [strikethrough]¥{res['original_total']:.2f}[/strikethrough]
    • 优惠减免： [bold green]-¥{res['saved_amount']:.2f}[/bold green] (立省 {res['discount_rate']}%)
    • 最终应付： [bold red]¥{res['payable_price']:.2f}[/bold red]
    • 验价状态： [bold green]{official_check.get('status', 'OK')}[/bold green] (官方 MCP calculate-price 实时验签)
    """
    console.print(Panel(summary_text, title="📊 官方结算核验单", border_style="green"))

    # 策略拆解
    console.print("\n[bold yellow]💡 精算师决策依据：[/bold yellow]")
    for idx, exp in enumerate(res.get("explanation", []), 1):
        console.print(f"  {idx}. {exp}")

    # 今日营销日历提示
    tips = radar.get_tips()
    if tips:
        console.print("\n[bold magenta]📅 麦麦活动雷达：[/bold magenta]")
        for tip in tips:
            console.print(f"  ⚡ {tip}")


def run_web(port: int = 8080):
    web_dir = BASE_DIR / "web"
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(web_dir), **kwargs)

    console.print(f"\n[bold green]🚀 正在启动麦门省钱管家 Web 演示面板...[/bold green]")
    console.print(f"🌐 本地访问地址: [link=http://localhost:{port}]http://localhost:{port}[/link]")
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    with socketserver.TCPServer(("", port), Handler) as httpd:
        console.print("[dim]按 Ctrl+C 可停止 Web 服务[/dim]")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Web 服务已安全关闭。[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="麦门极致省钱精算管家 (McSmartSaver)")
    parser.add_argument("--mode", choices=["budget_friendly", "coupon_maximizer", "expiring_rescue"], default="budget_friendly", help="精算模式")
    parser.add_argument("--budget", type=float, default=25.0, help="目标预算金额 (元)")
    parser.add_argument("--store", type=str, default="DEFAULT", help="目标餐厅 ID")
    parser.add_argument("--demo", action="store_true", help="强制使用高保真离线 Mock 模式演示")
    parser.add_argument("--web", action="store_true", help="启动交互式 Web 演示看板")
    parser.add_argument("--port", type=int, default=8080, help="Web 服务器端口")

    args = parser.parse_args()

    print_banner()

    if args.web:
        run_web(args.port)
        return

    # 初始化 MCP 客户端与求解器
    client = McDonaldMCPClient(force_demo=args.demo)
    
    # 自动执行一次一键领券
    console.print("[dim]正在同步麦当劳 MCP 服务... 调用 auto-bind-coupons 一键领券...[/dim]")
    bind_res = client.auto_bind_coupons()
    console.print(f"[green]✔ {bind_res.get('message', '已完成卡券资产同步')}[/green]")

    solver = SmartSaverSolver(client, store_id=args.store)
    radar = CalendarRadar(client.get_campaign_calendar())

    console.print(f"[dim]正在执行智能决策规划... 目标模式: {args.mode}[/dim]")
    result = solver.solve(mode=args.mode, target_budget=args.budget)

    display_result(result, radar)
    console.print("\n[dim]提示：运行 python main.py --web 可打开沉浸式可视化仪表盘[/dim]\n")


if __name__ == "__main__":
    main()
