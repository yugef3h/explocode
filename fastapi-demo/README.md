# FastAPI 双服务微服务示例

两个独立 FastAPI 服务，演示服务间 HTTP 调用：

| 服务 | 端口 | 职责 |
|------|------|------|
| `user-service` | 8001 | 用户查询 |
| `order-service` | 8002 | 订单管理，创建订单时校验用户 |

## 本地开发

```bash
# 安装依赖（各服务独立 venv 亦可）
pip install -r services/user-service/requirements.txt
pip install -r services/order-service/requirements.txt

# 终端 1
uvicorn app.main:app --reload --port 8001 --app-dir services/user-service

# 终端 2
USER_SERVICE_URL=http://127.0.0.1:8001 uvicorn app.main:app --reload --port 8002 --app-dir services/order-service
```

或使用 Makefile：

```bash
make install
make dev-user    # 终端 1
make dev-order   # 终端 2
```

## Docker Compose

```bash
docker compose up --build
```

- User API: http://localhost:8001/docs
- Order API: http://localhost:8002/docs

## 快速验证

```bash
# 创建用户
curl -X POST http://localhost:8001/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"alice"}'

# 创建订单（user_id 需存在）
curl -X POST http://localhost:8002/orders \
  -H 'Content-Type: application/json' \
  -d '{"user_id":1,"item":"book","amount":29.9}'
```
