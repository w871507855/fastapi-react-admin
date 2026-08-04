# AGENTS.md

FastAPI + React 通用后台（用户/角色/权限管理，RBAC）。后端 `backend/`，前端 `frontend/`。无测试、无 lint 配置；验证靠冒烟测试。

## 后端 (backend/)

- venv 在 `backend/.venv`（uv 创建，Python 3.11），不在仓库根。所有命令以 `backend/` 为 CWD。
- `.env`（在 `backend/`，参考 `.env.example`）必须存在：含 MySQL 连接与 `SECRET_KEY`。已 gitignore，不提交。
- 启动：`backend/.venv/bin/python main.py`（或 `backend/.venv/bin/uvicorn main:app --port 8000`），入口为 `backend/main.py`（前端已配 `/api` 代理到 8000）。
- 建库/建表/初始化：`alembic upgrade head` 后 `backend/.venv/bin/python -m scripts.seed`。种子写入超级管理员 `admin/admin123`、角色、权限树。
- Alembic 与 seed 脚本必须**先**调 `app.core.config.load_dotenv_if_exists()` 再 import app 模块（settings 在 import 时读取）。见 `alembic/env.py`、`scripts/seed.py`。
- 新增模型后需在 `app/models/__init__.py` 导入，否则 `alembic revision --autogenerate` 检测不到。
- `db/session.py` 用 `autoflush=True` —— 不要改回 False，seed 的关联写入依赖它。
- 统一响应 `{code, message, data}`（`app/schemas/common.py: success()`）；但 `HTTPException` 返回 FastAPI 原生 `{"detail": ...}`，前端拦截器同时读取 `message`/`detail`。

## 权限模型

- `permissions.type`: 1 目录 / 2 菜单 / 3 按钮；按钮 code 形如 `system:user:add`。
- 后端用 `Depends(require_permission("system:user:add"))` 校验；`is_superuser` 直接放行。
- 新增菜单/按钮后，前端侧边菜单来自 `GET /api/v1/auth/menus`（superuser 返回全量）。

## 前端 (frontend/)

- 纯 JS（无 TypeScript），JSX。Vite dev（5173），`npm run build` 做构建校验。
- 页面在 `src/pages/system/*/index.jsx` 时，import `api`/`components` 需 `../../../` 三级相对路径（易错）。
- 按钮权限用 `<AuthButton code="..." />`（无权限渲染 null）。
- axios 拦截器 `src/api/request.js`：自动带 Bearer token；401 自动登出跳 `/login`。
