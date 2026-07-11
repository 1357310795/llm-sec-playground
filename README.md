# LLM Security Playground

LLM Security Playground 是一个用于学习和演示大模型安全风险的前后端 Web 靶场。项目包含 Django 后端和 React/Vite 前端，覆盖角色绕过、指令优先级、输入混淆、RAG 间接提示注入、恶意 JSON Schema、Agent 工具误用等训练场景。

> 本项目面向授权教学和防御研究。场景中的 flag、文档、工具调用和邮件均为沙盒模拟数据，不会访问真实外部系统。

## 项目结构

```text
backend/    Django + Django REST Framework 后端
frontend/   React + Vite 前端
```

常用入口：

- 前端页面：`/`
- API：`/api/`
- Django Admin：`/admin/`
- OpenAPI Schema：`/api/schema/`
- Swagger UI：`/api/swagger/`

## 环境要求

- Python 3.12+
- uv
- Node.js 18+
- pnpm
- nginx（生产部署）

## 本地开发

### 1. 后端配置

```bash
cd backend
cp .env.example .env
```

按需修改 `.env`：

```env
DJANGO_SECRET_KEY="change-me"
DJANGO_DEBUG="true"
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
DJANGO_DISABLE_CSRF="false"
DJANGO_CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
DJANGO_CORS_ALLOW_ALL_ORIGINS="true"
DJANGO_STATIC_URL="/static/"
DJANGO_STATIC_ROOT="./staticfiles"

OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_API_KEY="sk-xxx"
OPENAI_MODEL="qwen3-14b"

# 用于 response_format / JSON Schema 约束解码，建议使用支持该能力的 OpenAI 官方兼容模型
OPENAI2_BASE_URL="https://api.openai.com/v1"
OPENAI2_API_KEY="sk-xxx"
OPENAI2_MODEL="gpt-4o"
```

安装依赖并初始化数据库：

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_scenarios
uv run python manage.py createsuperuser
```

启动后端：

```bash
uv run python manage.py runserver 127.0.0.1:8000
```

### 2. 前端配置

```bash
cd frontend
pnpm install
```

开发模式默认 API 地址来自 `frontend/src/api/client.ts`：

```ts
http://127.0.0.1:8000/api
```

启动前端：

```bash
pnpm dev
```

访问 Vite 输出的本地地址即可。

## 生产部署：nginx 静态前端 + Django 后端

推荐部署方式：

- nginx 直接 serve 前端构建产物
- nginx 将 `/api/` 和 `/admin/` 反向代理到 Django 后端
- Django 只监听本机地址，例如 `127.0.0.1:8000`

### 1. 后端生产环境变量

在 `backend/.env` 中配置，例如：

```env
DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
DJANGO_DEBUG="false"
DJANGO_ALLOWED_HOSTS="your-domain.com,127.0.0.1,localhost"
DJANGO_DISABLE_CSRF="true"
DJANGO_CSRF_TRUSTED_ORIGINS="http://your-domain.com"
DJANGO_CORS_ALLOWED_ORIGINS="http://your-domain.com"
DJANGO_CORS_ALLOW_ALL_ORIGINS="false"
DJANGO_STATIC_URL="/static/"
DJANGO_STATIC_ROOT="/var/www/llm-sec-playground/backend/staticfiles"
DJANGO_MEDIA_URL="/media/"
DJANGO_MEDIA_ROOT="/var/www/llm-sec-playground/backend/media"

DB_ENGINE="django.db.backends.sqlite3"
DB_NAME="/var/www/llm-sec-playground/backend/db.sqlite3"

OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_API_KEY="sk-xxx"
OPENAI_MODEL="qwen3-14b"
OPENAI2_BASE_URL="https://api.openai.com/v1"
OPENAI2_API_KEY="sk-xxx"
OPENAI2_MODEL="gpt-4o"
OPENAI_TIMEOUT_SECONDS="30"
OPENAI_MAX_TOKENS="700"
OPENAI_TEMPERATURE="0.2"
```

说明：

- 如果通过 nginx 同源代理 `/api/`，通常可以设置 `DJANGO_DISABLE_CSRF=true` 简化 API 调用。
- 如果要启用 CSRF，请保持 `DJANGO_DISABLE_CSRF=false`，并正确配置 `DJANGO_CSRF_TRUSTED_ORIGINS`。
- 如果改用 PostgreSQL/MySQL，需要同时安装对应 Django 数据库驱动。

### 2. 后端初始化

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py seed_scenarios
uv run python manage.py createsuperuser
uv run python manage.py collectstatic --noinput
```

启动后端示例：

```bash
uv run python manage.py runserver 127.0.0.1:8000
```

生产环境建议使用 gunicorn、uwsgi 或其他 WSGI/ASGI 进程管理方式，并由 systemd/supervisor 托管。

### 3. 前端构建

构建时将 API 地址设置为同源 `/api`：

```bash
cd frontend
pnpm install
VITE_API_BASE=/api pnpm build
```

构建产物默认在：

```text
frontend/dist
```

将该目录部署到 nginx 静态目录，例如：

```text
/var/www/llm-sec-playground/frontend/dist
```

### 4. nginx 配置示例

将下面配置保存为 nginx server 配置，例如 `/etc/nginx/conf.d/llm-sec-playground.conf`。

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/llm-sec-playground/frontend/dist;
    index index.html;

    client_max_body_size 10m;

    location /assets/ {
        try_files $uri =404;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/llm-sec-playground/backend/staticfiles/;
        access_log off;
        expires 30d;
    }

    location /media/ {
        alias /var/www/llm-sec-playground/backend/media/;
        access_log off;
        expires 30d;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

检查并重载 nginx：

```bash
nginx -t
systemctl reload nginx
```

## 常用管理命令

后端检查：

```bash
cd backend
uv run python manage.py check
```

运行测试：

```bash
cd backend
uv run pytest
```

重新写入训练场景种子数据：

```bash
cd backend
uv run python manage.py seed_scenarios
```

生成静态文件：

```bash
cd backend
uv run python manage.py collectstatic --noinput
```

前端类型检查：

```bash
cd frontend
pnpm run typecheck
```

前端构建：

```bash
cd frontend
VITE_API_BASE=/api pnpm build
```

## 部署排错

### collectstatic 报 STATIC_ROOT 未配置

确认 `.env` 中有：

```env
DJANGO_STATIC_ROOT="/var/www/llm-sec-playground/backend/staticfiles"
```

然后重新运行：

```bash
uv run python manage.py collectstatic --noinput
```

### API 报 CSRF Failed

如果你使用 nginx 同源代理，且希望禁用 CSRF：

```env
DJANGO_DISABLE_CSRF="true"
```

修改 `.env` 后必须重启后端进程。该配置会同时移除 Django CSRF middleware，并禁用 DRF 默认 SessionAuthentication，避免 API 仍触发 CSRF 检查。

### 前端请求到了 127.0.0.1:8000

生产构建时必须设置：

```bash
VITE_API_BASE=/api pnpm build
```

否则前端会使用默认开发 API 地址。

### Admin 静态样式丢失

确认执行过：

```bash
uv run python manage.py collectstatic --noinput
```

并确认 nginx 的 `/static/` alias 指向 `DJANGO_STATIC_ROOT`。