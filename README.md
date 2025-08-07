# SecureDrop - 安全文件交换平台

SecureDrop 是一个高度安全、策略可控的文件交换平台。管理员能够通过生成功能强大的、可定制策略的访问令牌，来精确管理临时用户的文件上传和下载行为。

## ✨ 功能特性

- **策略驱动的访问令牌**:
  - 设置过期时间
  - 限制使用次数
  - 允许/禁止上传和下载
  - 自定义访客页面标题和欢迎信息
  - 限制上传文件类型、大小
  - 基于文件夹授权下载
- **前后端分离架构**:
  - **后端**: 基于 FastAPI (Python) 构建，性能卓越。
  - **前端**: 基于 React 和 Ant Design 构建，界面专业美观。
- **单服务部署**: 前端构建后由 FastAPI 统一提供服务，简化部署。
- **安全设计**:
  - JWT (JSON Web Tokens) 用于管理员和访客会话认证。
  - 密码使用 bcrypt 哈希存储。
  - 防止路径遍历等常见 Web 漏洞。

## 🛠️ 技术栈

- **后端**: FastAPI, SQLAlchemy, Pydantic
- **前端**: React, Ant Design, React Router, Axios
- **数据库**: SQLite
- **UI 框架**: Ant Design

## 🚀 快速开始

### 先决条件

- Python 3.8+
- Node.js 16+ 和 npm
- (Windows) PowerShell 或 CMD

### 安装与配置

1.  **克隆仓库**:
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  **后端设置**:
    - **创建虚拟环境**:
      ```powershell
      python -m venv .venv
      ```
    - **激活虚拟环境**:
      ```powershell
      .\.venv\Scripts\activate.bat
      ```
    - **安装 Python 依赖**:
      ```powershell
      pip install -r secure-drop-backend/requirements.txt
      ```
    - **配置**: 复制 `secure-drop-backend/.env.example` 为 `secure-drop-backend/.env` 文件，根据需要调整数据库路径、密钥等设置。

3.  **前端设置**:
    - **进入前端目录**:
      ```powershell
      cd secure-drop-frontend
      ```
    - **安装 Node.js 依赖**:
      ```powershell
      npm install
      ```
    - **返回根目录**:
      ```powershell
      cd ..
      ```

### 运行项目

#### 开发模式

1.  **启动后端**:
    - 打开一个终端，进入 `secure-drop-backend` 目录，激活虚拟环境，然后运行:
      ```powershell
      uvicorn main:app --reload
      ```
    - 后端服务将运行在 `http://127.0.0.1:8000`。

2.  **启动前端**:
    - 打开**另一个**终端，进入 `secure-drop-frontend` 目录，然后运行:
      ```powershell
      npm start
      ```
    - 前端开发服务器将运行在 `http://localhost:3000` (或其他可用端口)。

#### 生产模式 (单服务部署)

1.  **构建前端应用**:
    - 进入 `secure-drop-frontend` 目录，运行:
      ```powershell
      npm run build
      ```
    - 这将在 `secure-drop-frontend` 下创建一个 `build` 目录。

2.  **创建初始管理员**:
    - 打开一个终端，进入 `secure-drop-backend` 目录，激活虚拟环境，然后运行 (将 `<your_password>` 替换为您的安全密码):
      ```powershell
      python create_admin.py --password <your_password>
      ```

3.  **启动生产服务器**:
    - 在项目根目录，直接运行启动脚本:
      ```powershell
      .\start_server.cmd
      ```
    - 或者手动执行:
      ```powershell
      cd secure-drop-backend
      ..\.venv\Scripts\activate.bat
      uvicorn main:app --host 0.0.0.0 --port 8000
      ```
    - 现在，您可以直接通过 `http://<your_server_ip>:8000` 访问整个应用。

## 📄 开源许可

该项目采用 MIT 许可。详情请见 [LICENSE](LICENSE) 文件。
