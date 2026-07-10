import requests

# API 地址
url = "http://localhost:8000/file_parse"

# 要解析的 PDF 文件
pdf_path = r"C:\Users\YuanYi\Desktop\LangChain.pdf"

# 发送 POST 请求
with open(pdf_path, 'rb') as f:
    files = {'files': f}
    # 对于本地 pipeline 后端，无需 server_url
    data = {'backend': 'pipeline'}
    response = requests.post(url, files=files, data=data)

# 处理返回结果
if response.status_code == 200:
    print(response.json())  # 或进一步处理
else:
    print(f"解析失败: {response.text}")