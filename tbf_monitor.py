#!/usr/bin/env python3
# ============================================
#   TBF-MONITOR v5.1 — MINIMAL DARK STYLE
#   by TBFPUMBA — Technology. Security. Efficiency.
# ============================================

import os
import sys
import time
import socket
import threading
import datetime
import random
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.prompt import Prompt
from rich import box
from rich.text import Text

console = Console()

# ============================================
#   КОНФІГУРАЦІЯ
# ============================================
HOST = '0.0.0.0'
PORT = 8080
EMERGENCY_MODE = False
logs = []
visitors = []
start_time = datetime.datetime.now()
server_instance = None
server_thread = None

# ============================================
#   СИСТЕМНІ ФУНКЦІЇ
# ============================================
def get_cpu():
    try:
        r = subprocess.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", shell=True, capture_output=True, text=True)
        return r.stdout.strip().replace('%us,', '') or "0"
    except:
        return "0"

def get_ram():
    try:
        r = subprocess.run("free -m | grep Mem | awk '{print $3, $2}'", shell=True, capture_output=True, text=True)
        parts = r.stdout.strip().split()
        return parts[0] if len(parts) >= 1 else "0", parts[1] if len(parts) >= 2 else "0"
    except:
        return "0", "0"

def get_disk():
    try:
        r = subprocess.run("df -h / | tail -n1 | awk '{print $5, $3, $2}'", shell=True, capture_output=True, text=True)
        parts = r.stdout.strip().split()
        return parts[0] if len(parts) >= 1 else "0%", parts[1] if len(parts) >= 2 else "0", parts[2] if len(parts) >= 3 else "0"
    except:
        return "0%", "0", "0"

def get_net():
    try:
        r = subprocess.run("cat /proc/net/dev | grep wlan0 | awk '{print $2, $10}'", shell=True, capture_output=True, text=True)
        parts = r.stdout.strip().split()
        if len(parts) >= 2:
            return int(parts[0]) // 1024**2, int(parts[1]) // 1024**2
        return 0, 0
    except:
        return 0, 0

# ============================================
#   HTTP-ОБРОБНИК
# ============================================
class MinimalHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logs.append(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {self.address_string()} | {format % args}")
        if len(logs) > 100:
            logs.pop(0)

    def do_GET(self):
        global EMERGENCY_MODE
        if EMERGENCY_MODE:
            time.sleep(random.uniform(1.0, 3.0))

        visitors.append(f"{self.address_string()} | {datetime.datetime.now().strftime('%H:%M:%S')}")
        if len(visitors) > 50:
            visitors.pop(0)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        cpu = get_cpu()
        ram_used, ram_total = get_ram()
        disk_p, disk_u, disk_t = get_disk()
        net_s, net_r = get_net()
        uptime_s = int((datetime.datetime.now() - start_time).total_seconds())
        uptime = f"{uptime_s // 3600}h {(uptime_s % 3600) // 60}m"

        html = f"""
        <html>
        <head><title>TBF-MONITOR</title></head>
        <body style="background:#0d0d0d;color:#33ff33;font-family:'Courier New',monospace;padding:30px;">
            <h1 style="color:#33ff33;font-weight:300;">> TBF-MONITOR</h1>
            <hr style="border-color:#33ff33;border-width:1px;">
            <p style="color:#33ff33;">STATUS: ACTIVE</p>
            <p style="color:#33ff33;">UPTIME: {uptime}</p>
            <p style="color:{'#ff3333' if EMERGENCY_MODE else '#33ff33'};">MODE: {'EMERGENCY' if EMERGENCY_MODE else 'NORMAL'}</p>
            <hr style="border-color:#33ff33;border-width:1px;">
            <p style="color:#33ff33;">CPU: {cpu}%</p>
            <p style="color:#33ff33;">RAM: {ram_used}MB / {ram_total}MB</p>
            <p style="color:#33ff33;">DISK: {disk_p} ({disk_u} / {disk_t})</p>
            <p style="color:#33ff33;">NET: TX {net_s}MB / RX {net_r}MB</p>
            <hr style="border-color:#33ff33;border-width:1px;">
            <p style="color:#33ff33;">VISITORS: {len(visitors)}</p>
            <p style="color:#33ff33;">LOGS: {len(logs)}</p>
            <hr style="border-color:#33ff33;border-width:1px;">
            <p><a href="/logs" style="color:#33ff33;">> VIEW LOGS</a></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

# ============================================
#   ЗАПУСК СЕРВЕРА
# ============================================
def start_server():
    global server_instance
    server_instance = HTTPServer((HOST, PORT), MinimalHandler)
    console.print(f"[green]Server running on http://{HOST}:{PORT}[/green]")
    console.print(f"[dim]http://127.0.0.1:{PORT}[/dim]")
    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[red]Server stopped[/red]")

def stop_server():
    global server_instance, server_thread
    if server_instance:
        console.print("[yellow]Stopping...[/yellow]")
        server_instance.shutdown()
        server_instance.server_close()
        server_instance = None
        server_thread = None
        console.print("[green]Stopped[/green]")
    else:
        console.print("[yellow]Not running[/yellow]")
    input("[dim]Press Enter...[/dim]")

# ============================================
#   МОНІТОРИНГ
# ============================================
def show_monitor():
    console.clear()
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            cpu = get_cpu()
            ram_u, ram_t = get_ram()
            disk_p, disk_u, disk_t = get_disk()
            net_s, net_r = get_net()
            uptime_s = int((datetime.datetime.now() - start_time).total_seconds())
            uptime = f"{uptime_s // 3600}h {(uptime_s % 3600) // 60}m"

            table = Table(show_header=False, box=box.SIMPLE, border_style="green")
            table.add_column("PARAMETER", style="white")
            table.add_column("VALUE", style="green")

            table.add_row("UPTIME", uptime)
            table.add_row("CPU", f"{cpu}%")
            table.add_row("RAM", f"{ram_u}MB / {ram_t}MB")
            table.add_row("DISK", f"{disk_p} ({disk_u}/{disk_t})")
            table.add_row("NET TX", f"{net_s}MB")
            table.add_row("NET RX", f"{net_r}MB")
            table.add_row("VISITORS", str(len(visitors)))
            table.add_row("LOGS", str(len(logs)))
            table.add_row("EMERGENCY", "ON" if EMERGENCY_MODE else "OFF")

            live.update(table)
            time.sleep(1)

# ============================================
#   ЛОГИ
# ============================================
def show_logs():
    console.clear()
    if not logs:
        console.print("[yellow]No logs[/yellow]")
        input("[dim]Press Enter...[/dim]")
        return

    for i, log in enumerate(logs[-10:], 1):
        console.print(f"{i}. {log}")
    input("\n[dim]Press Enter...[/dim]")

# ============================================
#   МЕНЮ (МІНІМАЛІСТИЧНИЙ)
# ============================================
def show_menu():
    console.clear()
    console.print("> TBF-MONITOR v5.1")
    console.print("─" * 30)
    console.print("1. Configure")
    console.print("2. Start server")
    console.print("3. Stop server")
    console.print("4. Emergency ON")
    console.print("5. Emergency OFF")
    console.print("6. Logs")
    console.print("7. Monitor")
    console.print("0. Exit")
    console.print("─" * 30)
    return Prompt.ask("[green]>[/green]")

# ============================================
#   НАЛАШТУВАННЯ
# ============================================
def setup_server():
    global HOST, PORT
    console.clear()
    console.print("> Configure")
    console.print("─" * 30)

    h = Prompt.ask("[green]IP[/green]", default=HOST)
    if h.strip():
        HOST = h.strip()

    p = Prompt.ask("[green]Port[/green]", default=str(PORT))
    if p.strip().isdigit():
        PORT = int(p.strip())

    console.print(f"[green]Set: {HOST}:{PORT}[/green]")
    time.sleep(0.5)

# ============================================
#   MAIN
# ============================================
def main():
    global PORT, EMERGENCY_MODE, HOST, server_thread

    while True:
        choice = show_menu()

        if choice == "1":
            setup_server()

        elif choice == "2":
            if server_thread and server_thread.is_alive():
                console.print("[yellow]Already running[/yellow]")
                input("[dim]Press Enter...[/dim]")
                continue

            console.print("[green]Starting...[/green]")
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            time.sleep(1)
            input("[dim]Press Enter...[/dim]")

        elif choice == "3":
            stop_server()

        elif choice == "4":
            EMERGENCY_MODE = True
            console.print("[red]Emergency ON[/red]")
            input("[dim]Press Enter...[/dim]")

        elif choice == "5":
            EMERGENCY_MODE = False
            console.print("[green]Emergency OFF[/green]")
            input("[dim]Press Enter...[/dim]")

        elif choice == "6":
            show_logs()

        elif choice == "7":
            show_monitor()

        elif choice == "0":
            if server_thread and server_thread.is_alive():
                stop_server()
            console.print("[red]Exit[/red]")
            sys.exit(0)

        else:
            console.print("[red]Invalid[/red]")
            time.sleep(1)

if __name__ == "__main__":
    main()
