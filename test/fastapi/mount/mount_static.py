from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

BASE_DIR = Path(__file__).parent.parent
print(BASE_DIR)
# 设置要挂载前端页面的路径
static_dir = BASE_DIR / "static"

app = FastAPI()

app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8003)