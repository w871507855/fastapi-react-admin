# FastAPI + React 通用后台管理系统

一个开箱即用的通用后台管理系统，包含**用户管理、角色管理、权限管理、登录认证**。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Alembic |
| 数据库 | MySQL 8 |
| 认证 | JWT + bcrypt |
| 前端 | React 18 / Vite / 纯 JavaScript |
| UI | Ant Design 5 / zustand / axios |

## 功能特性

- 用户登录（JWT）、当前用户信息、动态菜单
- 用户管理：分页查询、新增/编辑/删除、启停、重置密码、分配角色
- 角色管理：CRUD、菜单+按钮权限分配（树形勾选）
- 权限管理：目录/菜单/按钮三级权限树 CRUD
- RBAC 权限校验：后端接口级校验 + 前端按钮级显隐
- 超级管理员自动放行所有权限

## 项目结构

```
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── core/             # 配置 / 安全(JWT+bcrypt) / 依赖 / RBAC
│   │   ├── db/               # 数据库会话
│   │   ├── models/           # User / Role / Permission
│   │   ├── schemas/          # Pydantic 模型
│   │   └── api/v1/           # auth / users / roles / permissions / stats
│   ├── alembic/              # 数据库迁移
│   ├── scripts/seed.py       # 初始化种子数据
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 # React 前端
    ├── src/
    │   ├── api/              # axios 封装 + 接口定义
    │   ├── store/auth.js     # zustand 登录态
    │   ├── layouts/          # 后台布局 + 动态菜单
    │   ├── components/       # AuthButton 权限按钮
    │   └── pages/            # 登录/首页/用户/角色/权限
    └── vite.config.js        # /api 代理
```

## 快速开始

### 1. 初始化数据库

```bash
# 创建数据库（根据你的 MySQL 调整账号密码）
mysql -uroot -p -e "CREATE DATABASE IF NOT EXISTS fastapi_admin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. 启动后端

```bash
cd backend
cp .env.example .env        # 修改 .env 中的数据库密码、SECRET_KEY
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head        # 建表
python -m scripts.seed      # 初始化默认管理员/角色/权限

uvicorn app.main:app --reload --port 8000
```

默认管理员：`admin / admin123`（超级管理员，拥有全部权限）

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

前端开发服务器已配置 `/api` 代理到 `http://localhost:8000`。

## 常用接口

| 接口 | 说明 |
|---|---|
| `POST /api/v1/auth/login` | 登录，返回 token |
| `GET /api/v1/auth/me` | 当前用户信息 + 权限码 |
| `GET /api/v1/auth/menus` | 当前用户可见菜单树 |
| `GET /api/v1/users` | 用户分页列表 |
| `GET /api/v1/roles` | 角色分页列表 |
| `GET /api/v1/permissions/tree` | 权限树 |
| `GET /api/v1/stats` | 首页统计 |

统一响应格式：`{ "code": 0, "message": "ok", "data": ... }`，`code != 0` 表示失败。

## 权限设计

- `permissions.type`：`1` 目录、`2` 菜单、`3` 按钮
- 按钮权限编码格式：`system:user:add` 等，后端通过 `require_permission("system:user:add")` 校验
- 前端 `<AuthButton code="system:user:add">` 控制按钮显隐
- 超级管理员（`is_superuser=true`）跳过权限校验

## 生产部署注意

- 修改 `.env` 中 `SECRET_KEY` 为随机字符串
- 将 `DEBUG` 设为 `false`
- 构建前端：`npm run build`，产物在 `frontend/dist`
