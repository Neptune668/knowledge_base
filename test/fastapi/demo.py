from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import datetime
import requests
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
import urllib.parse

# ---------- 可选：解析 User-Agent（安装 pip install user-agents）----------
try:
    from user_agents import parse

    HAS_USER_AGENTS = True
except ImportError:
    HAS_USER_AGENTS = False

app = FastAPI()

# ---------- 配置日志 ----------
LOG_FILE = "access.log"
logger = logging.getLogger("access_log")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# ---------- 获取客户端真实 IP ----------
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


# ---------- 获取地理位置（扩展字段）----------
def get_location(ip: str) -> Dict[str, Any]:
    # 内网 IP 跳过查询
    private_prefixes = ("127.", "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.",
                        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
                        "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.")
    if ip.startswith(private_prefixes):
        return {
            "status": "private",
            "country": "内网/本地",
            "countryCode": "",
            "region": "",
            "regionName": "",
            "city": "本地",
            "zip": "",
            "lat": "",
            "lon": "",
            "timezone": "",
            "isp": "内网",
            "org": "",
            "as": "",
            "query": ip
        }
    try:
        # 请求大量字段
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                return data
            else:
                return {"status": "fail", "message": data.get("message", "未知错误"), "query": ip}
    except Exception as e:
        return {"status": "error", "message": str(e), "query": ip}
    return {"status": "unknown", "query": ip}


# ---------- 解析 User-Agent（可选）----------
def parse_user_agent(ua_string: str) -> Dict[str, str]:
    if not HAS_USER_AGENTS or not ua_string:
        return {"browser": "未知", "os": "未知", "device": "未知"}
    try:
        ua = parse(ua_string)
        return {
            "browser": f"{ua.browser.family} {ua.browser.version_string}",
            "os": f"{ua.os.family} {ua.os.version_string}",
            "device": f"{ua.device.family} ({ua.device.brand} {ua.device.model})".strip()
        }
    except:
        return {"browser": "解析失败", "os": "解析失败", "device": "解析失败"}


# ---------- 收集所有可用信息 ----------
def get_all_info(request: Request) -> Dict[str, Any]:
    # 基础客户端信息
    client_ip = get_client_ip(request)
    client_port = request.client.port if request.client else None

    # 请求方法、路径
    method = request.method
    path = request.url.path
    full_url = str(request.url)
    query_params = dict(request.query_params)

    # 请求头（全部转为字典）
    headers = dict(request.headers)

    # Cookie
    cookies = dict(request.cookies)

    # ASGI scope 信息（通过 request.scope 获取）
    scope = request.scope
    scheme = scope.get("scheme")
    server = scope.get("server")  # (host, port) tuple
    http_version = scope.get("http_version")
    root_path = scope.get("root_path")
    asgi_version = scope.get("asgi", {}).get("version")

    # 路径参数（如果定义了路由参数，但 GET 示例中没有）
    path_params = request.path_params  # 通常是空字典

    # 用户代理解析
    ua_string = headers.get("user-agent", "")
    ua_info = parse_user_agent(ua_string)

    # 地理位置
    location = get_location(client_ip)

    # 组装所有信息
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "client": {
            "ip": client_ip,
            "port": client_port
        },
        "server": {
            "host": server[0] if server else None,
            "port": server[1] if server else None,
            "scheme": scheme,
            "http_version": http_version,
            "root_path": root_path,
            "asgi_version": asgi_version
        },
        "request": {
            "method": method,
            "path": path,
            "full_url": full_url,
            "query_params": query_params,
            "path_params": path_params,
            "headers": headers,
            "cookies": cookies,
            "user_agent_parsed": ua_info
        },
        "location": location
    }
    return info


# ---------- 路由处理 ----------
@app.get("/", response_class=HTMLResponse)
@app.get("/read_root", response_class=HTMLResponse)
def read_root(request: Request):
    # 收集全部信息
    info = get_all_info(request)

    # 打印到控制台（缩略）
    print("=" * 80)
    print(f"访问时间: {info['timestamp']}")
    print(f"客户端: {info['client']['ip']}:{info['client']['port']}")
    print(f"请求: {info['request']['method']} {info['request']['path']}")
    print(f"地理位置: {info['location'].get('country')} {info['location'].get('city')}")
    print(f"User-Agent: {info['request']['headers'].get('user-agent', '')[:60]}...")
    print("=" * 80)

    # 写入日志（JSON 格式）
    logger.info(json.dumps(info, ensure_ascii=False, default=str))

    # ---------- 生成 HTML 页面（展示所有信息）----------
    # 由于信息太多，使用分组折叠的卡片展示

    # 辅助函数：生成键值对表格行
    def render_dict_table(data: dict, indent: int = 0) -> str:
        if not data:
            return "<tr><td colspan='2' style='text-align:center;color:#999;'>无数据</td></tr>"
        rows = []
        for k, v in data.items():
            if isinstance(v, dict):
                rows.append(
                    f"<tr><td class='label' style='vertical-align:top;'><strong>{k}</strong></td><td class='value'>{render_nested_dict(v)}</td></tr>")
            elif isinstance(v, list):
                rows.append(
                    f"<tr><td class='label'><strong>{k}</strong></td><td class='value'>{', '.join(str(i) for i in v)}</td></tr>")
            else:
                rows.append(f"<tr><td class='label'><strong>{k}</strong></td><td class='value'>{v}</td></tr>")
        return "".join(rows)

    def render_nested_dict(d: dict) -> str:
        if not d:
            return "<span style='color:#999;'>无</span>"
        html = "<table class='nested-table' style='width:100%;border-collapse:collapse;'>"
        for k, v in d.items():
            if isinstance(v, dict):
                html += f"<tr><td style='padding:2px 6px;font-weight:600;'>{k}</td><td style='padding:2px 6px;'>{render_nested_dict(v)}</td></tr>"
            else:
                html += f"<tr><td style='padding:2px 6px;font-weight:600;'>{k}</td><td style='padding:2px 6px;'>{v}</td></tr>"
        html += "</table>"
        return html

    # 构造 HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>请求信息全览</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                max-width: 1200px;
                margin: 30px auto;
                padding: 20px;
                background: #f0f2f5;
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 25px;
            }}
            .card h2 {{
                margin-top: 0;
                color: #34495e;
                border-left: 4px solid #3498db;
                padding-left: 12px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }}
            .info-table td {{
                padding: 6px 10px;
                border-bottom: 1px solid #eee;
                vertical-align: top;
            }}
            .info-table .label {{
                font-weight: 600;
                width: 25%;
                color: #555;
                background: #f8f9fa;
            }}
            .info-table .value {{
                color: #2c3e50;
                word-break: break-all;
            }}
            .nested-table td {{
                border-bottom: 1px dashed #ddd;
                padding: 4px 6px;
            }}
            .badge {{
                background: #3498db;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
            }}
            .footer {{
                text-align: center;
                color: #888;
                font-size: 13px;
                margin-top: 20px;
            }}
            details {{
                margin-top: 8px;
            }}
            summary {{
                cursor: pointer;
                color: #2980b9;
                font-weight: 600;
            }}
            .json-display {{
                background: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                overflow-x: auto;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>📊 完整请求信息</h1>

        <!-- 客户端基本信息 -->
        <div class="card">
            <h2>🌐 客户端信息</h2>
            <table class="info-table">
                <tr><td class="label">IP 地址</td><td class="value"><strong>{info['client']['ip']}</strong></td></tr>
                <tr><td class="label">端口</td><td class="value">{info['client']['port']}</td></tr>
            </table>
        </div>

        <!-- 地理位置 -->
        <div class="card">
            <h2>📍 地理位置</h2>
            <table class="info-table">
                {render_dict_table(info['location'])}
            </table>
        </div>

        <!-- 服务端信息 -->
        <div class="card">
            <h2>🖥️ 服务端信息</h2>
            <table class="info-table">
                {render_dict_table(info['server'])}
            </table>
        </div>

        <!-- 请求详情 -->
        <div class="card">
            <h2>📨 请求详情</h2>
            <table class="info-table">
                <tr><td class="label">方法</td><td class="value">{info['request']['method']}</td></tr>
                <tr><td class="label">路径</td><td class="value">{info['request']['path']}</td></tr>
                <tr><td class="label">完整 URL</td><td class="value" style="word-break:break-all;">{info['request']['full_url']}</td></tr>
                <tr><td class="label">查询参数</td><td class="value"><pre style="margin:0;">{json.dumps(info['request']['query_params'], indent=2, ensure_ascii=False)}</pre></td></tr>
                <tr><td class="label">路径参数</td><td class="value"><pre style="margin:0;">{json.dumps(info['request']['path_params'], indent=2, ensure_ascii=False)}</pre></td></tr>
            </table>
        </div>

        <!-- User-Agent 解析 -->
        <div class="card">
            <h2>🤖 User-Agent 解析</h2>
            <table class="info-table">
                <tr><td class="label">浏览器</td><td class="value">{info['request']['user_agent_parsed'].get('browser', '未知')}</td></tr>
                <tr><td class="label">操作系统</td><td class="value">{info['request']['user_agent_parsed'].get('os', '未知')}</td></tr>
                <tr><td class="label">设备</td><td class="value">{info['request']['user_agent_parsed'].get('device', '未知')}</td></tr>
            </table>
        </div>

        <!-- 请求头（可折叠） -->
        <div class="card">
            <h2>📋 请求头</h2>
            <details>
                <summary>点击展开/收起</summary>
                <div class="json-display">{json.dumps(info['request']['headers'], indent=2, ensure_ascii=False)}</div>
            </details>
        </div>

        <!-- Cookies -->
        <div class="card">
            <h2>🍪 Cookies</h2>
            <details>
                <summary>点击展开/收起</summary>
                <div class="json-display">{json.dumps(info['request']['cookies'], indent=2, ensure_ascii=False)}</div>
            </details>
        </div>

        <!-- 完整 JSON 日志（可折叠） -->
        <div class="card">
            <h2>📦 完整原始数据 (JSON)</h2>
            <details>
                <summary>点击展开/收起</summary>
                <div class="json-display">{json.dumps(info, indent=2, ensure_ascii=False, default=str)}</div>
            </details>
        </div>

        <div class="footer">
            🕒 {info['timestamp']} &nbsp;|&nbsp; 所有信息均已记录到日志文件 <code>{LOG_FILE}</code>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="192.168.63.57", port=8001)