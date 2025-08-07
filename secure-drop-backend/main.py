"""
FastAPI 应用主入口文件
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from domain.database import init_db
from interface import auth, admin, guest
from utils.logger import log

# 创建 FastAPI 应用实例
app = FastAPI(
    title="SecureDrop - 安全文件交换平台",
    description="一个高度安全、策略可控的文件交换平台。",
    version="1.0.0"
)

# 配置 CORS 中间件
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:12167", # 允许您的前端开发服务器端口
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    应用启动时执行的事件。
    """
    log.info("应用开始启动...")
    # 初始化数据库，如果表不存在则创建
    init_db()
    log.info("应用启动完成。")

# 包含认证路由
app.include_router(auth.router)
# 包含管理员路由
app.include_router(admin.router)
# 包含访客路由
app.include_router(guest.router)

# --- 托管前端静态文件 ---
# 注意：这个路径是相对于后端项目根目录的
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "secure-drop-frontend", "build")

# 1. 挂载 static 目录
if os.path.exists(os.path.join(FRONTEND_BUILD_DIR, "static")):
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(FRONTEND_BUILD_DIR, "static")),
        name="static",
    )

# 2. 根路径和其他静态文件（如 manifest.json, favicon.ico）
if os.path.exists(FRONTEND_BUILD_DIR):
    # 创建一个虚拟的 StaticFiles 实例来获取文件路径
    static_files_app = StaticFiles(directory=FRONTEND_BUILD_DIR)
    
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(request: Request, full_path: str):
        """
        Catch-all 路由，用于服务 React 应用。
        如果请求的路径是 API 路由，FastAPI 会优先匹配，不会进入这里。
        如果不是 API 路由，则尝试作为静态文件提供。
        如果找不到对应的静态文件，则返回 index.html，让前端路由接管。
        """
        # 检查是否是 API 请求
        if full_path.startswith("api/"):
            # 理论上 FastAPI 的路由会先匹配，但作为保险
            raise HTTPException(status_code=404, detail="Not Found")

        # 尝试查找静态文件
        static_file_path = os.path.join(FRONTEND_BUILD_DIR, full_path)
        if os.path.isfile(static_file_path):
            return await static_files_app.get_response(full_path, request.scope)
        
        # 如果找不到文件，则返回 index.html
        index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        return FileResponse(index_path)

    @app.get("/", include_in_schema=False)
    async def root():
        """
        根路径，返回 index.html。
        """
        index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        return FileResponse(index_path)
else:
    log.warning(f"前端构建目录未找到: {FRONTEND_BUILD_DIR}。将只提供 API 服务。")
